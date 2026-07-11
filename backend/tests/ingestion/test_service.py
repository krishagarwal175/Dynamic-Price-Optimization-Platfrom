"""Tests for the ingestion service: upload, import, and rollback."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.config import AppEnv, Settings
from app.core.errors import (
    ConflictError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
    ValidationError,
)
from app.models.dataset import DatasetKind, DatasetStatus
from app.models.product import Product
from app.services.ingestion import IngestionService
from app.storage.local import LocalFileStorage
from tests.support import catalog_df, make_business_db, to_csv_bytes


def _make_service(
    tmp_path: Path, *, max_upload_bytes: int = 10 * 1024 * 1024
) -> tuple[Session, IngestionService]:
    _, factory = make_business_db()
    session = factory()
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=AppEnv.LOCAL,
        database_url="sqlite://",
        file_storage_path=str(tmp_path / "storage"),
        max_upload_bytes=max_upload_bytes,
        preview_sample_rows=5,
    )
    storage = LocalFileStorage(tmp_path / "storage")
    return session, IngestionService(session, storage, settings)


def _upload_valid(service: IngestionService, filename: str = "catalog.csv") -> int:
    dataset = service.upload(
        filename=filename,
        content_type="text/csv",
        data=to_csv_bytes(catalog_df()),
        kind=DatasetKind.PRODUCT_CATALOG,
    )
    return dataset.id


@pytest.mark.integration
def test_upload_rejects_unsupported_type(tmp_path: Path) -> None:
    _, service = _make_service(tmp_path)
    with pytest.raises(UnsupportedMediaTypeError):
        service.upload(
            filename="data.txt",
            content_type="text/plain",
            data=b"x",
            kind=DatasetKind.PRODUCT_CATALOG,
        )


@pytest.mark.integration
def test_upload_rejects_too_large(tmp_path: Path) -> None:
    _, service = _make_service(tmp_path, max_upload_bytes=5)
    with pytest.raises(PayloadTooLargeError):
        service.upload(
            filename="catalog.csv",
            content_type="text/csv",
            data=to_csv_bytes(catalog_df()),
            kind=DatasetKind.PRODUCT_CATALOG,
        )


@pytest.mark.integration
def test_upload_persists_dataset_and_stores_file(tmp_path: Path) -> None:
    session, service = _make_service(tmp_path)
    dataset_id = _upload_valid(service)
    dataset = service._require(dataset_id)  # noqa: SLF001 - test inspects internal state
    assert dataset.status == DatasetStatus.UPLOADED.value
    assert service._storage.exists(dataset.storage_key)  # noqa: SLF001


@pytest.mark.integration
def test_import_happy_path(tmp_path: Path) -> None:
    session, service = _make_service(tmp_path)
    dataset_id = _upload_valid(service)

    dataset, summary = service.import_dataset(dataset_id)
    assert dataset.status == DatasetStatus.IMPORTED.value
    assert summary.products_created == 3
    assert summary.categories_created == 2  # Beverages, Snacks
    assert dataset.row_count == 3
    assert session.query(Product).count() == 3


@pytest.mark.integration
def test_import_rejects_invalid_dataset(tmp_path: Path) -> None:
    session, service = _make_service(tmp_path)
    bad = catalog_df().drop(columns=["base_price"])  # remove a required column
    dataset = service.upload(
        filename="bad.csv",
        content_type="text/csv",
        data=to_csv_bytes(bad),
        kind=DatasetKind.PRODUCT_CATALOG,
    )

    with pytest.raises(ValidationError):
        service.import_dataset(dataset.id)

    refreshed = service._require(dataset.id)  # noqa: SLF001
    assert refreshed.status == DatasetStatus.FAILED.value
    assert session.query(Product).count() == 0


@pytest.mark.integration
def test_import_rolls_back_on_integrity_error(tmp_path: Path) -> None:
    session, service = _make_service(tmp_path)

    # First dataset imports cleanly.
    first = _upload_valid(service, "first.csv")
    service.import_dataset(first)
    assert session.query(Product).count() == 3

    # Second dataset re-uses SKU-1 (valid on its own, but a DB unique conflict on import).
    conflict_rows = [
        {
            "sku": "SKU-1",
            "name": "Dup",
            "category": "Beverages",
            "unit_cost": "1.00",
            "base_price": "2.00",
        }
    ]
    second = service.upload(
        filename="second.csv",
        content_type="text/csv",
        data=to_csv_bytes(catalog_df(conflict_rows)),
        kind=DatasetKind.PRODUCT_CATALOG,
    )

    with pytest.raises(ConflictError):
        service.import_dataset(second.id)

    # Rollback: no new products, and the second dataset is marked failed.
    assert session.query(Product).count() == 3
    refreshed = service._require(second.id)  # noqa: SLF001
    assert refreshed.status == DatasetStatus.FAILED.value
