"""Storage abstraction.

Defines the storage contract so the rest of the application never hardcodes a backend.
Local filesystem is the only implementation in v1; object storage (e.g. S3) can be added
later behind the same protocol.
"""

from __future__ import annotations

from typing import Protocol


class StorageError(Exception):
    """Raised when a storage operation fails (e.g. missing key)."""


class FileStorage(Protocol):
    """A content-addressable-ish blob store keyed by an opaque string ``key``."""

    def save(self, key: str, data: bytes) -> str:
        """Persist ``data`` under ``key`` and return a storage URI for it."""
        ...

    def read(self, key: str) -> bytes:
        """Return the bytes stored under ``key``. Raises :class:`StorageError` if absent."""
        ...

    def delete(self, key: str) -> None:
        """Remove ``key`` if present (idempotent)."""
        ...

    def exists(self, key: str) -> bool:
        """Return whether ``key`` exists."""
        ...
