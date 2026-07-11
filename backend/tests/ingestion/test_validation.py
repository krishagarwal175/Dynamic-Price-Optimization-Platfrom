"""Tests for the structured validation framework."""

from __future__ import annotations

import pandas as pd
import pytest

from app.ingestion.catalog import PRODUCT_CATALOG_SCHEMA
from app.ingestion.validation import validate


def _codes(df: pd.DataFrame) -> set[str]:
    return {issue.code for issue in validate(df, PRODUCT_CATALOG_SCHEMA).issues}


@pytest.mark.unit
def test_valid_dataset_has_no_issues() -> None:
    df = pd.DataFrame(
        {
            "sku": ["A", "B"],
            "name": ["x", "y"],
            "category": ["c", "c"],
            "unit_cost": ["1.0", "2.0"],
            "base_price": ["2.0", "3.0"],
        },
        dtype=str,
    )
    assert validate(df, PRODUCT_CATALOG_SCHEMA).is_valid


@pytest.mark.unit
def test_empty_dataset_flagged() -> None:
    df = pd.DataFrame({c: [] for c in ["sku", "name", "category", "unit_cost", "base_price"]})
    assert "EMPTY_DATASET" in _codes(df)


@pytest.mark.unit
def test_missing_required_column() -> None:
    df = pd.DataFrame({"sku": ["A"], "name": ["x"], "category": ["c"], "unit_cost": ["1"]})
    assert "MISSING_COLUMN" in _codes(df)


@pytest.mark.unit
def test_invalid_numeric_and_negative() -> None:
    df = pd.DataFrame(
        {
            "sku": ["A", "B"],
            "name": ["x", "y"],
            "category": ["c", "c"],
            "unit_cost": ["not-a-number", "-3"],
            "base_price": ["2", "3"],
        },
        dtype=str,
    )
    codes = _codes(df)
    assert "INVALID_NUMERIC" in codes
    assert "NEGATIVE_VALUE" in codes


@pytest.mark.unit
def test_missing_required_value() -> None:
    df = pd.DataFrame(
        {
            "sku": ["A", None],
            "name": ["x", "y"],
            "category": ["c", "c"],
            "unit_cost": ["1", "2"],
            "base_price": ["2", "3"],
        },
        dtype=object,
    )
    assert "MISSING_VALUE" in _codes(df)


@pytest.mark.unit
def test_duplicate_unique_value() -> None:
    df = pd.DataFrame(
        {
            "sku": ["DUP", "DUP"],
            "name": ["x", "y"],
            "category": ["c", "c"],
            "unit_cost": ["1", "2"],
            "base_price": ["2", "3"],
        },
        dtype=str,
    )
    assert "DUPLICATE_VALUE" in _codes(df)


@pytest.mark.unit
def test_duplicate_column_detected() -> None:
    # pandas mangles a repeated header to "sku.1"; the validator maps it back to "sku".
    raw = pd.DataFrame([["A", "B", "x", "c", "1", "2"]])
    raw.columns = ["sku", "sku.1", "name", "category", "unit_cost", "base_price"]
    assert "DUPLICATE_COLUMN" in _codes(raw)


@pytest.mark.unit
def test_invalid_date() -> None:
    from app.ingestion.validation import ColumnSpec, ColumnType, DatasetSchema

    schema = DatasetSchema(columns=[ColumnSpec("when", ColumnType.DATE, required=True)])
    df = pd.DataFrame({"when": ["2026-01-01", "not-a-date"]}, dtype=str)
    codes = {i.code for i in validate(df, schema).issues}
    assert "INVALID_DATE" in codes
