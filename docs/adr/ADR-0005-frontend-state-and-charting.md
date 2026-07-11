# ADR-0005: Frontend state management and charting/table strategy

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[frontend_architecture]], [[ADR-0002-technology-stack]]

## Context

The frontend is a read-heavy analytics console: it fetches datasets and analysis/scenario
results and renders them as charts and tables, with some interactive forms (upload,
simulator inputs). We need a state and visualization approach that is modular, low-
ceremony, and easy to extend.

## Decision

- **Server state:** **TanStack Query** as the single source of truth for fetched data
  (caching, invalidation, loading/error).
- **Client/UI state:** **Zustand** for lightweight, feature-scoped UI state. No server
  data duplicated into client stores.
- **Charts:** **Recharts**, wrapped behind our own chart components.
- **Tables:** **TanStack Table** (headless) behind a shared `<DataTable>`.
- **Forms:** **React Hook Form + Zod**, with Zod schemas mirroring backend validation.
- **Styling/theme:** Tailwind CSS + CSS-variable theming for light/dark.

## Options considered

1. **TanStack Query + Zustand + Recharts + TanStack Table (chosen)** — clean separation of
   server vs client state; minimal boilerplate; declarative charts; headless tables.
2. **Redux Toolkit for everything** — powerful but heavyweight; conflates server cache
   with UI state; more ceremony than this app needs.
3. **Plain Context + fetch** — no dependencies, but hand-rolling caching/invalidation is
   error-prone and repetitive for a data-heavy UI.
4. **Chart library alternatives (Chart.js / D3 / Visx)** — D3/Visx are more flexible but
   more work; Recharts hits the simplicity/quality balance for standard dashboards.

## Consequences

- **Positive:** predictable data fetching, minimal boilerplate, swappable viz (libraries
  are wrapped), consistent theming.
- **Negative / trade-offs:** several libraries to learn; Recharts is less customizable
  than D3 for exotic visuals (acceptable; wrappers allow swapping later).
- **Follow-ups:** chart/table wrapper components defined in M10
  ([[implementation_roadmap]]).
