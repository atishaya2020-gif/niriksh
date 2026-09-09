from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    case_number: str
    title: str
    description: str | None = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_number: str
    title: str
    description: str | None
    created_at: datetime
