"""rename order to sort_order in route_major_stops (PostgreSQL reserved word)

Revision ID: b2c3d4e5f6a7
Revises: 3a951eafb9c3
Create Date: 2026-03-10

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "3a951eafb9c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "route_major_stops",
        "order",
        new_column_name="sort_order",
    )


def downgrade() -> None:
    op.alter_column(
        "route_major_stops",
        "sort_order",
        new_column_name="order",
    )
