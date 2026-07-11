"""Dataset preview generation for user inspection before import."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.ingestion.frames import coerce_dates


@dataclass(frozen=True)
class DatasetPreview:
    columns: list[str]
    inferred_types: dict[str, str]
    row_count: int
    missing_values: dict[str, int]
    duplicate_rows: int
    sample_rows: list[dict[str, Any]]


def _infer_type(series: pd.Series[str]) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return "unknown"
    numeric = pd.to_numeric(non_null, errors="coerce")
    if bool(numeric.notna().all()):
        return "integer" if bool((numeric == numeric.round()).all()) else "numeric"
    dates = coerce_dates(non_null)
    if bool(dates.notna().all()):
        return "date"
    return "string"


def build_preview(df: pd.DataFrame, sample_size: int) -> DatasetPreview:
    columns = [str(c) for c in df.columns]
    inferred = {col: _infer_type(df[col]) for col in columns}
    missing = {col: int(df[col].isna().sum()) for col in columns}
    duplicate_rows = int(df.duplicated().sum())

    head = df.head(max(sample_size, 0))
    # Replace NaN with None so the sample is JSON-serializable.
    safe = head.astype(object).where(pd.notna(head), None)
    sample_rows: list[dict[str, Any]] = safe.to_dict(orient="records")

    return DatasetPreview(
        columns=columns,
        inferred_types=inferred,
        row_count=int(len(df)),
        missing_values=missing,
        duplicate_rows=duplicate_rows,
        sample_rows=sample_rows,
    )
