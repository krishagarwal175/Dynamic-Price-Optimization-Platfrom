"""Validation coverage for optimization constraints — each guard branch fires."""

from __future__ import annotations

import pytest

from app.pricing.optimization.errors import InvalidInputError
from app.pricing.optimization.models import (
    Objective,
    OptimizationConstraints,
    OptimizationInput,
)
from app.pricing.optimization.validation import validate


def _input(constraints: OptimizationConstraints) -> OptimizationInput:
    return OptimizationInput(
        current_price=5.0,
        variable_cost=2.0,
        reference_demand=100.0,
        elasticity=-2.0,
        fixed_cost=0.0,
        objective=Objective.MAXIMIZE_REVENUE,
        constraints=constraints,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "constraints",
    [
        OptimizationConstraints(min_price=0.0),
        OptimizationConstraints(min_price=-1.0),
        OptimizationConstraints(max_price=0.0),
        OptimizationConstraints(min_margin_pct=1.0),
        OptimizationConstraints(min_margin_pct=-0.1),
        OptimizationConstraints(min_demand=-1.0),
        OptimizationConstraints(max_increase_pct=-0.1),
        OptimizationConstraints(max_decrease_pct=1.1),
        OptimizationConstraints(max_decrease_pct=-0.1),
    ],
)
def test_invalid_constraints_are_rejected(constraints: OptimizationConstraints) -> None:
    with pytest.raises(InvalidInputError):
        validate(_input(constraints))


@pytest.mark.unit
def test_min_price_exceeding_max_price_is_rejected() -> None:
    with pytest.raises(InvalidInputError):
        validate(_input(OptimizationConstraints(min_price=9.0, max_price=1.0)))


@pytest.mark.unit
def test_valid_constraints_pass() -> None:
    # No exception: a fully-specified, feasible constraint set validates cleanly.
    validate(
        _input(
            OptimizationConstraints(
                min_price=1.0,
                max_price=9.0,
                min_margin_pct=0.2,
                min_demand=0.0,
                max_increase_pct=0.5,
                max_decrease_pct=0.5,
            )
        )
    )
