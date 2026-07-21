from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import require_reviewer
from database import get_db
from models import AuditEvent, Citation, Regulation, ReviewDecision

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class ReviewRequest(BaseModel):
    decision: str
    notes: str | None = None


@router.post("/{regulation_id}")
def review_regulation(
    regulation_id: int,
    data: ReviewRequest,
    role: str = Depends(require_reviewer),
    reviewer_id: int | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not reviewer_id:
        raise HTTPException(status_code=422, detail="X-Reviewer-Id header required")
    if data.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=422, detail="Decision must be approve or reject")
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    if data.decision == "approve" and not regulation.citations:
        raise HTTPException(status_code=409, detail="A source citation is required before approval")
    regulation.status = "approved" if data.decision == "approve" else "rejected"
    regulation.approved_at = datetime.now(timezone.utc) if data.decision == "approve" else None
    decision = ReviewDecision(regulation_id=regulation.id, reviewer_id=reviewer_id, decision=data.decision, notes=data.notes)
    db.add(decision)
    db.add(AuditEvent(action=f"regulation.{data.decision}", entity_type="regulation", entity_id=regulation.id, details=data.notes))
    db.commit()
    return {"id": regulation.id, "status": regulation.status}


@router.get("/{regulation_id}/citations")
def list_citations(regulation_id: int, db: Session = Depends(get_db)):
    citations = db.query(Citation).filter(Citation.regulation_id == regulation_id).all()
    return {"citations": [{"id": c.id, "snapshot_id": c.snapshot_id, "location": c.location, "quote": c.quote} for c in citations]}
