"""Offset/limit pagination primitives, shared by all repositories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@dataclass(frozen=True)
class PageParams:
    """Validated pagination request. ``limit`` is clamped to ``[1, MAX_LIMIT]`` and
    ``offset`` to ``>= 0`` so repositories never receive out-of-range values."""

    limit: int = DEFAULT_LIMIT
    offset: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "limit", max(1, min(self.limit, MAX_LIMIT)))
        object.__setattr__(self, "offset", max(0, self.offset))


@dataclass(frozen=True)
class Page(Generic[T]):
    """A page of results plus the total count of matching rows."""

    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + len(self.items) < self.total

    @property
    def has_previous(self) -> bool:
        return self.offset > 0
