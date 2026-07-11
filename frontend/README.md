# Frontend — Pricing Console

React application that provides the catalog views, scenario simulator, and pricing
dashboards. No application code has been implemented yet; this document defines the
intended structure so implementation stays consistent.

## Structure (`src/`)

| Directory | Responsibility |
|-----------|----------------|
| `components/` | Reusable, mostly-presentational UI building blocks. No feature-specific logic. |
| `features/` | Feature-scoped modules bundling their own UI, state, and logic (e.g. scenario simulator). |
| `pages/` | Route-level views that compose features and components. |
| `services/` | API clients and data-fetching logic that talk to the backend. |
| `lib/` | Shared, framework-agnostic utilities and helpers. |

## Principles

- Features are self-contained; cross-feature sharing goes through `components/` or `lib/`.
- `services/` is the only layer that knows how to reach the backend.
- Keep `components/` dumb and reusable; keep business rules in `features/`.
