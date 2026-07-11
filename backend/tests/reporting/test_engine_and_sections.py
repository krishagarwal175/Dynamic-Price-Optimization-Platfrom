"""Unit tests for report composition — every section sourced from the engines."""

from __future__ import annotations

import pytest

from app.pricing.reporting import generate_report
from tests.reporting.support import make_report_input


@pytest.mark.unit
def test_report_has_all_sections() -> None:
    report = generate_report(make_report_input())
    assert report.metadata is not None
    assert report.executive_summary is not None
    assert report.financial is not None
    assert report.elasticity is not None
    assert report.forecast is not None
    assert report.optimization is not None
    assert report.scenario is not None
    assert report.recommendations is not None
    assert report.assumptions.assumptions
    assert report.limitations.limitations


@pytest.mark.unit
def test_metadata() -> None:
    report = generate_report(make_report_input())
    assert report.metadata.title == "Pricing Analysis Report"
    assert report.metadata.subject == "SKU-1 — Cola"
    assert report.metadata.scope == "product"
    assert report.metadata.objective == "maximize_gross_profit"


@pytest.mark.unit
def test_executive_summary_sourced_from_optimization() -> None:
    inp = make_report_input()
    ex = generate_report(inp).executive_summary
    assert ex.current_price == inp.optimization.baseline_price
    assert ex.recommended_price == inp.optimization.recommended_price
    assert ex.expected_revenue == inp.optimization.expected_revenue
    assert ex.expected_net_profit == inp.optimization.expected_net_profit
    assert ex.expected_improvement == inp.optimization.improvement
    assert "USD" in ex.overall_recommendation


@pytest.mark.unit
def test_financial_summary_sourced_from_finance() -> None:
    inp = make_report_input()
    fin = generate_report(inp).financial
    assert fin.revenue == float(inp.financial.revenue)
    assert fin.gross_profit == float(inp.financial.gross_profit)
    assert fin.net_profit == float(inp.financial.net_profit)
    assert fin.notes  # interpretive notes present


@pytest.mark.unit
def test_elasticity_summary_sourced_from_elasticity() -> None:
    inp = make_report_input()
    ela = generate_report(inp).elasticity
    assert ela.elasticity_coefficient == inp.elasticity.elasticity_coefficient
    assert ela.classification == inp.elasticity.classification.value
    assert ela.interpretation
    assert ela.business_implications


@pytest.mark.unit
def test_forecast_summary_sourced_from_forecast() -> None:
    inp = make_report_input()
    fc = generate_report(inp).forecast
    assert fc.selected_strategy == inp.forecast.selected_strategy.value
    assert fc.horizon == inp.forecast.horizon
    assert fc.forecast_values == tuple(p.predicted for p in inp.forecast.forecast)
    assert fc.assumptions


@pytest.mark.unit
def test_optimization_summary_sourced_from_optimization() -> None:
    inp = make_report_input()
    opt = generate_report(inp).optimization
    assert opt.optimal_price == inp.optimization.recommended_price
    assert opt.objective_value == inp.optimization.objective_value
    assert opt.improvement == inp.optimization.improvement
    assert opt.iterations == inp.optimization.iterations
    assert opt.search_range == (
        inp.optimization.search_lower,
        inp.optimization.search_upper,
    )


@pytest.mark.unit
def test_scenario_summary_sourced_from_simulation() -> None:
    inp = make_report_input()
    sc = generate_report(inp).scenario
    assert sc.best_scenario == inp.simulation.best_scenario
    assert sc.ranking == inp.simulation.ranking_by_objective
    assert len(sc.rows) == len(inp.simulation.scenarios)
    # rows preserve the simulation's per-scenario values
    first = sc.rows[0]
    src = next(s for s in inp.simulation.scenarios if s.label == first.label)
    assert first.revenue == src.revenue
    assert first.rank == src.rank


@pytest.mark.unit
def test_recommendations_present() -> None:
    rec = generate_report(make_report_input()).recommendations
    assert rec.pricing_action
    assert rec.recommendations
    assert rec.risks
    assert rec.monitoring
    assert rec.implementation_notes


@pytest.mark.unit
def test_assumptions_are_deduplicated() -> None:
    assumptions = generate_report(make_report_input()).assumptions.assumptions
    assert len(assumptions) == len(set(assumptions))


@pytest.mark.unit
def test_dataset_scope_adds_limitation() -> None:
    report = generate_report(make_report_input(scope="dataset", subject="Aggregate dataset"))
    assert any("aggregate" in limit.lower() for limit in report.limitations.limitations)


@pytest.mark.unit
def test_deterministic() -> None:
    assert generate_report(make_report_input()) == generate_report(make_report_input())
