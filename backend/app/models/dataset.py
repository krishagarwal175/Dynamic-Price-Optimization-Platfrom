"""Dataset entity: tracks an uploaded file through the ingestion lifecycle.

A Dataset records the stored upload and its status. Its rows are mapped into the business
entities (Category/Product) on import; the Dataset itself does not hold row data.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin


class DatasetKind(str, Enum):
    """The kind of business data a dataset carries (its import target)."""

    PRODUCT_CATALOG = "product_catalog"


class DatasetStatus(str, Enum):
    """Lifecycle status of an uploaded dataset."""

    UPLOADED = "uploaded"
    IMPORTED = "imported"
    FAILED = "failed"


class Dataset(Base, IntIdMixin, TimestampMixin):
    __tablename__ = "dataset"

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=DatasetStatus.UPLOADED.value,
        index=True,
    )
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
