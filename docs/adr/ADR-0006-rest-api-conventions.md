# ADR-0006: REST API conventions, versioning, and response/error envelope

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[api_design]], [[backend_architecture]]

## Context

The frontend and backend need a stable, predictable contract. We must fix the API style,
how it is versioned, and the shape of successful and error responses so the frontend can
handle them uniformly and the API can evolve without breaking clients.

## Decision

- **Style:** REST/JSON under a versioned base path **`/api/v1`** (URI versioning).
- **Success envelope:** `{ "data": …, "meta": { requestId, timestamp, [pagination] } }`.
- **Error envelope:** `{ "error": { code, message, details? }, "meta": {…} }`, produced by
  a single central error handler; internal details/stack traces never exposed.
- **Evolution:** within a major version, only additive/backward-compatible changes; any
  breaking change → `/api/v2` + a new ADR.
- **Resources:** plural nouns, nested sub-resources, verbs only for non-CRUD actions
  (`/scenarios/{id}/run`).

## Options considered

1. **URI versioning + consistent envelope (chosen)** — visible, simple, easy to route and
   cache; envelope gives the frontend one shape to handle.
2. **Header-based versioning** — cleaner URLs, but less visible/testable and easy to get
   wrong with caches/proxies.
3. **No envelope (bare resources)** — less nesting, but inconsistent error handling and no
   natural place for `meta`/pagination/correlation IDs.
4. **GraphQL** — flexible querying, but overkill for a small, well-known set of analytics
   resources; adds tooling and caching complexity.

## Consequences

- **Positive:** uniform client handling; clear evolution path; correlation IDs and
  pagination have a home; simple to document and test.
- **Negative / trade-offs:** slight payload verbosity from the envelope; discipline needed
  to keep `v1` additive-only.
- **Follow-ups:** envelope + error hierarchy implemented with the app shell in M2
  ([[implementation_roadmap]]).
