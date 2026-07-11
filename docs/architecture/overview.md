# Architecture Overview (Frozen — v1)

> Committed, distilled reference of the frozen v1 architecture. The full design and
> rationale live in the engineering vault (`vault4/02-Architecture/` and
> `vault4/04-Decisions-ADR/`); accepted ADRs are mirrored under [`docs/adr/`](../adr/).
>
> **Status:** Architecture frozen 2026-07-11. Structural changes require a new ADR.

## System at a glance

A single-page React console talks over REST (`/api/v1`) to a FastAPI backend, which runs
a deterministic pricing-analytics engine and persists to PostgreSQL; uploaded CSVs are
kept in file storage.

```
Browser (React SPA)  ──HTTPS/JSON──▶  FastAPI backend  ──▶  PostgreSQL
                                          │      │
                                   analytics    file storage (uploaded CSVs)
                                    engine
```

**Deployment boundaries:** static frontend build (CDN/nginx) · stateless backend
container (uvicorn/gunicorn) · managed PostgreSQL · attached file storage. v1 is fully
synchronous; a background worker is a deferred, ADR-gated extension.

## Technology stack (ADR-0002)

- **Frontend:** React + TypeScript (Vite), TanStack Query, Zustand, Recharts,
  TanStack Table, React Hook Form + Zod, Tailwind.
- **Backend:** Python + FastAPI, Pydantic v2, SQLAlchemy 2.0 + Alembic.
- **Database:** PostgreSQL. **Storage:** file abstraction (local → object storage).
- **Analytics:** pure Python (NumPy/pandas), deterministic, framework-free.

## Backend layering (ADR-0003)

Dependencies point inward; the domain and analytics layers are framework-free.

```
api → services → domain ← analytics (pricing/)
 │        │
 │        └─▶ repositories ─▶ PostgreSQL
schemas (validation)         core: config · logging · error handling
```

| Layer | Responsibility |
|-------|----------------|
| `api/` | HTTP adapter; translate requests ↔ DTOs; no business logic |
| `services/` | Use-case orchestration; transaction boundaries |
| `domain/` | Entities, value objects, invariants (framework-free) |
| `pricing/` | Deterministic analytics engines (framework-free) |
| `repositories/` | Only layer that touches the DB |
| `schemas/` | Pydantic DTOs + boundary validation |
| `core/` | Config, logging, error handling, app wiring |

## Analytics engine (ADR-0004)

Deterministic, pure, framework-independent sub-engines: **elasticity** (log-log
regression), **forecast** (moving average / linear trend / seasonal-naive, strategy
pattern), **optimization** (analytic / bounded search), **break-even**, **scenario**
(composes the others), **finance** (revenue/margin/contribution). No trained ML in v1.

## API (ADR-0006)

REST/JSON under `/api/v1` (URI versioning, additive-only within a major version).

- **Success:** `{ "data": …, "meta": { requestId, timestamp, [pagination] } }`
- **Error:** `{ "error": { code, message, details? }, "meta": {…} }`
- Endpoint groups: health · datasets · products · analysis · optimization · scenarios ·
  reports.

## Data model (v1)

`Dataset 1─∞ Product 1─∞ DemandRecord`; analytics results (`ElasticityResult`,
`ForecastResult`) and `Scenario 1─∞ ScenarioResult` attach to products. Core entities in
3NF; result tables are a rebuildable cache of deterministic computations. Money as
`NUMERIC`, never float.

## End-to-end data flow

```
Upload CSV → Validation → Persistence → Analytics → Scenario Engine → Dashboard → Report
```

## Testing (summary)

Test pyramid: many unit tests (domain + analytics validated against known answers),
integration tests (API↔services↔repositories against a test PostgreSQL), frontend
component/integration tests (Vitest + RTL + MSW). Tests are part of the Definition of Done.

## Security & configuration (v1 scope)

Typed settings from env vars (Pydantic Settings); secrets only via env, never committed;
layered input validation (Pydantic + domain invariants); parameterized queries. **No auth
in v1** (single-user/local), with the envelope/versioning leaving room to add it without
breaking clients; TLS at the ingress layer.

## Decision records

| ADR | Decision |
|-----|----------|
| [ADR-0002](../adr/ADR-0002-technology-stack.md) | Technology stack |
| [ADR-0003](../adr/ADR-0003-layered-backend-architecture.md) | Layered backend architecture |
| [ADR-0004](../adr/ADR-0004-deterministic-analytics-engine.md) | Deterministic analytics engine |
| [ADR-0005](../adr/ADR-0005-frontend-state-and-charting.md) | Frontend state & charting |
| [ADR-0006](../adr/ADR-0006-rest-api-conventions.md) | REST API conventions |

See the [implementation roadmap](../../../vault4/03-Planning/implementation_roadmap.md)
(vault) for the M0–M14 build sequence.
