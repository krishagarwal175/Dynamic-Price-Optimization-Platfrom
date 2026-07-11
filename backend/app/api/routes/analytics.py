"""Read-only analytics & optimization endpoints.

Exposes deterministic financial metrics, elasticity, forecasting, and a pricing-
optimization *recommendation* (advisory only). No endpoint modifies persisted data.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AnalyticsServiceDep
from app.pricing.optimization import Objective, OptimizationConstraints
from app.pricing.reporting import PricingReport, ReportFormat, render, to_dict
from app.pricing.simulation import ScenarioSpec, ScenarioType
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
from app.schemas.optimization import (
    DatasetOptimizationResponse,
    OptimizationResultSchema,
    ProductOptimizationResponse,
)
from app.schemas.report import DatasetReportResponse, ProductReportResponse
from app.schemas.simulation import (
    DatasetSimulationResponse,
    ProductSimulationResponse,
    SimulationResultSchema,
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

ObjectiveParam = Annotated[
    Objective,
    Query(description="Objective to maximize."),
]


def _constraints(
    min_price: float | None,
    max_price: float | None,
    min_margin_pct: float | None,
    min_profit: float | None,
    min_demand: float | None,
    max_increase_pct: float | None,
    max_decrease_pct: float | None,
) -> OptimizationConstraints:
    return OptimizationConstraints(
        min_price=min_price,
        max_price=max_price,
        min_margin_pct=min_margin_pct,
        min_profit=min_profit,
        min_demand=min_demand,
        max_increase_pct=max_increase_pct,
        max_decrease_pct=max_decrease_pct,
    )


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


@router.get(
    "/optimization",
    response_model=SuccessResponse[DatasetOptimizationResponse],
    summary="Recommended price for the aggregate dataset (advisory; read-only)",
)
def dataset_optimization(
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    min_price: float | None = None,
    max_price: float | None = None,
    min_margin_pct: float | None = None,
    min_profit: float | None = None,
    min_demand: float | None = None,
    max_increase_pct: float | None = None,
    max_decrease_pct: float | None = None,
) -> SuccessResponse[DatasetOptimizationResponse]:
    result = service.dataset_optimization(
        objective=objective,
        fixed_cost=fixed_cost,
        constraints=_constraints(
            min_price,
            max_price,
            min_margin_pct,
            min_profit,
            min_demand,
            max_increase_pct,
            max_decrease_pct,
        ),
    )
    return SuccessResponse(
        data=DatasetOptimizationResponse(
            scope="dataset",
            optimization=OptimizationResultSchema.model_validate(result),
        )
    )


@router.get(
    "/products/{product_id}/optimization",
    response_model=SuccessResponse[ProductOptimizationResponse],
    summary="Recommended price for a product (advisory; read-only)",
)
def product_optimization(
    product_id: int,
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    min_price: float | None = None,
    max_price: float | None = None,
    min_margin_pct: float | None = None,
    min_profit: float | None = None,
    min_demand: float | None = None,
    max_increase_pct: float | None = None,
    max_decrease_pct: float | None = None,
) -> SuccessResponse[ProductOptimizationResponse]:
    product, result = service.product_optimization(
        product_id,
        objective=objective,
        fixed_cost=fixed_cost,
        constraints=_constraints(
            min_price,
            max_price,
            min_margin_pct,
            min_profit,
            min_demand,
            max_increase_pct,
            max_decrease_pct,
        ),
    )
    return SuccessResponse(
        data=ProductOptimizationResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            optimization=OptimizationResultSchema.model_validate(result),
        )
    )


ScenarioParam = Annotated[
    ScenarioType | None,
    Query(description="Evaluate a single named scenario (plus baseline & recommended)."),
]


def _simulation_scenarios(
    scenario: ScenarioType | None,
    price: float | None,
    percentage_change: float | None,
) -> list[ScenarioSpec] | None:
    """Build the scenario list from query params, or ``None`` for the default set."""
    if scenario is None:
        return None
    base = [
        ScenarioSpec(ScenarioType.BASELINE, label="Baseline"),
        ScenarioSpec(ScenarioType.RECOMMENDED, label="Recommended"),
    ]
    if scenario is ScenarioType.BASELINE or scenario is ScenarioType.RECOMMENDED:
        return base
    if scenario is ScenarioType.FIXED_PRICE:
        label = f"${price:g}" if price is not None else "Fixed price"
        base.append(ScenarioSpec(ScenarioType.FIXED_PRICE, label=label, price=price))
    else:  # PERCENTAGE_INCREASE / PERCENTAGE_DECREASE
        sign = "+" if scenario is ScenarioType.PERCENTAGE_INCREASE else "-"
        label = f"{sign}{percentage_change:.0%}" if percentage_change is not None else "Custom %"
        base.append(ScenarioSpec(scenario, label=label, percentage=percentage_change))
    return base


@router.get(
    "/simulation",
    response_model=SuccessResponse[DatasetSimulationResponse],
    summary="What-if scenario simulation for the aggregate dataset (read-only)",
)
def dataset_simulation(
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    scenario: ScenarioParam = None,
    price: float | None = None,
    percentage_change: float | None = None,
) -> SuccessResponse[DatasetSimulationResponse]:
    result = service.dataset_simulation(
        objective=objective,
        fixed_cost=fixed_cost,
        scenarios=_simulation_scenarios(scenario, price, percentage_change),
    )
    return SuccessResponse(
        data=DatasetSimulationResponse(
            scope="dataset",
            simulation=SimulationResultSchema.model_validate(result),
        )
    )


@router.get(
    "/products/{product_id}/simulation",
    response_model=SuccessResponse[ProductSimulationResponse],
    summary="What-if scenario simulation for a product (read-only)",
)
def product_simulation(
    product_id: int,
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    scenario: ScenarioParam = None,
    price: float | None = None,
    percentage_change: float | None = None,
) -> SuccessResponse[ProductSimulationResponse]:
    product, result = service.product_simulation(
        product_id,
        objective=objective,
        fixed_cost=fixed_cost,
        scenarios=_simulation_scenarios(scenario, price, percentage_change),
    )
    return SuccessResponse(
        data=ProductSimulationResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            simulation=SimulationResultSchema.model_validate(result),
        )
    )


ReportFormatParam = Annotated[
    ReportFormat,
    Query(alias="format", description="Report output format: json, markdown, or text."),
]


def _rendered(
    report: PricingReport, fmt: ReportFormat
) -> tuple[dict[str, object] | None, str | None]:
    """Return (json_report, text_content) for the requested format."""
    if fmt is ReportFormat.JSON:
        return to_dict(report), None
    return None, render(report, fmt)


@router.get(
    "/report",
    response_model=SuccessResponse[DatasetReportResponse],
    summary="Full pricing analysis report for the aggregate dataset (read-only)",
)
def dataset_report(
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    report_format: ReportFormatParam = ReportFormat.JSON,
) -> SuccessResponse[DatasetReportResponse]:
    report = service.dataset_report(objective=objective, fixed_cost=fixed_cost)
    report_dict, content = _rendered(report, report_format)
    return SuccessResponse(
        data=DatasetReportResponse(
            scope="dataset", format=report_format, report=report_dict, content=content
        )
    )


@router.get(
    "/products/{product_id}/report",
    response_model=SuccessResponse[ProductReportResponse],
    summary="Full pricing analysis report for a product (read-only)",
)
def product_report(
    product_id: int,
    service: AnalyticsServiceDep,
    objective: ObjectiveParam = Objective.MAXIMIZE_GROSS_PROFIT,
    fixed_cost: FixedCost = Decimal("0"),
    report_format: ReportFormatParam = ReportFormat.JSON,
) -> SuccessResponse[ProductReportResponse]:
    product, report = service.product_report(product_id, objective=objective, fixed_cost=fixed_cost)
    report_dict, content = _rendered(report, report_format)
    return SuccessResponse(
        data=ProductReportResponse(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            format=report_format,
            report=report_dict,
            content=content,
        )
    )
