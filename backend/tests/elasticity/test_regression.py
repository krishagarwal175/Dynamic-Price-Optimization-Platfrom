"""Unit tests for the OLS regression and math primitives."""

from __future__ import annotations

import math

import pytest

from app.pricing.elasticity.errors import SingularRegressionError
from app.pricing.elasticity.mathematics import arc_elasticity, linspace, mean
from app.pricing.elasticity.regression import fit_ols


@pytest.mark.unit
def test_fit_exact_line() -> None:
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [3.0, 5.0, 7.0, 9.0]  # y = 2x + 1
    fit = fit_ols(xs, ys)
    assert fit.slope == pytest.approx(2.0)
    assert fit.intercept == pytest.approx(1.0)
    assert fit.r_squared == pytest.approx(1.0)
    assert fit.residual_std == pytest.approx(0.0)


@pytest.mark.unit
def test_singular_predictor_raises() -> None:
    with pytest.raises(SingularRegressionError):
        fit_ols([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])


@pytest.mark.unit
def test_r_squared_none_when_response_constant() -> None:
    fit = fit_ols([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])
    assert fit.r_squared is None


@pytest.mark.unit
def test_arc_elasticity_matches_hand_calc() -> None:
    # ((80-100)/90) / ((12-10)/11) = -0.2222 / 0.1818 = -1.2222
    assert arc_elasticity(10, 100, 12, 80) == pytest.approx(-1.222222, rel=1e-5)


@pytest.mark.unit
def test_linspace_inclusive() -> None:
    grid = linspace(1.0, 5.0, 5)
    assert grid == [1.0, 2.0, 3.0, 4.0, 5.0]


@pytest.mark.unit
def test_mean() -> None:
    assert mean([2.0, 4.0, 6.0]) == pytest.approx(4.0)
    assert math.isclose(mean([1.0]), 1.0)
