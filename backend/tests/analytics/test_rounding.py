"""Unit tests for rounding/division helpers."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.pricing.finance.rounding import money, ratio, safe_div, units


@pytest.mark.unit
def test_money_half_up() -> None:
    assert money(Decimal("1.005")) == Decimal("1.01")
    assert money(Decimal("1.004")) == Decimal("1.00")


@pytest.mark.unit
def test_ratio_four_places() -> None:
    assert ratio(Decimal("0.66666")) == Decimal("0.6667")


@pytest.mark.unit
def test_units_two_places() -> None:
    assert units(Decimal("30.005")) == Decimal("30.01")


@pytest.mark.unit
def test_safe_div_guards_zero() -> None:
    assert safe_div(Decimal("10"), Decimal("0")) is None
    assert safe_div(Decimal("10"), Decimal("4")) == Decimal("2.5")
