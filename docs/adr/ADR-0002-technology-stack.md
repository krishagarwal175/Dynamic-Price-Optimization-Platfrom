# ADR-0002: Technology stack selection

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[system_architecture]], [[ADR-0003-layered-backend-architecture]],
  [[ADR-0005-frontend-state-and-charting]]

## Context

The platform needs a stack that is productive, widely understood (interview value),
strong for numerical/analytics work, and simple to operate. It is a data-in →
analytics → dashboards application, read-heavy on the frontend and computation-heavy on
the backend.

## Decision

We will build with:

- **Frontend:** React + TypeScript, bundled with **Vite**.
- **Backend:** **Python + FastAPI**, with Pydantic v2 for validation and SQLAlchemy 2.0 +
  Alembic for persistence/migrations.
- **Database:** **PostgreSQL**.
- **Analytics:** pure Python with NumPy/pandas for math (kept framework-free).
- **Packaging/deploy:** Docker containers; frontend as a static build.

## Options considered

1. **Python/FastAPI + React + PostgreSQL (chosen)** — Python is the natural home for
   analytics (NumPy/pandas), FastAPI gives typed, fast APIs; React+TS is the standard,
   interview-relevant frontend; PostgreSQL is a robust, free relational store.
2. **Node/TypeScript full-stack (Nest/Express)** — one language, but weaker analytics
   ecosystem; would push numeric work into a less natural environment.
3. **Django** — batteries-included, but heavier than needed and less API-first than
   FastAPI for this use case.
4. **NoSQL (MongoDB) store** — flexible, but the data is inherently relational
   (datasets→products→records); relational integrity is a better fit.

## Consequences

- **Positive:** best-in-class analytics libraries; fast, typed APIs; strong hiring-signal
  stack; relational integrity for the domain.
- **Negative / trade-offs:** two languages (Python + TypeScript) to maintain; a running
  PostgreSQL is required for integration tests (mitigated with containers).
- **Follow-ups:** [[ADR-0003-layered-backend-architecture]] (structure),
  [[ADR-0005-frontend-state-and-charting]] (frontend libraries).

## Notes
Exact minor library choices (e.g., UUID vs bigserial keys) are deferred to
implementation and remain within this stack decision.
