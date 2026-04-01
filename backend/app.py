from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from models import Region as RegionModel
from models import Route as RouteModel
from models import RouteStation as RouteStationModel
from models import Station as StationModel
from models import TransportSystem as TransportSystemModel
from models import (
    db,
    route_regions,
    region_transport_systems,
    station_nearby_stations,
    station_connected_regions,
)
from schemas import ErrorResponse, Pagination
from schemas import Region as RegionSchema
from schemas import RegionsListResponse
from schemas import Route as RouteSchema
from schemas import RoutesListResponse
from schemas import Station as StationSchema
from schemas import StationsListResponse

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://railreach:railreach@localhost:5432/railreach",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

BASE_URL = "http://railreach.me"
API_BASE = "http://localhost:3001"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DATA_DIR = PROJECT_ROOT / "data"


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(",", "")
    if normalized.lower().endswith("million"):
        try:
            return int(float(normalized[:-7].strip()) * 1_000_000)
        except ValueError:
            return None

    normalized = normalized.replace("$", "").replace("%", "")
    try:
        return int(float(normalized))
    except ValueError:
        return None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(",", "").replace("%", "").replace("$", "")
    try:
        return float(normalized)
    except ValueError:
        return None


def _to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    text = str(value).strip()
    return [text] if text else []


def _to_region_codes(value: Any) -> list[str]:
    return [item.upper() for item in _to_list(value)]


def _slugify(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower())
    normalized = re.sub(r"-+", "-", normalized)
    return normalized.strip("-")


def _fallback_file_candidates(kind: str) -> tuple[Path, ...]:
    return (
        DATA_DIR / f"{kind}.json",
        DATA_DIR / "raw" / f"{kind}.json",
    )


def _load_fallback_records(kind: str) -> list[dict[str, Any]]:
    for path in _fallback_file_candidates(kind):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    return []


def _normalize_region_payload(
    record: dict[str, Any], fallback_id: int
) -> dict[str, Any]:
    code = str(record.get("code", "")).strip().upper()
    return {
        "id": _parse_int(record.get("id")) or fallback_id,
        "name": str(record.get("name") or code or f"Region {fallback_id}"),
        "code": code,
        "population": _parse_int(record.get("population")),
        "median_household_income": _parse_int(
            record.get("medianHouseholdIncome", record.get("median_household_income"))
        ),
        "no_vehicle_available_percent": _parse_float(
            record.get("noVehicleAvailablePercent", record.get("noVehicleAvailable"))
        ),
        "poverty_rate_percent": _parse_float(
            record.get("povertyRatePercent", record.get("povertyStatus"))
        ),
        "public_transportation_to_work": _to_list(
            record.get(
                "publicTransportationToWork",
                record.get("public_transportation_to_work"),
            )
        ),
        "image_url": record.get("imageUrl", record.get("image_url")),
        "wikipedia_url": record.get("wikipediaUrl", record.get("wikipedia_url")),
        "tourism_url": record.get("tourismUrl", record.get("tourism_url")),
        "twitter_url": record.get("twitterUrl", record.get("twitter_url")),
        "railroads_overview": record.get(
            "railroadsOverview", record.get("railroads_overview")
        ),
        "number_of_amtrak_stations": _parse_int(
            record.get(
                "numberOfAmtrakStations", record.get("number_of_amtrak_stations")
            )
        ),
        "number_of_amtrak_routes": _parse_int(
            record.get("numberOfAmtrakRoutes", record.get("number_of_amtrak_routes"))
        ),
        "updated_at": record.get("updatedAt", record.get("updated_at")),
    }


