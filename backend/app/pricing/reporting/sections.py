"""Section builders: assemble each report section from the engine outputs.

Every value is read from an analytics-engine result — nothing is recomputed here.
"""

from __future__ import annotations

from app.pricing.reporting import diagnostics as dx
from app.pricing.reporting.models import (
    AssumptionSection,
    ElasticitySummary,
    ExecutiveSummary,
    FinancialSummary,
    ForecastSummary,
    LimitationSection,
    Metadata,
    OptimizationSummary,
    RecommendationSection,
    ReportInput,
    ScenarioRow,
    ScenarioSummary,
)

_REPORT_TITLE = "Pricing Analysis Report"

_BASE_LIMITATIONS = (
    "Competitor reactions and pricing responses are not modelled.",
    "Inventory, capacity, and supply constraints are ignored.",
    "Demand is modelled with constant elasticity anchored at the current price.",
    "Scenarios are deterministic point estimates (no probability distribution).",
)


def build_metadata(inp: ReportInput) -> Metadata:
    return Metadata(
        title=_REPORT_TITLE,
        scope=inp.scope,
        subject=inp.subject,
        currency=inp.currency,
        objective=inp.objective.value,
        generated_at=inp.generated_at,
    )


def build_executive_summary(inp: ReportInput) -> ExecutiveSummary:
    opt = inp.optimization
    return ExecutiveSummary(
        overall_recommendation=dx.overall_recommendation(
            opt.baseline_price, opt.recommended_price, inp.currency
        ),
        current_price=opt.baseline_price,
        recommended_price=opt.recommended_price,
        expected_demand=opt.expected_demand,
        expected_revenue=opt.expected_revenue,
        expected_net_profit=opt.expected_net_profit,
        expected_improvement=opt.improvement,
        primary_objective=inp.objective.value,
        key_conclusion=dx.key_conclusion(
            inp.objective.value, opt.improvement, inp.elasticity.classification.value
        ),
    )


def build_financial_summary(inp: ReportInput) -> FinancialSummary:
    fin = inp.financial
    return FinancialSummary(
        revenue=float(fin.revenue),
        gross_profit=float(fin.gross_profit),
        contribution_margin=float(fin.contribution_margin),
        net_profit=float(fin.net_profit),
        gross_margin=None if fin.gross_margin is None else float(fin.gross_margin),
        contribution_margin_ratio=(
            None if fin.contribution_margin_ratio is None else float(fin.contribution_margin_ratio)
        ),
        average_selling_price=(
            None if fin.average_selling_price is None else float(fin.average_selling_price)
        ),
        unit_cost=None if fin.unit_cost is None else float(fin.unit_cost),
        notes=dx.financial_notes(
            float(fin.net_profit),
            None if fin.gross_margin is None else float(fin.gross_margin),
        ),
    )


def build_elasticity_summary(inp: ReportInput) -> ElasticitySummary:
    ela = inp.elasticity
    classification = ela.classification.value
    return ElasticitySummary(
        elasticity_coefficient=ela.elasticity_coefficient,
        classification=classification,
        r_squared=ela.diagnostics.r_squared,
        interpretation=dx.elasticity_interpretation(classification, ela.elasticity_coefficient),
        business_implications=dx.elasticity_implications(classification),
    )


def build_forecast_summary(inp: ReportInput) -> ForecastSummary:
    fc = inp.forecast
    values = tuple(point.predicted for point in fc.forecast)
    return ForecastSummary(
        selected_strategy=fc.selected_strategy.value,
        horizon=fc.horizon,
        forecast_values=values,
        assumptions=fc.diagnostics.assumptions,
        confidence_notes=fc.diagnostics.notes,
        interpretation=dx.forecast_interpretation(fc.selected_strategy.value, values),
    )


def build_optimization_summary(inp: ReportInput) -> OptimizationSummary:
    opt = inp.optimization
    return OptimizationSummary(
        objective=opt.objective.value,
        optimal_price=opt.recommended_price,
        objective_value=opt.objective_value,
        improvement=opt.improvement,
        binding_constraints=opt.active_constraints,
        search_range=(opt.search_lower, opt.search_upper),
        iterations=opt.iterations,
        notes=opt.notes,
    )


def build_scenario_summary(inp: ReportInput) -> ScenarioSummary:
    sim = inp.simulation
    rows = tuple(
        ScenarioRow(
            label=s.label,
            price=s.price,
            demand=s.demand,
            revenue=s.revenue,
            net_profit=s.net_profit,
            revenue_change_pct=s.vs_baseline.revenue_pct,
            profit_change_pct=s.vs_baseline.net_profit_pct,
            rank=s.rank,
        )
        for s in sim.scenarios
    )
    worst = sim.ranking_by_objective[-1] if sim.ranking_by_objective else sim.best_scenario
    return ScenarioSummary(
        rows=rows,
        best_scenario=sim.best_scenario,
        worst_scenario=worst,
        ranking=sim.ranking_by_objective,
        observations=sim.notes,
    )


def build_recommendations(inp: ReportInput) -> RecommendationSection:
    opt = inp.optimization
    classification = inp.elasticity.classification.value
    return RecommendationSection(
        pricing_action=dx.pricing_action(opt.baseline_price, opt.recommended_price, inp.currency),
        recommendations=dx.recommendations(
            improvement=opt.improvement,
            classification=classification,
            binding_constraints=opt.active_constraints,
        ),
        risks=dx.risks(classification, inp.elasticity.diagnostics.r_squared),
        monitoring=dx.monitoring(),
        implementation_notes=dx.implementation_notes(inp.scope),
    )


def build_assumptions(inp: ReportInput) -> AssumptionSection:
    collected: list[str] = [
        "Single-product analysis and optimization (no cross-product effects).",
        "Every figure is produced by the platform's deterministic analytics engines.",
    ]
    collected.extend(inp.elasticity.diagnostics.assumptions)
    collected.extend(inp.forecast.diagnostics.assumptions)
    collected.extend(inp.optimization.assumptions)
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for assumption in collected:
        if assumption not in seen:
            seen.add(assumption)
            unique.append(assumption)
    return AssumptionSection(assumptions=tuple(unique))


def build_limitations(inp: ReportInput) -> LimitationSection:
    limitations = list(_BASE_LIMITATIONS)
    if inp.scope == "dataset":
        limitations.append("Dataset figures aggregate all products into a single demand model.")
    return LimitationSection(limitations=tuple(limitations))
