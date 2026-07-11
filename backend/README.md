# Backend — Pricing Service

FastAPI service that exposes the pricing, simulation, and catalog capabilities of the
platform. This document defines the layered structure that implementation follows.

> **Status (M2 — Backend Foundation):** infrastructure only. The service boots with typed
> configuration, structured logging, a request-correlation middleware, a global exception
> handler + standard response/error envelope, OpenAPI docs, and a health endpoint. **No**
> pricing, analytics, forecasting, or optimization logic exists yet (later milestones).

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
- Swagger UI: `/docs` · ReDoc: `/redoc` · OpenAPI schema: `/openapi.json`

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