def _normalize_station_payload(
    record: dict[str, Any], fallback_id: int, region_ids_by_code: dict[str, int]
) -> dict[str, Any]:
    region_value = record.get(
        "regionCode", record.get("regionId", record.get("region_id"))
    )
    region_code: str | None = None
    region_id: int | None = None

    if (
        isinstance(region_value, str)
        and region_value.strip()
        and not region_value.strip().isdigit()
    ):
        region_code = region_value.strip().upper()
        region_id = region_ids_by_code.get(region_code)
    else:
        region_id = _parse_int(region_value)

    code = str(record.get("code") or f"ST{fallback_id}").strip().upper()
    return {
        "id": _parse_int(record.get("id")) or fallback_id,
        "name": str(record.get("name") or code),
        "code": code,
        "address": record.get("address"),
        "timezone": record.get("timezone"),
        "description": record.get("description"),
        "hours": record.get("hours"),
        "nearby_stations": _to_list(
            record.get("nearbyStations", record.get("nearby_stations"))
        ),
        "points_of_interest": _to_list(
            record.get("pointsOfInterest", record.get("points_of_interest"))
        ),
        "connected_destinations": _to_list(
            record.get("connectedDestinations", record.get("connected_destinations"))
        ),
        "image_url": record.get("imageUrl", record.get("image_url")),
        "region_id": region_id,
        "region_code": region_code,
        "routes_served_count": _parse_int(
            record.get("routesServedCount", record.get("routes_served_count"))
        ),
        "amtrak_url": record.get("amtrakUrl", record.get("amtrak_url")),
        "wikipedia_url": record.get("wikipediaUrl", record.get("wikipedia_url")),
        "facebook_url": record.get("facebookUrl", record.get("facebook_url")),
        "twitter_url": record.get("twitterUrl", record.get("twitter_url")),
        "poi_image_url": record.get("poiImageUrl", record.get("poi_image_url")),
        "poi_image_label": record.get("poiImageLabel", record.get("poi_image_label")),
        "history": record.get("history"),
        "updated_at": record.get("updatedAt", record.get("updated_at")),
    }


def _normalize_route_payload(
    record: dict[str, Any], fallback_id: int
) -> dict[str, Any]:
    name = str(record.get("name") or f"Route {fallback_id}")
    slug = str(record.get("slug") or _slugify(name))
    return {
        "id": _parse_int(record.get("id")) or fallback_id,
        "name": name,
        "major_stops": _to_list(record.get("majorStops", record.get("major_stops"))),
        "description": record.get("description"),
        "menu": _to_list(record.get("menu")),
        "travel_time_in_hours": record.get(
            "travelTimeInHours", record.get("travel_time_in_hours")
        ),
        "regions_spanned": _to_region_codes(
            record.get("regionsSpanned", record.get("regions_spanned"))
        ),
        "stations_served": _parse_int(
            record.get("stationsServed", record.get("stations_served"))
        ),
        "image_url": record.get("imageUrl", record.get("image_url")),
        "amtrak_url": record.get("amtrakUrl", record.get("amtrak_url")),
        "wikipedia_url": record.get("wikipediaUrl", record.get("wikipedia_url")),
        "youtube_url": record.get("youtubeUrl", record.get("youtube_url")),
        "updated_at": record.get("updatedAt", record.get("updated_at")),
        "slug": slug,
    }


@lru_cache(maxsize=1)
def _load_fallback_data() -> dict[str, list[dict[str, Any]]]:
    raw_regions = _load_fallback_records("regions")
    raw_stations = _load_fallback_records("stations")
    raw_routes = _load_fallback_records("routes")

    regions = [
        _normalize_region_payload(record, idx)
        for idx, record in enumerate(raw_regions, start=1)
    ]
    region_ids_by_code = {
        region["code"]: int(region["id"])
        for region in regions
        if region.get("code") and region.get("id") is not None
    }
    stations = [
        _normalize_station_payload(record, idx, region_ids_by_code)
        for idx, record in enumerate(raw_stations, start=1)
    ]
    routes = [
        _normalize_route_payload(record, idx)
        for idx, record in enumerate(raw_routes, start=1)
    ]

    return {
        "regions": regions,
        "stations": stations,
        "routes": routes,
    }


def _fallback_data_available() -> bool:
    data = _load_fallback_data()
    return bool(data["regions"] or data["stations"] or data["routes"])


def _paginate_items(items: list[dict[str, Any]], page: int, page_size: int):
    total_items = len(items)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = min(page, total_pages)
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_items, total_pages, page


