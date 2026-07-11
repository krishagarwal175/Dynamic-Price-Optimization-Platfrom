# ADR-0008: Core business data model (revises the v1 entity set)

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[database_design]], [[ADR-0003-layered-backend-architecture]],
  [[ADR-0007-persistence-conventions]]

## Context

M5 implements the concrete business data model. The frozen [[database_design]] v1 sketched
the core entities as **Dataset → Product → DemandRecord** plus result entities
(Elasticity/Forecast/Scenario…). The M5 requirement reframes the domain around
**Category, Product, HistoricalSale, Competitor**. This materially revises the frozen
transactional entity set, so per the freeze discipline it is recorded here.

## Decision

Adopt the following as the core business data model:

- **Category** 1─∞ **Product** 1─∞ **HistoricalSale**
- **Product** 1─∞ **CompetitorPrice** ∞─1 **Competitor**

Details:

1. **HistoricalSale** replaces/renames the v1 **DemandRecord** (observed quantity + unit
   price per date).
2. **Category** and **Competitor** are added; **CompetitorPrice** is introduced as the
   normalized association object required to express "competitor pricing per product"
   (avoids repeating competitor identity per observation).
3. **Dataset** is dropped from the core model for now (no upload/ingestion concept until a
   later milestone); the analytics/result entities (Elasticity/Forecast/Scenario/…) remain
   **deferred to their milestones**, unchanged.
4. **ORM models live in a new `app/models/` package** (persistence/entity models). This
   refines the [[ADR-0003-layered-backend-architecture]] module map: `app/domain/` stays
   reserved for framework-free logic (value objects, rules), while SQLAlchemy entities live
   in `app/models/`. Chosen over maintaining a duplicate pure-domain mirror, to stay
   professional-but-not-overengineered.
5. **Pydantic schemas** (`app/schemas/`) are separate DTOs (Create/Update/Read/Summary),
   independent of the ORM models.
6. Persistence conventions follow [[ADR-0007-persistence-conventions]] (integer keys,
   timestamp mixins, Alembic-only schema, service-owned transactions).

## Options considered

- **Keep the v1 Dataset/DemandRecord model** — but M5 explicitly requires
  Category/Competitor and a catalog-centric model; Dataset belongs with ingestion, not the
  core catalog.
- **Fold competitor prices onto the Competitor row** — denormalized; can't express
  per-product price history. Rejected in favor of the `CompetitorPrice` association object.
- **ORM models in `app/domain/`** — contradicts ADR-0003's framework-free domain. Rejected
  in favor of a dedicated `app/models/` package.

## Consequences

- **Positive:** clean, normalized (3NF) catalog model; clear separation of ORM entities,
  DTOs, and (future) pure domain logic; extensible.
- **Negative / trade-offs:** the v1 entity list in [[database_design]] is superseded for
  the core catalog (that doc now carries an amendment banner pointing here). Result and
  ingestion entities are still to come.
- **Follow-ups:** ingestion/dataset concept and analytics/result entities arrive in their
  roadmap milestones, each with migrations and (if architectural) their own ADR.

## Notes
This ADR revises the data model only; the broader frozen architecture
([[system_architecture]], layering, API conventions) is unchanged.
