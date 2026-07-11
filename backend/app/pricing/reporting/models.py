"""Structured report models (framework-free).

Each section has its own immutable model — no giant free-form strings. The ``ReportInput``
bundles the *outputs* of the existing analytics engines; the reporting engine only reads and
re-organizes them (every number originates from an analytics engine).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.pricing.elasticity import ElasticityAnalysis
from app.pricing.finance import FinancialMetrics
from app.pricing.forecasting import ForecastResult
from app.pricing.optimization import OptimizationResult
from app.pricing.optimization.models import Objective
from app.pricing.simulation import SimulationResult

__all__ = [
    "AssumptionSection",
    "ElasticitySummary",
    "ExecutiveSummary",
    "FinancialSummary",
    "ForecastSummary",
    "LimitationSection",
    "Metadata",
    "Objective",
    "OptimizationSummary",
    "PricingReport",
    "RecommendationSection",
    "ReportInput",
    "ScenarioRow",
    "ScenarioSummary",
]


@dataclass(frozen=True)
class ReportInput:
    """Everything the report composes — the outputs of the analytics engines + metadata."""

    scope: str  # "product" | "dataset"
    subject: str  # e.g. "SKU-1 — Cola" or "Aggregate dataset"
    currency: str
    objective: Objective
    financial: FinancialMetrics
    elasticity: ElasticityAnalysis
    forecast: ForecastResult
    optimization: OptimizationResult
    simulation: SimulationResult
    generated_at: str | None = None  # caller-supplied ISO timestamp (optional)


@dataclass(frozen=True)
class Metadata:
    title: str
    scope: str
    subject: str
    currency: str
    objective: str
    generated_at: str | None


@dataclass(frozen=True)
class ExecutiveSummary:
    overall_recommendation: str
    current_price: float
    recommended_price: float
    expected_demand: float
    expected_revenue: float
    expected_net_profit: float
    expected_improvement: float
    primary_objective: str
    key_conclusion: str


@dataclass(frozen=True)
class FinancialSummary:
    revenue: float
    gross_profit: float
    contribution_margin: float
    net_profit: float
    gross_margin: float | None
    contribution_margin_ratio: float | None
    average_selling_price: float | None
    unit_cost: float | None
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ElasticitySummary:
    elasticity_coefficient: float
    classification: str
    r_squared: float | None
    interpretation: str
    business_implications: tuple[str, ...]


@dataclass(frozen=True)
class ForecastSummary:
    selected_strategy: str
    horizon: int
    forecast_values: tuple[float, ...]
    assumptions: tuple[str, ...]
    confidence_notes: tuple[str, ...]
    interpretation: str


@dataclass(frozen=True)
class OptimizationSummary:
    objective: str
    optimal_price: float
    objective_value: float
    improvement: float
    binding_constraints: tuple[str, ...]
    search_range: tuple[float, float]
    iterations: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioRow:
    label: str
    price: float
    demand: float
    revenue: float
    net_profit: float
    revenue_change_pct: float | None
    profit_change_pct: float | None
    rank: int


@dataclass(frozen=True)
class ScenarioSummary:
    rows: tuple[ScenarioRow, ...]
    best_scenario: str
    worst_scenario: str
    ranking: tuple[str, ...]
    observations: tuple[str, ...]


@dataclass(frozen=True)
class RecommendationSection:
    pricing_action: str
    recommendations: tuple[str, ...]
    risks: tuple[str, ...]
    monitoring: tuple[str, ...]
    implementation_notes: tuple[str, ...]


@dataclass(frozen=True)
class AssumptionSection:
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class LimitationSection:
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class PricingReport:
    metadata: Metadata
    executive_summary: ExecutiveSummary
    financial: FinancialSummary
    elasticity: ElasticitySummary
    forecast: ForecastSummary
    optimization: OptimizationSummary
    scenario: ScenarioSummary
    recommendations: RecommendationSection
    assumptions: AssumptionSection
    limitations: LimitationSection
