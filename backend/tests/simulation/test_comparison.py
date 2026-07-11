"""Tests for comparison generation: deltas, ranking, and per-scenario correctness."""

from __future__ import annotations

import pytest

from app.pricing.simulation import (
    Objective,
    ScenarioSpec,
    ScenarioType,
    SimulationInput,
    default_scenarios,
    simulate,
)


def _input(**overrides: object) -> SimulationInput:
    base: dict[str, object] = {
        "current_price": 5.0,
        "baseline_demand": 100.0,
        "elasticity": -2.0,
        "unit_cost": 2.0,
        "fixed_cost": 50.0,
        "objective": Objective.MAXIMIZE_GROSS_PROFIT,
        "recommended_price": 4.0,
        "scenarios": default_scenarios(recommended_available=True),
    }
    base.update(overrides)
    return SimulationInput(**base)  # type: ignore[arg-type]


def _by_label(result, label):  # type: ignore[no-untyped-def]
    return next(s for s in result.scenarios if s.label == label)


@pytest.mark.unit
def test_contribution_margin_equals_gross_profit() -> None:
    for s in simulate(_input()).scenarios:
        assert s.contribution_margin == s.gross_profit


@pytest.mark.unit
def test_objective_value_matches_gross_profit_for_that_objective() -> None:
    for s in simulate(_input(objective=Objective.MAXIMIZE_GROSS_PROFIT)).scenarios:
        assert s.objective_value == pytest.approx(s.gross_profit)


@pytest.mark.unit
def test_objective_value_matches_revenue_for_revenue_objective() -> None:
    for s in simulate(_input(objective=Objective.MAXIMIZE_REVENUE)).scenarios:
        assert s.objective_value == pytest.approx(s.revenue)


@pytest.mark.unit
def test_vs_baseline_revenue_delta_matches() -> None:
    result = simulate(_input())
    baseline = _by_label(result, "Baseline")
    plus10 = _by_label(result, "+10%")
    assert plus10.vs_baseline.revenue_abs == pytest.approx(
        plus10.revenue - baseline.revenue, abs=0.01
    )
    assert plus10.vs_baseline.revenue_pct == pytest.approx(
        (plus10.revenue - baseline.revenue) / baseline.revenue * 100, abs=0.05
    )


@pytest.mark.unit
def test_vs_recommended_delta_zero_for_recommended() -> None:
    rec = _by_label(simulate(_input()), "Recommended")
    assert rec.vs_recommended is not None
    assert rec.vs_recommended.revenue_abs == pytest.approx(0.0, abs=0.01)
    assert rec.vs_recommended.net_profit_abs == pytest.approx(0.0, abs=0.01)


@pytest.mark.unit
def test_margin_points_increase_with_price() -> None:
    result = simulate(_input())
    plus20 = _by_label(result, "+20%")
    minus20 = _by_label(result, "-20%")
    assert plus20.vs_baseline.margin_points > 0  # higher price -> higher margin
    assert minus20.vs_baseline.margin_points < 0


@pytest.mark.unit
def test_ranks_are_a_permutation() -> None:
    result = simulate(_input())
    ranks = sorted(s.rank for s in result.scenarios)
    assert ranks == list(range(1, len(result.scenarios) + 1))


@pytest.mark.unit
def test_rank_one_is_best_objective_value() -> None:
    result = simulate(_input())
    best = min(result.scenarios, key=lambda s: s.rank)
    assert best.objective_value == max(s.objective_value for s in result.scenarios)


@pytest.mark.unit
def test_ranking_by_revenue_is_descending() -> None:
    result = simulate(_input())
    by_label = {s.label: s for s in result.scenarios}
    revenues = [by_label[label].revenue for label in result.ranking_by_revenue]
    assert revenues == sorted(revenues, reverse=True)


@pytest.mark.unit
def test_ranking_by_net_profit_is_descending() -> None:
    result = simulate(_input())
    by_label = {s.label: s for s in result.scenarios}
    profits = [by_label[label].net_profit for label in result.ranking_by_net_profit]
    assert profits == sorted(profits, reverse=True)


@pytest.mark.unit
def test_all_scenario_types_evaluate() -> None:
    scenarios = (
        ScenarioSpec(ScenarioType.BASELINE, label="Baseline"),
        ScenarioSpec(ScenarioType.RECOMMENDED, label="Recommended"),
        ScenarioSpec(ScenarioType.FIXED_PRICE, label="Fixed", price=7.0),
        ScenarioSpec(ScenarioType.PERCENTAGE_INCREASE, label="+15%", percentage=0.15),
        ScenarioSpec(ScenarioType.PERCENTAGE_DECREASE, label="-15%", percentage=0.15),
    )
    result = simulate(_input(scenarios=scenarios))
    types = {s.scenario_type for s in result.scenarios}
    assert types == set(ScenarioType)


@pytest.mark.unit
def test_fixed_price_below_cost_allowed_but_flags_negative_margin() -> None:
    scenarios = (
        ScenarioSpec(ScenarioType.BASELINE, label="Baseline"),
        ScenarioSpec(ScenarioType.FIXED_PRICE, label="$1", price=1.0),
    )
    result = simulate(_input(scenarios=scenarios))
    cheap = _by_label(result, "$1")
    assert cheap.margin_pct < 0  # price below unit cost


@pytest.mark.unit
def test_decrease_scenario_notes_mention_increase_in_demand() -> None:
    minus20 = _by_label(simulate(_input()), "-20%")
    assert any("Demand increased" in n for n in minus20.diagnostics.notes)


@pytest.mark.unit
def test_zero_baseline_demand_gives_none_pct() -> None:
    result = simulate(_input(baseline_demand=0.0))
    plus10 = _by_label(result, "+10%")
    # demand stays 0 (constant elasticity scales 0), so pct change vs baseline is undefined
    assert plus10.vs_baseline.revenue_pct is None
