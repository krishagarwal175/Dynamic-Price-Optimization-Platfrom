"""Unit tests for the elasticity engine — correctness against known models."""

from __future__ import annotations

import pytest

from app.pricing.elasticity import Observation, analyze_elasticity
from app.pricing.elasticity.diagnostics import classify
from app.pricing.elasticity.errors import (
    DegenerateDataError,
    InsufficientObservationsError,
    InvalidObservationError,
)
from app.pricing.elasticity.models import ElasticityClass, ElasticityMethod


def _constant_elasticity(coef: float, elasticity: float, prices: list[float]) -> list[Observation]:
    """Points on Q = coef · P^elasticity (a perfect log-log line)."""
    return [Observation(price=p, quantity=coef * (p**elasticity)) for p in prices]


@pytest.mark.unit
def test_recovers_known_constant_elasticity() -> None:
    obs = _constant_elasticity(100.0, -2.0, [1, 2, 4, 5, 8])
    result = analyze_elasticity(obs)
    assert result.method is ElasticityMethod.LOG_LOG
    assert result.elasticity_coefficient == pytest.approx(-2.0, abs=1e-6)
    assert result.diagnostics.r_squared == pytest.approx(1.0)
    assert result.classification is ElasticityClass.ELASTIC  # |−2| = 2


@pytest.mark.unit
def test_unit_elastic() -> None:
    obs = _constant_elasticity(100.0, -1.0, [1, 2, 4, 5])
    result = analyze_elasticity(obs)
    assert result.elasticity_coefficient == pytest.approx(-1.0, abs=1e-6)
    assert result.classification is ElasticityClass.UNIT_ELASTIC


@pytest.mark.unit
def test_inelastic() -> None:
    obs = _constant_elasticity(100.0, -0.5, [1, 4, 9, 16])
    result = analyze_elasticity(obs)
    assert result.elasticity_coefficient == pytest.approx(-0.5, abs=1e-6)
    assert result.classification is ElasticityClass.INELASTIC


@pytest.mark.unit
def test_highly_elastic() -> None:
    obs = _constant_elasticity(100.0, -3.0, [1, 2, 3, 4])
    result = analyze_elasticity(obs)
    assert result.classification is ElasticityClass.HIGHLY_ELASTIC


@pytest.mark.unit
def test_two_points_use_arc_method() -> None:
    result = analyze_elasticity([Observation(10, 100), Observation(12, 80)])
    assert result.method is ElasticityMethod.ARC
    assert result.elasticity_coefficient == pytest.approx(-1.222222, rel=1e-5)


@pytest.mark.unit
def test_supplementary_measures_present_for_regression() -> None:
    obs = _constant_elasticity(100.0, -2.0, [1, 2, 4, 5])
    result = analyze_elasticity(obs)
    assert result.arc_elasticity is not None
    assert result.point_elasticity is not None


@pytest.mark.unit
def test_curves_generated() -> None:
    obs = _constant_elasticity(100.0, -2.0, [1, 2, 4, 5])
    result = analyze_elasticity(obs, unit_cost=0.5, curve_points=10)
    assert len(result.demand_curve) == 10
    assert len(result.revenue_curve) == 10
    assert result.profit_curve is not None
    # demand is downward-sloping for negative elasticity
    quantities = [pt.value for pt in result.demand_curve]
    assert quantities == sorted(quantities, reverse=True)


@pytest.mark.unit
def test_profit_curve_absent_without_unit_cost() -> None:
    obs = _constant_elasticity(100.0, -2.0, [1, 2, 4, 5])
    assert analyze_elasticity(obs).profit_curve is None


@pytest.mark.unit
def test_diagnostics_fields() -> None:
    obs = _constant_elasticity(100.0, -2.0, [1, 2, 4, 5])
    diag = analyze_elasticity(obs).diagnostics
    assert diag.sample_size == 4
    assert diag.distinct_prices == 4
    assert len(diag.assumptions) >= 1
    assert any("R²" in note for note in diag.notes)


@pytest.mark.unit
def test_insufficient_observations() -> None:
    with pytest.raises(InsufficientObservationsError):
        analyze_elasticity([Observation(1, 10)])


@pytest.mark.unit
def test_identical_prices_is_degenerate() -> None:
    with pytest.raises(DegenerateDataError):
        analyze_elasticity([Observation(5, 10), Observation(5, 20), Observation(5, 15)])


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad",
    [Observation(0, 10), Observation(-1, 10), Observation(5, 0), Observation(5, -3)],
)
def test_invalid_observations(bad: Observation) -> None:
    with pytest.raises(InvalidObservationError):
        analyze_elasticity([bad, Observation(6, 12), Observation(7, 9)])


@pytest.mark.unit
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, ElasticityClass.PERFECTLY_INELASTIC),
        (-0.5, ElasticityClass.INELASTIC),
        (-1.0, ElasticityClass.UNIT_ELASTIC),
        (-1.5, ElasticityClass.ELASTIC),
        (-2.0, ElasticityClass.ELASTIC),
        (-3.0, ElasticityClass.HIGHLY_ELASTIC),
        (-1e7, ElasticityClass.PERFECTLY_ELASTIC),
    ],
)
def test_classification_thresholds(value: float, expected: ElasticityClass) -> None:
    assert classify(value) is expected
