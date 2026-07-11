"""Small pandas helpers shared across the ingestion layer."""

from __future__ import annotations

import warnings
from typing import Any

import pandas as pd


def coerce_dates(series: pd.Series[str]) -> pd.Series[Any]:
    """Best-effort date coercion, suppressing pandas' format-guess ``UserWarning``.

    This is deliberate type inference / validation over free-form text, not authoritative
    parsing, so the "could not infer format" notice is noise here.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.to_datetime(series, errors="coerce")
