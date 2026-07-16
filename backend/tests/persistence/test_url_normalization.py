"""The legacy ``postgres://`` scheme (Supabase/Heroku) is rewritten to ``postgresql://``."""

from __future__ import annotations

import pytest

from app.core.database import _normalize_url


@pytest.mark.unit
def test_postgres_scheme_is_rewritten() -> None:
    assert _normalize_url("postgres://u:p@host:5432/db") == "postgresql://u:p@host:5432/db"


@pytest.mark.unit
def test_other_schemes_are_untouched() -> None:
    assert _normalize_url("postgresql://u:p@host/db") == "postgresql://u:p@host/db"
    assert _normalize_url("sqlite:///./var/dpop.db") == "sqlite:///./var/dpop.db"
    assert _normalize_url("sqlite://") == "sqlite://"
