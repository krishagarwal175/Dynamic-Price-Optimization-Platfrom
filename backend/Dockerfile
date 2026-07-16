# Production image for the PricingLab API (FastAPI + SQLAlchemy).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first (better layer caching), including the PostgreSQL driver.
COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts
RUN pip install --upgrade pip && pip install -e ".[prod]"

# Runtime storage for uploads (ephemeral on most hosts; the console is read-only).
ENV FILE_STORAGE_PATH=/tmp/storage
EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
