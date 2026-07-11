"""File storage abstraction and implementations."""

from __future__ import annotations

from app.storage.base import FileStorage, StorageError
from app.storage.local import LocalFileStorage

__all__ = ["FileStorage", "LocalFileStorage", "StorageError"]
