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
from app.schemas.elasticity import (
    DatasetElasticityResponse,
    ElasticityAnalysisSchema,
    ProductElasticityResponse,
)
from app.schemas.envelope import SuccessResponse
from app.schemas.forecast import (
    DatasetForecastResponse,
    ForecastResultSchema,
    ProductForecastResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

FixedCost = Annotated[
    Decimal,
    Query(ge=0, description="Optional total fixed cost used for net profit and break-even."),
]

Horizon = Annotated[
    int,
    Query(ge=1, le=60, description="Number of future periods to forecast."),
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


@router.get(
    "/elasticity",
    response_model=SuccessResponse[DatasetElasticityResponse],
    summary="Price elasticity of demand for the whole dataset",
)
def dataset_elasticity(
    service: AnalyticsServiceDep,
) -> SuccessResponse[DatasetElasticityResponse]:
    analysis = service.dataset_elasticity()
    return SuccessResponse(
        data=DatasetElasticityResponse(
            scope="dataset",
            analysis=ElasticityAnalysisSchema.model_validate(analysis),
        )
    )


@router.get(
    "/products/{product_id}/elasticity",
    response_model=SuccessResponse[ProductElasticityResponse],
    summary="Price elasticity of demand for a product",
)
def product_elasticity(
    product_id: int,
    service: AnalyticsServiceDep,
) -> SuccessResponse[ProductElasticityResponse]:
    product, analysis = service.product_elasticity(product_id)
    return SuccessResponse(
        data=ProductElasticityResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            analysis=ElasticityAnalysisSchema.model_validate(analysis),
        )
    )


@router.get(
    "/forecast",
    response_model=SuccessResponse[DatasetForecastResponse],
    summary="Demand forecast for the whole dataset",
)
def dataset_forecast(
    service: AnalyticsServiceDep,
    horizon: Horizon = 4,
) -> SuccessResponse[DatasetForecastResponse]:
    result = service.dataset_forecast(horizon=horizon)
    return SuccessResponse(
        data=DatasetForecastResponse(
            scope="dataset",
            forecast=ForecastResultSchema.model_validate(result),
        )
    )


@router.get(
    "/products/{product_id}/forecast",
    response_model=SuccessResponse[ProductForecastResponse],
    summary="Demand forecast for a product",
)
def product_forecast(
    product_id: int,
    service: AnalyticsServiceDep,
    horizon: Horizon = 4,
) -> SuccessResponse[ProductForecastResponse]:
    product, result = service.product_forecast(product_id, horizon=horizon)
    return SuccessResponse(
        data=ProductForecastResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            forecast=ForecastResultSchema.model_validate(result),
        )
    )
