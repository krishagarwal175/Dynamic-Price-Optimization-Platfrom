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
