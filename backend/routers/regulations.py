from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Regulation, Industry

router = APIRouter(prefix="/api/regulations", tags=["regulations"])


@router.get("")
def list_regulations(
    industry: Optional[str] = None,
    impact_level: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List regulations with optional filters."""
    query = db.query(Regulation).order_by(Regulation.created_at.desc())

    if industry:
        query = query.join(Industry).filter(Industry.slug == industry)
    if impact_level:
        query = query.filter(Regulation.impact_level == impact_level)

    total = query.count()
    regulations = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "regulations": [
            {
                "id": r.id,
                "title": r.title,
                "document_number": r.document_number,
                "abstract": r.abstract,
                "summary": r.summary,
                "impact_level": r.impact_level,
                "publication_date": r.publication_date.isoformat() if r.publication_date else None,
                "effective_date": r.effective_date.isoformat() if r.effective_date else None,
                "source_url": r.source_url,
                "industry": r.industry.name if r.industry else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in regulations
        ],
    }


@router.get("/{regulation_id}")
def get_regulation(regulation_id: int, db: Session = Depends(get_db)):
    """Get a single regulation by ID."""
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        return {"error": "Not found"}, 404

    return {
        "id": regulation.id,
        "title": regulation.title,
        "document_number": regulation.document_number,
        "abstract": regulation.abstract,
        "summary": regulation.summary,
        "impact_level": regulation.impact_level,
        "publication_date": regulation.publication_date.isoformat() if regulation.publication_date else None,
        "effective_date": regulation.effective_date.isoformat() if regulation.effective_date else None,
        "source_url": regulation.source_url,
        "industry": regulation.industry.name if regulation.industry else None,
        "created_at": regulation.created_at.isoformat() if regulation.created_at else None,
    }
