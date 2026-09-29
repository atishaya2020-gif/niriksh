from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEVELOPMENT_SECRET_KEY = "development-only-secret-not-for-production"
DEVELOPMENT_ADMIN_PASSWORD = "admin123"
DEVELOPMENT_NEO4J_PASSWORD = "password"
DEVELOPMENT_CORS_ORIGINS = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)


class Settings(BaseSettings):
    app_name: str = "Niriksh Backend"
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = DEVELOPMENT_SECRET_KEY
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://niriksh:niriksh@localhost:5432/niriksh"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = DEVELOPMENT_NEO4J_PASSWORD

    cors_origins: str = DEVELOPMENT_CORS_ORIGINS

    admin_username: str = "admin"
    admin_password: str = DEVELOPMENT_ADMIN_PASSWORD

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_deployment_configuration(self):
        if self.environment == "development":
            return self

        if len(self.secret_key) < 32 or self.secret_key == DEVELOPMENT_SECRET_KEY:
            raise ValueError("Production security configuration is invalid")

        if not self.admin_password or self.admin_password == DEVELOPMENT_ADMIN_PASSWORD:
            raise ValueError("Production security configuration is invalid")

        if not self.neo4j_password or self.neo4j_password == DEVELOPMENT_NEO4J_PASSWORD:
            raise ValueError("Production security configuration is invalid")

        origins = self.cors_origin_list
        if not origins or "*" in origins or any("localhost" in origin or "127.0.0.1" in origin for origin in origins):
            raise ValueError("Production CORS configuration is invalid")

        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
