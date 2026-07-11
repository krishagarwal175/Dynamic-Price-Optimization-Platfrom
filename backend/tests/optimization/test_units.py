"""Unit tests for optimization building blocks: models, objectives, constraints, search."""

from __future__ import annotations

import pytest

from app.pricing.optimization.constraints import (
    MinMarginConstraint,
    MinPriceConstraint,
    build_constraints,
)
from app.pricing.optimization.errors import InfeasibleConstraintsError
from app.pricing.optimization.models import (
    DemandModel,
    Objective,
    OptimizationConstraints,
    PricingContext,
)
from app.pricing.optimization.objective_functions import OBJECTIVES, revenue
from app.pricing.optimization.search import maximize


def _ctx(elasticity: float = -2.0) -> PricingContext:
    model = DemandModel(reference_price=5.0, reference_demand=100.0, elasticity=elasticity)
    return PricingContext(demand_model=model, variable_cost=2.0, fixed_cost=0.0)


@pytest.mark.unit
def test_demand_model_constant_elasticity() -> None:
    model = DemandModel(reference_price=5.0, reference_demand=100.0, elasticity=-2.0)
    assert model.demand(5.0) == pytest.approx(100.0)
    assert model.demand(10.0) == pytest.approx(25.0)  # doubling price quarters demand


@pytest.mark.unit
def test_objective_functions() -> None:
    ctx = _ctx()
    assert revenue(5.0, ctx) == pytest.approx(500.0)  # 5 * 100
    assert OBJECTIVES[Objective.MAXIMIZE_GROSS_PROFIT](5.0, ctx) == pytest.approx(300.0)  # 3*100
    assert set(OBJECTIVES) == set(Objective)


@pytest.mark.unit
def test_constraint_bounds_and_feasibility() -> None:
    ctx = _ctx()
    assert MinPriceConstraint(4.0).bounds() == (4.0, None)
    margin = MinMarginConstraint(0.5)
    assert margin.feasible(4.0, ctx) is True  # (4-2)/4 = 0.5
    assert margin.feasible(3.0, ctx) is False  # (3-2)/3 = 0.33


@pytest.mark.unit
def test_build_constraints_from_spec() -> None:
    spec = OptimizationConstraints(min_price=1.0, max_price=9.0, min_margin_pct=0.3)
    constraints = build_constraints(spec, current_price=5.0)
    assert len(constraints) == 3


@pytest.mark.unit
def test_search_finds_maximum() -> None:
    # maximize -(x-3)^2 over [0,10] -> x=3
    result = maximize(lambda x: -((x - 3) ** 2), lambda _x: True, 0.0, 10.0)
    assert result.best_price == pytest.approx(3.0, abs=1e-3)
    assert result.iterations > 0


@pytest.mark.unit
def test_search_raises_when_nothing_feasible() -> None:
    with pytest.raises(InfeasibleConstraintsError):
        maximize(lambda x: x, lambda _x: False, 0.0, 10.0)
