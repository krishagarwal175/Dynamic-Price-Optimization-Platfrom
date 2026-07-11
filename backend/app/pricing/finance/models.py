"""Value objects for the financial-metrics engine (framework-free)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SaleLine:
    """One unit-economics observation: ``quantity`` sold at ``unit_price`` for a product
    whose variable cost is ``unit_cost``. The engine consumes plain lines like these and
    knows nothing about the ORM or where they came from."""

    quantity: int
    unit_price: Decimal
    unit_cost: Decimal


@dataclass(frozen=True)
class FinancialMetrics:
    """Deterministic financial metrics for a set of sale lines.

    Ratio and per-unit fields are ``None`` when undefined (e.g. a margin when revenue is
    zero, or break-even when contribution per unit is not positive).
    """

    total_units: int
    revenue: Decimal
    gross_revenue: Decimal
    cogs: Decimal
    total_variable_cost: Decimal
    total_fixed_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    contribution_margin: Decimal
    gross_margin: Decimal | None
    contribution_margin_ratio: Decimal | None
    average_selling_price: Decimal | None
    unit_cost: Decimal | None
    profit_per_unit: Decimal | None
    breakeven_units: Decimal | None
    breakeven_revenue: Decimal | None
