# Developer entry point for the Dynamic Pricing Optimization Platform.
# Commands wrap the backend (Python/FastAPI) and frontend (React/Vite) stacks so local
# validation matches the CI jobs exactly. Run `make help` for the list.

BACKEND := backend
FRONTEND := frontend

.DEFAULT_GOAL := help

.PHONY: help install install-backend install-frontend \
        dev-backend dev-frontend \
        lint typecheck test build check \
        lint-backend typecheck-backend test-backend \
        lint-frontend typecheck-frontend test-frontend build-frontend

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install backend + frontend dependencies

install-backend: ## Install backend dependencies (editable, with dev extras)
	cd $(BACKEND) && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies (reproducible)
	cd $(FRONTEND) && npm ci

dev-backend: ## Run the backend dev server (http://127.0.0.1:8000)
	cd $(BACKEND) && uvicorn app.main:app --reload

dev-frontend: ## Run the frontend dev server (http://localhost:5173)
	cd $(FRONTEND) && npm run dev

# --- Aggregate quality gates (mirror CI) -----------------------------------

lint: lint-backend lint-frontend ## Lint both stacks
typecheck: typecheck-backend typecheck-frontend ## Type-check both stacks
test: test-backend test-frontend ## Test both stacks
build: build-frontend ## Build the frontend production bundle

check: lint typecheck test build ## Run the full local validation gate

# --- Backend ---------------------------------------------------------------

lint-backend:
	cd $(BACKEND) && ruff check . && black --check .

typecheck-backend:
	cd $(BACKEND) && mypy app

test-backend:
	cd $(BACKEND) && pytest

# --- Frontend --------------------------------------------------------------

lint-frontend:
	cd $(FRONTEND) && npm run lint

typecheck-frontend:
	cd $(FRONTEND) && npm run typecheck

test-frontend:
	cd $(FRONTEND) && npm test

build-frontend:
	cd $(FRONTEND) && npm run build
