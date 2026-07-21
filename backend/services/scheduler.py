from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import SessionLocal
from models import RegulatorySource, Regulation, Subscriber, Alert, Industry, SourceSnapshot, RegulationVersion, Citation
from services.diffing import normalize_content, content_hash, deterministic_diff
from scrapers import FederalRegisterScraper, RSSMonitor, StateRegulatoryScraper
from services.summarizer import RegulationSummarizer
from services.alerter import AlertService


class MonitoringScheduler:
    """Orchestrates periodic monitoring of regulatory sources."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.federal_scraper = FederalRegisterScraper()
        self.rss_monitor = RSSMonitor()
        self.state_scraper = StateRegulatoryScraper()
        self.summarizer = RegulationSummarizer()
        self.alerter = AlertService()

    def start(self):
        """Start the monitoring scheduler."""
        # Check Federal Register every hour
        self.scheduler.add_job(
            self.check_federal_register,
            IntervalTrigger(hours=1),
            id="federal_register",
            name="Federal Register Monitor",
            replace_existing=True,
        )

        # Check RSS feeds every 30 minutes
        self.scheduler.add_job(
            self.check_rss_feeds,
            IntervalTrigger(minutes=30),
            id="rss_feeds",
            name="RSS Feed Monitor",
            replace_existing=True,
        )

        # Check state sites every 4 hours
        self.scheduler.add_job(
            self.check_state_sites,
            IntervalTrigger(hours=4),
            id="state_sites",
            name="State Regulatory Monitor",
            replace_existing=True,
        )

        self.scheduler.start()

    def stop(self):
        """Stop the monitoring scheduler."""
        self.scheduler.shutdown()

    async def check_federal_register(self):
        """Check Federal Register for new documents."""
        print(f"[{datetime.now(timezone.utc)}] Checking Federal Register...")
        try:
            documents = await self.federal_scraper.fetch_recent_documents(days_back=1)
            await self._process_documents(documents)
        except Exception as e:
            print(f"Error checking Federal Register: {e}")

    async def check_rss_feeds(self):
        """Check all RSS feeds for new entries."""
        print(f"[{datetime.now(timezone.utc)}] Checking RSS feeds...")
        try:
            all_feeds = await self.rss_monitor.fetch_all_feeds()
            for industry, entries in all_feeds.items():
                await self._process_documents(entries, default_industry=industry)
        except Exception as e:
            print(f"Error checking RSS feeds: {e}")

    async def check_state_sites(self):
        """Check state regulatory sites for updates."""
        print(f"[{datetime.now(timezone.utc)}] Checking state sites...")
        try:
            all_states = await self.state_scraper.scrape_all_states()
            for state, updates in all_states.items():
                await self._process_documents(updates)
        except Exception as e:
            print(f"Error checking state sites: {e}")

    async def _process_documents(self, documents: list[dict], default_industry: str = None):
        """Process new documents: summarize and alert subscribers."""
        db = SessionLocal()
        try:
            for doc in documents:
                # Skip if already in database
                if doc.get("document_number"):
                    existing = db.query(Regulation).filter(
                        Regulation.document_number == doc["document_number"]
                    ).first()
                    if existing:
                        continue

                # Classify industry
                try:
                    industries = await self.summarizer.classify_industry(
                        doc.get("title", ""), doc.get("abstract", "")
                    )
                except Exception:
                    industries = [default_industry] if default_industry else ["general"]

                # Generate summary
                try:
                    summary_result = await self.summarizer.summarize(
                        doc.get("title", ""),
                        doc.get("abstract", ""),
                        doc.get("raw_content", ""),
                    )
                except Exception as e:
                    print(f"Summarization failed for '{doc.get('title', '')}': {e}")
                    summary_result = {"summary": doc.get("abstract", ""), "impact_level": "medium"}

                # Find or create industry
                industry_name = industries[0] if industries else (default_industry or "general")
                industry = db.query(Industry).filter(Industry.slug == industry_name).first()

                source = db.query(RegulatorySource).filter(RegulatorySource.url == doc.get("source_url", "")).first()
                if not source and doc.get("source_url"):
                    source = RegulatorySource(
                        name=doc.get("feed_name") or doc.get("state") or doc.get("source_type", "source"),
                        source_type=doc.get("source_type", "unknown"),
                        url=doc["source_url"],
                    )
                    db.add(source)
                    db.flush()

                source_content = doc.get("raw_content") or doc.get("abstract") or doc.get("title", "")
                snapshot = SourceSnapshot(
                    source_id=source.id if source else 0,
                    content=source_content,
                    content_type="text/plain",
                    sha256=content_hash(source_content),
                ) if source else None
                if snapshot:
                    db.add(snapshot)
                    db.flush()

                # Store regulation
                regulation = Regulation(
                    title=doc.get("title", ""),
                    document_number=doc.get("document_number"),
                    abstract=doc.get("abstract", ""),
                    summary=summary_result["summary"],
                    impact_level=summary_result["impact_level"],
                    publication_date=datetime.fromisoformat(doc["publication_date"]) if doc.get("publication_date") else None,
                    effective_date=datetime.fromisoformat(doc["effective_date"]) if doc.get("effective_date") else None,
                    source_url=doc.get("source_url", ""),
                    raw_content=source_content,
                    source_id=source.id if source else None,
                    industry_id=industry.id if industry else None,
                )
                db.add(regulation)
                db.commit()
                db.refresh(regulation)
                if snapshot:
                    previous = db.query(RegulationVersion).filter(RegulationVersion.regulation_id == regulation.id).order_by(RegulationVersion.version_number.desc()).first()
                    previous_content = previous.normalized_content if previous else ""
                    db.add(RegulationVersion(
                        regulation_id=regulation.id,
                        snapshot_id=snapshot.id,
                        version_number=(previous.version_number + 1) if previous else 1,
                        normalized_content=normalize_content(source_content),
                        content_hash=content_hash(source_content),
                        diff_from_previous=deterministic_diff(previous_content, source_content)["unified_diff"] if previous else None,
                    ))
                    db.add(Citation(
                        regulation_id=regulation.id,
                        snapshot_id=snapshot.id,
                        location="source abstract or captured content",
                        quote=source_content[:1000],
                    ))
                    db.commit()

                # Alert subscribers
                await self._notify_subscribers(db, regulation, industry)

        finally:
            db.close()

    async def _notify_subscribers(self, db: Session, regulation: Regulation, industry):
        """Send alerts to relevant subscribers."""
        if not industry:
            return

        subscribers = (
            db.query(Subscriber)
            .filter(Subscriber.is_active == True)
            .filter(Subscriber.industries.any(Industry.id == industry.id))
            .all()
        )

        if regulation.status != "approved":
            return

        for subscriber in subscribers:
            delivery_key = f"regulation:{regulation.id}:subscriber:{subscriber.id}"
            existing_alert = db.query(Alert).filter(Alert.delivery_key == delivery_key).first()
            if existing_alert:
                continue
            alert = Alert(
                subscriber_id=subscriber.id,
                regulation_id=regulation.id,
                delivery_key=delivery_key,
                delivery_status="pending",
            )
            db.add(alert)
            db.flush()

            result = self.alerter.send_alert(
                to_email=subscriber.email,
                to_name=subscriber.name,
                regulation={
                    "title": regulation.title,
                    "summary": regulation.summary,
                    "impact_level": regulation.impact_level,
                    "effective_date": str(regulation.effective_date) if regulation.effective_date else None,
                    "source_url": regulation.source_url,
                },
            )

            alert.delivery_status = result["status"]
            if result["status"] == "sent":
                alert.sent_at = datetime.now(timezone.utc)

            db.commit()
