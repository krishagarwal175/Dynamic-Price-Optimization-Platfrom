"""initial empty baseline

Establishes the migration baseline for the schema. No tables yet — business entities are
introduced in later milestones, each via its own migration.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-11
"""

from __future__ import annotations

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