def _fallback_list_response(
    endpoint: str,
    kind: str,
    schema_class: type[RegionSchema] | type[StationSchema] | type[RouteSchema],
    response_class: (
        type[RegionsListResponse]
        | type[StationsListResponse]
        | type[RoutesListResponse]
    ),
):
    page, page_size, extra = _get_pagination_params()
    records = _load_fallback_data().get(kind, [])

    sort_by = request.args.get("sortBy")
    direction = request.args.get("direction", "asc")

    if sort_by:

        def extract_minutes(t_str):
            if not t_str or not isinstance(t_str, str):
                return 0
            h = 0
            m = 0
            h_match = re.search(r"(\d+)\s*hour", t_str)
            if h_match:
                h = int(h_match.group(1))
            m_match = re.search(r"(\d+)\s*minute", t_str)
            if m_match:
                m = int(m_match.group(1))
            return h * 60 + m

        def sort_key(x):
            val = x.get(sort_by)
            if sort_by == "travel_time_in_hours":
                return extract_minutes(val)
            if sort_by == "stations_served" or sort_by == "number_of_amtrak_stations":
                return int(val) if val is not None else 0
            if val is None:
                return ""
            return str(val).lower()

        records = sorted(records, key=sort_key, reverse=(direction == "desc"))

    items, total_items, total_pages, page = _paginate_items(records, page, page_size)
    pagination_data = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "has_next_page": page < total_pages,
        "has_previous_page": page > 1,
        "links": _pagination_links(endpoint, page, page_size, total_pages, extra),
    }
    response = response_class(
        data=[schema_class.model_validate(item) for item in items],
        pagination=Pagination.model_validate(pagination_data),
    )
    return jsonify(response.model_dump(by_alias=True))


def _find_region_record(id_or_code: str, regions: list[dict[str, Any]]):
    parsed_id = _parse_int(id_or_code)
    target = id_or_code.strip().lower()
    for region in regions:
        if parsed_id is not None and region.get("id") == parsed_id:
            return region
        if str(region.get("code", "")).lower() == target:
            return region
        if str(region.get("name", "")).lower() == target:
            return region
    return None


def _find_station_record(id_or_code: str, stations: list[dict[str, Any]]):
    parsed_id = _parse_int(id_or_code)
    target = id_or_code.strip().lower()
    for station in stations:
        if parsed_id is not None and station.get("id") == parsed_id:
            return station
        if str(station.get("code", "")).lower() == target:
            return station
    return None


def _find_route_record(id_or_slug: str, routes: list[dict[str, Any]]):
    parsed_id = _parse_int(id_or_slug)
    target = id_or_slug.strip().lower()
    target_slug = _slugify(id_or_slug)
    for route in routes:
        if parsed_id is not None and route.get("id") == parsed_id:
            return route
        route_name = str(route.get("name", ""))
        route_slug = str(route.get("slug") or _slugify(route_name))
        if route_slug == target or route_slug == target_slug:
            return route
        if route_name.lower() == target:
            return route
    return None


def _station_matches_route(station: dict[str, Any], route: dict[str, Any]) -> bool:
    station_name = str(station.get("name", "")).lower()
    station_code = str(station.get("code", "")).lower()
    major_stops = [
        stop
        for stop in (str(item).lower() for item in route.get("major_stops", []))
        if len(stop) >= 4
        and stop not in {"amtrak", "train", "route", "travel", "enjoy", "take", "the"}
    ]
    if any(stop in station_name or station_name in stop for stop in major_stops):
        return True
    if station_code and any(stop == station_code for stop in major_stops):
        return True
    return False


def _fallback_region_instance(id_or_code: str):
    fallback = _load_fallback_data()
    region = _find_region_record(id_or_code, fallback["regions"])
    if region is None:
        return jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)), 404

    region_data = dict(region)
    region_code = str(region_data.get("code", "")).upper()
    region_data["linked_stations"] = [
        station
        for station in fallback["stations"]
        if station.get("region_code") == region_code
    ]
    region_data["linked_routes"] = [
        route
        for route in fallback["routes"]
        if region_code in route.get("regions_spanned", [])
    ]
    return jsonify(RegionSchema.model_validate(region_data).model_dump(by_alias=True))


