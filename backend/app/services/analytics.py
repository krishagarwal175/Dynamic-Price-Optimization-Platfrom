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


def _weighted_unit_cost(rows: list[tuple[int, Decimal, Decimal]]) -> float | None:
    """COGS-weighted average unit cost across rows, for the dataset-scope profit curve."""
    total_units = sum(quantity for quantity, _price, _cost in rows)
    if total_units <= 0:
        return None
    total_cost = sum(cost * quantity for quantity, _price, cost in rows)
    return float(Decimal(total_cost) / Decimal(total_units))
