# ADR-0004: Deterministic, framework-independent analytics engine (no ML in v1)

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[analytics_architecture]], [[ADR-0003-layered-backend-architecture]],
  [[testing_strategy]]

## Context

The core value is pricing analytics: elasticity, forecasting, optimization, break-even,
scenarios, and financial metrics. We must decide the modelling approach and where this
logic lives. The project prioritizes maintainability, testability, explainability, and
interview value, and wants to avoid unnecessary complexity in v1.

## Decision

The analytics engine will be **deterministic and framework-independent**:

- **Deterministic classical methods** in v1 (log-log regression for elasticity; moving
  average / linear trend / seasonal-naive for forecasting; analytic or bounded-search
  optimization). **No trained ML models in v1.**
- The engine is **pure**: no I/O, no DB, no framework, no hidden state; it consumes plain
  data and returns plain results.
- Forecasting and optimization use a **strategy pattern** so alternative methods
  (including a future ML forecaster) plug in behind the same interface.

## Options considered

1. **Deterministic classical analytics, pure engine (chosen)** — explainable, testable
   against closed-form answers, reproducible, fast; strong interview narrative.
2. **ML-based forecasting/elasticity now** — potentially more accurate on rich data, but
   adds training pipelines, model storage, non-determinism, and heavy deps — premature for
   v1 and harder to validate.
3. **Analytics embedded in services/endpoints** — less indirection, but couples math to
   the web/DB and destroys testability and reuse.

## Consequences

- **Positive:** results are explainable and auditable; sub-engines unit-tested with known
  answers; engine is portable (CLI/worker/API); simple to reason about.
- **Negative / trade-offs:** classical methods may underperform ML on complex demand
  patterns — accepted for v1 and mitigated by the strategy seam for later ML.
- **Follow-ups:** ML forecaster / model registry are documented future extensions
  ([[database_design]] extensibility, [[future_roadmap]]), each requiring a new ADR.