def _fallback_station_instance(id_or_code: str):
    fallback = _load_fallback_data()
    station = _find_station_record(id_or_code, fallback["stations"])
    if station is None:
        return jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)), 404

    station_data = dict(station)
    region_code = station_data.get("region_code")
    route_slugs = {
        slug
        for slug in _to_list(
            station_data.get("routeSlugs", station_data.get("route_slugs", []))
        )
        if slug
    }

    if route_slugs:
        station_data["linked_routes"] = [
            route
            for route in fallback["routes"]
            if str(route.get("slug", "")) in route_slugs
        ]
    else:
        station_data["linked_routes"] = [
            route
            for route in fallback["routes"]
            if _station_matches_route(station_data, route)
        ]

    if not station_data["linked_routes"] and region_code:
        station_data["linked_routes"] = [
            route
            for route in fallback["routes"]
            if region_code in route.get("regions_spanned", [])
        ][:24]

    station_data["linked_region"] = next(
        (
            region
            for region in fallback["regions"]
            if str(region.get("code", "")).upper() == str(region_code).upper()
        ),
        None,
    )
    return jsonify(StationSchema.model_validate(station_data).model_dump(by_alias=True))


def _fallback_route_instance(id_or_slug: str):
    fallback = _load_fallback_data()
    route = _find_route_record(id_or_slug, fallback["routes"])
    if route is None:
        return jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)), 404

    route_data = dict(route)

    explicit_station_codes = {
        str(code).strip().upper()
        for code in _to_list(
            route_data.get("stationCodes", route_data.get("station_codes", []))
        )
        if str(code).strip()
    }

    if explicit_station_codes:
        matched_stations = [
            station
            for station in fallback["stations"]
            if str(station.get("code", "")).upper() in explicit_station_codes
        ]
    else:
        matched_stations = [
            station
            for station in fallback["stations"]
            if _station_matches_route(station, route_data)
        ]

    if not matched_stations:
        route_regions = set(route_data.get("regions_spanned", []))
        matched_stations = [
            station
            for station in fallback["stations"]
            if station.get("region_code") in route_regions
        ]
    route_data["linked_stations"] = matched_stations[:36]
    route_data["linked_regions"] = [
        region
        for region in fallback["regions"]
        if region.get("code") in route_data.get("regions_spanned", [])
    ]
    return jsonify(RouteSchema.model_validate(route_data).model_dump(by_alias=True))


def orm_to_dict(orm_obj: RegionModel | StationModel | RouteModel):
    base = {c.key: getattr(orm_obj, c.key) for c in orm_obj.__table__.columns}
    if isinstance(orm_obj, RegionModel):
        base["public_transportation_to_work"] = [
            t.name for t in orm_obj.transport_systems
        ]
    elif isinstance(orm_obj, StationModel):
        base["nearby_stations"] = [
            f"{s.name} ({s.code})" if s.code else s.name
            for s in orm_obj.nearby_station_refs
        ]
        base["points_of_interest"] = list(orm_obj.points_of_interest or [])
        base["connected_destinations"] = [
            r.name for r in orm_obj.connected_regions_refs
        ]
        if orm_obj.region:
            base["region_code"] = orm_obj.region.code
    elif isinstance(orm_obj, RouteModel):
        major_refs = sorted(
            (rs for rs in orm_obj.route_station_refs if rs.is_major),
            key=lambda rs: rs.sort_order if rs.sort_order is not None else 999,
        )
        base["major_stops"] = [rs.station.name for rs in major_refs]
        base["menu"] = list(orm_obj.menu or [])
        base["regions_spanned"] = [r.code for r in orm_obj.regions_refs]
        base["stations_served"] = len(orm_obj.route_station_refs) or None
    return base


def serialize(
    schema_class: type[RegionSchema] | type[StationSchema] | type[RouteSchema],
    obj: RegionModel | StationModel | RouteModel | dict[str, Any],
):
    data = orm_to_dict(obj) if hasattr(obj, "__table__") else obj
    return schema_class.model_validate(data).model_dump(by_alias=True)


def _extra_query_params(exclude: tuple[str, ...] = ("page", "pageSize")):
    parts = []
    for key, val in request.args.items():
        if key not in exclude and val:
            parts.append(f"&{key}={val}")
    return "".join(parts) if parts else ""


