"""Interpretation helpers — turn engine numbers into business language.

Pure text composition. These functions *describe* results produced elsewhere; they never
compute business metrics.
"""

from __future__ import annotations

_PRICE_EPS = 1e-6


def overall_recommendation(current_price: float, recommended_price: float, currency: str) -> str:
    if abs(recommended_price - current_price) <= _PRICE_EPS:
        return f"Maintain the current price of {_money(current_price, currency)}."
    direction = "increase" if recommended_price > current_price else "reduce"
    return (
        f"{direction.capitalize()} the price from {_money(current_price, currency)} to "
        f"{_money(recommended_price, currency)}."
    )


def key_conclusion(objective: str, improvement: float, classification: str) -> str:
    goal = objective.replace("maximize_", "").replace("_", " ")
    if improvement > _PRICE_EPS:
        return (
            f"Repricing is expected to improve {goal} by {improvement:,.2f} versus the "
            f"current price, given {classification.replace('_', ' ')} demand."
        )
    return (
        f"The current price is already near-optimal for {goal}; no material improvement is "
        "expected from repricing."
    )


def elasticity_interpretation(classification: str, coefficient: float) -> str:
    magnitude = abs(coefficient)
    if classification == "perfectly_inelastic":
        return "Demand does not respond to price changes."
    if classification in ("inelastic",):
        return (
            f"Demand is inelastic (|E|={magnitude:.2f} < 1): quantity changes less than "
            "proportionally to price, so higher prices tend to raise revenue."
        )
    if classification == "unit_elastic":
        return (
            "Demand is unit elastic (|E|≈1): revenue is roughly insensitive to small price moves."
        )
    if classification in ("elastic", "highly_elastic"):
        return (
            f"Demand is elastic (|E|={magnitude:.2f} > 1): quantity changes more than "
            "proportionally to price, so lower prices tend to raise revenue."
        )
    return "Demand is perfectly elastic: customers will not tolerate any price increase."


def elasticity_implications(classification: str) -> tuple[str, ...]:
    if classification in ("inelastic", "perfectly_inelastic"):
        return (
            "There is room to raise price with limited volume loss.",
            "Revenue is likely maximized at a higher price than today.",
        )
    if classification == "unit_elastic":
        return ("Price changes have little effect on revenue; focus on margin and cost.",)
    return (
        "Price increases risk significant volume loss.",
        "Discounts can materially grow unit volume.",
    )


def forecast_interpretation(strategy: str, values: tuple[float, ...]) -> str:
    if not values:
        return "No forecast is available."
    first = values[0]
    return (
        f"The '{strategy.replace('_', ' ')}' method projects demand of about {first:,.2f} "
        "units per period over the horizon (flat projection)."
    )


def financial_notes(net_profit: float, gross_margin: float | None) -> tuple[str, ...]:
    notes: list[str] = []
    notes.append("Net profit is positive." if net_profit > 0 else "Net profit is non-positive.")
    if gross_margin is not None:
        notes.append(f"Gross margin is {gross_margin * 100:.1f}%.")
    return tuple(notes)


def pricing_action(current_price: float, recommended_price: float, currency: str) -> str:
    if abs(recommended_price - current_price) <= _PRICE_EPS:
        return "Hold price steady."
    verb = "Raise" if recommended_price > current_price else "Lower"
    return f"{verb} price to {_money(recommended_price, currency)}."


def recommendations(
    *, improvement: float, classification: str, binding_constraints: tuple[str, ...]
) -> tuple[str, ...]:
    items: list[str] = []
    if improvement > _PRICE_EPS:
        items.append("Adopt the recommended price to capture the projected profit uplift.")
    else:
        items.append("Keep the current price; revisit if costs or demand shift.")
    if classification in ("elastic", "highly_elastic"):
        items.append("Consider targeted promotions to exploit high price sensitivity.")
    else:
        items.append("Test modest price increases to capture inelastic demand.")
    if binding_constraints:
        items.append(
            "Relaxing binding constraints (" + ", ".join(binding_constraints) + ") may unlock "
            "further gains."
        )
    return tuple(items)


def risks(classification: str, r_squared: float | None) -> tuple[str, ...]:
    items: list[str] = []
    if r_squared is not None and r_squared < 0.5:
        items.append(f"Elasticity fit is weak (R²={r_squared:.2f}); estimates are uncertain.")
    if classification in ("elastic", "highly_elastic"):
        items.append("A price increase could cause larger-than-expected volume loss.")
    items.append("Competitor reactions and market shifts are not modelled.")
    return tuple(items)


def monitoring() -> tuple[str, ...]:
    return (
        "Track realized demand versus the forecast after any price change.",
        "Re-estimate elasticity as new sales accumulate.",
        "Watch margin and net profit against the projections.",
    )


def implementation_notes(scope: str) -> tuple[str, ...]:
    notes = [
        "Apply the price change gradually and observe the demand response.",
        "This report is advisory; no prices are changed automatically.",
    ]
    if scope == "dataset":
        notes.append(
            "Dataset-level figures aggregate all products; validate per product before acting."
        )
    return tuple(notes)


def _money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"
