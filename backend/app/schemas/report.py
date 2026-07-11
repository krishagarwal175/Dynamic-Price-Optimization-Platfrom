"""Report API schemas.

The structured report is returned as a JSON object (``report``) when ``format=json``, or as
a rendered string (``content``) for markdown/text. Both live in one envelope so the
endpoint shape is stable across formats.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.pricing.reporting import ReportFormat


class DatasetReportResponse(BaseModel):
    scope: str
    format: ReportFormat
    report: dict[str, Any] | None = None
    content: str | None = None


class ProductReportResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    format: ReportFormat
    report: dict[str, Any] | None = None
    content: str | None = None
