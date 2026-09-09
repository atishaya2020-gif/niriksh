import sys
from app.db.postgres import Base, SessionLocal, engine
from app.db.models import Case
from app.services.ingestion import import_csv

path = sys.argv[1] if len(sys.argv) > 1 else "data/cybercrime_combined_dataset.csv"

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    case = db.query(Case).filter_by(case_number="DEMO-SIH-26189").first()
    if not case:
        case = Case(case_number="DEMO-SIH-26189", title="Niriksh SIH Synthetic Investigation", description="Synthetic demo case dataset.")
        db.add(case)
        db.commit()
        db.refresh(case)
    result = import_csv(db, case, path)
    print(f"Import results for case {case.id}:")
    print(f"Received: {result['records_received']}")
    print(f"Imported: {result['records_imported']}")
    print(f"Skipped:  {result['records_skipped']}")
    print(f"Failed:   {result['records_failed']}")
    if result.get('errors'):
        print(f"Errors ({len(result['errors'])}):")
        for error in result['errors']:
            print(error)
finally:
    db.close()
