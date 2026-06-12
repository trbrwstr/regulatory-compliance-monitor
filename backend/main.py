from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, SessionLocal
from models import Industry
from routers import alerts_router, subscriptions_router, sources_router, regulations_router
from services.scheduler import MonitoringScheduler


scheduler = MonitoringScheduler()


def seed_industries():
    """Seed default industries if not present."""
    db = SessionLocal()
    try:
        defaults = [
            {"name": "Fintech", "slug": "fintech", "description": "Financial technology and banking regulations"},
            {"name": "Healthcare", "slug": "healthcare", "description": "Healthcare and pharmaceutical regulations"},
            {"name": "Food Service", "slug": "food_service", "description": "Food safety and restaurant regulations"},
            {"name": "General", "slug": "general", "description": "General regulatory updates"},
        ]
        for ind in defaults:
            existing = db.query(Industry).filter(Industry.slug == ind["slug"]).first()
            if not existing:
                db.add(Industry(**ind))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    seed_industries()
    scheduler.start()
    yield
    # Shutdown
    scheduler.stop()


app = FastAPI(
    title="Regulatory Compliance Monitor",
    description="AI-powered regulatory monitoring with plain-English impact summaries",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regulations_router)
app.include_router(alerts_router)
app.include_router(subscriptions_router)
app.include_router(sources_router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "regulatory-compliance-monitor"}


@app.get("/api/dashboard/stats")
def dashboard_stats():
    """Get dashboard overview statistics."""
    from models import Regulation, Alert, Subscriber
    db = SessionLocal()
    try:
        total_regulations = db.query(Regulation).count()
        high_impact = db.query(Regulation).filter(Regulation.impact_level == "high").count()
        total_alerts = db.query(Alert).count()
        alerts_sent = db.query(Alert).filter(Alert.delivery_status == "sent").count()
        total_subscribers = db.query(Subscriber).filter(Subscriber.is_active == True).count()

        return {
            "total_regulations": total_regulations,
            "high_impact_regulations": high_impact,
            "total_alerts": total_alerts,
            "alerts_sent": alerts_sent,
            "active_subscribers": total_subscribers,
        }
    finally:
        db.close()


@app.post("/api/monitor/trigger")
async def trigger_monitoring():
    """Manually trigger a monitoring cycle (for testing)."""
    await scheduler.check_federal_register()
    return {"status": "triggered", "message": "Federal Register check initiated"}
