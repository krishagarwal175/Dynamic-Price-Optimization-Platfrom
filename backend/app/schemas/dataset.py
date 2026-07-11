"""Dataset & ingestion API schemas (independent of ORM models)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORM_CONFIG


class DatasetRead(BaseModel):
    model_config = ORM_CONFIG

    id: int
    original_filename: str
    content_type: str
    kind: str
    status: str
    size_bytes: int
    row_count: int | None
    error_summary: str | None
    created_at: datetime
    updated_at: datetime


class DatasetSummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    original_filename: str
    kind: str
    status: str


class ValidationIssueSchema(BaseModel):
    code: str
    message: str
    column: str | None = None
    row: int | None = None


class ValidationReportSchema(BaseModel):
    is_valid: bool
    truncated: bool
    issues: list[ValidationIssueSchema]


class PreviewResponse(BaseModel):
    dataset_id: int
    columns: list[str]
    inferred_types: dict[str, str]
    row_count: int
    missing_values: dict[str, int]
    duplicate_rows: int
    sample_rows: list[dict[str, Any]]
    validation: ValidationReportSchema


class ImportResultResponse(BaseModel):
    dataset_id: int
    status: str
    rows_imported: int
    categories_created: int
    products_created: int
