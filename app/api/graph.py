from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.db.models import User
from app.services.graph_service import get_graph

router = APIRouter(prefix="/graph", tags=["Graph"])


from app.services.authorization import get_authorized_case
from app.db.postgres import get_db
from sqlalchemy.orm import Session

@router.get("")
def graph(case_id: int | None = Query(default=None), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if case_id:
        get_authorized_case(db, user, case_id, "network:view")
    return get_graph(case_id=case_id, db=db, user=user)

@router.get("/entity/{entity_id}")
def entity_graph(entity_id: str, depth: int = Query(default=2, ge=1, le=4), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_graph(entity_id=entity_id, depth=depth, db=db, user=user)
