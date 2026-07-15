"""Ingestion error types.

Upload/parse failures are exceptions (they abort the request); data-quality problems are
returned as structured validation issues, not exceptions (see ``validation``).
"""

from __future__ import annotations


class IngestionError(Exception):
    """Base class for ingestion failures."""


class UnsupportedFileTypeError(IngestionError):
    """The uploaded file type is not supported."""


class ParsingError(IngestionError):
    """The file could not be parsed into a table."""
