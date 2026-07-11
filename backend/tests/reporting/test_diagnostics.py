"""Unit tests for the interpretation (diagnostics) helpers."""

from __future__ import annotations

import pytest

from app.pricing.reporting import diagnostics as dx


@pytest.mark.unit
def test_overall_recommendation_hold() -> None:
    assert "Maintain" in dx.overall_recommendation(5.0, 5.0, "USD")


@pytest.mark.unit
def test_overall_recommendation_increase() -> None:
    msg = dx.overall_recommendation(5.0, 6.0, "USD")
    assert "Increase" in msg
    assert "USD 6.00" in msg


@pytest.mark.unit
def test_overall_recommendation_reduce() -> None:
    assert "Reduce" in dx.overall_recommendation(5.0, 4.0, "USD")


@pytest.mark.unit
def test_key_conclusion_improvement() -> None:
    msg = dx.key_conclusion("maximize_gross_profit", 12.5, "elastic")
    assert "improve gross profit" in msg


@pytest.mark.unit
def test_key_conclusion_no_improvement() -> None:
    msg = dx.key_conclusion("maximize_revenue", 0.0, "inelastic")
    assert "already near-optimal" in msg


@pytest.mark.unit
@pytest.mark.parametrize(
    ("classification", "needle"),
    [
        ("inelastic", "inelastic"),
        ("elastic", "elastic"),
        ("unit_elastic", "unit elastic"),
        ("perfectly_inelastic", "does not respond"),
        ("perfectly_elastic", "perfectly elastic"),
    ],
)
def test_elasticity_interpretation(classification: str, needle: str) -> None:
    text = dx.elasticity_interpretation(classification, -1.5)
    assert needle in text


@pytest.mark.unit
def test_elasticity_implications_inelastic_vs_elastic() -> None:
    inelastic = dx.elasticity_implications("inelastic")
    elastic = dx.elasticity_implications("elastic")
    assert any("raise price" in i for i in inelastic)
    assert any("volume loss" in i for i in elastic)


@pytest.mark.unit
def test_forecast_interpretation() -> None:
    assert "projects demand" in dx.forecast_interpretation("naive", (10.0, 10.0))
    assert "No forecast" in dx.forecast_interpretation("naive", ())


@pytest.mark.unit
def test_financial_notes() -> None:
    notes = dx.financial_notes(100.0, 0.6)
    assert any("positive" in n for n in notes)
    assert any("60.0%" in n for n in notes)
    assert any("non-positive" in n for n in dx.financial_notes(-1.0, None))


@pytest.mark.unit
def test_pricing_action() -> None:
    assert dx.pricing_action(5.0, 5.0, "USD") == "Hold price steady."
    assert "Raise" in dx.pricing_action(5.0, 6.0, "USD")
    assert "Lower" in dx.pricing_action(5.0, 4.0, "USD")


@pytest.mark.unit
def test_recommendations_include_constraint_note() -> None:
    recs = dx.recommendations(
        improvement=10.0, classification="elastic", binding_constraints=("min_price>=4.5",)
    )
    assert any("Adopt the recommended price" in r for r in recs)
    assert any("binding constraints" in r for r in recs)


@pytest.mark.unit
def test_risks_flag_weak_fit() -> None:
    risks = dx.risks("elastic", 0.2)
    assert any("weak" in r for r in risks)
    assert any("Competitor" in r for r in risks)


@pytest.mark.unit
def test_monitoring_and_implementation() -> None:
    assert len(dx.monitoring()) >= 2
    product_notes = dx.implementation_notes("product")
    dataset_notes = dx.implementation_notes("dataset")
    assert any("advisory" in n for n in product_notes)
    assert any("aggregate" in n for n in dataset_notes)
