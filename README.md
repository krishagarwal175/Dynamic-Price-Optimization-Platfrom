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

## Deployment

The frontend is a static SPA (Vercel); the FastAPI backend is hosted separately. The two
connect via one environment variable (`VITE_API_BASE_URL`).

### Free, no credit card — both tiers on Vercel

Render / Railway / Fly / Koyeb / Hugging Face now gate free compute behind a card or a quota.
The reliable free path runs **both** the frontend and the backend on Vercel (Hobby tier is
free, no card): the backend is a Python **serverless function** ([`backend/api/index.py`](backend/api/index.py))
serving the read-only API from a pre-seeded SQLite bundled in the deploy — no database
service, no card. Create **two Vercel projects** from the same repo:

**Backend project** (Root Directory = `backend`):
1. Vercel → Add New → Project → import the repo → set **Root Directory = `backend`**.
2. Vercel detects the Python function via [`backend/vercel.json`](backend/vercel.json)
   (routes all requests to `api/index.py`). Uploads are disabled here, so pandas isn't
   bundled and the function stays small; the demo data is already inside `api/seed.sqlite`.
3. Add env var **`CORS_ALLOWED_ORIGINS`** = your frontend URL (from the next project).
4. Deploy → your API is at `https://<backend-project>.vercel.app` (health at `/api/v1/health`).

**Frontend project** (Root Directory = `frontend`):
1. Vercel → Add New → Project → import the repo → set **Root Directory = `frontend`**.
2. Add env var **`VITE_API_BASE_URL`** = the backend URL from above.
3. Deploy. Then paste this frontend URL back into the backend project's
   `CORS_ALLOWED_ORIGINS` and redeploy the backend.

> The serverless backend's SQLite is read-only demo data (regenerated per cold start); great
> for a showcase. For persistent/writable data or dataset uploads, use the container path below.

### Container / managed (Render blueprint — requires a card on file)

**Frontend → Vercel**

1. Import the GitHub repo in Vercel and set **Root Directory = `frontend`** (build config
   lives in [`frontend/vercel.json`](frontend/vercel.json): framework `vite`, output `dist`,
   SPA rewrite so deep links resolve).
2. Add an environment variable **`VITE_API_BASE_URL`** = your backend origin, e.g.
   `https://api.your-host.com` (the client appends `/api/v1`). See
   [`frontend/.env.example`](frontend/.env.example).
3. Deploy. Every push to `main` redeploys automatically.

   CLI alternative: `cd frontend && npx vercel --prod` (prompts for login the first time).

**Backend → Render (Docker + Postgres)**

A one-click blueprint lives at [`render.yaml`](render.yaml) ([`backend/Dockerfile`](backend/Dockerfile)):

1. In Render → **New → Blueprint** → pick this repo. It provisions a free PostgreSQL
   database and the API web service, and wires `DATABASE_URL` automatically.
2. On first boot the container runs `alembic upgrade head` and an **idempotent demo seed**
   ([`backend/scripts/seed.py`](backend/scripts/seed.py)) — the dashboards come up populated.
3. Set **`CORS_ALLOWED_ORIGINS`** to your Vercel origin (e.g. `https://your-app.vercel.app`)
   and redeploy. `APP_ENV=production` (disables docs) and `FILE_STORAGE_PATH=/tmp/storage`
   are set by the blueprint.
4. Copy the service URL (e.g. `https://pricinglab-api.onrender.com`) into Vercel's
   `VITE_API_BASE_URL` and redeploy the frontend — the console is now live end-to-end.

Any Docker/Postgres host works the same way; the only required config is `DATABASE_URL`,
`APP_ENV=production`, and `CORS_ALLOWED_ORIGINS`.

**Local development is unaffected:** with `VITE_API_BASE_URL` empty, the client uses
`/api/v1` and the Vite dev server proxies it to `http://127.0.0.1:8000`; the backend still
defaults to SQLite.

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
