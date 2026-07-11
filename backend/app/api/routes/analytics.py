"""Read-only financial-analytics endpoints.

Exposes deterministic financial metrics only — no pricing recommendations, elasticity,
forecasting, or optimization.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AnalyticsServiceDep
from app.schemas.analytics import (
    CategoryFinancialsResponse,
    DatasetFinancialsResponse,
    FinancialMetricsSchema,
    ProductFinancialsResponse,
)
from app.schemas.envelope import SuccessResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

FixedCost = Annotated[
    Decimal,
    Query(ge=0, description="Optional total fixed cost used for net profit and break-even."),
]


@router.get(
    "/financial",
    response_model=SuccessResponse[DatasetFinancialsResponse],
    summary="Financial metrics for the whole dataset",
)
def dataset_financials(
    service: AnalyticsServiceDep,
    fixed_cost: FixedCost = Decimal("0"),
) -> SuccessResponse[DatasetFinancialsResponse]:
    metrics = service.dataset_financials(fixed_cost=fixed_cost)
    return SuccessResponse(
        data=DatasetFinancialsResponse(
            scope="dataset",
            metrics=FinancialMetricsSchema.model_validate(metrics),
        )
    )


@router.get(
    "/products/{product_id}",
    response_model=SuccessResponse[ProductFinancialsResponse],
    summary="Financial metrics for a product",
)
def product_financials(
    product_id: int,
    service: AnalyticsServiceDep,
    fixed_cost: FixedCost = Decimal("0"),
) -> SuccessResponse[ProductFinancialsResponse]:
    product, metrics = service.product_financials(product_id, fixed_cost=fixed_cost)
    return SuccessResponse(
        data=ProductFinancialsResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            metrics=FinancialMetricsSchema.model_validate(metrics),
        )
    )


@router.get(
    "/categories/{category_id}",
    response_model=SuccessResponse[CategoryFinancialsResponse],
    summary="Financial metrics for a category",
)
def category_financials(
    category_id: int,
    service: AnalyticsServiceDep,
    fixed_cost: FixedCost = Decimal("0"),
) -> SuccessResponse[CategoryFinancialsResponse]:
    category, metrics = service.category_financials(category_id, fixed_cost=fixed_cost)
    return SuccessResponse(
        data=CategoryFinancialsResponse(
            category_id=category.id,
            name=category.name,
            metrics=FinancialMetricsSchema.model_validate(metrics),
        )
    )
