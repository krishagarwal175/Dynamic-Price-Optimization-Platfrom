"""Local filesystem implementation of :class:`FileStorage`."""

from __future__ import annotations

from pathlib import Path

from app.storage.base import StorageError


class LocalFileStorage:
    """Store blobs under a root directory. Keys are treated as relative paths.

    Keys are sanitized to stay within the root (no traversal outside it).
    """

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        target = (self._root / key).resolve()
        if self._root not in target.parents and target != self._root:
            raise StorageError(f"Refusing to access key outside storage root: {key!r}")
        return target

    def save(self, key: str, data: bytes) -> str:
        target = self._resolve(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target.as_uri()

    def read(self, key: str) -> bytes:
        target = self._resolve(key)
        try:
            return target.read_bytes()
        except FileNotFoundError as exc:
            raise StorageError(f"No object stored under key: {key!r}") from exc

    def delete(self, key: str) -> None:
        target = self._resolve(key)
        target.unlink(missing_ok=True)

    def exists(self, key: str) -> bool:
        return self._resolve(key).is_file()
