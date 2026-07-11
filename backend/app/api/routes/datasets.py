"""Dataset ingestion endpoints: upload -> preview -> import."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import IngestionServiceDep
from app.models.dataset import DatasetKind
from app.schemas.dataset import (
    DatasetRead,
    ImportResultResponse,
    PreviewResponse,
    ValidationIssueSchema,
    ValidationReportSchema,
)
from app.schemas.envelope import SuccessResponse
from app.services.ingestion import PreviewResult

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post(
    "/upload",
    response_model=SuccessResponse[DatasetRead],
    status_code=201,
    summary="Upload a dataset file",
    description="Upload a CSV or Excel (.xlsx) file. The file is stored and registered; "
    "no rows are imported until the import endpoint is called.",
)
async def upload_dataset(
    service: IngestionServiceDep,
    file: Annotated[UploadFile, File()],
    kind: Annotated[DatasetKind, Form()] = DatasetKind.PRODUCT_CATALOG,
) -> SuccessResponse[DatasetRead]:
    data = await file.read()
    dataset = service.upload(
        filename=file.filename or "upload",
        content_type=file.content_type,
        data=data,
        kind=kind,
    )
    return SuccessResponse(data=DatasetRead.model_validate(dataset))


def _to_preview_response(result: PreviewResult) -> PreviewResponse:
    preview = result.preview
    report = result.report
    return PreviewResponse(
        dataset_id=result.dataset.id,
        columns=preview.columns,
        inferred_types=preview.inferred_types,
        row_count=preview.row_count,
        missing_values=preview.missing_values,
        duplicate_rows=preview.duplicate_rows,
        sample_rows=preview.sample_rows,
        validation=ValidationReportSchema(
            is_valid=report.is_valid,
            truncated=report.truncated,
            issues=[
                ValidationIssueSchema(
                    code=issue.code,
                    message=issue.message,
                    column=issue.column,
                    row=issue.row,
                )
                for issue in report.issues
            ],
        ),
    )


@router.get(
    "/{dataset_id}/preview",
    response_model=SuccessResponse[PreviewResponse],
    summary="Preview a dataset",
    description="Return detected columns, inferred types, row/missing/duplicate summaries, "
    "sample rows, and a structured validation report. Does not persist any data.",
)
def preview_dataset(
    dataset_id: int, service: IngestionServiceDep
) -> SuccessResponse[PreviewResponse]:
    result = service.preview(dataset_id)
    return SuccessResponse(data=_to_preview_response(result))


@router.post(
    "/{dataset_id}/import",
    response_model=SuccessResponse[ImportResultResponse],
    summary="Import a validated dataset",
    description="Validate and, if valid, import the dataset into the business entities "
    "within a single transaction. A failed import rolls back and marks the dataset failed.",
)
def import_dataset(
    dataset_id: int, service: IngestionServiceDep
) -> SuccessResponse[ImportResultResponse]:
    dataset, summary = service.import_dataset(dataset_id)
    return SuccessResponse(
        data=ImportResultResponse(
            dataset_id=dataset.id,
            status=dataset.status,
            rows_imported=summary.rows_imported,
            categories_created=summary.categories_created,
            products_created=summary.products_created,
        )
    )
