"""File parsing: bytes -> pandas DataFrame.

This layer only turns a file into a table. It knows nothing about business rules — data
validation lives in ``app.ingestion.validation``.
"""

from __future__ import annotations

import io
from enum import Enum

import pandas as pd

from app.ingestion.errors import ParsingError, UnsupportedFileTypeError


class FileFormat(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"


_EXTENSION_FORMATS = {
    ".csv": FileFormat.CSV,
    ".xlsx": FileFormat.XLSX,
}

_CONTENT_TYPE_FORMATS = {
    "text/csv": FileFormat.CSV,
    "application/vnd.ms-excel": FileFormat.CSV,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileFormat.XLSX,
}


def detect_format(filename: str, content_type: str | None) -> FileFormat:
    """Determine the file format from extension (preferred) or content type."""
    lowered = filename.lower()
    for ext, fmt in _EXTENSION_FORMATS.items():
        if lowered.endswith(ext):
            return fmt
    if content_type and content_type in _CONTENT_TYPE_FORMATS:
        return _CONTENT_TYPE_FORMATS[content_type]
    raise UnsupportedFileTypeError(
        f"Unsupported file type for {filename!r}. Supported: .csv, .xlsx"
    )


def parse(
    filename: str,
    content_type: str | None,
    data: bytes,
    *,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """Parse raw bytes into a DataFrame according to the detected format.

    Columns are read as-is (dtype coercion is the validator's job). When ``max_rows`` is
    given, CSV reading is bounded to ``max_rows + 1`` rows so an oversized file cannot be
    fully materialized in memory; the caller enforces the hard cap. Raises
    :class:`UnsupportedFileTypeError` or :class:`ParsingError`.
    """
    fmt = detect_format(filename, content_type)
    nrows = max_rows + 1 if max_rows is not None else None
    try:
        if fmt is FileFormat.CSV:
            return pd.read_csv(io.BytesIO(data), dtype=str, keep_default_na=True, nrows=nrows)
        return pd.read_excel(io.BytesIO(data), dtype=str, engine="openpyxl", nrows=nrows)
    except UnsupportedFileTypeError:
        raise
    except pd.errors.EmptyDataError:
        # An empty/headerless file parses to an empty frame; treat as a valid-but-empty
        # table so the validator can report it as a structured issue.
        return pd.DataFrame()
    except Exception as exc:  # noqa: BLE001 - normalize any parser failure
        raise ParsingError(f"Could not parse {filename!r}: {exc}") from exc
