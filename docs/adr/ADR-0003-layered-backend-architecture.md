# ADR-0003: Layered backend architecture with a framework-independent core

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[backend_architecture]], [[analytics_architecture]],
  [[ADR-0004-deterministic-analytics-engine]]

## Context

The backend mixes web concerns (HTTP), orchestration, business rules, heavy numerical
analytics, and persistence. Without clear boundaries this becomes an untestable tangle.
We want high testability, swappable infrastructure, and clarity — without enterprise
over-engineering.

## Decision

We will adopt a **layered / clean architecture** with the dependency rule pointing
inward: `api → services → domain`, with `repositories` and `pricing` (analytics) as
adapters services depend on. The **domain and analytics layers are framework-free** (no
FastAPI, SQLAlchemy, or Pydantic imports). Cross-cutting concerns (config, logging, error
handling) live in `core/`.

Module layout: `api/`, `schemas/`, `services/`, `domain/`, `pricing/`, `repositories/`,
`core/` (as detailed in [[backend_architecture]]).

## Options considered

1. **Layered/clean architecture (chosen)** — clear boundaries, pure testable core,
   swappable persistence; modest indirection.
2. **Framework-centric "fat router" (logic in endpoints)** — fastest to start, but couples
   business logic to HTTP and the ORM; poor testability; degrades quickly.
3. **Full hexagonal architecture with ports/adapters everywhere** — maximally decoupled
   but overkill for v1; more ceremony than value here.

## Consequences

- **Positive:** domain + analytics unit-tested with no framework/DB; persistence and web
  frameworks are swappable; responsibilities are obvious.
- **Negative / trade-offs:** a few more layers/objects than a naive approach; discipline
  needed to keep framework code out of the core.
- **Follow-ups:** [[ADR-0004-deterministic-analytics-engine]] builds on the pure core;
  repository seam realized in M4 ([[implementation_roadmap]]).
