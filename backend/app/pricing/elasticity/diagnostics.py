"""Classification and diagnostic helpers for elasticity results (explainability)."""

from __future__ import annotations

from app.pricing.elasticity.models import ElasticityClass, ElasticityMethod

_UNIT_EPSILON = 1e-9
_HIGHLY_ELASTIC_THRESHOLD = 2.0
_PERFECTLY_ELASTIC_THRESHOLD = 1e6  # finite proxy for |E| → ∞ (theoretical)


def classify(elasticity: float) -> ElasticityClass:
    """Classify demand by the magnitude of the elasticity coefficient.

    Thresholds (on |E|): 0 → perfectly inelastic; (0, 1) → inelastic; ≈1 → unit elastic;
    (1, 2] → elastic; (2, ∞) → highly elastic; effectively infinite → perfectly elastic.
    """
    magnitude = abs(elasticity)
    if magnitude >= _PERFECTLY_ELASTIC_THRESHOLD:
        return ElasticityClass.PERFECTLY_ELASTIC
    if magnitude == 0:
        return ElasticityClass.PERFECTLY_INELASTIC
    if abs(magnitude - 1.0) <= _UNIT_EPSILON:
        return ElasticityClass.UNIT_ELASTIC
    if magnitude < 1.0:
        return ElasticityClass.INELASTIC
    if magnitude <= _HIGHLY_ELASTIC_THRESHOLD:
        return ElasticityClass.ELASTIC
    return ElasticityClass.HIGHLY_ELASTIC


def build_assumptions(method: ElasticityMethod) -> tuple[str, ...]:
    common = (
        "Observations are independent and drawn from comparable conditions.",
        "Prices and quantities are strictly positive.",
    )
    if method is ElasticityMethod.LOG_LOG:
        return (
            "Demand follows a constant-elasticity (log-log) form: ln(Q) = a + b·ln(P).",
            *common,
        )
    return (
        "Only two price points available; elasticity estimated by the midpoint arc formula.",
        *common,
    )


def build_notes(
    *,
    method: ElasticityMethod,
    r_squared: float | None,
    sample_size: int,
    distinct_prices: int,
) -> tuple[str, ...]:
    notes: list[str] = []
    if sample_size < 5:
        notes.append(f"Small sample (n={sample_size}); estimates are low-confidence.")
    if distinct_prices < 3:
        notes.append(f"Only {distinct_prices} distinct price level(s); limited price variation.")
    if method is ElasticityMethod.LOG_LOG and r_squared is not None:
        quality = "strong" if r_squared >= 0.7 else "weak" if r_squared < 0.3 else "moderate"
        notes.append(f"Model fit is {quality} (R²={r_squared:.3f}).")
    if method is ElasticityMethod.ARC:
        notes.append("Arc elasticity is a two-point approximation, not a fitted model.")
    return tuple(notes)