def _get_pagination_params():
    page = max(1, request.args.get("page", 1, type=int))
    page_size = max(1, min(100, request.args.get("pageSize", 10, type=int)))
    return page, page_size, _extra_query_params()


def _paginate_query(query: Any, page: int, page_size: int):
    total_items = query.count()
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = min(page, total_pages)
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total_items, total_pages, page


def _pagination_links(
    endpoint: str, page: int, page_size: int, total_pages: int, extra: str = ""
):
    def url(p):
        return f"{BASE_URL}{endpoint}?page={p}&pageSize={page_size}{extra}"

    return {
        "self_link": url(page),
        "next_link": url(page + 1) if page < total_pages else None,
        "previous": url(page - 1) if page > 1 else None,
        "first": url(1),
        "last": url(total_pages),
    }


def _paginated_response(
    endpoint: str,
    query: Any,
    schema_class: type[RegionSchema] | type[StationSchema] | type[RouteSchema],
    response_class: (
        type[RegionsListResponse]
        | type[StationsListResponse]
        | type[RoutesListResponse]
    ),
):
    page, page_size, extra = _get_pagination_params()
    items, total_items, total_pages, page = _paginate_query(query, page, page_size)
    pagination_data = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "has_next_page": page < total_pages,
        "has_previous_page": page > 1,
        "links": _pagination_links(endpoint, page, page_size, total_pages, extra),
    }
    response = response_class(
        data=[schema_class.model_validate(orm_to_dict(item)) for item in items],
        pagination=Pagination.model_validate(pagination_data),
    )
    return jsonify(response.model_dump(by_alias=True))

def _apply_fulltext_search(query: Any, model: Any, search_term: str):
    pattern = f"%{search_term}%"

    if model is StationModel:
        conditions = []
        for col in model.__table__.columns:
            if isinstance(col.type, (db.Text, db.String)):
                conditions.append(col.ilike(pattern))
        conditions.append(
            db.cast(StationModel.points_of_interest, db.Text).ilike(pattern)
        )
        region_match = db.session.query(RegionModel.id).filter(
            RegionModel.name.ilike(pattern)
        ).subquery()
        conditions.append(StationModel.region_id.in_(db.select(region_match)))
        route_match = db.session.query(RouteStationModel.station_id).join(
            RouteModel, RouteModel.id == RouteStationModel.route_id
        ).filter(RouteModel.name.ilike(pattern)).subquery()
        conditions.append(StationModel.id.in_(db.select(route_match)))
        nearby_match = db.session.query(station_nearby_stations.c.station_id).join(
            StationModel, StationModel.id == station_nearby_stations.c.nearby_station_id
        ).filter(StationModel.name.ilike(pattern)).subquery()
        conditions.append(model.id.in_(db.select(nearby_match)))
        connected_match = db.session.query(station_connected_regions.c.station_id).join(
            RegionModel, RegionModel.id == station_connected_regions.c.region_id
        ).filter(RegionModel.name.ilike(pattern)).subquery()
        conditions.append(model.id.in_(db.select(connected_match)))

        return query.filter(db.or_(*conditions))

    if model is RouteModel:
        conditions = []
        for col in model.__table__.columns:
            if isinstance(col.type, (db.Text, db.String)):
                conditions.append(col.ilike(pattern))
        conditions.append(
            db.cast(RouteModel.menu, db.Text).ilike(pattern)
        )
        region_match = db.session.query(route_regions.c.route_id).join(
            RegionModel, RegionModel.id == route_regions.c.region_id
        ).filter(RegionModel.name.ilike(pattern)).subquery()
        conditions.append(RouteModel.id.in_(db.select(region_match)))
        station_match = db.session.query(RouteStationModel.route_id).join(
            StationModel, StationModel.id == RouteStationModel.station_id
        ).filter(StationModel.name.ilike(pattern)).subquery()
        conditions.append(RouteModel.id.in_(db.select(station_match)))

        return query.filter(db.or_(*conditions))

    if model is RegionModel:
        conditions = []
        for col in model.__table__.columns:
            if isinstance(col.type, (db.Text, db.String)):
                conditions.append(col.ilike(pattern))
        transport_match = db.session.query(region_transport_systems.c.region_id).join(
            TransportSystemModel, TransportSystemModel.id == region_transport_systems.c.transport_system_id
        ).filter(TransportSystemModel.name.ilike(pattern)).subquery()
        conditions.append(RegionModel.id.in_(db.select(transport_match)))
        station_match = db.session.query(StationModel.region_id).filter(
            StationModel.name.ilike(pattern)
        ).subquery()
        conditions.append(RegionModel.id.in_(db.select(station_match)))
        route_match = db.session.query(route_regions.c.region_id).join(
            RouteModel, RouteModel.id == route_regions.c.route_id
        ).filter(RouteModel.name.ilike(pattern)).subquery()
        conditions.append(RegionModel.id.in_(db.select(route_match)))

        return query.filter(db.or_(*conditions))

    return query



