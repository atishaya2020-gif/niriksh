import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Case, User
from app.db.postgres import get_db
from app.services.ingestion import import_csv

router = APIRouter(tags=["Ingestion"])


@router.post("/cases/{case_id}/upload-csv")
async def upload_csv(case_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV file required")
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    try:
        with open(path, "wb") as output:
            output.write(await file.read())
        result = import_csv(db, case, path)
        return {"case_id": case_id, **result}
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
