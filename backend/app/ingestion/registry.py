"""Registry mapping a dataset kind to its schema and importer.

Adding a new dataset type = add a schema + importer and register it here; the service and
API are unchanged.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd
from sqlalchemy.orm import Session

from app.ingestion.catalog import ImportSummary, ProductCatalogImporter
from app.ingestion.validation import DatasetSchema
from app.models.dataset import DatasetKind


class Importer(Protocol):
    schema: DatasetSchema

    def run(self, session: Session, df: pd.DataFrame) -> ImportSummary: ...


_REGISTRY: dict[DatasetKind, Importer] = {
    DatasetKind.PRODUCT_CATALOG: ProductCatalogImporter(),
}


def get_importer(kind: DatasetKind) -> Importer:
    return _REGISTRY[kind]


def get_schema(kind: DatasetKind) -> DatasetSchema:
    return _REGISTRY[kind].schema
