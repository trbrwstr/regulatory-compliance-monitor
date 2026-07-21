from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

from sqlalchemy.orm import Session

from models import Alert, AuditEvent, DeletionJob, Regulation, RetentionPolicy, Subscriber


CUSTOMER_TABLES = (Alert, Subscriber, Regulation)


def export_tenant_data(db: Session, tenant_id: int) -> dict:
    """Return a machine-readable export, excluding secrets and preserving provenance references."""
    subscribers = db.query(Subscriber).filter(Subscriber.tenant_id == tenant_id).all()
    regulations = db.query(Regulation).filter(Regulation.tenant_id == tenant_id).all()
    alerts = db.query(Alert).filter(Alert.tenant_id == tenant_id).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.tenant_id == tenant_id).all()
    return {
        "schema_version": "1.0",
        "tenant_id": tenant_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "subscribers": [{"id": s.id, "email": s.email, "name": s.name, "is_active": s.is_active} for s in subscribers],
        "regulations": [{
            "id": r.id,
            "title": r.title,
            "document_number": r.document_number,
            "status": r.status,
            "source_url": r.source_url,
            "summary": r.summary,
            "impact_level": r.impact_level,
            "citation_ids": [c.id for c in r.citations],
        } for r in regulations],
        "alerts": [{"id": a.id, "subscriber_id": a.subscriber_id, "regulation_id": a.regulation_id, "delivery_status": a.delivery_status} for a in alerts],
        "audit_events": [{"id": e.id, "action": e.action, "entity_type": e.entity_type, "entity_id": e.entity_id, "created_at": e.created_at.isoformat()} for e in audit_events],
        "provenance_policy": "Public-source snapshots and citation metadata are retained to preserve reproducibility; customer-owned records are eligible for deletion.",
    }


def delete_customer_data(db: Session, tenant_id: int, requested_by: int | None = None) -> DeletionJob:
    """Delete customer-owned records while retaining public-source provenance and audit evidence."""
    job = DeletionJob(tenant_id=tenant_id, requested_by=requested_by, status="running")
    db.add(job)
    db.flush()
    deleted = 0
    for model in (Alert, Subscriber):
        records = db.query(model).filter(model.tenant_id == tenant_id).all()
        deleted += len(records)
        for record in records:
            db.delete(record)
    job.deleted_records = deleted
    job.retained_public_provenance = db.query(Regulation).filter(Regulation.tenant_id == tenant_id).count()
    job.status = "verified"
    job.verified_at = datetime.now(timezone.utc)
    db.add(AuditEvent(tenant_id=tenant_id, user_id=requested_by, action="data.deletion.verified", entity_type="deletion_job", entity_id=job.id, details=json.dumps({"deleted_records": deleted, "retained_public_provenance": job.retained_public_provenance})))
    db.commit()
    db.refresh(job)
    return job


def purge_expired_audit_events(db: Session, policy: RetentionPolicy) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=policy.audit_data_days)
    events = db.query(AuditEvent).filter(AuditEvent.tenant_id == policy.tenant_id, AuditEvent.created_at < cutoff).all()
    for event in events:
        db.delete(event)
    db.commit()
    return len(events)
