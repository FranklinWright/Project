"""Refactor schema: route stops->stations, regions/stations m2m, menu/poi arrays, destinations->regions

Revision ID: d5e6f7a8b9c4
Revises: b2c3d4e5f6a7
Create Date: 2026-03-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d5e6f7a8b9c4"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clear data so seed can repopulate with new structure (needed when migrating from pre-refactor)
    op.execute(sa.text("DELETE FROM route_menu_items"))
    op.execute(sa.text("DELETE FROM route_major_stops"))
    op.execute(sa.text("DELETE FROM station_points_of_interest"))
    op.execute(sa.text("DELETE FROM station_connected_destinations"))
    op.execute(sa.text("DELETE FROM station_nearby_stations"))
    op.execute(sa.text("DELETE FROM region_transport_systems"))
    op.execute(sa.text("DELETE FROM stations"))
    op.execute(sa.text("DELETE FROM routes"))
    op.execute(sa.text("DELETE FROM menu_items"))
    op.execute(sa.text("DELETE FROM points_of_interest"))
    op.execute(sa.text("DELETE FROM destinations"))
    op.execute(sa.text("DELETE FROM stops"))
    op.execute(sa.text("DELETE FROM transport_systems"))
    op.execute(sa.text("DELETE FROM regions"))

    # Drop old junction tables and tables (order matters for FKs)
    op.drop_table("route_menu_items")
    op.drop_table("route_major_stops")
    op.drop_table("station_points_of_interest")
    op.drop_table("station_connected_destinations")
    op.drop_table("menu_items")
    op.drop_table("points_of_interest")
    op.drop_table("destinations")
    op.drop_table("stops")

    # Add new columns
    op.add_column(
        "stations",
        sa.Column("points_of_interest", postgresql.ARRAY(sa.Text()), nullable=True),
    )
    op.add_column(
        "routes",
        sa.Column("menu", postgresql.ARRAY(sa.Text()), nullable=True),
    )

    # Remove old route columns
    op.drop_column("routes", "regions_spanned")
    op.drop_column("routes", "stations_served")

    # Create new junction tables
    op.create_table(
        "station_connected_regions",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("station_id", "region_id"),
    )
    op.create_table(
        "route_major_stations",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("route_id", "station_id"),
    )
    op.create_table(
        "route_regions",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("route_id", "region_id"),
    )
    op.create_table(
        "route_stations",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("route_id", "station_id"),
    )


def downgrade() -> None:
    op.drop_table("route_stations")
    op.drop_table("route_regions")
    op.drop_table("route_major_stations")
    op.drop_table("station_connected_regions")

    op.drop_column("routes", "menu")
    op.drop_column("stations", "points_of_interest")

    op.add_column("routes", sa.Column("stations_served", sa.Integer(), nullable=True))
    op.add_column("routes", sa.Column("regions_spanned", sa.Text(), nullable=True))

    op.create_table(
        "stops",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "destinations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "points_of_interest",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "station_connected_destinations",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("destination_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"]),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("station_id", "destination_id"),
    )
    op.create_table(
        "station_points_of_interest",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("point_of_interest_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["point_of_interest_id"], ["points_of_interest.id"]),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("station_id", "point_of_interest_id"),
    )
    op.create_table(
        "route_major_stops",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("stop_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["stop_id"], ["stops.id"]),
        sa.PrimaryKeyConstraint("route_id", "stop_id"),
    )
    op.create_table(
        "route_menu_items",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.PrimaryKeyConstraint("route_id", "menu_item_id"),
    )
