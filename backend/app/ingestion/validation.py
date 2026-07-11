"""Reusable, structured dataset validation.

A dataset is validated against a :class:`DatasetSchema` (a list of :class:`ColumnSpec`).
Problems are returned as structured :class:`ValidationIssue` records rather than raised,
so callers can present them all at once. Parsing/format errors remain exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import pandas as pd

from app.ingestion.frames import coerce_dates

MAX_ISSUES = 200


class ColumnType(str, Enum):
    STRING = "string"
    NUMERIC = "numeric"
    DATE = "date"


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: ColumnType = ColumnType.STRING
    required: bool = True
    non_negative: bool = False
    unique: bool = False


@dataclass(frozen=True)
class DatasetSchema:
    columns: list[ColumnSpec]

    @property
    def required_columns(self) -> list[str]:
        return [c.name for c in self.columns if c.required]


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    column: str | None = None
    row: int | None = None  # 1-based data row (excludes header), when applicable


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    truncated: bool = False

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def _add(self, issue: ValidationIssue) -> None:
        if len(self.issues) >= MAX_ISSUES:
            self.truncated = True
            return
        self.issues.append(issue)


def _duplicate_columns(columns: list[str]) -> list[str]:
    """Detect duplicate source columns via pandas' ``name.N`` mangling."""
    duplicates = []
    for col in columns:
        base, _, suffix = col.rpartition(".")
        if base and suffix.isdigit() and base in columns:
            duplicates.append(base)
    return sorted(set(duplicates))


def validate(df: pd.DataFrame, schema: DatasetSchema) -> ValidationReport:
    report = ValidationReport()

    for base in _duplicate_columns(list(df.columns)):
        report._add(ValidationIssue("DUPLICATE_COLUMN", f"Duplicate column {base!r}.", column=base))

    if df.shape[0] == 0:
        report._add(ValidationIssue("EMPTY_DATASET", "The dataset contains no rows."))

    present = set(df.columns)
    for spec in schema.columns:
        if spec.required and spec.name not in present:
            report._add(
                ValidationIssue(
                    "MISSING_COLUMN",
                    f"Required column {spec.name!r} is missing.",
                    column=spec.name,
                )
            )

    for spec in schema.columns:
        if spec.name not in present:
            continue
        _validate_column(df[spec.name], spec, report)

    return report


def _row_numbers(mask: pd.Series[bool]) -> list[int]:
    """1-based positional row numbers where ``mask`` is True."""
    return [pos + 1 for pos, flag in enumerate(mask.tolist()) if flag]


def _validate_column(series: pd.Series[str], spec: ColumnSpec, report: ValidationReport) -> None:
    missing = series.isna()
    if spec.required:
        for row in _row_numbers(missing):
            report._add(
                ValidationIssue(
                    "MISSING_VALUE",
                    f"Missing required value in {spec.name!r}.",
                    column=spec.name,
                    row=row,
                )
            )

    if spec.dtype is ColumnType.NUMERIC:
        coerced = pd.to_numeric(series, errors="coerce")
        invalid = coerced.isna() & series.notna()
        for row in _row_numbers(invalid):
            report._add(
                ValidationIssue(
                    "INVALID_NUMERIC",
                    f"Value in {spec.name!r} is not a valid number.",
                    column=spec.name,
                    row=row,
                )
            )
        if spec.non_negative:
            negative = coerced < 0
            for row in _row_numbers(negative.fillna(False)):
                report._add(
                    ValidationIssue(
                        "NEGATIVE_VALUE",
                        f"Value in {spec.name!r} must not be negative.",
                        column=spec.name,
                        row=row,
                    )
                )

    if spec.dtype is ColumnType.DATE:
        coerced = coerce_dates(series)
        invalid = coerced.isna() & series.notna()
        for row in _row_numbers(invalid):
            report._add(
                ValidationIssue(
                    "INVALID_DATE",
                    f"Value in {spec.name!r} is not a valid date.",
                    column=spec.name,
                    row=row,
                )
            )

    if spec.unique:
        duplicated = series.duplicated(keep=False) & series.notna()
        for row in _row_numbers(duplicated):
            report._add(
                ValidationIssue(
                    "DUPLICATE_VALUE",
                    f"Duplicate value in unique column {spec.name!r}.",
                    column=spec.name,
                    row=row,
                )
            )
