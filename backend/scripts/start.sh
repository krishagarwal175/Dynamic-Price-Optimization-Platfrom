#!/usr/bin/env sh
# Container entrypoint: bring the schema up to date, seed demo data on a fresh DB, then
# serve. Migrations run at start because the free tier has a single instance (no race).
set -e

echo "→ Applying database migrations…"
alembic upgrade head

echo "→ Seeding demo data (idempotent)…"
python scripts/seed.py || echo "  seed skipped/failed — continuing"

echo "→ Starting API on port ${PORT:-8000}…"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
