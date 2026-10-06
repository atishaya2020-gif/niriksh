from pydantic import BaseModel, ConfigDict, field_validator

from app.core.roles import normalize_role


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str

    @field_validator("role", mode="before")
    @classmethod
    def _normalize_role(cls, value):
        return normalize_role(value)
