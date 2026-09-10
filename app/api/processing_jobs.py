from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import PROCESSING_STATUSES, Case, ProcessingJob, User
from app.db.postgres import get_db
from app.services.processing_jobs import retry_job_graph, utcnow


router = APIRouter(prefix="/processing-jobs", tags=["Processing"])


def serialize_job(job: ProcessingJob) -> dict:
    return {
        "id": job.id,
        "case_id": job.case_id,
        "uploader_id": job.uploader_id,
        "status": job.status,
        "stage": job.stage,
        "source_filename": job.source_filename,
        "source_sha256": job.source_sha256,
        "source_size_bytes": job.source_size_bytes,
        "records_received": job.records_received,
        "records_processed": job.records_processed,
        "entities_extracted": job.entities_extracted,
        "relationships_detected": job.relationships_detected,
        "matches_found": job.matches_found,
        "alerts_generated": job.alerts_generated,
        "attempt_count": job.attempt_count,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }


@router.post("/cases/{case_id}/start")
def start_processing_job(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    existing = (
        db.query(ProcessingJob)
        .filter(
            ProcessingJob.case_id == case_id,
            ProcessingJob.status.in_(["GRAPH_PENDING", "FAILED", "COMPLETED_WITH_WARNINGS"]),
        )
        .order_by(ProcessingJob.id.desc())
        .first()
    )
    if existing:
        result = retry_job_graph(db, existing)
        if not result.get("success"):
            raise HTTPException(status_code=409, detail=result.get("message") or "Unable to retry processing job")
        return {
            "success": True,
            "data": serialize_job(existing),
            "message": "Existing processing job retried",
        }

    job = ProcessingJob(
        case_id=case_id,
        uploader_id=user.id,
        status="RECEIVED",
        stage="RECEIVED",
        started_at=utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {
        "success": True,
        "data": serialize_job(job),
        "message": "Processing job created",
    }


@router.post("/{job_id}/retry")
def retry_processing_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    result = retry_job_graph(db, job)
    if not result.get("success"):
        raise HTTPException(status_code=409, detail=result.get("message") or "Unable to retry processing job")
    return {
        "success": True,
        "data": serialize_job(job),
        "message": "Processing job retried",
    }


@router.get("/{job_id}")
def get_processing_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return {
        "success": True,
        "data": serialize_job(job),
        "message": "Processing job retrieved",
    }


@router.get("/cases/{case_id}")
def list_case_processing_jobs(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.case_id == case_id)
        .order_by(ProcessingJob.id.desc())
        .all()
    )
    return {
        "success": True,
        "data": {
            "case_id": case_id,
            "statuses": PROCESSING_STATUSES,
            "jobs": [serialize_job(job) for job in jobs],
        },
        "message": "Processing jobs retrieved",
    }
