"""Vercel Python serverless entry for the read-only PricingLab API.

Copies the pre-seeded demo database (bundled next to this file) into the writable ``/tmp``
on cold start, then exposes the FastAPI app. Uploads are disabled, so the pandas/openpyxl
ingestion stack is never imported and the function stays small and fast.
"""

from __future__ import annotations

import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(_HERE)
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

# /tmp is the only writable path on the serverless filesystem.
_DB_PATH = "/tmp/pricinglab.db"
if not os.path.exists(_DB_PATH):
    shutil.copyfile(os.path.join(_HERE, "seed.sqlite"), _DB_PATH)

os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("ENABLE_UPLOADS", "false")
os.environ.setdefault("FILE_STORAGE_PATH", "/tmp/storage")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")

from app.main import app  # noqa: E402  (env + DB must be ready before the app is imported)

__all__ = ["app"]
