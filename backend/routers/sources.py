from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import RegulatorySource, Industry

router = APIRouter(prefix="/api/sources", tags=["sources"])


class SourceCreate(BaseModel):
    name: str
    source_type: str  # "federal_register", "rss", "state_site"
    url: str
    check_interval_minutes: int = 60


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """List all regulatory sources."""
    sources = db.query(RegulatorySource).all()
    return {
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "source_type": s.source_type,
                "url": s.url,
                "is_active": s.is_active,
                "last_checked": s.last_checked.isoformat() if s.last_checked else None,
                "check_interval_minutes": s.check_interval_minutes,
            }
            for s in sources
        ]
    }


@router.post("")
def create_source(data: SourceCreate, db: Session = Depends(get_db)):
    """Add a new regulatory source."""
    source = RegulatorySource(
        name=data.name,
        source_type=data.source_type,
        url=data.url,
        check_interval_minutes=data.check_interval_minutes,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "url": source.url,
    }


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a regulatory source."""
    source = db.query(RegulatorySource).filter(RegulatorySource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(source)
    db.commit()
    return {"status": "deleted", "id": source_id}


@router.get("/industries")
def list_industries(db: Session = Depends(get_db)):
    """List all industries."""
    industries = db.query(Industry).all()
    return {
        "industries": [
            {
                "id": i.id,
                "name": i.name,
                "slug": i.slug,
                "description": i.description,
            }
            for i in industries
        ]
    }
