from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import ProcessingJob, RawRecord
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
    Update a processing job using a short PostgreSQL transaction.

    Important:
    Never keep a PostgreSQL transaction open while Neo4j or another
    external service is doing long-running work.
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
    Load all records belonging to a processing job.

    Uses one PostgreSQL query instead of one query per record.
    This is important for large imports such as the 10,000-row SIH dataset.
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

    # Preserve the original job record order.
    return [
        records_by_id[record_id]
        for record_id in record_ids
        if record_id in records_by_id
    ]


def sync_job_graph(
    db: Session,
    job: ProcessingJob,
) -> dict:
    """
    Synchronize the processing job's records into Neo4j.

    Critical transaction rule:

        PostgreSQL work
              ↓
        COMMIT / ROLLBACK
              ↓
        Neo4j long-running operation
              ↓
        PostgreSQL short status update

    This prevents Neon/PostgreSQL from killing an idle transaction while
    Neo4j is processing thousands of records.
    """

    if job.status == "CANCELLED":
        return {
            "success": False,
            "message": "Processing job is cancelled",
        }

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

    job.attempt_count = (job.attempt_count or 0) + 1

    try:
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # 3. Read PostgreSQL data BEFORE starting Neo4j work
    # ---------------------------------------------------------

    rows = raw_rows_for_job(
        db,
        job,
    )

    case_id = job.case_id

    # ---------------------------------------------------------
    # 4. IMPORTANT:
    #    End any PostgreSQL transaction before Neo4j starts.
    # ---------------------------------------------------------

    db.rollback()

    # ---------------------------------------------------------
    # 5. Long-running Neo4j operation
    #
    #    There must NOT be an open PostgreSQL transaction here.
    # ---------------------------------------------------------

    try:
        result = import_csv_batch(
            rows,
            case_id,
        )

    except Exception as exc:
        error_message = f"Graph: {exc}"

        # Make sure the SQLAlchemy session is clean before
        # attempting the failure update.
        try:
            db.rollback()
        except Exception:
            pass

        try:
            update_job(
                db,
                job,
                "FAILED",
                error_message=error_message,
            )
        except Exception:
            # The original Neo4j error is more useful than a
            # secondary PostgreSQL status-update error.
            pass

        return {
            "success": False,
            "message": error_message,
        }

    # ---------------------------------------------------------
    # 6. Neo4j succeeded.
    #
    #    Now update PostgreSQL with the results.
    # ---------------------------------------------------------

    entities_extracted = int(
        result.get("entities_extracted", 0) or 0
    )

    relationships_detected = int(
        result.get("relationships_detected", 0) or 0
    )

    job.entities_extracted = entities_extracted
    job.relationships_detected = relationships_detected
    job.error_message = None

    # ---------------------------------------------------------
    # 7. Short PostgreSQL transaction.
    #
    #    This happens AFTER Neo4j has finished.
    # ---------------------------------------------------------

    try:
        update_job(
            db,
            job,
            "COMPLETED",
        )

    except Exception as exc:
        # If the final status update itself fails, make one clean
        # retry using a fresh transaction.
        try:
            db.rollback()

            refreshed_job = db.get(
                ProcessingJob,
                job.id,
            )

            if refreshed_job is not None:
                refreshed_job.status = "COMPLETED"
                refreshed_job.stage = "COMPLETED"
                refreshed_job.entities_extracted = entities_extracted
                refreshed_job.relationships_detected = (
                    relationships_detected
                )
                refreshed_job.error_message = None
                refreshed_job.completed_at = utcnow()

                db.commit()
                db.refresh(refreshed_job)

                job = refreshed_job

        except Exception:
            # At this point Neo4j has already completed successfully.
            # Do not report the graph operation itself as failed.
            db.rollback()

            return {
                "success": True,
                "data": result,
                "warning": (
                    "Neo4j synchronization completed, but the "
                    "processing-job status could not be persisted."
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
    has not completed successfully.
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