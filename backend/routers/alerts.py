from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Alert, Regulation, Subscriber

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(
    status: Optional[str] = None,
    subscriber_id: Optional[int] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List alerts with optional filters."""
    query = db.query(Alert).order_by(Alert.created_at.desc())

    if status:
        query = query.filter(Alert.delivery_status == status)
    if subscriber_id:
        query = query.filter(Alert.subscriber_id == subscriber_id)

    total = query.count()
    alerts = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "alerts": [
            {
                "id": a.id,
                "subscriber": {"id": a.subscriber.id, "name": a.subscriber.name, "email": a.subscriber.email},
                "regulation": {
                    "id": a.regulation.id,
                    "title": a.regulation.title,
                    "impact_level": a.regulation.impact_level,
                },
                "delivery_status": a.delivery_status,
                "is_read": a.is_read,
                "sent_at": a.sent_at.isoformat() if a.sent_at else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ],
    }


@router.patch("/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Not found"}, 404

    alert.is_read = True
    db.commit()
    return {"status": "ok", "alert_id": alert_id}


@router.get("/stats")
def alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics."""
    total = db.query(Alert).count()
    sent = db.query(Alert).filter(Alert.delivery_status == "sent").count()
    pending = db.query(Alert).filter(Alert.delivery_status == "pending").count()
    failed = db.query(Alert).filter(Alert.delivery_status == "failed").count()

    return {
        "total": total,
        "sent": sent,
        "pending": pending,
        "failed": failed,
    }
