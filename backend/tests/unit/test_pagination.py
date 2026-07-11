"""Unit tests for pagination primitives."""

from __future__ import annotations

import pytest

from app.repositories.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page, PageParams


@pytest.mark.unit
def test_defaults() -> None:
    params = PageParams()
    assert params.limit == DEFAULT_LIMIT
    assert params.offset == 0


@pytest.mark.unit
def test_limit_is_clamped_to_bounds() -> None:
    assert PageParams(limit=0).limit == 1
    assert PageParams(limit=10_000).limit == MAX_LIMIT


@pytest.mark.unit
def test_offset_is_never_negative() -> None:
    assert PageParams(offset=-5).offset == 0


@pytest.mark.unit
def test_page_navigation_flags() -> None:
    page: Page[int] = Page(items=[1, 2], total=5, limit=2, offset=0)
    assert page.has_next is True
    assert page.has_previous is False

    middle: Page[int] = Page(items=[3, 4], total=5, limit=2, offset=2)
    assert middle.has_next is True
    assert middle.has_previous is True

    last: Page[int] = Page(items=[5], total=5, limit=2, offset=4)
    assert last.has_next is False
    assert last.has_previous is True
