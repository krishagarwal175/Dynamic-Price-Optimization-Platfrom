"""Shared schema building blocks."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import ConfigDict, Field

# Non-negative money with fixed precision, mirroring the ORM ``Numeric(12, 2)`` columns.
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]

# ISO-4217-style 3-letter currency code.
CurrencyCode = Annotated[str, Field(min_length=3, max_length=3)]

# Input schemas reject unknown fields (strict boundary validation).
INPUT_CONFIG = ConfigDict(extra="forbid")

# Read schemas are populated from ORM objects.
ORM_CONFIG = ConfigDict(from_attributes=True)
