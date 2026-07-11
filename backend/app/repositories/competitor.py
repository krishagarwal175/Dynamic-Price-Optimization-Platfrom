"""Competitor persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competitor import Competitor
from app.repositories.base import BaseRepository


class CompetitorRepository(BaseRepository[Competitor]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Competitor)

    def get_by_name(self, name: str) -> Competitor | None:
        return self._session.scalar(select(Competitor).where(Competitor.name == name))
