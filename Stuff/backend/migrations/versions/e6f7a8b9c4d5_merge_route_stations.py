"""Merge route_major_stations into route_stations with is_major flag

Revision ID: e6f7a8b9c4d5
Revises: c4d5e6f7a8b9
Create Date: 2026-03-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e6f7a8b9c4d5"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to route_stations
    op.add_column(
        "route_stations",
        sa.Column("is_major", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "route_stations",
        sa.Column("sort_order", sa.Integer(), nullable=True),
    )

    # Update: set is_major=True and sort_order for rows that exist in route_major_stations
    op.execute(sa.text("""
        UPDATE route_stations rs
        SET is_major = true, sort_order = rms.sort_order
        FROM route_major_stations rms
        WHERE rs.route_id = rms.route_id AND rs.station_id = rms.station_id
    """))

    # Drop route_major_stations
    op.drop_table("route_major_stations")


def downgrade() -> None:
    # Recreate route_major_stations
    op.create_table(
        "route_major_stations",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("route_id", "station_id"),
    )

    # Copy major stops back
    op.execute(sa.text("""
        INSERT INTO route_major_stations (route_id, station_id, sort_order)
        SELECT route_id, station_id, COALESCE(sort_order, 0)
        FROM route_stations WHERE is_major = true
    """))

    # Drop new columns from route_stations
    op.drop_column("route_stations", "sort_order")
    op.drop_column("route_stations", "is_major")