def _apply_sorting_and_filtering(query: Any, model: Any, default_sort: str):
    new_query = query

    q = request.args.get("q")
    if q:
        new_query = _apply_fulltext_search(new_query, model, q)

    for column in model.__table__.columns:
        val = request.args.get(column.key)
        if val:
            if isinstance(column.type, (db.Text, db.String)):
                new_query = new_query.filter(column.ilike(f"%{val}%"))
            else:
                new_query = new_query.filter(column == val)
    sort_by = request.args.get("sortBy", default_sort)
    direction = request.args.get("direction", "asc")

    if model is RouteModel and sort_by == "stations_served":
        subq = (
            db.session.query(
                RouteStationModel.route_id,
                db.func.count(RouteStationModel.station_id).label("st_count"),
            )
            .group_by(RouteStationModel.route_id)
            .subquery()
        )
        new_query = new_query.outerjoin(subq, subq.c.route_id == RouteModel.id)
        col = db.func.coalesce(subq.c.st_count, 0)
        new_query = new_query.order_by(
            col.desc() if direction == "desc" else col.asc(), RouteModel.name.asc()
        )
        return new_query
    if model is RouteModel and sort_by == "travel_time_in_hours":
        hours = db.cast(
            db.func.substring(RouteModel.travel_time_in_hours, "^([0-9]+)"), db.Integer
        )
        new_query = new_query.order_by(
            hours.desc() if direction == "desc" else hours.asc(),
            RouteModel.name.asc(),
        )
        return new_query

    if hasattr(model, sort_by):
        col = getattr(model, sort_by)
        new_query = new_query.order_by(col.desc() if direction == "desc" else col.asc())
    return new_query

