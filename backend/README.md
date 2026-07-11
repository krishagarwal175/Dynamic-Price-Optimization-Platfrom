# Backend — Pricing Service

FastAPI service that exposes the pricing, simulation, and catalog capabilities of the
platform. No application code has been implemented yet; this document defines the
intended structure so implementation stays consistent.

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
