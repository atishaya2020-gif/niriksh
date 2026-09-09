from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.models import Case, User
from app.db.postgres import get_db
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = Case(**payload.model_dump(), created_by=user.id)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=list[CaseResponse])
def list_cases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Case).order_by(Case.id.desc()).all()


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.get(Case, case_id)
