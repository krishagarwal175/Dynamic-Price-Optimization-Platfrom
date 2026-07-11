"""Dataset persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Dataset)

    def get_by_storage_key(self, storage_key: str) -> Dataset | None:
        return self._session.scalar(select(Dataset).where(Dataset.storage_key == storage_key))
