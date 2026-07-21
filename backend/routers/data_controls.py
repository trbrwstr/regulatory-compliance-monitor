from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth import require_api_key, require_reviewer
from database import get_db
from models import DeletionJob, RetentionPolicy
from services.data_lifecycle import delete_customer_data, export_tenant_data

router = APIRouter(prefix="/api/data", tags=["data-controls"])


def tenant_header(x_tenant_id: int | None = Header(default=None)) -> int:
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-Id header required")
    return x_tenant_id


@router.get("/export")
def export_data(
    tenant_id: int = Depends(tenant_header),
    _: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return JSONResponse(content=export_tenant_data(db, tenant_id))


@router.post("/deletion")
def request_deletion(
    tenant_id: int = Depends(tenant_header),
    reviewer_role: str = Depends(require_reviewer),
    x_user_id: int | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_user_id:
        raise HTTPException(status_code=422, detail="X-User-Id header required")
    job = delete_customer_data(db, tenant_id, x_user_id)
    return {
        "id": job.id,
        "status": job.status,
        "deleted_records": job.deleted_records,
        "retained_public_provenance": job.retained_public_provenance,
        "verified_at": job.verified_at.isoformat() if job.verified_at else None,
    }


@router.get("/deletion/{job_id}")
def get_deletion_job(job_id: int, _: str = Depends(require_api_key), db: Session = Depends(get_db)):
    job = db.query(DeletionJob).filter(DeletionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Deletion job not found")
    return {"id": job.id, "status": job.status, "deleted_records": job.deleted_records, "retained_public_provenance": job.retained_public_provenance, "verified_at": job.verified_at.isoformat() if job.verified_at else None}
