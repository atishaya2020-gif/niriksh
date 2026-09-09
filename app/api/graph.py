from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.db.models import User
from app.services.graph_service import get_graph

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("")
def graph(case_id: int | None = Query(default=None), user: User = Depends(get_current_user)):
    return get_graph(case_id=case_id)


@router.get("/entity/{entity_id}")
def entity_graph(entity_id: str, depth: int = Query(default=2, ge=1, le=4), user: User = Depends(get_current_user)):
    return get_graph(entity_id=entity_id, depth=depth)
