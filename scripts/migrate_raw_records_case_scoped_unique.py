import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.postgres import engine

DUPLICATE_QUERY = text(
    """
    SELECT case_id, record_id, count(*) AS duplicate_count
    FROM raw_records
    GROUP BY case_id, record_id
    HAVING count(*) > 1
    ORDER BY case_id, record_id
    """
)
CONSTRAINT_QUERY = text(
    """
    SELECT conname, contype, pg_get_constraintdef(oid) AS definition
    FROM pg_constraint
    WHERE conrelid = 'raw_records'::regclass
    ORDER BY conname
    """
)
INDEX_QUERY = text(
    """
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE schemaname = current_schema() AND tablename = 'raw_records'
    ORDER BY indexname
    """
)


def print_state(connection, heading: str):
    print(heading)
    print("Constraints:")
    for row in connection.execute(CONSTRAINT_QUERY).mappings():
        print(dict(row))
    print("Indexes:")
    for row in connection.execute(INDEX_QUERY).mappings():
        print(dict(row))


def main():
    with engine.begin() as connection:
        duplicates = list(connection.execute(DUPLICATE_QUERY).mappings())
        if duplicates:
            print("Migration aborted: duplicate (case_id, record_id) pairs found.")
            for row in duplicates:
                print(dict(row))
            raise SystemExit(1)

        print_state(connection, "Before migration")
        connection.execute(text("ALTER TABLE raw_records DROP CONSTRAINT IF EXISTS raw_records_record_id_key"))
        connection.execute(text("DROP INDEX IF EXISTS ix_raw_records_record_id"))
        connection.execute(
            text(
                "ALTER TABLE raw_records "
                "ADD CONSTRAINT uq_raw_records_case_id_record_id UNIQUE (case_id, record_id)"
            )
        )
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_raw_records_record_id ON raw_records (record_id)"))
        print_state(connection, "After migration")


if __name__ == "__main__":
    main()
