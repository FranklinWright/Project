"""SQLAlchemy models for RailReach API."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------------------------------------------------------------------------
# Lookup / entity tables
# ---------------------------------------------------------------------------


class TransportSystem(db.Model):
    """Public transportation systems (e.g. BART, CTA)."""

    __tablename__ = "transport_systems"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False, unique=True)


# ---------------------------------------------------------------------------
# Junction / association tables
# ---------------------------------------------------------------------------

region_transport_systems = db.Table(
    "region_transport_systems",
    db.Column("region_id", db.Integer, db.ForeignKey("regions.id"), primary_key=True),
    db.Column(
        "transport_system_id",
        db.Integer,
        db.ForeignKey("transport_systems.id"),
        primary_key=True,
    ),
)

station_nearby_stations = db.Table(
    "station_nearby_stations",
    db.Column("station_id", db.Integer, db.ForeignKey("stations.id"), primary_key=True),
    db.Column(
        "nearby_station_id",
        db.Integer,
        db.ForeignKey("stations.id"),
        primary_key=True,
    ),
)

station_connected_regions = db.Table(
    "station_connected_regions",
    db.Column("station_id", db.Integer, db.ForeignKey("stations.id"), primary_key=True),
    db.Column("region_id", db.Integer, db.ForeignKey("regions.id"), primary_key=True),
)

route_regions = db.Table(
    "route_regions",
    db.Column("route_id", db.Integer, db.ForeignKey("routes.id"), primary_key=True),
    db.Column("region_id", db.Integer, db.ForeignKey("regions.id"), primary_key=True),
)


class RouteStation(db.Model):
    """Junction: routes to stations with is_major and sort_order for major stops."""

    __tablename__ = "route_stations"

    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), primary_key=True)
    is_major = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, nullable=True)

    route = db.relationship("Route", backref=db.backref("route_station_refs", lazy="joined"))
    station = db.relationship("Station", backref=db.backref("route_refs", lazy="dynamic"))


# ---------------------------------------------------------------------------
# Main models
# ---------------------------------------------------------------------------


class Region(db.Model):
    __tablename__ = "regions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    code = db.Column(db.Text(), nullable=False)
    population = db.Column(db.Integer)
    median_household_income = db.Column(db.Integer)
    no_vehicle_available_percent = db.Column(db.Float)
    poverty_rate_percent = db.Column(db.Float)
    image_url = db.Column(db.Text())
    wikipedia_url = db.Column(db.Text())
    tourism_url = db.Column(db.Text())
    twitter_url = db.Column(db.Text())
    railroads_overview = db.Column(db.Text())
    number_of_amtrak_stations = db.Column(db.Integer)
    number_of_amtrak_routes = db.Column(db.Integer)
    updated_at = db.Column(db.Text())

    transport_systems = db.relationship(
        "TransportSystem",
        secondary=region_transport_systems,
        backref=db.backref("regions", lazy="dynamic"),
        lazy="joined",
    )


class Station(db.Model):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    code = db.Column(db.Text(), nullable=False)
    address = db.Column(db.Text())
    timezone = db.Column(db.Text())
    description = db.Column(db.Text)
    hours = db.Column(db.Text())
    image_url = db.Column(db.Text())
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"))
    region = db.relationship("Region", backref="stations")
    routes_served_count = db.Column(db.Integer)
    amtrak_url = db.Column(db.Text())
    wikipedia_url = db.Column(db.Text())
    facebook_url = db.Column(db.Text())
    twitter_url = db.Column(db.Text())
    poi_image_url = db.Column(db.Text())
    poi_image_label = db.Column(db.Text())
    history = db.Column(db.Text())
    updated_at = db.Column(db.Text())
    points_of_interest = db.Column(db.ARRAY(db.Text), nullable=True)

    nearby_station_refs = db.relationship(
        "Station",
        secondary=station_nearby_stations,
        primaryjoin=(station_nearby_stations.c.station_id == id),
        secondaryjoin=(station_nearby_stations.c.nearby_station_id == id),
        backref=db.backref("nearby_to_stations", lazy="dynamic"),
        lazy="joined",
    )
    connected_regions_refs = db.relationship(
        "Region",
        secondary=station_connected_regions,
        backref=db.backref("stations_connected_to", lazy="dynamic"),
        lazy="joined",
    )


class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text)
    travel_time_in_hours = db.Column(db.Text())
    image_url = db.Column(db.Text())
    amtrak_url = db.Column(db.Text())
    wikipedia_url = db.Column(db.Text())
    youtube_url = db.Column(db.Text())
    updated_at = db.Column(db.Text())
    menu = db.Column(db.ARRAY(db.Text), nullable=True)

    regions_refs = db.relationship(
        "Region",
        secondary=route_regions,
        backref=db.backref("routes", lazy="dynamic"),
        lazy="joined",
    )
    # route_station_refs: list of RouteStation (has .station, .is_major, .sort_order)
