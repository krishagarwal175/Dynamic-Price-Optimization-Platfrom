"""Tests for preview generation."""

from __future__ import annotations

import pandas as pd
import pytest

from app.ingestion.preview import build_preview


@pytest.mark.unit
def test_preview_reports_structure() -> None:
    df = pd.DataFrame(
        {
            "sku": ["A", "B", "A"],
            "price": ["1.5", "2.0", None],
            "when": ["2026-01-01", "2026-01-02", "2026-01-03"],
        },
        dtype=object,
    )
    preview = build_preview(df, sample_size=2)

    assert preview.columns == ["sku", "price", "when"]
    assert preview.row_count == 3
    assert preview.missing_values["price"] == 1
    assert preview.inferred_types["price"] == "numeric"
    assert preview.inferred_types["when"] == "date"
    assert len(preview.sample_rows) == 2


@pytest.mark.unit
def test_preview_counts_duplicate_rows() -> None:
    df = pd.DataFrame({"a": ["1", "1"], "b": ["x", "x"]}, dtype=str)
    preview = build_preview(df, sample_size=5)
    assert preview.duplicate_rows == 1


@pytest.mark.unit
def test_preview_sample_is_json_safe() -> None:
    df = pd.DataFrame({"a": ["1", None]}, dtype=object)
    preview = build_preview(df, sample_size=5)
    assert preview.sample_rows[1]["a"] is None
