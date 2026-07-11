"""Application configuration.

NOTE (brownfield): settings are read from the environment *mostly*. A few values
are hardcoded as fallbacks below — this is one of the intentional smells the
workshop's AI Layer later flags. Do not "fix" without a workshop stage calling for it.
"""
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # smell: hardcoded DB url fallback (host port 5433 -> container 5432)
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://schedulr:schedulr@localhost:5433/schedulr"
    )

    # smell: secret default baked in instead of failing loudly when unset
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # smell: legacy session tokens live alongside JWT (two auth patterns)
    session_token_ttl_seconds: int = 86400

    # smell: hardcoded CORS origin
    cors_origin: str = "http://localhost:3000"

    app_name: str = "Schedulr"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
