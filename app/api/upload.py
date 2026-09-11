import hashlib
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Case, ProcessingJob, User
from app.db.postgres import SessionLocal, get_db
from app.services.ingestion import import_csv
from app.services.processing_jobs import utcnow


router = APIRouter(tags=["Ingestion"])


@router.post("/cases/{case_id}/upload-csv")
async def upload_csv(
    case_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV file required")

    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    contents = await file.read()

    source_sha256 = hashlib.sha256(contents).hexdigest()

    job = ProcessingJob(
        case_id=case_id,
        uploader_id=user.id,
        status="RECEIVED",
        stage="RECEIVED",
        source_filename=file.filename,
        source_sha256=source_sha256,
        source_size_bytes=len(contents),
        started_at=utcnow(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    job_id = job.id

    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)

    try:
        with open(path, "wb") as output:
            output.write(contents)

        result = import_csv(
            db,
            case,
            path,
            job=job,
        )

        # import_csv() may release/close the original database
        # session during long Neo4j processing. Re-read the job
        # from a completely fresh session before building the
        # HTTP response.
        fresh_db = SessionLocal()

        try:
            fresh_job = fresh_db.get(ProcessingJob, job_id)

            if fresh_job is None:
                raise HTTPException(
                    status_code=500,
                    detail="Processing job could not be retrieved after processing",
                )

            return {
                "success": True,
                "data": {
                    "case_id": case_id,
                    "job": {
                        "id": fresh_job.id,
                        "status": fresh_job.status,
                        "stage": fresh_job.stage,
                        "source_filename": fresh_job.source_filename,
                        "source_sha256": fresh_job.source_sha256,
                        "source_size_bytes": fresh_job.source_size_bytes,
                        "records_received": fresh_job.records_received,
                        "records_processed": fresh_job.records_processed,
                        "entities_extracted": fresh_job.entities_extracted,
                        "relationships_detected": fresh_job.relationships_detected,
                        "matches_found": fresh_job.matches_found,
                        "alerts_generated": fresh_job.alerts_generated,
                        "attempt_count": fresh_job.attempt_count,
                        "error_message": fresh_job.error_message,
                    },
                    **result,
                },
                "message": "CSV upload processed",
            }

        finally:
            fresh_db.close()

    finally:
        try:
            os.remove(path)
        except OSError:
            pass