"""Deterministic financial-metrics engine.

Pure business logic: given sale lines (and an optional fixed cost) it computes a full set
of financial metrics. No I/O, no framework, no hidden state — the same inputs always yield
the same output.

Formulas (all sums are over the provided sale lines):

    total_units            = Σ quantity
    revenue = gross_revenue = Σ (unit_price × quantity)
    cogs = total_variable_cost = Σ (unit_cost × quantity)
    gross_profit           = revenue − cogs
    contribution_margin    = revenue − total_variable_cost
    net_profit             = gross_profit − total_fixed_cost
    gross_margin           = gross_profit / revenue                 (None if revenue = 0)
    contribution_margin_%  = contribution_margin / revenue          (None if revenue = 0)
    average_selling_price  = revenue / total_units                  (None if units = 0)
    unit_cost (weighted)   = cogs / total_units                     (None if units = 0)
    profit_per_unit        = ASP − weighted_unit_cost
    breakeven_units        = fixed_cost / (contribution_margin / units)  (None if CM/unit ≤ 0)
    breakeven_revenue      = fixed_cost / contribution_margin_ratio      (None if ratio ≤ 0)

Assumptions & limitations are documented in
``vault4/07-Features/financial-metrics-engine.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from app.pricing.errors import InsufficientDataError, InvalidInputError
from app.pricing.finance.models import FinancialMetrics, SaleLine
from app.pricing.finance.rounding import money, ratio, safe_div, units

_ZERO = Decimal("0")


def compute_financials(
    lines: Iterable[SaleLine],
    *,
    fixed_cost: Decimal = _ZERO,
) -> FinancialMetrics:
    """Compute financial metrics for ``lines``.

    Raises :class:`InvalidInputError` for negative inputs and
    :class:`InsufficientDataError` when there are no units to derive metrics from.
    """
    if fixed_cost < 0:
        raise InvalidInputError("fixed_cost must not be negative.")

    materialized = list(lines)
    total_units = 0
    revenue = _ZERO
    cogs = _ZERO

    for line in materialized:
        if line.quantity < 0:
            raise InvalidInputError("Sale quantity must not be negative.")
        if line.unit_price < 0:
            raise InvalidInputError("Unit price must not be negative.")
        if line.unit_cost < 0:
            raise InvalidInputError("Unit cost must not be negative.")
        quantity = Decimal(line.quantity)
        total_units += line.quantity
        revenue += line.unit_price * quantity
        cogs += line.unit_cost * quantity

    if not materialized or total_units <= 0:
        raise InsufficientDataError("No sales units available to compute metrics.")

    total_variable_cost = cogs
    gross_profit = revenue - cogs
    contribution_margin = revenue - total_variable_cost
    net_profit = gross_profit - fixed_cost

    gross_margin = safe_div(gross_profit, revenue)
    contribution_margin_ratio = safe_div(contribution_margin, revenue)
    average_selling_price = safe_div(revenue, Decimal(total_units))
    weighted_unit_cost = safe_div(cogs, Decimal(total_units))
    contribution_per_unit = safe_div(contribution_margin, Decimal(total_units))

    profit_per_unit: Decimal | None = None
    if average_selling_price is not None and weighted_unit_cost is not None:
        profit_per_unit = average_selling_price - weighted_unit_cost

    breakeven_units: Decimal | None = None
    if contribution_per_unit is not None and contribution_per_unit > 0:
        breakeven_units = safe_div(fixed_cost, contribution_per_unit)

    breakeven_revenue: Decimal | None = None
    if contribution_margin_ratio is not None and contribution_margin_ratio > 0:
        breakeven_revenue = safe_div(fixed_cost, contribution_margin_ratio)

    return FinancialMetrics(
        total_units=total_units,
        revenue=money(revenue),
        gross_revenue=money(revenue),
        cogs=money(cogs),
        total_variable_cost=money(total_variable_cost),
        total_fixed_cost=money(fixed_cost),
        gross_profit=money(gross_profit),
        net_profit=money(net_profit),
        contribution_margin=money(contribution_margin),
        gross_margin=None if gross_margin is None else ratio(gross_margin),
        contribution_margin_ratio=(
            None if contribution_margin_ratio is None else ratio(contribution_margin_ratio)
        ),
        average_selling_price=(
            None if average_selling_price is None else money(average_selling_price)
        ),
        unit_cost=None if weighted_unit_cost is None else money(weighted_unit_cost),
        profit_per_unit=None if profit_per_unit is None else money(profit_per_unit),
        breakeven_units=None if breakeven_units is None else units(breakeven_units),
        breakeven_revenue=None if breakeven_revenue is None else money(breakeven_revenue),
    )
