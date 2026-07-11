"""Structured, human-readable diagnostics for a scenario outcome."""

from __future__ import annotations

from app.pricing.simulation.models import ScenarioDiagnostics, ScenarioType

_EPS = 1e-9


def build_diagnostics(
    *,
    scenario_type: ScenarioType,
    price_change_pct: float | None,
    demand_change_pct: float | None,
    revenue_delta: float,
    net_profit_delta: float,
    margin_points: float,
    is_recommended: bool,
) -> ScenarioDiagnostics:
    revenue_improved = revenue_delta > _EPS
    profit_improved = net_profit_delta > _EPS
    margin_improved = margin_points > _EPS

    notes: list[str] = []

    if price_change_pct is None or abs(price_change_pct) < 0.01:
        notes.append("Price is unchanged from the baseline.")
    else:
        direction = "increased" if price_change_pct > 0 else "decreased"
        notes.append(f"Price {direction} by {abs(price_change_pct):.1f}% vs baseline.")

    if demand_change_pct is not None and abs(demand_change_pct) >= 0.01:
        d_direction = "decreased" if demand_change_pct < 0 else "increased"
        notes.append(
            f"Demand {d_direction} by {abs(demand_change_pct):.1f}% per the elasticity model."
        )

    notes.append("Revenue improved." if revenue_improved else _revenue_note(revenue_delta))
    notes.append("Net profit improved." if profit_improved else _profit_note(net_profit_delta))
    notes.append("Gross margin improved." if margin_improved else _margin_note(margin_points))

    if price_change_pct is not None:
        if price_change_pct > _EPS and not profit_improved:
            notes.append("Demand loss outweighed the price increase.")
        elif price_change_pct < -_EPS and not profit_improved:
            notes.append("Added volume did not offset the lower price.")
        elif price_change_pct > _EPS and profit_improved:
            notes.append("The higher price more than offset the demand loss.")

    if is_recommended:
        notes.append("This is the optimizer-recommended price.")

    return ScenarioDiagnostics(
        price_change_pct=None if price_change_pct is None else round(price_change_pct, 2),
        demand_change_pct=None if demand_change_pct is None else round(demand_change_pct, 2),
        revenue_improved=revenue_improved,
        profit_improved=profit_improved,
        margin_improved=margin_improved,
        is_recommended=is_recommended,
        notes=tuple(notes),
    )


def _revenue_note(delta: float) -> str:
    return "Revenue unchanged." if abs(delta) <= _EPS else "Revenue declined."


def _profit_note(delta: float) -> str:
    return "Net profit unchanged." if abs(delta) <= _EPS else "Net profit declined."


def _margin_note(points: float) -> str:
    return "Gross margin unchanged." if abs(points) <= _EPS else "Gross margin declined."
