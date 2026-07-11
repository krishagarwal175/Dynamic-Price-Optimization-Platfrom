# ADR-0009: Dataset ingestion pipeline architecture

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[system_architecture]], [[ADR-0003-layered-backend-architecture]],
  [[ADR-0008-core-business-data-model]], [[database_design]]

## Context

M6 implements the platform's first end-to-end workflow: **upload → validation → preview →
normalization → persistence**. The frozen [[system_architecture]] already lists a File
Storage subsystem and this exact data flow, but the concrete structure, the parsing
engine, and the validation framework need to be fixed — and they add new packages and a
heavy dependency (pandas), so the decision is recorded.

## Decision

1. **Storage abstraction** (`app/storage/`): a `FileStorage` `Protocol` with a
   `LocalFileStorage` implementation (v1). Injected via `app.state.file_storage`;
   object storage (S3) can be added later behind the same protocol. Storage logic is not
   hardcoded anywhere else.
2. **Parsing** (`app/ingestion/parsing.py`): **pandas**-based (`read_csv`/`read_excel`
   with `openpyxl`), format detected by extension then content-type. Parsing yields a
   string DataFrame and is **independent of business validation**.
3. **Structured validation** (`app/ingestion/validation.py`): a reusable, schema-driven
   framework (`DatasetSchema`/`ColumnSpec`) that returns **structured `ValidationIssue`
   records, not exceptions**, for data-quality problems (missing/duplicate columns, empty
   dataset, invalid numeric/date, missing values, negatives, duplicate uniques). Only
   parse/format/size failures remain exceptions → mapped to typed `AppError`s
   (415 `UNSUPPORTED_MEDIA_TYPE`, 413 `PAYLOAD_TOO_LARGE`).
4. **Preview** (`app/ingestion/preview.py`): read-only summary (columns, inferred types,
   row/missing/duplicate counts, first-N rows) plus the validation report. **No
   persistence.**
5. **Import via registry** (`app/ingestion/registry.py` + `catalog.py`): a
   `DatasetKind → (schema, importer)` registry. `ProductCatalogImporter` normalizes and
   maps rows into `Category`/`Product` **through the repository layer**, inside a **single
   transaction** — any error rolls back completely; the `Dataset` status lifecycle is
   `uploaded → imported | failed`.
6. **Dataset entity** (`app/models/dataset.py`): added now (its introduction was deferred
   by [[ADR-0008-core-business-data-model]]). Tracks the stored upload + lifecycle status;
   holds no row data.
7. **New packages** `app/storage/` and `app/ingestion/` extend the module map from
   [[ADR-0003-layered-backend-architecture]]; the ingestion service lives in
   `app/services/`, endpoints in `app/api/routes/datasets.py`.
8. **Dependencies**: `pandas`, `openpyxl`, `python-multipart`. mypy `warn_return_any` is
   relaxed **only** at the pandas-boundary modules (parsing/preview/validation/frames);
   all business logic stays fully strict.

## Options considered

- **Parsing engine:** hand-rolled CSV vs **pandas**. pandas is the standard for tabular
  data and gives CSV+Excel uniformly; chosen despite its weight.
- **Validation as exceptions vs structured issues:** structured issues let the preview
  surface every problem at once — chosen; exceptions reserved for hard failures.
- **Importer dispatch:** `if/elif` on kind vs a **registry**. The registry keeps the
  service/API closed to modification when new dataset kinds are added — chosen.

## Consequences

- **Positive:** clean separation (storage / parse / validate / preview / import);
  extensible via the registry; storage swappable; reproducible, structured validation.
- **Negative / trade-offs:** pandas is a heavy dependency; its partial typing forced a
  narrow mypy relaxation at the boundary. Only the product-catalog kind exists so far.
- **Follow-ups:** additional dataset kinds (e.g. sales/competitor imports) add a schema +
  importer + `DatasetKind`; object storage backend when needed. Analytics remain future.

## Notes
No analytics/pricing/forecasting/optimization is introduced. The broader frozen
architecture (layering, API envelope, versioning) is unchanged.
