"""Read-only catalog endpoints (products & categories) for the console frontend.

Thin presentation reads via the catalog service; no business/analytics logic. No endpoint
modifies persisted data.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CatalogServiceDep
from app.schemas.catalog import CategoryListResponse, ProductListResponse
from app.schemas.category import CategorySummary
from app.schemas.envelope import SuccessResponse
from app.schemas.product import ProductRead, ProductSummary

router = APIRouter(tags=["catalog"])

LimitParam = Annotated[int, Query(ge=1, le=200, description="Page size.")]
OffsetParam = Annotated[int, Query(ge=0, description="Page offset.")]


@router.get(
    "/products",
    response_model=SuccessResponse[ProductListResponse],
    summary="List catalog products (paginated, searchable)",
)
def list_products(
    service: CatalogServiceDep,
    search: str | None = None,
    category_id: int | None = None,
    limit: LimitParam = 50,
    offset: OffsetParam = 0,
) -> SuccessResponse[ProductListResponse]:
    page = service.list_products(query=search, category_id=category_id, limit=limit, offset=offset)
    return SuccessResponse(
        data=ProductListResponse(
            items=[ProductSummary.model_validate(p) for p in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
    )


@router.get(
    "/products/{product_id}",
    response_model=SuccessResponse[ProductRead],
    summary="Get a catalog product",
)
def get_product(product_id: int, service: CatalogServiceDep) -> SuccessResponse[ProductRead]:
    return SuccessResponse(data=ProductRead.model_validate(service.get_product(product_id)))


@router.get(
    "/categories",
    response_model=SuccessResponse[CategoryListResponse],
    summary="List catalog categories",
)
def list_categories(service: CatalogServiceDep) -> SuccessResponse[CategoryListResponse]:
    categories = service.list_categories()
    return SuccessResponse(
        data=CategoryListResponse(
            items=[CategorySummary.model_validate(c) for c in categories],
            total=len(categories),
        )
    )
