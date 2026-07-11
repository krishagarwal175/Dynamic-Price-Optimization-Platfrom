# Dynamic Pricing Optimization Platform

A platform for data-driven price optimization: it models demand elasticity, runs
pricing scenarios, and recommends revenue- or margin-optimal prices across a product
catalog.

> **Status:** Architecture frozen. Application implementation has not yet begun.
> This repository contains the engineering scaffold, the frozen architecture blueprint
> ([`docs/architecture/overview.md`](docs/architecture/overview.md) and
> [`docs/adr/`](docs/adr/)), and the documentation contract that all future work follows.
> Structural changes to the architecture require a new ADR.

---

## What this project is

| Layer | Responsibility |
|-------|----------------|
| **Frontend** (`frontend/`) | React application: catalog views, scenario simulator, pricing dashboards. |
| **Backend** (`backend/`) | FastAPI service exposing pricing, simulation, and catalog APIs. |
| **Pricing Engine** (`backend/app/pricing/`) | Elasticity modelling and price optimization logic. |
| **Docs** (`docs/`) | Repo-facing architecture, ADR mirror, and diagrams. |

## Repository layout

```
Dynamic-Pricing-Optimization-Platform/
├── backend/                 # FastAPI service + pricing engine
│   ├── app/
│   │   ├── api/             # HTTP route layer (endpoints)
│   │   ├── core/           # Config, settings, security, app wiring
│   │   ├── domain/         # Domain entities & business rules (framework-free)
│   │   ├── services/       # Application/use-case orchestration
│   │   ├── pricing/        # Elasticity + optimization engine
│   │   ├── repositories/   # Data-access layer (persistence boundary)
│   │   └── schemas/        # Pydantic request/response DTOs
│   └── tests/              # unit/ and integration/ suites
├── frontend/               # React application
│   └── src/
│       ├── components/     # Reusable presentational components
│       ├── features/       # Feature-scoped modules (state + UI + logic)
│       ├── pages/          # Route-level views
│       ├── services/       # API clients / data fetching
│       └── lib/            # Shared utilities and helpers
├── docs/                   # Repo-facing documentation
│   ├── architecture/       # Rendered architecture references
│   ├── adr/                # Committed mirror of accepted ADRs
│   └── diagrams/           # Exported diagrams / assets
├── data/                   # Sample datasets & fixtures (non-production)
├── scripts/                # Developer & operational scripts
├── deploy/                 # Dockerfiles, compose, infrastructure config
└── .github/workflows/      # CI/CD pipelines
```

## Engineering memory (the vault)

The authoritative engineering history — decisions, session logs, architecture state,
roadmap, audits, and research — lives in the **`vault4/`** Obsidian vault, a sibling
folder to this repository. The vault is **not** committed to Git; it is the local,
long-lived knowledge base. Every milestone in this repo must be reflected in the vault
per the [Definition of Done](../vault4/99-Standards/definition_of_done.md).

## Conventions

- Commits follow [Conventional Commits](https://www.conventionalcommits.org/).
- One commit per completed milestone — no micro-commits.
- Documentation and vault synchronization are part of "done," not an afterthought.
