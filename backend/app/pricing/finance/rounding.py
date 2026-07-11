"""Deterministic rounding and safe division for financial calculations.

All monetary values are quantized to 2 decimal places and all ratios to 4, using
banker-free ``ROUND_HALF_UP`` so results are stable and predictable.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")
RATIO_QUANTUM = Decimal("0.0001")
UNITS_QUANTUM = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Quantize a monetary value to 2 decimal places."""
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def ratio(value: Decimal) -> Decimal:
    """Quantize a ratio (e.g. a margin) to 4 decimal places."""
    return value.quantize(RATIO_QUANTUM, rounding=ROUND_HALF_UP)


def units(value: Decimal) -> Decimal:
    """Quantize a (possibly fractional) unit count to 2 decimal places."""
    return value.quantize(UNITS_QUANTUM, rounding=ROUND_HALF_UP)


def safe_div(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    """Return ``numerator / denominator`` or ``None`` when the denominator is zero."""
    if denominator == 0:
        return None
    return numerator / denominator
