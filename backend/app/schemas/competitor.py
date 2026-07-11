"""Competitor API schemas (independent of the ORM model)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import INPUT_CONFIG, ORM_CONFIG


class CompetitorBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    website: str | None = Field(default=None, max_length=255)


class CompetitorCreate(CompetitorBase):
    model_config = INPUT_CONFIG


class CompetitorUpdate(BaseModel):
    model_config = INPUT_CONFIG

    name: str | None = Field(default=None, min_length=1, max_length=150)
    website: str | None = Field(default=None, max_length=255)


class CompetitorRead(CompetitorBase):
    model_config = ORM_CONFIG

    id: int
    created_at: datetime
    updated_at: datetime


class CompetitorSummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    name: str
