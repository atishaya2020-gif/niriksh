from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Any

from app.db.models import MATCH_STATUSES


class MatchReview(BaseModel):
    status: str = Field(..., description=f"Must be one of {MATCH_STATUSES}")


class EntityMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    source_entity_id: str
    candidate_entity_id: str
    source_entity_type: str
    candidate_entity_type: str
    match_score: float
    confidence: float
    matching_factors: dict[str, Any] | None
    status: str
    reviewed_by: int | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
