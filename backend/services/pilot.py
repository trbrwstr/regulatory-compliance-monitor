from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models import AuditEvent, PilotObservation, PilotRun


def create_pilot_run(db: Session, name: str, reviewer_id: int, source_register: str) -> PilotRun:
    run = PilotRun(name=name, reviewer_id=reviewer_id, source_register=source_register, status="active")
    db.add(run)
    db.flush()
    db.add(AuditEvent(user_id=reviewer_id, action="pilot.started", entity_type="pilot_run", entity_id=run.id, details=source_register))
    db.commit()
    db.refresh(run)
    return run


def record_observation(db: Session, run_id: int, source_url: str, manual_found: bool, product_found: bool, correction_count: int, manual_latency_seconds: float | None, product_latency_seconds: float | None, time_saved_minutes: float | None, notes: str | None) -> PilotObservation:
    observation = PilotObservation(
        pilot_run_id=run_id,
        source_url=source_url,
        manual_found=manual_found,
        product_found=product_found,
        correction_count=correction_count,
        manual_latency_seconds=manual_latency_seconds,
        product_latency_seconds=product_latency_seconds,
        time_saved_minutes=time_saved_minutes,
        notes=notes,
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return observation


def close_pilot_run(db: Session, run_id: int) -> dict:
    run = db.query(PilotRun).filter(PilotRun.id == run_id).first()
    if not run:
        return {}
    observations = db.query(PilotObservation).filter(PilotObservation.pilot_run_id == run_id).all()
    manual_items = sum(item.manual_found for item in observations)
    product_items = sum(item.product_found for item in observations)
    missed_items = sum(item.manual_found and not item.product_found for item in observations)
    run.status = "completed"
    run.closed_at = datetime.now(timezone.utc)
    run.manual_items = manual_items
    run.product_items = product_items
    run.missed_items = missed_items
    run.correction_count = sum(item.correction_count for item in observations)
    run.time_saved_minutes = sum(item.time_saved_minutes or 0 for item in observations)
    db.add(AuditEvent(user_id=run.reviewer_id, action="pilot.completed", entity_type="pilot_run", entity_id=run.id, details=f"missed_items={missed_items}"))
    db.commit()
    return {
        "id": run.id,
        "status": run.status,
        "manual_items": manual_items,
        "product_items": product_items,
        "missed_items": missed_items,
        "correction_count": run.correction_count,
        "time_saved_minutes": run.time_saved_minutes,
        "observations": len(observations),
    }
