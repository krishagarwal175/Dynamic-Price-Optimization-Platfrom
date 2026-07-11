"""Build a full ``ReportInput`` from real engine outputs (deterministic)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from app.pricing.elasticity import Observation as EObs
from app.pricing.elasticity import analyze_elasticity
from app.pricing.finance import SaleLine, compute_financials
from app.pricing.forecasting import Observation as FObs
from app.pricing.forecasting import forecast_demand
from app.pricing.optimization import Objective, OptimizationInput, optimize
from app.pricing.reporting import ReportInput
from app.pricing.simulation import SimulationInput, default_scenarios, simulate

# Two price levels giving elasticity ~ -2 across six dated periods.
_PAIRS = [(4, 100), (6, 44), (4, 100), (6, 44), (4, 100), (6, 44)]


def make_report_input(**overrides: Any) -> ReportInput:
    objective = overrides.get("objective", Objective.MAXIMIZE_GROSS_PROFIT)
    financial = compute_financials([SaleLine(q, Decimal(str(p)), Decimal("2")) for p, q in _PAIRS])
    elasticity = analyze_elasticity(
        [EObs(price=float(p), quantity=float(q)) for p, q in _PAIRS], unit_cost=2.0
    )
    forecast = forecast_demand(
        [
            FObs(period=date(2026, 1, 1) + timedelta(days=i), demand=float(q))
            for i, (_p, q) in enumerate(_PAIRS)
        ],
        horizon=3,
    )
    baseline_demand = forecast.forecast[0].predicted
    optimization = optimize(
        OptimizationInput(
            current_price=5.0,
            variable_cost=2.0,
            reference_demand=baseline_demand,
            elasticity=elasticity.elasticity_coefficient,
            objective=objective,
        )
    )
    simulation = simulate(
        SimulationInput(
            current_price=5.0,
            baseline_demand=baseline_demand,
            elasticity=elasticity.elasticity_coefficient,
            unit_cost=2.0,
            fixed_cost=0.0,
            objective=objective,
            recommended_price=optimization.recommended_price,
            scenarios=default_scenarios(recommended_available=True),
        )
    )
    base: dict[str, Any] = {
        "scope": "product",
        "subject": "SKU-1 — Cola",
        "currency": "USD",
        "objective": objective,
        "financial": financial,
        "elasticity": elasticity,
        "forecast": forecast,
        "optimization": optimization,
        "simulation": simulation,
    }
    base.update(overrides)
    return ReportInput(**base)
