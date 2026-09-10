from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Any

from app.db.models import EVIDENCE_TYPES, VERIFICATION_STATUSES


class EvidenceCreate(BaseModel):
    record_id: str | None = None
    evidence_type: str = Field(..., description=f"Must be one of {EVIDENCE_TYPES}")
    source: str
    description: str
    collection_timestamp: datetime | None = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    evidence_metadata: dict[str, Any] | None = None


class EvidenceVerify(BaseModel):
    status: str = Field(..., description=f"Must be one of {VERIFICATION_STATUSES}")
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    record_id: str | None
    evidence_type: str
    source: str
    description: str
    collection_timestamp: datetime | None
    verification_status: str
    confidence: float
    evidence_metadata: dict[str, Any] | None
    verified_by: int | None
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
