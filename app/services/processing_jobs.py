from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import ProcessingJob, RawRecord
from app.services.graph_service import import_csv_batch


TERMINAL_STATUSES = {"COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED", "CANCELLED"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def update_job(db: Session, job: ProcessingJob, status: str, *, error_message: str | None = None):
    job.status = status
    job.stage = status
    if error_message is not None:
        job.error_message = error_message
    if status not in TERMINAL_STATUSES and job.started_at is None:
        job.started_at = utcnow()
    if status in TERMINAL_STATUSES:
        job.completed_at = utcnow()
    db.commit()
    db.refresh(job)
    return job


def raw_rows_for_job(db: Session, job: ProcessingJob) -> list[dict]:
    record_ids = job.record_ids or []
    if not record_ids:
        return []
    query = db.query(RawRecord)
    if hasattr(query, "filter_by"):
        records = []
        for record_id in record_ids:
            match = query.filter_by(case_id=job.case_id, record_id=record_id).first()
            if match is not None:
                records.append(match)
        return [record.payload for record in records]
    records = query.filter(RawRecord.case_id == job.case_id, RawRecord.record_id.in_(record_ids)).all()
    return [record.payload for record in records]


def sync_job_graph(db: Session, job: ProcessingJob) -> dict:
    if job.status == "CANCELLED":
        return {"success": False, "message": "Processing job is cancelled"}

    update_job(db, job, "GRAPH_SYNCING")
    job.attempt_count += 1
    db.commit()
    db.refresh(job)

    try:
        result = import_csv_batch(raw_rows_for_job(db, job), job.case_id)
    except Exception as exc:
        update_job(db, job, "FAILED", error_message=f"Graph: {exc}")
        return {"success": False, "message": job.error_message}

    job.entities_extracted = result["entities_extracted"]
    job.relationships_detected = result["relationships_detected"]
    job.error_message = None
    update_job(db, job, "COMPLETED")
    return {"success": True, "data": result}


def retry_job_graph(db: Session, job: ProcessingJob) -> dict:
    if job.status not in {"GRAPH_PENDING", "FAILED", "COMPLETED_WITH_WARNINGS"}:
        return {"success": False, "message": f"Job cannot be retried from {job.status}"}
    return sync_job_graph(db, job)
