from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import require_reviewer
from database import get_db
from models import PilotObservation, PilotRun
from services.pilot import close_pilot_run, create_pilot_run, record_observation

router = APIRouter(prefix="/api/pilots", tags=["pilots"])


class PilotCreate(BaseModel):
    name: str
    source_register: str


class ObservationCreate(BaseModel):
    source_url: str
    manual_found: bool
    product_found: bool
    correction_count: int = 0
    manual_latency_seconds: float | None = None
    product_latency_seconds: float | None = None
    time_saved_minutes: float | None = None
    notes: str | None = None


@router.post("")
def start_pilot(data: PilotCreate, reviewer_id: int, _: str = Depends(require_reviewer), db: Session = Depends(get_db)):
    run = create_pilot_run(db, data.name, reviewer_id, data.source_register)
    return {"id": run.id, "status": run.status, "created_at": run.created_at.isoformat()}


@router.post("/{run_id}/observations")
def add_observation(run_id: int, data: ObservationCreate, _: str = Depends(require_reviewer), db: Session = Depends(get_db)):
    if not db.query(PilotRun).filter(PilotRun.id == run_id).first():
        raise HTTPException(status_code=404, detail="Pilot run not found")
    observation = record_observation(db, run_id, **data.model_dump())
    return {"id": observation.id, "pilot_run_id": observation.pilot_run_id}


@router.post("/{run_id}/close")
def finish_pilot(run_id: int, _: str = Depends(require_reviewer), db: Session = Depends(get_db)):
    result = close_pilot_run(db, run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pilot run not found")
    return result


@router.get("")
def list_pilots(_: str = Depends(require_reviewer), db: Session = Depends(get_db)):
    runs = db.query(PilotRun).order_by(PilotRun.created_at.desc()).all()
    return {"pilots": [{"id": r.id, "name": r.name, "status": r.status, "manual_items": r.manual_items, "product_items": r.product_items, "missed_items": r.missed_items, "correction_count": r.correction_count, "time_saved_minutes": r.time_saved_minutes} for r in runs]}
