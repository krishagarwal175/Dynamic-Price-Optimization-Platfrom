"""Hardening coverage for ingestion: re-import conflict, parse failure, row cap."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.config import AppEnv, Settings
from app.core.errors import ConflictError, PayloadTooLargeError, ValidationError
from app.models.dataset import DatasetKind
from app.services.ingestion import IngestionService
from app.storage.local import LocalFileStorage
from tests.support import catalog_df, make_business_db, to_csv_bytes


def _make_service(
    tmp_path: Path, *, max_dataset_rows: int = 100_000
) -> tuple[Session, IngestionService]:
    _, factory = make_business_db()
    session = factory()
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=AppEnv.LOCAL,
        database_url="sqlite://",
        file_storage_path=str(tmp_path / "storage"),
        max_dataset_rows=max_dataset_rows,
        preview_sample_rows=5,
    )
    storage = LocalFileStorage(tmp_path / "storage")
    return session, IngestionService(session, storage, settings)


def _upload_valid(service: IngestionService) -> int:
    dataset = service.upload(
        filename="catalog.csv",
        content_type="text/csv",
        data=to_csv_bytes(catalog_df()),
        kind=DatasetKind.PRODUCT_CATALOG,
    )
    return dataset.id


@pytest.mark.integration
def test_reimport_is_rejected_as_conflict(tmp_path: Path) -> None:
    _, service = _make_service(tmp_path)
    dataset_id = _upload_valid(service)
    service.import_dataset(dataset_id)
    with pytest.raises(ConflictError):
        service.import_dataset(dataset_id)


@pytest.mark.integration
def test_unparseable_file_surfaces_as_validation_error(tmp_path: Path) -> None:
    _, service = _make_service(tmp_path)
    # Valid .xlsx extension/content-type, but the bytes are not a real workbook.
    dataset = service.upload(
        filename="broken.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        data=b"this is not a real xlsx file",
        kind=DatasetKind.PRODUCT_CATALOG,
    )
    with pytest.raises(ValidationError):
        service.preview(dataset.id)


@pytest.mark.integration
def test_row_cap_is_enforced(tmp_path: Path) -> None:
    _, service = _make_service(tmp_path, max_dataset_rows=2)
    dataset_id = _upload_valid(service)  # the fixture catalog has 3 rows
    with pytest.raises(PayloadTooLargeError):
        service.preview(dataset_id)
