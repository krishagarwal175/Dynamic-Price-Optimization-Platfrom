"""ORM models (business entities).

Importing this package registers every model on ``Base.metadata`` so Alembic
autogenerate and ``relationship`` string resolution see the full mapping.
"""

from __future__ import annotations

from app.models.category import Category
from app.models.competitor import Competitor
from app.models.competitor_price import CompetitorPrice
from app.models.historical_sale import HistoricalSale
from app.models.product import Product

__all__ = [
    "Category",
    "Competitor",
    "CompetitorPrice",
    "HistoricalSale",
    "Product",
]
