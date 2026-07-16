---
title: PricingLab API
emoji: 📈
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# PricingLab API

Backend for the PricingLab console — a FastAPI service with pure, deterministic pricing
analytics engines (financial metrics, elasticity, forecasting, optimization, simulation,
reporting). Runs on SQLite with a seed-on-boot so the endpoints return real data.

Health: `/api/v1/health` · Interactive docs are disabled in production.

> This `README.md` and the sibling `Dockerfile` are the only two files this Space needs;
> the backend source is cloned from the public GitHub repository at build time.
