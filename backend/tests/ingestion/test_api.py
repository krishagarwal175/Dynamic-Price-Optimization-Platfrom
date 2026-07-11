"""End-to-end API tests for the ingestion endpoints."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401  (register models before create_all)
from app.core.config import AppEnv, Settings
from app.core.database import Base
from app.main import create_app
from tests.support import catalog_df, to_csv_bytes, to_xlsx_bytes


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=AppEnv.LOCAL,
        app_name="Test API",
        log_level="WARNING",
        cors_allowed_origins=["http://testserver"],
        database_url="sqlite://",
        file_storage_path=str(tmp_path / "storage"),
        preview_sample_rows=5,
    )
    application = create_app(settings)
    Base.metadata.create_all(application.state.db_engine)
    with TestClient(application) as test_client:
        yield test_client


def _upload(
    client: TestClient,
    *,
    filename: str = "catalog.csv",
    content: bytes | None = None,
    content_type: str = "text/csv",
) -> int:
    payload = content if content is not None else to_csv_bytes(catalog_df())
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": (filename, payload, content_type)},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


@pytest.mark.integration
def test_upload_preview_import_flow(client: TestClient) -> None:
    dataset_id = _upload(client)

    preview = client.get(f"/api/v1/datasets/{dataset_id}/preview")
    assert preview.status_code == 200
    body = preview.json()["data"]
    assert body["row_count"] == 3
    assert body["validation"]["is_valid"] is True
    assert set(body["columns"]) >= {"sku", "name", "category", "unit_cost", "base_price"}

    result = client.post(f"/api/v1/datasets/{dataset_id}/import")
    assert result.status_code == 200
    data = result.json()["data"]
    assert data["status"] == "imported"
    assert data["products_created"] == 3


@pytest.mark.integration
def test_xlsx_upload_supported(client: TestClient) -> None:
    dataset_id = _upload(
        client,
        filename="catalog.xlsx",
        content=to_xlsx_bytes(catalog_df()),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    result = client.post(f"/api/v1/datasets/{dataset_id}/import")
    assert result.status_code == 200


@pytest.mark.integration
def test_unsupported_type_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("data.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


@pytest.mark.integration
def test_import_invalid_dataset_returns_422(client: TestClient) -> None:
    bad = catalog_df().drop(columns=["base_price"])
    dataset_id = _upload(client, filename="bad.csv", content=to_csv_bytes(bad))

    result = client.post(f"/api/v1/datasets/{dataset_id}/import")
    assert result.status_code == 422
    body = result.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert len(body["error"]["details"]) >= 1


@pytest.mark.integration
def test_preview_missing_dataset_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/datasets/999/preview")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
