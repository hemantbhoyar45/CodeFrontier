from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KNOWBRIDGE_",
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "KNOWBRIDGE API"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = Field(min_length=1)
    redis_url: str = Field(min_length=1)
    jwt_secret_key: str = Field(
        default="local-development-only-secret-key-change-me", min_length=32
    )
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    rate_limit_per_minute: int = Field(default=120, ge=1)
    auth_rate_limit_per_minute: int = Field(default=10, ge=1)
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True
    frontend_base_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def require_production_secret(self) -> "Settings":
        if (
            self.environment == "production"
            and self.jwt_secret_key == "local-development-only-secret-key-change-me"
        ):
            raise ValueError("KNOWBRIDGE_JWT_SECRET_KEY must be configured in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
