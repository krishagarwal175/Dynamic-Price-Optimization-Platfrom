"""Unit tests for the pricing-optimization engine — correctness & explanations."""

from __future__ import annotations

import pytest

from app.pricing.optimization import (
    Objective,
    OptimizationConstraints,
    OptimizationInput,
    optimize,
)
from app.pricing.optimization.errors import InfeasibleConstraintsError, InvalidInputError


def _input(**overrides: object) -> OptimizationInput:
    base: dict[str, object] = {
        "current_price": 5.0,
        "variable_cost": 2.0,
        "reference_demand": 100.0,
        "elasticity": -2.0,
        "objective": Objective.MAXIMIZE_GROSS_PROFIT,
    }
    base.update(overrides)
    return OptimizationInput(**base)  # type: ignore[arg-type]


@pytest.mark.unit
def test_profit_optimum_matches_closed_form() -> None:
    # P* = c·E/(E+1) = 2·(-2)/(-1) = 4 for elastic demand
    result = optimize(_input())
    assert result.recommended_price == pytest.approx(4.0, abs=0.01)
    # gross profit at P=4: Q=100·(4/5)^-2=156.25 ; (4-2)·156.25 = 312.5
    assert result.objective_value == pytest.approx(312.5, abs=0.5)
    assert result.improvement > 0


@pytest.mark.unit
def test_net_profit_shifts_value_by_fixed_cost() -> None:
    gross = optimize(_input(objective=Objective.MAXIMIZE_GROSS_PROFIT))
    net = optimize(_input(objective=Objective.MAXIMIZE_NET_PROFIT, fixed_cost=50.0))
    # same argmax, objective value lower by the fixed cost
    assert net.recommended_price == pytest.approx(gross.recommended_price, abs=0.05)
    assert net.objective_value == pytest.approx(gross.objective_value - 50.0, abs=0.5)


@pytest.mark.unit
def test_revenue_objective_is_monotonic_to_lower_bound() -> None:
    # constant elasticity -2 -> revenue = k/P, decreasing -> optimum at the lower bound
    result = optimize(_input(objective=Objective.MAXIMIZE_REVENUE))
    assert result.recommended_price == pytest.approx(2.5, abs=0.01)  # 50% of 5
    assert "lower bound" in " ".join(result.notes)


@pytest.mark.unit
def test_min_price_constraint_binds() -> None:
    result = optimize(_input(constraints=OptimizationConstraints(min_price=4.5)))
    assert result.recommended_price == pytest.approx(4.5, abs=0.01)
    assert any("min_price" in c for c in result.active_constraints)


@pytest.mark.unit
def test_max_increase_constraint_caps_price() -> None:
    # profit optimum would be below current (4 < 5); use inelastic demand so optimum is high
    result = optimize(
        _input(elasticity=-1.2, constraints=OptimizationConstraints(max_increase_pct=0.1))
    )
    assert result.recommended_price <= 5.0 * 1.1 + 1e-6


@pytest.mark.unit
def test_infeasible_margin_raises() -> None:
    # (P-2)/P >= 0.9 -> P >= 20, but search upper is 10 -> infeasible
    with pytest.raises(InfeasibleConstraintsError):
        optimize(_input(constraints=OptimizationConstraints(min_margin_pct=0.9)))


@pytest.mark.unit
def test_impossible_price_constraints_raise() -> None:
    with pytest.raises(InvalidInputError):
        optimize(_input(constraints=OptimizationConstraints(min_price=8, max_price=4)))


@pytest.mark.unit
@pytest.mark.parametrize(
    "overrides",
    [
        {"current_price": 0.0},
        {"variable_cost": -1.0},
        {"fixed_cost": -1.0},
        {"reference_demand": 0.0},
    ],
)
def test_invalid_inputs_raise(overrides: dict[str, object]) -> None:
    with pytest.raises(InvalidInputError):
        optimize(_input(**overrides))


@pytest.mark.unit
def test_deterministic() -> None:
    assert optimize(_input()) == optimize(_input())


@pytest.mark.unit
def test_explanation_fields_present() -> None:
    result = optimize(_input())
    assert result.expected_demand > 0
    assert result.expected_revenue > 0
    assert result.search_lower < result.search_upper
    assert result.iterations > 0
    assert len(result.assumptions) >= 1
    assert len(result.notes) >= 1
    assert result.baseline_price == pytest.approx(5.0)


@pytest.mark.unit
def test_min_margin_feasible_is_respected() -> None:
    # margin at recommendation must be >= 0.5  ((P-2)/P >= 0.5 -> P >= 4)
    result = optimize(_input(constraints=OptimizationConstraints(min_margin_pct=0.5)))
    margin = (result.recommended_price - 2.0) / result.recommended_price
    assert margin >= 0.5 - 1e-6
