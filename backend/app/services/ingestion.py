"""Ingestion service: orchestrates upload → preview → import.

Coordinates file storage, parsing, validation, preview, and the transactional import,
using the repository layer for persistence. Business-rule failures surface as typed
:class:`AppError`s; data-quality problems surface as a structured validation report.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import PurePosixPath

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import transaction
from app.core.errors import (
    ConflictError,
    NotFoundError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
    ValidationError,
)
from app.core.logging import get_logger
from app.ingestion.catalog import ImportSummary
from app.ingestion.errors import ParsingError, UnsupportedFileTypeError
from app.ingestion.parsing import detect_format, parse
from app.ingestion.preview import DatasetPreview, build_preview
from app.ingestion.registry import get_importer, get_schema
from app.ingestion.validation import ValidationReport, validate
from app.models.dataset import Dataset, DatasetKind, DatasetStatus
from app.repositories.dataset import DatasetRepository
from app.schemas.envelope import ErrorDetail
from app.storage.base import FileStorage

logger = get_logger(__name__)

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class PreviewResult:
    dataset: Dataset
    preview: DatasetPreview
    report: ValidationReport


def _safe_filename(filename: str) -> str:
    base = PurePosixPath(filename.replace("\\", "/")).name or "upload"
    return _SAFE_NAME.sub("_", base)


def _to_details(report: ValidationReport) -> list[ErrorDetail]:
    details = []
    for issue in report.issues:
        field = issue.column or "dataset"
        prefix = f"row {issue.row}: " if issue.row is not None else ""
        details.append(ErrorDetail(field=field, issue=f"{prefix}{issue.message}"))
    return details


class IngestionService:
    def __init__(self, session: Session, storage: FileStorage, settings: Settings) -> None:
        self._session = session
        self._storage = storage
        self._settings = settings
        self._datasets = DatasetRepository(session)

    # ---------------------------------------------------------------- upload
    def upload(
        self,
        *,
        filename: str,
        content_type: str | None,
        data: bytes,
        kind: DatasetKind,
    ) -> Dataset:
        if len(data) > self._settings.max_upload_bytes:
            raise PayloadTooLargeError(
                f"File exceeds the maximum upload size of "
                f"{self._settings.max_upload_bytes} bytes."
            )
        try:
            detect_format(filename, content_type)
        except UnsupportedFileTypeError as exc:
            raise UnsupportedMediaTypeError(str(exc)) from exc

        key = f"datasets/{uuid.uuid4().hex}/{_safe_filename(filename)}"
        uri = self._storage.save(key, data)

        dataset = Dataset(
            original_filename=filename,
            content_type=content_type or "",
            storage_key=key,
            storage_uri=uri,
            size_bytes=len(data),
            kind=kind.value,
            status=DatasetStatus.UPLOADED.value,
        )
        with transaction(self._session):
            self._datasets.add(dataset)
        logger.info("Dataset uploaded (id=%s, kind=%s)", dataset.id, dataset.kind)
        return dataset

    # --------------------------------------------------------------- preview
    def preview(self, dataset_id: int) -> PreviewResult:
        dataset = self._require(dataset_id)
        df = self._load_dataframe(dataset)
        kind = DatasetKind(dataset.kind)
        report = validate(df, get_schema(kind))
        preview = build_preview(df, self._settings.preview_sample_rows)
        return PreviewResult(dataset=dataset, preview=preview, report=report)

    # ---------------------------------------------------------------- import
    def import_dataset(self, dataset_id: int) -> tuple[Dataset, ImportSummary]:
        dataset = self._require(dataset_id)
        if dataset.status == DatasetStatus.IMPORTED.value:
            raise ConflictError("Dataset has already been imported.")

        df = self._load_dataframe(dataset)
        kind = DatasetKind(dataset.kind)
        report = validate(df, get_schema(kind))
        if not report.is_valid:
            self._mark_failed(dataset, f"{len(report.issues)} validation issue(s)")
            raise ValidationError("Dataset failed validation.", details=_to_details(report))

        importer = get_importer(kind)
        try:
            with transaction(self._session):
                summary = importer.run(self._session, df)
                dataset.status = DatasetStatus.IMPORTED.value
                dataset.row_count = summary.rows_imported
                dataset.error_summary = None
        except IntegrityError as exc:
            self._mark_failed(dataset, "Data conflict during import")
            raise ConflictError(
                "Import failed due to a data conflict (e.g. duplicate SKU)."
            ) from exc

        logger.info(
            "Dataset imported (id=%s, rows=%s, products=%s)",
            dataset.id,
            summary.rows_imported,
            summary.products_created,
        )
        return dataset, summary

    # --------------------------------------------------------------- helpers
    def _require(self, dataset_id: int) -> Dataset:
        dataset = self._datasets.get(dataset_id)
        if dataset is None:
            raise NotFoundError(f"Dataset {dataset_id} not found.")
        return dataset

    def _load_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        data = self._storage.read(dataset.storage_key)
        max_rows = self._settings.max_dataset_rows
        try:
            df = parse(
                dataset.original_filename,
                dataset.content_type or None,
                data,
                max_rows=max_rows,
            )
        except UnsupportedFileTypeError as exc:
            raise UnsupportedMediaTypeError(str(exc)) from exc
        except ParsingError as exc:
            # A malformed-but-typed file is a client/data problem (422), not a server
            # fault. Log the real cause; return a generic, non-leaky message.
            logger.warning("Dataset parse failed (id=%s): %s", dataset.id, exc)
            raise ValidationError(
                "The uploaded file could not be parsed as a valid CSV or Excel dataset."
            ) from exc
        if len(df) > max_rows:
            raise PayloadTooLargeError(f"Dataset exceeds the maximum of {max_rows} rows.")
        return df

    def _mark_failed(self, dataset: Dataset, summary: str) -> None:
        with transaction(self._session):
            dataset.status = DatasetStatus.FAILED.value
            dataset.error_summary = summary
