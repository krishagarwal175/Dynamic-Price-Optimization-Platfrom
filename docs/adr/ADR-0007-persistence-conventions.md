# ADR-0007: Persistence conventions — surrogate keys, timestamps, and Alembic-only schema

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[database_design]], [[backend_architecture]],
  [[ADR-0002-technology-stack]], [[ADR-0003-layered-backend-architecture]]

## Context

[[database_design]] explicitly deferred the surrogate-key type "to implementation time".
M4 builds the persistence foundation, so the project-wide model conventions must be fixed
now — every future entity will inherit them, making these cross-cutting decisions worth
recording. We also need a firm rule on how the schema evolves.

## Decision

1. **Integer surrogate primary keys** (`IntIdMixin`: autoincrement `id`) are the default
   key convention. (UUIDs remain a per-entity option if a future entity needs
   externally-exposed or merge-safe ids; that would be noted on the entity.)
2. **Timestamp columns** `created_at` / `updated_at` are provided by a shared
   `TimestampMixin`, timezone-aware and database-populated (`server_default`/`onupdate`).
3. **Schema evolves exclusively through Alembic migrations.** The application never calls
   `Base.metadata.create_all()` at startup; startup only verifies connectivity.
4. **Deterministic constraint naming** via a `MetaData` naming convention on `Base`, so
   Alembic autogenerate yields stable, reviewable migrations.
5. **Transaction ownership:** the request-scoped session (`get_db`) does not auto-commit;
   services own the write boundary via a `transaction()` helper (aligns with
   [[backend_architecture]]).

## Options considered

- **Integer vs UUID keys:** integers are simpler, smaller, and sufficient for an
  internal analytics tool; UUIDs add value mainly for distributed/exposed ids — deferred,
  not adopted wholesale.
- **`create_all()` vs Alembic:** `create_all()` is convenient but drifts from real schema
  history and cannot express data/edits — rejected for anything but test scaffolding.
- **Auto-commit session vs service-owned transactions:** service-owned boundaries keep
  the persistence layer independent of business intent — chosen.

## Consequences

- **Positive:** consistent, predictable models; reviewable migrations; clean SQLite→
  PostgreSQL portability; persistence independent of business logic.
- **Negative / trade-offs:** integer keys are not globally unique (revisit per-entity if
  needed); every schema change requires a migration (intended discipline).
- **Follow-ups:** first business entities (M5+) subclass `BaseRepository` and add their
  own migrations.

## Notes
This ADR records conventions only; it does not alter the frozen architecture
([[architecture_state]]), it implements a detail [[database_design]] deferred to M4.
