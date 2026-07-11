"""Category API schemas (independent of the ORM model)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import INPUT_CONFIG, ORM_CONFIG


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryCreate(CategoryBase):
    model_config = INPUT_CONFIG


class CategoryUpdate(BaseModel):
    model_config = INPUT_CONFIG

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryRead(CategoryBase):
    model_config = ORM_CONFIG

    id: int
    created_at: datetime
    updated_at: datetime


class CategorySummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    name: str
