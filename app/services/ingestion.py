from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import pandas as pd

from app.db.models import Case, RawRecord
from app.services.graph_service import create_record_graph
from app.services.normalization import clean_text, parse_datetime

EXPECTED_DROP_COLUMNS = {"Unnamed: 12"}


def read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df.drop(columns=[column for column in EXPECTED_DROP_COLUMNS if column in df.columns])


def import_csv(db: Session, case: Case, path: str) -> dict:
    df = read_csv(path)
    result = {
        "records_received": len(df),
        "records_imported": 0,
        "records_skipped": 0,
        "records_failed": 0,
        "graph_failed": 0,
        "errors": [],
    }
    imported_rows = []

    for row_number, record in enumerate(df.to_dict(orient="records"), start=2):
        record_id = clean_text(record.get("record_id"))
        if not record_id:
            result["records_skipped"] += 1
            result["errors"].append({"row": row_number, "reason": "Missing record_id"})
            continue
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
            imported_rows.append(record)
            result["records_imported"] += 1
        except IntegrityError:
            result["records_skipped"] += 1
        except Exception as exc:
            result["records_failed"] += 1
            result["errors"].append({"row": row_number, "record_id": record_id, "reason": str(exc)})

    db.commit()

    for row in imported_rows:
        record_id = clean_text(row.get("record_id"))
        try:
            create_record_graph(row, case.id)
        except Exception as exc:
            result["graph_failed"] += 1
            result["errors"].append({"record_id": record_id, "reason": f"Graph: {exc}"})

    result["status"] = "completed" if not result["records_failed"] and not result["graph_failed"] else "completed_with_errors"
    return result
