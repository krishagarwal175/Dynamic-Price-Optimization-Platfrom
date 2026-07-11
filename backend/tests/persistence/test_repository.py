"""Tests for the generic repository foundation."""

from __future__ import annotations

import pytest

from app.core.database import session_scope, transaction
from app.repositories.base import BaseRepository
from app.repositories.pagination import Page, PageParams
from tests.support import ExampleRecord, make_memory_db


@pytest.mark.integration
def test_add_and_get() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session, transaction(session):
        repo: BaseRepository[ExampleRecord] = BaseRepository(session, ExampleRecord)
        created = repo.add(ExampleRecord(name="a"))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.name == "a"


@pytest.mark.integration
def test_get_missing_returns_none_and_exists_false() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session:
        repo: BaseRepository[ExampleRecord] = BaseRepository(session, ExampleRecord)
        assert repo.get(999) is None
        assert repo.exists(999) is False


@pytest.mark.integration
def test_count_and_delete() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session, transaction(session):
        repo: BaseRepository[ExampleRecord] = BaseRepository(session, ExampleRecord)
        a = repo.add(ExampleRecord(name="a"))
        repo.add(ExampleRecord(name="b"))
        assert repo.count() == 2
        repo.delete(a)
        assert repo.count() == 1


@pytest.mark.integration
def test_list_paginates() -> None:
    _, factory = make_memory_db()
    with session_scope(factory) as session, transaction(session):
        repo: BaseRepository[ExampleRecord] = BaseRepository(session, ExampleRecord)
        for i in range(5):
            repo.add(ExampleRecord(name=f"n{i}"))

        page = repo.list(PageParams(limit=2, offset=0))
        assert isinstance(page, Page)
        assert len(page.items) == 2
        assert page.total == 5
        assert page.has_next is True
        assert page.has_previous is False

        last = repo.list(PageParams(limit=2, offset=4))
        assert len(last.items) == 1
        assert last.has_next is False
        assert last.has_previous is True
