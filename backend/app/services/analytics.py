"""Analytics service: loads persisted data and delegates to the pure analytics engines.

This is the boundary between the framework-free analytics engines and the rest of the
app. It loads data via repositories, feeds plain value objects to the engine, and maps
analytics domain errors onto API errors. It contains no financial formulas itself.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.category import Category
from app.models.product import Product
from app.pricing.elasticity import ElasticityAnalysis, Observation, analyze_elasticity
from app.pricing.errors import AnalyticsError, InsufficientDataError
from app.pricing.finance import FinancialMetrics, SaleLine, compute_financials
from app.pricing.forecasting import ForecastResult, forecast_demand
from app.pricing.forecasting import Observation as ForecastObservation
from app.pricing.optimization import (
    Objective,
    OptimizationConstraints,
    OptimizationInput,
    OptimizationResult,
    optimize,
)
from app.pricing.reporting import PricingReport, ReportInput, generate_report
from app.pricing.simulation import (
    ScenarioSpec,
    SimulationInput,
    SimulationResult,
    default_scenarios,
    simulate,
)
from app.repositories.category import CategoryRepository
from app.repositories.historical_sale import HistoricalSaleRepository
from app.repositories.product import ProductRepository

_ZERO = Decimal("0")


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self._products = ProductRepository(session)
        self._categories = CategoryRepository(session)
        self._sales = HistoricalSaleRepository(session)

    def dataset_financials(self, *, fixed_cost: Decimal = _ZERO) -> FinancialMetrics:
        rows = self._sales.unit_economics()
        return self._compute(rows, fixed_cost)

    def product_financials(
        self, product_id: int, *, fixed_cost: Decimal = _ZERO
    ) -> tuple[Product, FinancialMetrics]:
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} not found.")
        rows = self._sales.unit_economics(product_id=product_id)
        return product, self._compute(rows, fixed_cost)

    def category_financials(
        self, category_id: int, *, fixed_cost: Decimal = _ZERO
    ) -> tuple[Category, FinancialMetrics]:
        category = self._categories.get(category_id)
        if category is None:
            raise NotFoundError(f"Category {category_id} not found.")
        rows = self._sales.unit_economics(category_id=category_id)
        return category, self._compute(rows, fixed_cost)

    def _compute(
        self, rows: list[tuple[int, Decimal, Decimal]], fixed_cost: Decimal
    ) -> FinancialMetrics:
        lines = [
            SaleLine(quantity=quantity, unit_price=unit_price, unit_cost=unit_cost)
            for quantity, unit_price, unit_cost in rows
        ]
        try:
            return compute_financials(lines, fixed_cost=fixed_cost)
        except InsufficientDataError as exc:
            raise ValidationError(str(exc)) from exc
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc

    # --------------------------------------------------------------- elasticity
    def dataset_elasticity(self) -> ElasticityAnalysis:
        rows = self._sales.unit_economics()
        return self._analyze(rows, _weighted_unit_cost(rows))

    def product_elasticity(self, product_id: int) -> tuple[Product, ElasticityAnalysis]:
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} not found.")
        rows = self._sales.unit_economics(product_id=product_id)
        return product, self._analyze(rows, float(product.unit_cost))

    def _analyze(
        self, rows: list[tuple[int, Decimal, Decimal]], unit_cost: float | None
    ) -> ElasticityAnalysis:
        observations = [
            Observation(price=float(unit_price), quantity=float(quantity))
            for quantity, unit_price, _unit_cost in rows
        ]
        try:
            return analyze_elasticity(observations, unit_cost=unit_cost)
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc

    # --------------------------------------------------------------- forecasting
    def dataset_forecast(self, *, horizon: int = 4) -> ForecastResult:
        rows = self._sales.demand_by_period()
        return self._forecast(rows, horizon)

    def product_forecast(
        self, product_id: int, *, horizon: int = 4
    ) -> tuple[Product, ForecastResult]:
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} not found.")
        rows = self._sales.demand_by_period(product_id=product_id)
        return product, self._forecast(rows, horizon)

    def _forecast(self, rows: list[tuple[date, int]], horizon: int) -> ForecastResult:
        observations = [
            ForecastObservation(period=period, demand=float(quantity)) for period, quantity in rows
        ]
        try:
            return forecast_demand(observations, horizon=horizon)
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc

    # --------------------------------------------------------------- optimization
    def product_optimization(
        self,
        product_id: int,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        constraints: OptimizationConstraints | None = None,
    ) -> tuple[Product, OptimizationResult]:
        product, elasticity_analysis = self.product_elasticity(product_id)
        _, forecast_result = self.product_forecast(product_id)
        reference_demand = forecast_result.forecast[0].predicted
        result = self._optimize(
            current_price=float(product.base_price),
            variable_cost=float(product.unit_cost),
            reference_demand=reference_demand,
            elasticity=elasticity_analysis.elasticity_coefficient,
            objective=objective,
            fixed_cost=fixed_cost,
            constraints=constraints,
        )
        return product, result

    def dataset_optimization(
        self,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        constraints: OptimizationConstraints | None = None,
    ) -> OptimizationResult:
        # Aggregate the dataset as a single representative product (average selling price,
        # weighted unit cost, aggregate elasticity + forecast). This is a single-curve
        # optimization, not joint multi-product optimization.
        elasticity_analysis = self.dataset_elasticity()
        forecast_result = self.dataset_forecast()
        rows = self._sales.unit_economics()
        current_price = _average_selling_price(rows)
        variable_cost = _weighted_unit_cost(rows) or 0.0
        if current_price is None:
            raise ValidationError("No sales data available to optimize.")
        return self._optimize(
            current_price=current_price,
            variable_cost=variable_cost,
            reference_demand=forecast_result.forecast[0].predicted,
            elasticity=elasticity_analysis.elasticity_coefficient,
            objective=objective,
            fixed_cost=fixed_cost,
            constraints=constraints,
        )

    def _optimize(
        self,
        *,
        current_price: float,
        variable_cost: float,
        reference_demand: float,
        elasticity: float,
        objective: Objective,
        fixed_cost: Decimal,
        constraints: OptimizationConstraints | None,
    ) -> OptimizationResult:
        opt_input = OptimizationInput(
            current_price=current_price,
            variable_cost=variable_cost,
            reference_demand=reference_demand,
            elasticity=elasticity,
            fixed_cost=float(fixed_cost),
            objective=objective,
            constraints=constraints or OptimizationConstraints(),
        )
        try:
            return optimize(opt_input)
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc

    # --------------------------------------------------------------- simulation
    def product_simulation(
        self,
        product_id: int,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        scenarios: list[ScenarioSpec] | None = None,
    ) -> tuple[Product, SimulationResult]:
        product, elasticity_analysis = self.product_elasticity(product_id)
        _, forecast_result = self.product_forecast(product_id)
        _, optimization = self.product_optimization(product_id, objective=objective)
        result = self._simulate(
            current_price=float(product.base_price),
            variable_cost=float(product.unit_cost),
            baseline_demand=forecast_result.forecast[0].predicted,
            elasticity=elasticity_analysis.elasticity_coefficient,
            recommended_price=optimization.recommended_price,
            constraint_summary=", ".join(optimization.active_constraints) or None,
            objective=objective,
            fixed_cost=fixed_cost,
            scenarios=scenarios,
        )
        return product, result

    def dataset_simulation(
        self,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        scenarios: list[ScenarioSpec] | None = None,
    ) -> SimulationResult:
        elasticity_analysis = self.dataset_elasticity()
        forecast_result = self.dataset_forecast()
        optimization = self.dataset_optimization(objective=objective)
        rows = self._sales.unit_economics()
        current_price = _average_selling_price(rows)
        if current_price is None:
            raise ValidationError("No sales data available to simulate.")
        return self._simulate(
            current_price=current_price,
            variable_cost=_weighted_unit_cost(rows) or 0.0,
            baseline_demand=forecast_result.forecast[0].predicted,
            elasticity=elasticity_analysis.elasticity_coefficient,
            recommended_price=optimization.recommended_price,
            constraint_summary=", ".join(optimization.active_constraints) or None,
            objective=objective,
            fixed_cost=fixed_cost,
            scenarios=scenarios,
        )

    def _simulate(
        self,
        *,
        current_price: float,
        variable_cost: float,
        baseline_demand: float,
        elasticity: float,
        recommended_price: float | None,
        constraint_summary: str | None,
        objective: Objective,
        fixed_cost: Decimal,
        scenarios: list[ScenarioSpec] | None,
    ) -> SimulationResult:
        sim_input = SimulationInput(
            current_price=current_price,
            baseline_demand=baseline_demand,
            elasticity=elasticity,
            unit_cost=variable_cost,
            fixed_cost=float(fixed_cost),
            objective=objective,
            recommended_price=recommended_price,
            constraint_summary=constraint_summary,
            scenarios=(
                tuple(scenarios)
                if scenarios is not None
                else default_scenarios(recommended_available=recommended_price is not None)
            ),
        )
        try:
            return simulate(sim_input)
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc

    # --------------------------------------------------------------- reporting
    def product_report(
        self,
        product_id: int,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        scenarios: list[ScenarioSpec] | None = None,
    ) -> tuple[Product, PricingReport]:
        product, financial = self.product_financials(product_id, fixed_cost=fixed_cost)
        _, elasticity = self.product_elasticity(product_id)
        _, forecast = self.product_forecast(product_id)
        _, optimization = self.product_optimization(
            product_id, objective=objective, fixed_cost=fixed_cost
        )
        _, simulation = self.product_simulation(
            product_id, objective=objective, fixed_cost=fixed_cost, scenarios=scenarios
        )
        report = self._report(
            scope="product",
            subject=f"{product.sku} — {product.name}",
            currency=product.currency,
            objective=objective,
            financial=financial,
            elasticity=elasticity,
            forecast=forecast,
            optimization=optimization,
            simulation=simulation,
        )
        return product, report

    def dataset_report(
        self,
        *,
        objective: Objective,
        fixed_cost: Decimal = _ZERO,
        scenarios: list[ScenarioSpec] | None = None,
    ) -> PricingReport:
        return self._report(
            scope="dataset",
            subject="Aggregate dataset",
            currency="USD",
            objective=objective,
            financial=self.dataset_financials(fixed_cost=fixed_cost),
            elasticity=self.dataset_elasticity(),
            forecast=self.dataset_forecast(),
            optimization=self.dataset_optimization(objective=objective, fixed_cost=fixed_cost),
            simulation=self.dataset_simulation(
                objective=objective, fixed_cost=fixed_cost, scenarios=scenarios
            ),
        )

    def _report(
        self,
        *,
        scope: str,
        subject: str,
        currency: str,
        objective: Objective,
        financial: FinancialMetrics,
        elasticity: ElasticityAnalysis,
        forecast: ForecastResult,
        optimization: OptimizationResult,
        simulation: SimulationResult,
    ) -> PricingReport:
        report_input = ReportInput(
            scope=scope,
            subject=subject,
            currency=currency,
            objective=objective,
            financial=financial,
            elasticity=elasticity,
            forecast=forecast,
            optimization=optimization,
            simulation=simulation,
        )
        try:
            return generate_report(report_input)
        except AnalyticsError as exc:
            raise ValidationError(str(exc)) from exc


def _weighted_unit_cost(rows: list[tuple[int, Decimal, Decimal]]) -> float | None:
    """COGS-weighted average unit cost across rows, for the dataset-scope profit curve."""
    total_units = sum(quantity for quantity, _price, _cost in rows)
    if total_units <= 0:
        return None
    total_cost = sum(cost * quantity for quantity, _price, cost in rows)
    return float(Decimal(total_cost) / Decimal(total_units))


def _average_selling_price(rows: list[tuple[int, Decimal, Decimal]]) -> float | None:
    """Volume-weighted average selling price (ASP) = revenue / units."""
    total_units = sum(quantity for quantity, _price, _cost in rows)
    if total_units <= 0:
        return None
    total_revenue = sum(price * quantity for quantity, price, _cost in rows)
    return float(Decimal(total_revenue) / Decimal(total_units))
