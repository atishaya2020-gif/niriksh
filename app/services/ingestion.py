from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import pandas as pd

from app.db.models import Case, ProcessingJob, RawRecord
from app.services.graph_service import import_csv_batch
from app.services.normalization import clean_text, parse_datetime
from app.services.processing_jobs import sync_job_graph, update_job

EXPECTED_DROP_COLUMNS = {"Unnamed: 12"}


def read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df.drop(columns=[column for column in EXPECTED_DROP_COLUMNS if column in df.columns])


def persist_csv_records(db: Session, case: Case, path: str) -> dict:
    df = read_csv(path)
    result = {
        "records_received": len(df),
        "records_imported": 0,
        "records_skipped": 0,
        "records_failed": 0,
        "graph_failed": 0,
        "errors": [],
        "imported_record_ids": [],
        "all_record_ids": [],
    }

    for row_number, record in enumerate(df.to_dict(orient="records"), start=2):
        record_id = clean_text(record.get("record_id"))
        if not record_id:
            result["records_skipped"] += 1
            result["errors"].append({"row": row_number, "reason": "Missing record_id"})
            continue
        result["all_record_ids"].append(record_id)
        if db.query(RawRecord).filter_by(case_id=case.id, record_id=record_id).first():
            result["records_skipped"] += 1
            continue

        raw = RawRecord(
            record_id=record_id,
            case_id=case.id,
            category=clean_text(record.get("category")) or "Unknown",
            incident_datetime=parse_datetime(record.get("incident_datetime")),
            payload={key: clean_text(value) for key, value in record.items()},
        )
        try:
            with db.begin_nested():
                db.add(raw)
                db.flush()
            result["imported_record_ids"].append(record_id)
            result["records_imported"] += 1
        except IntegrityError:
            result["records_skipped"] += 1
        except Exception as exc:
            result["records_failed"] += 1
            result["errors"].append({"row": row_number, "record_id": record_id, "reason": str(exc)})

    db.commit()
    return result


def import_csv(db: Session, case: Case, path: str, job: ProcessingJob | None = None) -> dict:
    if job is not None:
        update_job(db, job, "VALIDATING")
        update_job(db, job, "PERSISTING_RECORDS")

    result = persist_csv_records(db, case, path)
    result["entities_extracted"] = 0
    result["relationships_detected"] = 0

    if job is not None:
        job.records_received = result["records_received"]
        job.records_processed = result["records_imported"]
        job.record_ids = result["imported_record_ids"] or result["all_record_ids"]
        db.commit()
        db.refresh(job)

    if result["records_failed"]:
        if job is not None:
            update_job(db, job, "FAILED", error_message="; ".join(error["reason"] for error in result["errors"]))
        result["status"] = "completed_with_errors"
        return result

    graph_rows_exist = bool(job.record_ids if job is not None else result["imported_record_ids"] or result["all_record_ids"])
    if not graph_rows_exist:
        if job is not None:
            update_job(db, job, "COMPLETED")
        result["status"] = "completed"
        return result

    if job is not None:
        update_job(db, job, "GRAPH_PENDING")
        graph_result = sync_job_graph(db, job)
        if not graph_result.get("success"):
            result["graph_failed"] += max(len(job.record_ids or []), 1)
            result["errors"].append({"reason": graph_result.get("message") or "Graph synchronization failed"})
            result["status"] = "completed_with_errors"
            return result
        result["entities_extracted"] = job.entities_extracted
        result["relationships_detected"] = job.relationships_detected
        result["status"] = "completed"
        return result

    from app.services.graph_service import import_csv_batch

    rows = []
    if result["imported_record_ids"]:
        query = db.query(RawRecord)
        if hasattr(query, "filter_by"):
            records = []
            for record_id in result["imported_record_ids"]:
                match = query.filter_by(case_id=case.id, record_id=record_id).first()
                if match is not None:
                    records.append(match)
        else:
            records = query.filter(RawRecord.case_id == case.id, RawRecord.record_id.in_(result["imported_record_ids"])).all()
        rows = [record.payload for record in records]
    if rows:
        try:
            graph_result = import_csv_batch(rows, case.id)
            result["entities_extracted"] = graph_result["entities_extracted"]
            result["relationships_detected"] = graph_result["relationships_detected"]
        except Exception as exc:
            result["graph_failed"] += len(rows)
            result["errors"].append({"reason": f"Graph: {exc}"})

    result["status"] = "completed" if not result["records_failed"] and not result["graph_failed"] else "completed_with_errors"
    return result
