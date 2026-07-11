"""Unit tests for typed configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import AppEnv, Settings


@pytest.mark.unit
def test_defaults_are_applied() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.app_env is AppEnv.LOCAL
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.log_level == "INFO"
    assert settings.is_production is False


@pytest.mark.unit
def test_log_level_is_normalized() -> None:
    settings = Settings(_env_file=None, log_level="debug")  # type: ignore[call-arg]
    assert settings.log_level == "DEBUG"


@pytest.mark.unit
def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="verbose")  # type: ignore[call-arg]


@pytest.mark.unit
def test_cors_origins_parsed_from_comma_separated_string() -> None:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        cors_allowed_origins="http://a.com, http://b.com ,",
    )
    assert settings.cors_allowed_origins == ["http://a.com", "http://b.com"]


@pytest.mark.unit
def test_production_flag() -> None:
    settings = Settings(_env_file=None, app_env="production")  # type: ignore[call-arg]
    assert settings.is_production is True
