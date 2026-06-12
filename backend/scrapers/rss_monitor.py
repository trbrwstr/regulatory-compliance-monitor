import feedparser
import httpx
from datetime import datetime, timezone
from typing import Optional
from time import mktime


class RSSMonitor:
    """Monitors RSS feeds from regulatory bodies and industry organizations."""

    # Default feeds for monitored industries
    DEFAULT_FEEDS = {
        "fintech": [
            {
                "name": "SEC Rules",
                "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=RULE&dateb=&owner=include&count=40&search_text=&output=atom",
            },
            {
                "name": "CFPB Newsroom",
                "url": "https://www.consumerfinance.gov/about-us/newsroom/feed/",
            },
        ],
        "healthcare": [
            {
                "name": "FDA Press Releases",
                "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml",
            },
            {
                "name": "CMS Newsroom",
                "url": "https://www.cms.gov/newsroom/rss-feeds",
            },
        ],
        "food_service": [
            {
                "name": "FDA Food Safety",
                "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-safety/rss.xml",
            },
            {
                "name": "USDA Food Safety",
                "url": "https://www.fsis.usda.gov/feeds/fsis-recalls-rss-feed.xml",
            },
        ],
    }

    def __init__(self, feeds: Optional[dict] = None):
        self.feeds = feeds or self.DEFAULT_FEEDS

    async def fetch_feed(self, url: str) -> list[dict]:
        """Fetch and parse a single RSS feed."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        feed = feedparser.parse(response.text)
        entries = []

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)

            entries.append({
                "title": entry.get("title", ""),
                "abstract": entry.get("summary", ""),
                "source_url": entry.get("link", ""),
                "publication_date": published.isoformat() if published else None,
                "source_type": "rss",
            })

        return entries

    async def fetch_industry_feeds(self, industry: str) -> list[dict]:
        """Fetch all feeds for a given industry."""
        feeds = self.feeds.get(industry, [])
        all_entries = []

        for feed_config in feeds:
            try:
                entries = await self.fetch_feed(feed_config["url"])
                for entry in entries:
                    entry["feed_name"] = feed_config["name"]
                all_entries.extend(entries)
            except Exception as e:
                print(f"Error fetching feed {feed_config['name']}: {e}")

        return all_entries

    async def fetch_all_feeds(self) -> dict[str, list[dict]]:
        """Fetch all configured feeds across all industries."""
        results = {}
        for industry in self.feeds:
            results[industry] = await self.fetch_industry_feeds(industry)
        return results
