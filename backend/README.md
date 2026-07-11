# Backend — Pricing Service

FastAPI service that exposes the pricing, simulation, and catalog capabilities of the
platform. This document defines the layered structure that implementation follows.

> **Status (through M6):** infrastructure + data model + ingestion. The service boots with
> typed configuration, structured logging, a request-correlation middleware, a global
> exception handler + standard response/error envelope, OpenAPI docs, a health endpoint, a
> **persistence foundation** (SQLAlchemy 2.0, Alembic, generic repository base), the
> **core business data model** (Category/Product/HistoricalSale/Competitor), and a
> **dataset ingestion pipeline** (upload → validation → preview → import for CSV/Excel).
> **No** pricing, analytics, forecasting, optimization, or reporting logic yet.

## Quick start

```bash
cd backend
python -m venv .venv
./.venv/Scripts/python -m pip install -e ".[dev]"   # Windows; use .venv/bin on POSIX
cp .env.example .env                                 # optional; sane defaults otherwise

# Run the API (http://127.0.0.1:8000)
./.venv/Scripts/python -m uvicorn app.main:app --reload
```

- Health: `GET /api/v1/health`
- Dataset ingestion: `POST /api/v1/datasets/upload` · `GET /api/v1/datasets/{id}/preview`
  · `POST /api/v1/datasets/{id}/import`
- Swagger UI: `/docs` · ReDoc: `/redoc` · OpenAPI schema: `/openapi.json`

## Database & migrations

The database provider is chosen entirely by the `DATABASE_URL` setting — SQLite locally
and in tests, PostgreSQL in deployment — with no code changes. Schema is owned **only** by
Alembic; the application never creates tables at startup (it just verifies connectivity).

```bash
# Apply all migrations (creates ./var/dpop.db by default)
./.venv/Scripts/python -m alembic upgrade head

# Inspect / move through history
./.venv/Scripts/python -m alembic current
./.venv/Scripts/python -m alembic downgrade -1

# Create a new migration when models change (later milestones)
./.venv/Scripts/python -m alembic revision --autogenerate -m "add product table"
```

Model/persistence conventions (integer keys, timestamp mixins, Alembic-only schema) are
recorded in ADR-0007.

## Quality & tests — local validation

Run these **in this order**. This is the *same* sequence, in the same order, that the CI
pipeline enforces on every push and pull request
([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) — CI is simply this sequence
on a clean clone. If it passes here, it passes in CI.

```bash
ruff check .        # 1. lint + import order   (fail on any lint error)
black --check .     # 2. formatting            (check only; never auto-format in CI)
mypy app            # 3. strict type checking
pytest              # 4. unit + integration test suite
```

On Windows, prefix each with the venv path, e.g. `./.venv/Scripts/ruff check .`.

All four gates must be green before a milestone is considered done (see the project
Definition of Done). Tool configuration is centralized in
[`pyproject.toml`](pyproject.toml) so local and CI runs are identical.

## Layered structure (`app/`)

The backend follows a layered / clean-architecture separation. Dependencies point
inward: `api → services → domain`, with `repositories` and `pricing` as adapters the
services depend on. Framework concerns never leak into `domain`.

| Directory | Responsibility |
|-----------|----------------|
| `api/` | HTTP route layer. Translates requests/responses to service calls. Thin — no business logic. |
| `core/` | Cross-cutting infrastructure: configuration, settings, security, app startup/wiring. |
| `domain/` | Framework-free domain entities, value objects, and business rules. The heart of the system. |
| `services/` | Application/use-case orchestration. Coordinates domain, pricing, and repositories. |
| `pricing/` | The pricing engine: demand elasticity modelling and price optimization algorithms. |
| `repositories/` | Persistence boundary. Abstracts data access away from services. |
| `schemas/` | Pydantic DTOs for request/response validation and serialization. |

## Tests (`tests/`)

- `unit/` — fast, isolated tests of domain rules and pricing logic.
- `integration/` — tests spanning API, services, and persistence.

Every feature must ship with tests before it can be marked done.
