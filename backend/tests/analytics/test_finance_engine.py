"""Unit tests for the financial-metrics engine — every formula and edge case."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.pricing.errors import InsufficientDataError, InvalidInputError
from app.pricing.finance import SaleLine, compute_financials


def _lines() -> list[SaleLine]:
    # revenue = 10*5 + 5*6 = 80 ; cogs = 15*2 = 30 ; units = 15
    return [
        SaleLine(quantity=10, unit_price=Decimal("5.00"), unit_cost=Decimal("2.00")),
        SaleLine(quantity=5, unit_price=Decimal("6.00"), unit_cost=Decimal("2.00")),
    ]


@pytest.mark.unit
def test_core_metrics() -> None:
    m = compute_financials(_lines())
    assert m.total_units == 15
    assert m.revenue == Decimal("80.00")
    assert m.gross_revenue == Decimal("80.00")
    assert m.cogs == Decimal("30.00")
    assert m.total_variable_cost == Decimal("30.00")
    assert m.gross_profit == Decimal("50.00")
    assert m.contribution_margin == Decimal("50.00")
    assert m.gross_margin == Decimal("0.6250")
    assert m.contribution_margin_ratio == Decimal("0.6250")
    assert m.average_selling_price == Decimal("5.33")  # 80/15 = 5.3333 -> 5.33
    assert m.unit_cost == Decimal("2.00")
    assert m.profit_per_unit == Decimal("3.33")  # 5.3333 - 2 -> 3.33


@pytest.mark.unit
def test_fixed_cost_drives_net_profit_and_breakeven() -> None:
    m = compute_financials(_lines(), fixed_cost=Decimal("100.00"))
    assert m.total_fixed_cost == Decimal("100.00")
    assert m.net_profit == Decimal("-50.00")  # 50 - 100
    # contribution per unit = 50/15 = 3.3333 ; breakeven units = 100 / 3.3333 = 30
    assert m.breakeven_units == Decimal("30.00")
    # breakeven revenue = fixed / CM ratio = 100 / 0.625 = 160
    assert m.breakeven_revenue == Decimal("160.00")


@pytest.mark.unit
def test_zero_fixed_cost_breakeven_is_zero() -> None:
    m = compute_financials(_lines())
    assert m.net_profit == Decimal("50.00")
    assert m.breakeven_units == Decimal("0.00")
    assert m.breakeven_revenue == Decimal("0.00")


@pytest.mark.unit
def test_zero_revenue_yields_undefined_ratios() -> None:
    m = compute_financials([SaleLine(5, Decimal("0.00"), Decimal("2.00"))])
    assert m.revenue == Decimal("0.00")
    assert m.gross_margin is None
    assert m.contribution_margin_ratio is None
    assert m.average_selling_price == Decimal("0.00")
    assert m.unit_cost == Decimal("2.00")
    assert m.profit_per_unit == Decimal("-2.00")
    # selling below cost -> break-even unreachable
    assert m.breakeven_units is None
    assert m.breakeven_revenue is None


@pytest.mark.unit
def test_selling_at_cost_has_no_finite_breakeven() -> None:
    m = compute_financials(
        [SaleLine(4, Decimal("2.00"), Decimal("2.00"))], fixed_cost=Decimal("10.00")
    )
    assert m.contribution_margin == Decimal("0.00")
    assert m.breakeven_units is None
    assert m.breakeven_revenue is None


@pytest.mark.unit
def test_rounding_half_up() -> None:
    # revenue 100 over 3 units -> ASP 33.3333 -> 33.33 ; 100/8=12.5 handled elsewhere
    m = compute_financials([SaleLine(3, Decimal("33.335"), Decimal("10.00"))])
    # revenue = 3 * 33.335 = 100.005 -> 100.01 (half up)
    assert m.revenue == Decimal("100.01")


@pytest.mark.unit
def test_empty_input_raises_insufficient_data() -> None:
    with pytest.raises(InsufficientDataError):
        compute_financials([])


@pytest.mark.unit
def test_zero_total_units_raises_insufficient_data() -> None:
    with pytest.raises(InsufficientDataError):
        compute_financials([SaleLine(0, Decimal("5.00"), Decimal("2.00"))])


@pytest.mark.unit
@pytest.mark.parametrize(
    "line",
    [
        SaleLine(-1, Decimal("5.00"), Decimal("2.00")),
        SaleLine(1, Decimal("-5.00"), Decimal("2.00")),
        SaleLine(1, Decimal("5.00"), Decimal("-2.00")),
    ],
)
def test_negative_inputs_raise_invalid_input(line: SaleLine) -> None:
    with pytest.raises(InvalidInputError):
        compute_financials([line])


@pytest.mark.unit
def test_negative_fixed_cost_raises() -> None:
    with pytest.raises(InvalidInputError):
        compute_financials(_lines(), fixed_cost=Decimal("-1"))
