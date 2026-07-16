"""Typed application configuration.

A single, validated settings object sourced from environment variables (and an optional
local ``.env``). No other module reads ``os.environ`` directly — see
``vault4/02-Architecture/security_and_configuration.md``.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class AppEnv(str, Enum):
    """Deployment environment the service is running in."""

    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Runtime configuration, validated at startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: AppEnv = Field(default=AppEnv.LOCAL)
    app_name: str = Field(default="Dynamic Pricing Optimization Platform API")
    api_v1_prefix: str = Field(default="/api/v1")
    log_level: str = Field(default="INFO")
    # NoDecode: don't let pydantic-settings JSON-parse this list from the env var; the
    # ``_split_origins`` validator below accepts a plain comma-separated string instead
    # (e.g. CORS_ALLOWED_ORIGINS="https://a.example,https://b.example").
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # Persistence. A SQLAlchemy URL; the provider is swappable via configuration alone
    # (SQLite locally / in tests, PostgreSQL in deployment). See
    # vault4/02-Architecture/database_design.md.
    database_url: str = Field(default="sqlite:///./var/dpop.db")
    db_echo: bool = Field(default=False)

    # Dataset ingestion (upload endpoints). Disabled in read-only deployments (e.g. the
    # serverless build) so the heavy pandas/openpyxl dependencies are never imported.
    enable_uploads: bool = Field(default=True)

    # File storage & upload limits (dataset ingestion).
    file_storage_path: str = Field(default="./var/storage")
    max_upload_bytes: int = Field(default=10 * 1024 * 1024)  # 10 MiB
    # Bound the parsed table to guard against decompression/expansion (a small file can
    # inflate to an enormous DataFrame, especially .xlsx). Rows beyond this are rejected.
    max_dataset_rows: int = Field(default=100_000)
    preview_sample_rows: int = Field(default=20)

    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        normalized = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}, got {value!r}")
        return normalized

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Allow a comma-separated string (env var) as well as a list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("cors_allowed_origins")
    @classmethod
    def _reject_wildcard_with_credentials(cls, value: list[str]) -> list[str]:
        """Credentialed CORS must use explicit origins.

        The app sends ``allow_credentials=True``; combining that with a ``"*"`` origin is
        insecure (and rejected by browsers). Fail fast on a misconfiguration rather than
        silently exposing credentialed cross-origin access.
        """
        if "*" in value:
            raise ValueError(
                "cors_allowed_origins may not contain '*' because credentialed CORS is "
                "enabled; list explicit origins instead."
            )
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env is AppEnv.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return the cached, process-wide settings instance."""
    return Settings()
