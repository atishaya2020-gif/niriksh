from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import ProcessingJob, RawRecord
from app.db.postgres import SessionLocal
from app.services.graph_service import import_csv_batch


TERMINAL_STATUSES = {
    "COMPLETED",
    "COMPLETED_WITH_WARNINGS",
    "FAILED",
    "CANCELLED",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def update_job(
    db: Session,
    job: ProcessingJob,
    status: str,
    *,
    error_message: str | None = None,
):
    """
    Persist a short processing-job status transaction.

    This function is only intended for short PostgreSQL operations.
    Never use it while Neo4j is doing long-running work.
    """

    job.status = status
    job.stage = status

    if error_message is not None:
        job.error_message = error_message

    if status not in TERMINAL_STATUSES and job.started_at is None:
        job.started_at = utcnow()

    if status in TERMINAL_STATUSES:
        job.completed_at = utcnow()

    try:
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    return job


def raw_rows_for_job(
    db: Session,
    job: ProcessingJob,
) -> list[dict]:
    """
    Load all PostgreSQL payloads belonging to a processing job.

    One query is used instead of querying each record individually.
    """

    record_ids = job.record_ids or []

    if not record_ids:
        return []

    records = (
        db.query(RawRecord)
        .filter(
            RawRecord.case_id == job.case_id,
            RawRecord.record_id.in_(record_ids),
        )
        .all()
    )

    records_by_id = {
        record.record_id: record.payload
        for record in records
    }

    return [
        records_by_id[record_id]
        for record_id in record_ids
        if record_id in records_by_id
    ]


def _persist_final_job_state(
    job_id: int,
    *,
    status: str,
    entities_extracted: int,
    relationships_detected: int,
    error_message: str | None = None,
) -> ProcessingJob | None:
    """
    Persist final processing state using a completely fresh PostgreSQL
    session.

    The original request session is deliberately NOT reused here.

    This prevents a Neon PostgreSQL connection from remaining associated
    with a long-running Neo4j transaction.
    """

    status_db = SessionLocal()

    try:
        fresh_job = status_db.get(
            ProcessingJob,
            job_id,
        )

        if fresh_job is None:
            status_db.rollback()
            return None

        fresh_job.status = status
        fresh_job.stage = status

        fresh_job.entities_extracted = int(
            entities_extracted or 0
        )

        fresh_job.relationships_detected = int(
            relationships_detected or 0
        )

        fresh_job.error_message = error_message

        if status in TERMINAL_STATUSES:
            fresh_job.completed_at = utcnow()

        status_db.commit()
        status_db.refresh(fresh_job)

        return fresh_job

    except Exception:
        status_db.rollback()
        raise

    finally:
        status_db.close()


def _copy_job_state(
    source: ProcessingJob,
    target: ProcessingJob,
) -> None:
    """
    Copy persisted values back onto the original request-local object.

    The original SQLAlchemy session may already have been closed by the
    time this function runs, so copy the values explicitly.
    """

    target.status = source.status
    target.stage = source.stage

    target.entities_extracted = (
        source.entities_extracted
    )

    target.relationships_detected = (
        source.relationships_detected
    )

    target.error_message = (
        source.error_message
    )

    target.completed_at = (
        source.completed_at
    )

    target.attempt_count = (
        source.attempt_count
    )


def sync_job_graph(
    db: Session,
    job: ProcessingJob,
) -> dict:
    """
    Synchronize a processing job's records into Neo4j.

    Transaction lifecycle:

        PostgreSQL status update
                ↓
        PostgreSQL data read
                ↓
        CLOSE PostgreSQL session
                ↓
        Long-running Neo4j operation
                ↓
        NEW PostgreSQL session
                ↓
        Final job status update

    The important part is that the PostgreSQL session is completely
    closed before Neo4j processing begins.
    """

    if job.status == "CANCELLED":
        return {
            "success": False,
            "message": "Processing job is cancelled",
        }

    job_id = job.id
    case_id = job.case_id

    # ---------------------------------------------------------
    # 1. Mark job as GRAPH_SYNCING
    # ---------------------------------------------------------

    update_job(
        db,
        job,
        "GRAPH_SYNCING",
    )

    # ---------------------------------------------------------
    # 2. Increment attempt count
    # ---------------------------------------------------------

    job.attempt_count = (
        job.attempt_count or 0
    ) + 1

    try:
        db.commit()
        db.refresh(job)

    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # 3. Read all PostgreSQL records BEFORE Neo4j work
    # ---------------------------------------------------------

    rows = raw_rows_for_job(
        db,
        job,
    )

    # ---------------------------------------------------------
    # 4. CRITICAL
    #
    # Completely close the original PostgreSQL session.
    #
    # rollback() ends the transaction.
    # close() additionally releases the SQLAlchemy connection.
    # ---------------------------------------------------------

    try:
        db.rollback()
    finally:
        db.close()

    # ---------------------------------------------------------
    # 5. Long-running Neo4j operation
    #
    # NO PostgreSQL session is active here.
    # ---------------------------------------------------------

    try:
        result = import_csv_batch(
            rows,
            case_id,
        )

    except Exception as exc:

        error_message = (
            f"Graph: {exc}"
        )

        # Use a completely fresh PostgreSQL session.
        try:
            failed_job = _persist_final_job_state(
                job_id,
                status="FAILED",
                entities_extracted=0,
                relationships_detected=0,
                error_message=error_message,
            )

            if failed_job is not None:
                _copy_job_state(
                    failed_job,
                    job,
                )

        except Exception:
            # Preserve the original graph error.
            pass

        return {
            "success": False,
            "message": error_message,
        }

    # ---------------------------------------------------------
    # 6. Neo4j succeeded
    # ---------------------------------------------------------

    entities_extracted = int(
        result.get(
            "entities_extracted",
            0,
        ) or 0
    )

    relationships_detected = int(
        result.get(
            "relationships_detected",
            0,
        ) or 0
    )

    # ---------------------------------------------------------
    # 7. Persist final state using a NEW PostgreSQL session
    # ---------------------------------------------------------

    try:

        final_job = _persist_final_job_state(
            job_id,
            status="COMPLETED",
            entities_extracted=entities_extracted,
            relationships_detected=relationships_detected,
            error_message=None,
        )

        if final_job is not None:

            _copy_job_state(
                final_job,
                job,
            )

        else:

            # Database row unexpectedly disappeared.
            # Keep the request-local object accurate.
            job.status = "COMPLETED"
            job.stage = "COMPLETED"

            job.entities_extracted = (
                entities_extracted
            )

            job.relationships_detected = (
                relationships_detected
            )

    except Exception as exc:

        # Neo4j already completed successfully.
        #
        # Do NOT report the graph processing as failed just because
        # the final PostgreSQL status update encountered a problem.

        return {
            "success": True,
            "data": result,
            "warning": (
                "Neo4j synchronization completed, "
                "but the processing-job status could not "
                f"be persisted: {exc}"
            ),
        }

    return {
        "success": True,
        "data": result,
    }


def retry_job_graph(
    db: Session,
    job: ProcessingJob,
) -> dict:
    """
    Retry graph synchronization for a job whose graph stage
    did not complete successfully.
    """

    if job.status not in {
        "GRAPH_PENDING",
        "FAILED",
        "COMPLETED_WITH_WARNINGS",
    }:
        return {
            "success": False,
            "message": (
                f"Job cannot be retried from {job.status}"
            ),
        }

    return sync_job_graph(
        db,
        job,
    )