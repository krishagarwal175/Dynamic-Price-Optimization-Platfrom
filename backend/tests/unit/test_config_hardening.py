"""Configuration hardening: credentialed CORS must not use a wildcard origin."""

from __future__ import annotations

import pytest

from app.core.config import Settings


@pytest.mark.unit
def test_wildcard_cors_origin_is_rejected() -> None:
    with pytest.raises(ValueError):
        Settings(  # type: ignore[call-arg]
            _env_file=None,
            cors_allowed_origins=["*"],
        )


@pytest.mark.unit
def test_comma_separated_origins_are_split() -> None:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        cors_allowed_origins="http://a.example, http://b.example",
    )
    assert settings.cors_allowed_origins == ["http://a.example", "http://b.example"]


@pytest.mark.unit
def test_cors_origins_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    # Reproduces deployment: a plain origin string set via env var (not a JSON list). The
    # NoDecode annotation + validator must accept it instead of trying to JSON-parse it.
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.vercel.app")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.cors_allowed_origins == ["https://app.vercel.app"]


@pytest.mark.unit
def test_cors_origins_from_env_var_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://a.app,https://b.app")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.cors_allowed_origins == ["https://a.app", "https://b.app"]
