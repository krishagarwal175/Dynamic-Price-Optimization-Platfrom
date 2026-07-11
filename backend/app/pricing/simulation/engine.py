"""Deterministic scenario-simulation engine (pure business logic).

Answers "what-if this pricing decision were made?" by evaluating each scenario with the
platform's existing deterministic models — it **composes**, never re-derives:

* **Demand propagation** uses the constant-elasticity ``DemandModel`` from the optimization
  engine: ``Q(P) = Q₀·(P/P₀)^E`` anchored at the current price.
* **Financial metrics** reuse the optimization objective functions:
  ``revenue = P·Q``, ``gross_profit = (P−c)·Q`` (= contribution margin in v1),
  ``net_profit = gross_profit − F``, ``margin = (P−c)/P``.

For each scenario it computes those metrics, their deltas vs the **baseline** (current
price) and vs the **optimizer recommendation**, ranks scenarios by the chosen objective
(and by revenue and net profit), and attaches structured diagnostics. No optimization, no
forecasting, no probabilistic simulation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.pricing.optimization.models import DemandModel, PricingContext
from app.pricing.optimization.objective_functions import (
    OBJECTIVES,
    gross_profit,
    net_profit,
    revenue,
)
from app.pricing.simulation.diagnostics import build_diagnostics
from app.pricing.simulation.errors import SimulationExecutionError
from app.pricing.simulation.models import (
    DeltaSet,
    ScenarioResult,
    ScenarioType,
    SimulationInput,
    SimulationResult,
)
from app.pricing.simulation.scenarios import resolve_price
from app.pricing.simulation.validation import validate_input

_PRICE_DP = 2
_QTY_DP = 4
_MONEY_DP = 2
_PCT_DP = 2
_RATIO_DP = 4
_REC_TOL = 1e-6


@dataclass(frozen=True)
class _Metrics:
    price: float
    demand: float
    revenue: float
    gross_profit: float
    net_profit: float
    margin: float
    objective_value: float


def simulate(inp: SimulationInput) -> SimulationResult:
    """Evaluate every scenario deterministically. Raises structured domain errors."""
    validate_input(inp)

    ctx = PricingContext(
        demand_model=DemandModel(
            reference_price=inp.current_price,
            reference_demand=inp.baseline_demand,
            elasticity=inp.elasticity,
        ),
        variable_cost=inp.unit_cost,
        fixed_cost=inp.fixed_cost,
    )
    objective_fn = OBJECTIVES[inp.objective]

    def metrics_at(price: float) -> _Metrics:
        try:
            demand = ctx.demand(price)
            margin = (price - inp.unit_cost) / price if price > 0 else 0.0
            return _Metrics(
                price=price,
                demand=demand,
                revenue=revenue(price, ctx),
                gross_profit=gross_profit(price, ctx),
                net_profit=net_profit(price, ctx),
                margin=margin,
                objective_value=objective_fn(price, ctx),
            )
        except (ArithmeticError, ValueError) as exc:  # pragma: no cover - guarded upstream
            raise SimulationExecutionError(f"Failed to evaluate price {price}: {exc}") from exc

    baseline = metrics_at(inp.current_price)
    recommended = metrics_at(inp.recommended_price) if inp.recommended_price is not None else None

    evaluated: list[tuple[str, ScenarioType, _Metrics]] = []
    baseline_label = ""
    for spec in inp.scenarios:
        price = resolve_price(spec, inp)
        evaluated.append((spec.label, spec.type, metrics_at(price)))
        if spec.type is ScenarioType.BASELINE:
            baseline_label = spec.label

    objective_order = _ranked_labels(evaluated, key=lambda m: m.objective_value)
    revenue_order = _ranked_labels(evaluated, key=lambda m: m.revenue)
    profit_order = _ranked_labels(evaluated, key=lambda m: m.net_profit)
    rank_by_label = {label: i + 1 for i, label in enumerate(objective_order)}

    results = tuple(
        _build_result(
            label=label,
            scenario_type=scenario_type,
            metrics=metrics,
            baseline=baseline,
            recommended=recommended,
            rank=rank_by_label[label],
            is_recommended=_is_recommended(metrics.price, inp.recommended_price),
        )
        for label, scenario_type, metrics in evaluated
    )

    best = objective_order[0]
    notes = _overall_notes(best, baseline_label, evaluated, recommended is not None)

    return SimulationResult(
        objective=inp.objective,
        baseline_label=baseline_label or inp.scenarios[0].label,
        scenarios=results,
        ranking_by_objective=objective_order,
        ranking_by_revenue=revenue_order,
        ranking_by_net_profit=profit_order,
        best_scenario=best,
        notes=notes,
    )


def _ranked_labels(
    evaluated: list[tuple[str, ScenarioType, _Metrics]],
    *,
    key: Callable[[_Metrics], float],
) -> tuple[str, ...]:
    order = sorted(evaluated, key=lambda item: key(item[2]), reverse=True)
    return tuple(label for label, _type, _metrics in order)


def _is_recommended(price: float, recommended_price: float | None) -> bool:
    return recommended_price is not None and abs(price - recommended_price) <= _REC_TOL


def _pct(new: float, base: float) -> float | None:
    return None if base == 0 else (new - base) / base * 100.0


def _delta(metrics: _Metrics, reference: _Metrics) -> DeltaSet:
    return DeltaSet(
        demand_abs=round(metrics.demand - reference.demand, _QTY_DP),
        demand_pct=_round_opt(_pct(metrics.demand, reference.demand), _PCT_DP),
        revenue_abs=round(metrics.revenue - reference.revenue, _MONEY_DP),
        revenue_pct=_round_opt(_pct(metrics.revenue, reference.revenue), _PCT_DP),
        gross_profit_abs=round(metrics.gross_profit - reference.gross_profit, _MONEY_DP),
        gross_profit_pct=_round_opt(_pct(metrics.gross_profit, reference.gross_profit), _PCT_DP),
        net_profit_abs=round(metrics.net_profit - reference.net_profit, _MONEY_DP),
        net_profit_pct=_round_opt(_pct(metrics.net_profit, reference.net_profit), _PCT_DP),
        margin_points=round((metrics.margin - reference.margin) * 100.0, _PCT_DP),
    )


def _build_result(
    *,
    label: str,
    scenario_type: ScenarioType,
    metrics: _Metrics,
    baseline: _Metrics,
    recommended: _Metrics | None,
    rank: int,
    is_recommended: bool,
) -> ScenarioResult:
    vs_baseline = _delta(metrics, baseline)
    vs_recommended = _delta(metrics, recommended) if recommended is not None else None
    diagnostics = build_diagnostics(
        scenario_type=scenario_type,
        price_change_pct=_pct(metrics.price, baseline.price),
        demand_change_pct=_pct(metrics.demand, baseline.demand),
        revenue_delta=metrics.revenue - baseline.revenue,
        net_profit_delta=metrics.net_profit - baseline.net_profit,
        margin_points=(metrics.margin - baseline.margin) * 100.0,
        is_recommended=is_recommended,
    )
    return ScenarioResult(
        label=label,
        scenario_type=scenario_type,
        price=round(metrics.price, _PRICE_DP),
        demand=round(metrics.demand, _QTY_DP),
        revenue=round(metrics.revenue, _MONEY_DP),
        gross_profit=round(metrics.gross_profit, _MONEY_DP),
        contribution_margin=round(metrics.gross_profit, _MONEY_DP),
        net_profit=round(metrics.net_profit, _MONEY_DP),
        margin_pct=round(metrics.margin, _RATIO_DP),
        objective_value=round(metrics.objective_value, _MONEY_DP),
        vs_baseline=vs_baseline,
        vs_recommended=vs_recommended,
        rank=rank,
        diagnostics=diagnostics,
    )


def _overall_notes(
    best: str,
    baseline_label: str,
    evaluated: list[tuple[str, ScenarioType, _Metrics]],
    has_recommended: bool,
) -> tuple[str, ...]:
    notes: list[str] = [f"'{best}' maximizes the chosen objective among evaluated scenarios."]
    recommended_label = next(
        (label for label, stype, _m in evaluated if stype is ScenarioType.RECOMMENDED), None
    )
    if has_recommended and recommended_label is not None:
        if best == recommended_label:
            notes.append("The optimizer recommendation remains optimal among these scenarios.")
        else:
            notes.append(
                f"'{best}' scores higher than the optimizer recommendation on this objective "
                "(the optimizer may be constrained differently)."
            )
    if best == baseline_label:
        notes.append("The current price is already the best of the evaluated options.")
    return tuple(notes)


def _round_opt(value: float | None, digits: int) -> float | None:
    return None if value is None else round(value, digits)
