"""add cuttings support

Revision ID: a1b2c3d4e5f6
Revises: 8c932c12fd37
Create Date: 2026-07-12 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "8c932c12fd37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "plant",
        sa.Column("kind", sa.String(), nullable=False, server_default="semi_hydro"),
    )
    op.add_column("plant", sa.Column("monitor_interval_days", sa.Integer(), nullable=True))
    op.add_column("plant", sa.Column("next_monitor_date", sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("plant", "next_monitor_date")
    op.drop_column("plant", "monitor_interval_days")
    op.drop_column("plant", "kind")
