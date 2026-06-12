from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_db
from models import Subscriber, Industry

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


class SubscriberCreate(BaseModel):
    email: str
    name: str
    industries: list[str] = []


class SubscriberUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    industries: Optional[list[str]] = None


@router.get("")
def list_subscribers(db: Session = Depends(get_db)):
    """List all subscribers."""
    subscribers = db.query(Subscriber).all()
    return {
        "subscribers": [
            {
                "id": s.id,
                "email": s.email,
                "name": s.name,
                "is_active": s.is_active,
                "industries": [i.slug for i in s.industries],
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subscribers
        ]
    }


@router.post("")
def create_subscriber(data: SubscriberCreate, db: Session = Depends(get_db)):
    """Create a new subscriber."""
    existing = db.query(Subscriber).filter(Subscriber.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")

    subscriber = Subscriber(email=data.email, name=data.name)

    # Link industries
    if data.industries:
        industries = db.query(Industry).filter(Industry.slug.in_(data.industries)).all()
        subscriber.industries = industries

    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    return {
        "id": subscriber.id,
        "email": subscriber.email,
        "name": subscriber.name,
        "industries": [i.slug for i in subscriber.industries],
    }


@router.put("/{subscriber_id}")
def update_subscriber(subscriber_id: int, data: SubscriberUpdate, db: Session = Depends(get_db)):
    """Update a subscriber."""
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    if data.name is not None:
        subscriber.name = data.name
    if data.is_active is not None:
        subscriber.is_active = data.is_active
    if data.industries is not None:
        industries = db.query(Industry).filter(Industry.slug.in_(data.industries)).all()
        subscriber.industries = industries

    db.commit()
    db.refresh(subscriber)

    return {
        "id": subscriber.id,
        "email": subscriber.email,
        "name": subscriber.name,
        "is_active": subscriber.is_active,
        "industries": [i.slug for i in subscriber.industries],
    }


@router.delete("/{subscriber_id}")
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    """Delete a subscriber."""
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    db.delete(subscriber)
    db.commit()
    return {"status": "deleted", "id": subscriber_id}
