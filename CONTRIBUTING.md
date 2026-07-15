# Contributing Guide

This project follows a strict, documentation-first engineering workflow. The goal is
that **no architectural decision or implementation detail is ever lost.**

## The golden rule

> A change is not "done" when the code works. It is done when the code works, the
> tests pass, the docs and vault are updated, and the work is committed and pushed.

See the full [Definition of Done](../vault4/99-Standards/definition_of_done.md).

## Workflow (summary)

Every feature moves through these stages. The full description lives in
[`development_workflow.md`](../vault4/99-Standards/development_workflow.md).

```
Planning → Architecture Review → Implementation → Testing →
Documentation → Vault Sync → Git Commit → Push → Completion
```

## Local development

Two processes run side by side (the frontend dev server proxies `/api` to the backend):

| Stack | Directory | Setup | Run | Quality gate |
|-------|-----------|-------|-----|--------------|
| Backend | `backend/` | `pip install -e ".[dev]"` | `uvicorn app.main:app --reload` | `ruff check .` · `black --check .` · `mypy app` · `pytest` |
| Frontend | `frontend/` | `npm install` | `npm run dev` | `npm run lint` · `npm run typecheck` · `npm test` · `npm run build` |

A root [`Makefile`](Makefile) wraps both stacks (`make install`, `make lint`, `make typecheck`,
`make test`, `make build`, `make check`) so local commands match the CI jobs exactly. CI runs
the backend and frontend gates as two independent jobs (`.github/workflows/ci.yml`).

## Commit conventions

- Format: `type: short imperative summary` (Conventional Commits).
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `build`, `ci`.
- **One commit per completed milestone.** No micro-commits.
- Never rewrite published history. Never force-push unless explicitly instructed.
- Commits are authored by the local Git identity only — no external attribution.

## Branching

- `main` is always releasable.
- Feature work happens on `feat/<name>`, fixes on `fix/<name>`.
- Merge to `main` only after the Definition of Done is satisfied.

## Where things are documented

| Concern | Home |
|---------|------|
| Why a decision was made | ADR in `vault4/04-Decisions-ADR/` (mirrored to `docs/adr/`) |
| What is built and how it works | `vault4/07-Features/` |
| Current state of the system | `vault4/02-Architecture/architecture_state.md` |
| What was done in a work session | `vault4/06-Session-Logs/` |
| Known problems | `vault4/09-Bug-Reports/known_issues.md` |
| User-facing change history | `vault4/11-Changelog/changelog.md` |