def _stringify_search_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(_stringify_search_value(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_stringify_search_value(v) for v in value)
    return str(value)

def _build_search_blob(payload: dict[str, Any]) -> str:
    return _stringify_search_value(payload).lower()

def _score_search_blob(blob: str, normalized_query: str, terms: list[str]) -> int:
    if not terms:
        return 0
    phrase_hits = blob.count(normalized_query) if normalized_query else 0
    term_hits = [blob.count(term) for term in terms]
    matched_terms = sum(1 for count in term_hits if count > 0)
    total_hits = sum(term_hits)
    if matched_terms == 0:
        return 0
    score = phrase_hits * 1000 + matched_terms * 120 + total_hits * 30
    if matched_terms == len(terms):
        score += 400
    return score

def _collect_search_items() -> list[dict[str, Any]]:
    try:
        regions = [
            RegionSchema.model_validate(orm_to_dict(region)).model_dump(by_alias=True)
            for region in RegionModel.query.all()
        ]
        stations = [
            StationSchema.model_validate(orm_to_dict(station)).model_dump(by_alias=True)
            for station in StationModel.query.all()
        ]
        routes = [
            RouteSchema.model_validate(orm_to_dict(route)).model_dump(by_alias=True)
            for route in RouteModel.query.all()
        ]
    except Exception:
        if not _fallback_data_available():
            raise
        fallback = _load_fallback_data()
        regions = [
            RegionSchema.model_validate(item).model_dump(by_alias=True)
            for item in fallback["regions"]
        ]
        stations = [
            StationSchema.model_validate(item).model_dump(by_alias=True)
            for item in fallback["stations"]
        ]
        routes = [
            RouteSchema.model_validate(item).model_dump(by_alias=True)
            for item in fallback["routes"]
        ]

    items: list[dict[str, Any]] = []
    items.extend({"modelType": "region", "item": region} for region in regions)
    items.extend({"modelType": "station", "item": station} for station in stations)
    items.extend({"modelType": "route", "item": route} for route in routes)
    return items

def _search_items(raw_query: str) -> list[dict[str, Any]]:
    terms = [term for term in re.findall(r"[a-z0-9]+", raw_query.lower()) if term]
    normalized_query = " ".join(terms)
    if not terms:
        return []

    scored: list[dict[str, Any]] = []
    for candidate in _collect_search_items():
        item = candidate["item"]
        score = _score_search_blob(_build_search_blob(item), normalized_query, terms)
        name = str(item.get("name", "")).lower()
        code = str(item.get("code", "")).lower()

        if normalized_query and normalized_query in name:
            score += 2200
        if terms and all(term in name for term in terms):
            score += 1200
        for term in terms:
            if name.startswith(term):
                score += 140
            elif term in name:
                score += 90
            if code and term == code:
                score += 320

        if score <= 0:
            continue
        scored.append(
            {
                "modelType": candidate["modelType"],
                "score": score,
                "item": item,
                "_name": name,
            }
        )

    scored.sort(key=lambda entry: (-entry["score"], entry["modelType"], entry["_name"]))
    for entry in scored:
        entry.pop("_name", None)
    return scored

@app.route("/api/search")
def search_site():
    raw_query = (request.args.get("q") or "").strip()
    page, page_size, extra = _get_pagination_params()

    results = _search_items(raw_query) if raw_query else []
    items, total_items, total_pages, page = _paginate_items(results, page, page_size)

    pagination_data = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "has_next_page": page < total_pages,
        "has_previous_page": page > 1,
        "links": _pagination_links("/api/search", page, page_size, total_pages, extra),
    }
    return jsonify(
        {
            "data": items,
            "pagination": Pagination.model_validate(pagination_data).model_dump(by_alias=True),
            "query": raw_query,
        }
    )

@app.route("/api/regions")
def list_regions():
    try:
        query = _apply_sorting_and_filtering(RegionModel.query, RegionModel, "name")
        return _paginated_response(
            "/api/regions", query, RegionSchema, RegionsListResponse
        )
    except Exception:
        if _fallback_data_available():
            return _fallback_list_response(
                "/api/regions", "regions", RegionSchema, RegionsListResponse
            )
        raise


@app.route("/api/regions/<id_or_code>")
def get_region(id_or_code: str):
    try:
        region = None
        try:
            rid = int(id_or_code)
            region = RegionModel.query.get(rid)
        except ValueError:
            region = RegionModel.query.filter(
                (RegionModel.code == id_or_code) | (RegionModel.name == id_or_code)
            ).first()

        if region is None:
            if _fallback_data_available():
                return _fallback_region_instance(id_or_code)
            return (
                jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)),
                404,
            )

        data = orm_to_dict(region)
        data["linked_stations"] = [orm_to_dict(s) for s in region.stations]
        data["linked_routes"] = [orm_to_dict(r) for r in region.routes.all()]
        return jsonify(RegionSchema.model_validate(data).model_dump(by_alias=True))
    except Exception:
        if _fallback_data_available():
            return _fallback_region_instance(id_or_code)
        raise


@app.route("/api/stations")
def list_stations():
    try:
        query = _apply_sorting_and_filtering(StationModel.query, StationModel, "name")
        return _paginated_response(
            "/api/stations", query, StationSchema, StationsListResponse
        )
    except Exception:
        if _fallback_data_available():
            return _fallback_list_response(
                "/api/stations", "stations", StationSchema, StationsListResponse
            )
        raise


@app.route("/api/stations/<id_or_code>")
def get_station(id_or_code: str):
    try:
        station = None
        try:
            sid = int(id_or_code)
            station = StationModel.query.get(sid)
        except ValueError:
            station = StationModel.query.filter(StationModel.code == id_or_code).first()

        if station is None:
            if _fallback_data_available():
                return _fallback_station_instance(id_or_code)
            return (
                jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)),
                404,
            )

        data = orm_to_dict(station)
        data["linked_routes"] = [orm_to_dict(rs.route) for rs in station.route_refs]
        if station.region:
            data["linked_region"] = orm_to_dict(station.region)
        else:
            data["linked_region"] = None
        return jsonify(StationSchema.model_validate(data).model_dump(by_alias=True))
    except Exception:
        if _fallback_data_available():
            return _fallback_station_instance(id_or_code)
        raise


