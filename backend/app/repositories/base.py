"""Generic repository foundation.

Provides the persistence contract (:class:`AbstractRepository`) and a reusable
:class:`BaseRepository` with common CRUD + pagination. Concrete, entity-specific
repositories (Product, Scenario, …) are **not** defined here — they arrive with their
domain entities in later milestones by subclassing :class:`BaseRepository`.
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.repositories.pagination import Page, PageParams

ModelT = TypeVar("ModelT", bound=Base)


class AbstractRepository(Protocol[ModelT]):
    """The persistence contract every repository satisfies."""

    def add(self, entity: ModelT) -> ModelT: ...
    def get(self, entity_id: object) -> ModelT | None: ...
    def list(self, params: PageParams | None = ...) -> Page[ModelT]: ...
    def delete(self, entity: ModelT) -> None: ...
    def count(self) -> int: ...


class BaseRepository(Generic[ModelT]):
    """Reusable CRUD implementation bound to a session and a model type.

    Does not commit — the caller owns the transaction boundary
    (:func:`app.core.database.transaction`).
    """

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    def add(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        self._session.flush()  # assign PK / defaults without committing
        return entity

    def add_all(self, entities: list[ModelT]) -> list[ModelT]:
        """Add many entities with a single flush.

        The bulk write path (e.g. dataset import): one ``flush`` round-trip instead of one
        per row. The caller still owns the transaction boundary.
        """
        if not entities:
            return entities
        self._session.add_all(entities)
        self._session.flush()
        return entities

    def get(self, entity_id: object) -> ModelT | None:
        return self._session.get(self._model, entity_id)

    def list(self, params: PageParams | None = None) -> Page[ModelT]:
        params = params or PageParams()
        stmt = select(self._model).limit(params.limit).offset(params.offset)
        items = list(self._session.scalars(stmt).all())
        return Page(
            items=items,
            total=self.count(),
            limit=params.limit,
            offset=params.offset,
        )

    def delete(self, entity: ModelT) -> None:
        self._session.delete(entity)
        self._session.flush()

    def count(self) -> int:
        stmt = select(func.count()).select_from(self._model)
        return self._session.scalar(stmt) or 0

    def exists(self, entity_id: object) -> bool:
        return self.get(entity_id) is not None
