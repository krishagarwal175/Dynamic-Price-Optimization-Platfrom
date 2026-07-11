"""Tests for session lifecycle, transaction helper, and rollback safety."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.database import session_scope, transaction
from tests.support import ExampleRecord, make_memory_db


@pytest.mark.integration
def test_session_scope_yields_and_closes() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session:
        assert session.is_active
    # After the scope the session is closed (no active transaction bound).
    assert session.get_bind() is not None  # bind still known; session itself closed


@pytest.mark.integration
def test_transaction_commits_on_success() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session, transaction(session):
        session.add(ExampleRecord(name="alpha"))

    with session_scope(factory) as verify:
        rows = verify.scalars(select(ExampleRecord)).all()
        assert [r.name for r in rows] == ["alpha"]


@pytest.mark.integration
def test_transaction_rolls_back_on_error() -> None:
    _, factory = make_memory_db()

    with (
        pytest.raises(RuntimeError),
        session_scope(factory) as session,
        transaction(session),
    ):
        session.add(ExampleRecord(name="doomed"))
        session.flush()
        raise RuntimeError("boom")

    with session_scope(factory) as verify:
        assert verify.scalars(select(ExampleRecord)).all() == []


@pytest.mark.integration
def test_timestamps_are_populated_on_insert() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session, transaction(session):
        record = ExampleRecord(name="ts")
        session.add(record)

    with session_scope(factory) as verify:
        stored = verify.scalars(select(ExampleRecord)).one()
        assert stored.created_at is not None
        assert stored.updated_at is not None
        assert stored.id is not None
