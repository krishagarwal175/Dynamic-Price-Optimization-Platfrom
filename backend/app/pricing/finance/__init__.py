"""Financial-metrics sub-engine (pure, deterministic)."""

from __future__ import annotations

from app.pricing.finance.engine import compute_financials
from app.pricing.finance.models import FinancialMetrics, SaleLine

__all__ = ["FinancialMetrics", "SaleLine", "compute_financials"]
