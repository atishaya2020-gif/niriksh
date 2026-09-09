from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Niriksh Backend"
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://niriksh:niriksh@localhost:5432/niriksh"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
