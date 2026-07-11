"""Value objects for the elasticity engine (framework-free)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ElasticityMethod(str, Enum):
    """How the headline elasticity coefficient was estimated."""

    LOG_LOG = "log_log"  # constant-elasticity regression: ln(Q) = a + b·ln(P)
    ARC = "arc"  # midpoint arc elasticity between two price points


class ElasticityClass(str, Enum):
    """Qualitative classification based on |elasticity| (see feature doc for thresholds)."""

    PERFECTLY_INELASTIC = "perfectly_inelastic"  # |E| = 0
    INELASTIC = "inelastic"  # 0 < |E| < 1
    UNIT_ELASTIC = "unit_elastic"  # |E| = 1
    ELASTIC = "elastic"  # 1 < |E| ≤ 2
    HIGHLY_ELASTIC = "highly_elastic"  # 2 < |E| < ∞
    PERFECTLY_ELASTIC = "perfectly_elastic"  # |E| → ∞ (theoretical)


@dataclass(frozen=True)
class Observation:
    """A single (price, quantity) observation fed to the engine."""

    price: float
    quantity: float


@dataclass(frozen=True)
class RegressionDiagnostics:
    """Explainability outputs for the fitted model."""

    slope: float
    intercept: float
    r_squared: float | None
    residual_std: float
    sample_size: int
    distinct_prices: int
    assumptions: tuple[str, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class CurvePoint:
    """A single (price, value) point on a curve — value is quantity, revenue, or profit."""

    price: float
    value: float


@dataclass(frozen=True)
class ElasticityAnalysis:
    """The full deterministic result of an elasticity analysis."""

    method: ElasticityMethod
    elasticity_coefficient: float
    classification: ElasticityClass
    arc_elasticity: float | None
    point_elasticity: float | None
    diagnostics: RegressionDiagnostics
    demand_curve: tuple[CurvePoint, ...]
    revenue_curve: tuple[CurvePoint, ...]
    profit_curve: tuple[CurvePoint, ...] | None
