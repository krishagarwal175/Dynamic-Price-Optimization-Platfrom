"""Tests for the parsing layer (bytes -> DataFrame)."""

from __future__ import annotations

import pytest

from app.ingestion.errors import UnsupportedFileTypeError
from app.ingestion.parsing import FileFormat, detect_format, parse
from tests.support import catalog_df, to_csv_bytes, to_xlsx_bytes


@pytest.mark.unit
def test_detect_format_by_extension() -> None:
    assert detect_format("a.csv", None) is FileFormat.CSV
    assert detect_format("a.xlsx", None) is FileFormat.XLSX


@pytest.mark.unit
def test_detect_format_by_content_type() -> None:
    fmt = detect_format(
        "noext",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert fmt is FileFormat.XLSX


@pytest.mark.unit
def test_unsupported_type_raises() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        detect_format("data.txt", "text/plain")


@pytest.mark.integration
def test_parse_csv_roundtrip() -> None:
    df = parse("catalog.csv", "text/csv", to_csv_bytes(catalog_df()))
    assert list(df.columns) == ["sku", "name", "category", "unit_cost", "base_price"]
    assert len(df) == 3


@pytest.mark.integration
def test_parse_xlsx_roundtrip() -> None:
    df = parse("catalog.xlsx", None, to_xlsx_bytes(catalog_df()))
    assert len(df) == 3
    assert "sku" in df.columns


@pytest.mark.integration
def test_parse_empty_file_returns_empty_frame() -> None:
    df = parse("empty.csv", "text/csv", b"")
    assert df.empty