@app.route("/api/routes")
def list_routes():
    try:
        query = _apply_sorting_and_filtering(RouteModel.query, RouteModel, "name")
        return _paginated_response(
            "/api/routes", query, RouteSchema, RoutesListResponse
        )
    except Exception:
        if _fallback_data_available():
            return _fallback_list_response(
                "/api/routes", "routes", RouteSchema, RoutesListResponse
            )
        raise


@app.route("/api/routes/<id_or_slug>")
def get_route(id_or_slug: str):
    try:
        route = None
        try:
            rid = int(id_or_slug)
            route = RouteModel.query.get(rid)
        except ValueError:
            slug = id_or_slug.replace("-", " ").lower()
            route = RouteModel.query.filter(
                db.func.lower(RouteModel.name) == slug
            ).first()

        if route is None:
            if _fallback_data_available():
                return _fallback_route_instance(id_or_slug)
            return (
                jsonify(ErrorResponse(error="Not found").model_dump(by_alias=True)),
                404,
            )

        data = orm_to_dict(route)
        major_refs = sorted(
            (rs for rs in route.route_station_refs if rs.is_major),
            key=lambda rs: rs.sort_order if rs.sort_order is not None else 999,
        )
        data["linked_stations"] = [orm_to_dict(rs.station) for rs in major_refs]
        data["linked_regions"] = [orm_to_dict(r) for r in route.regions_refs]
        return jsonify(RouteSchema.model_validate(data).model_dump(by_alias=True))
    except Exception:
        if _fallback_data_available():
            return _fallback_route_instance(id_or_slug)
        raise


def _render_ssr(path: str):
    env = os.environ.copy()
    env["NODE_ENV"] = "production"
    port = request.environ.get("SERVER_PORT") or os.environ.get("PORT", "8000")
    env["API_BASE"] = f"http://127.0.0.1:{port}"

    result = subprocess.run(
        ["node", "./backend/ssr-render.mjs", path],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=15,
        env=env,
    )
    if result.returncode != 0:
        logger.error(
            "SSR subprocess failed (code=%s): stderr=%s stdout=%s",
            result.returncode,
            result.stderr,
            result.stdout,
        )
        return "", {}

    try:
        data = json.loads(result.stdout.strip())
        return data.get("html", ""), data.get("dehydratedState", {})
    except json.JSONDecodeError as e:
        logger.error("SSR output not valid JSON: %s stdout=%s", e, result.stdout)
        return "", {}


def _serve_ssr_html(path: str):
    index_path = DIST_DIR / "index.html"
    if not index_path.exists():
        return "Build the frontend first: make build-frontend", 503

    template = index_path.read_text(encoding="utf-8")
    ssr_content, dehydrated_state = _render_ssr(path)

    try:
        rendered = render_template_string(
            template,
            ssr_content=ssr_content,
            dehydrated_state=dehydrated_state,
        )
    except Exception:
        return send_from_directory(str(DIST_DIR), "index.html")

    return (
        rendered,
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


@app.route("/")
def index():
    return _serve_ssr_html("/")


@app.route("/<path:path>")
def frontend(path: str):
    if path.startswith("api/"):
        return {"error": "Not found"}, 404
    static_extensions = {"js", "css", "ico", "svg", "png", "jpg", "jpeg", "webp"}
    if "." in path and path.rsplit(".", 1)[-1].lower() in static_extensions:
        file_path = DIST_DIR / path
        if file_path.exists() and file_path.is_file():
            dir_part = str(file_path.parent)
            name_part = file_path.name
            return send_from_directory(dir_part, name_part)
    return _serve_ssr_html("/" + path)


if __name__ == "__main__":
    print("DATABASE_URL:", os.environ.get("DATABASE_URL"))
    app.run(
        port=int(os.environ.get("PORT", "3001")),
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        threaded=True,
        host="0.0.0.0",
    )
