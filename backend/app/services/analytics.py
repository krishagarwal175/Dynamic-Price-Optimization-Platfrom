"""Analytics service: loads persisted data and delegates to the pure analytics engines.

This is the boundary between the framework-free analytics engines and the rest of the
app. It loads data via repositories, feeds plain value objects to the engine, and maps
analytics domain errors onto API errors. It contains no financial formulas itself.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.category import Category
from app.models.product import Product
from app.pricing.errors import AnalyticsError, InsufficientDataError
from app.pricing.finance import FinancialMetrics, SaleLine, compute_financials
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
