# Dynamic Pricing Optimization Platform

[![CI](https://github.com/krishagarwal175/Dynamic-Price-Optimization-Platfrom/actions/workflows/ci.yml/badge.svg)](https://github.com/krishagarwal175/Dynamic-Price-Optimization-Platfrom/actions/workflows/ci.yml)

A platform for data-driven price optimization: it models demand elasticity, runs
pricing scenarios, and recommends revenue- or margin-optimal prices across a product
catalog.

> **Status:** Version 1 — feature-complete and hardened. The backend provides a
> persistence layer, dataset ingestion, five pure deterministic analytics engines
> (financial metrics, price elasticity, demand forecasting, pricing optimization, scenario
> simulation), a reporting/export engine, and a catalog API — all behind a versioned REST
> API with a consistent response envelope. The frontend is a read-only React console over
> that API. Architecture is frozen; structural changes require a new ADR
> ([`docs/architecture/overview.md`](docs/architecture/overview.md), [`docs/adr/`](docs/adr/)).

---

## Quickstart

Prerequisites: **Python 3.11** and **Node 20**. The backend and frontend run as two
processes; the frontend dev server proxies `/api` to the backend on port 8000.

```bash
# Backend (terminal 1) — http://127.0.0.1:8000  (docs at /docs)
cd backend
python -m venv .venv && . .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload

# Frontend (terminal 2) — http://localhost:5173
cd frontend
npm install
npm run dev
```

A root [`Makefile`](Makefile) wraps both stacks so local commands match CI exactly:

```bash
make install      # backend deps + npm ci
make lint         # ruff + eslint
make typecheck    # mypy (strict) + tsc
make test         # pytest + vitest
make build        # frontend production build
make check        # everything above, the full local gate
```

---

## Deployment (Vercel)

The frontend is a static SPA and deploys to Vercel; the FastAPI backend is hosted
separately (Render / Railway / Fly / a VM). The two connect via one environment variable.

**Frontend → Vercel**

1. Import the GitHub repo in Vercel and set **Root Directory = `frontend`** (build config
   lives in [`frontend/vercel.json`](frontend/vercel.json): framework `vite`, output `dist`,
   SPA rewrite so deep links resolve).
2. Add an environment variable **`VITE_API_BASE_URL`** = your backend origin, e.g.
   `https://api.your-host.com` (the client appends `/api/v1`). See
   [`frontend/.env.example`](frontend/.env.example).
3. Deploy. Every push to `main` redeploys automatically.

   CLI alternative: `cd frontend && npx vercel --prod` (prompts for login the first time).

**Backend → any host**

Run the published container/app and set its config:

- `DATABASE_URL` — a PostgreSQL URL (SQLite is dev-only).
- `APP_ENV=production` — disables interactive docs.
- `CORS_ALLOWED_ORIGINS` — must include the Vercel origin, e.g.
  `https://your-app.vercel.app` (comma-separated; a `*` wildcard is rejected while
  credentials are enabled).

**Local development is unaffected:** with `VITE_API_BASE_URL` empty, the client uses
`/api/v1` and the Vite dev server proxies it to `http://127.0.0.1:8000`.

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
