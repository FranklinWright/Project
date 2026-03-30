#!/usr/bin/env python3
"""Seed RailReach PostgreSQL database from scraped JSON files.

Uses the Flask backend models and DATABASE_URL. Run migrations first (make migrate).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRAPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "backend"))
sys.path.insert(0, str(_SCRAPE_DIR))

from python.common import (log_error, log_info, log_warn,
                           parse_currency_to_int, parse_percent_to_float,
                           parse_population_to_int, resolve_output_path,
                           to_list)

DEFAULT_STATIONS = "data/raw/stations.json"
DEFAULT_ROUTES = "data/raw/routes.json"
DEFAULT_REGIONS = "data/raw/regions.json"
load_dotenv()
DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://railreach:railreach@localhost:5432/railreach",
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed RailReach database from scraped JSON files (uses Flask backend + PostgreSQL)"
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="PostgreSQL connection URL",
    )
    parser.add_argument("--stations-file", default=DEFAULT_STATIONS)
    parser.add_argument("--routes-file", default=DEFAULT_ROUTES)
    parser.add_argument("--regions-file", default=DEFAULT_REGIONS)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding (keeps schema)",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected list payload in {path}")

    return [item for item in payload if isinstance(item, dict)]


def parse_region_codes(regions_spanned: Any) -> list[str]:
    """Parse regionsSpanned from list or comma-separated string."""
    if isinstance(regions_spanned, list):
        return [str(c).strip().upper() for c in regions_spanned if c]
    s = str(regions_spanned or "")
    return [item.strip().upper() for item in s.split(",") if item.strip()]


def parse_station_codes(station_codes: Any) -> list[str]:
    """Parse stationCodes from list or comma-separated string."""
    if isinstance(station_codes, list):
        return [str(code).strip().upper() for code in station_codes if str(code).strip()]
    text = str(station_codes or "")
    return [item.strip().upper() for item in text.split(",") if item.strip()]


def slugify(text: str) -> str:
    """Generate a simple URL slug for route name matching."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def parse_nearby_code(entry: str) -> str | None:
    """Extract station code from 'Name (CODE)' or 'CODE' format."""
    match = re.search(r"\(([A-Za-z0-9]+)\)\s*$", str(entry).strip())
    if match:
        return match.group(1).upper()
    s = str(entry).strip().upper()
    return s if len(s) >= 2 and len(s) <= 6 else None


def parse_destination_region_code(entry: str) -> str | None:
    """Extract state/region code from 'City, ST' or 'City, State' format."""
    parts = [p.strip() for p in str(entry).split(",") if p.strip()]
    if not parts:
        return None
    last = parts[-1].upper()
    if len(last) == 2:
        return last
    return None


def infer_station_route_links(
    station_payloads: list[dict[str, Any]],
    route_payloads: list[dict[str, Any]],
) -> dict[str, set[str]]:
    """Map station code -> set of route names that serve it."""
    route_metadata: list[dict[str, Any]] = []
    for route in route_payloads:
        route_name = str(route.get("name", "")).strip()
        if not route_name:
            continue

        explicit_station_codes = set(
            parse_station_codes(route.get("stationCodes", route.get("station_codes", [])))
        )
        route_slug = str(route.get("slug") or "").strip().lower() or slugify(route_name)
        route_stops = [
            str(stop).strip().lower()
            for stop in to_list(route.get("majorStops", []))
            if str(stop).strip()
        ]
        route_metadata.append(
            {
                "name": route_name,
                "slug": route_slug,
                "station_codes": explicit_station_codes,
                "major_stops": route_stops,
            }
        )

    links: dict[str, set[str]] = {}
    for station in station_payloads:
        station_code = str(station.get("code", "")).upper().strip()
        if not station_code:
            continue

        station_name = str(station.get("name", "")).lower()
        destinations = [str(item).lower() for item in to_list(station.get("connectedDestinations", []))]
        station_route_slugs = {
            str(slug).strip().lower()
            for slug in to_list(station.get("routeSlugs", station.get("route_slugs", [])))
            if str(slug).strip()
        }

        station_links: set[str] = set()
        for route in route_metadata:
            route_name = str(route["name"])
            route_stops = list(route["major_stops"])

            if station_code in route["station_codes"]:
                station_links.add(route_name)
                continue

            if station_route_slugs and route["slug"] in station_route_slugs:
                station_links.add(route_name)
                continue

            if any(stop and stop in station_name for stop in route_stops):
                station_links.add(route_name)
                continue

            if any(
                stop and any(stop in dest for dest in destinations)
                for stop in route_stops
            ):
                station_links.add(route_name)
                continue
                database_url = normalize_database_url(str(args.database_url))
                if database_url.startswith("sqlite"):
                    log_error("This script requires PostgreSQL. Use DATABASE_URL or --database-url.")
                    return 1

            if route_name.lower() in station_name:
                station_links.add(route_name)

        links[station_code] = station_links

    return links


def main() -> int:
    args = parse_args()

    database_url = normalize_database_url(str(args.database_url))
    if database_url.startswith("sqlite"):
        log_error("This script requires PostgreSQL. Use DATABASE_URL or --database-url.")
        return 1

    # Ensure backend app/model imports see the selected DB URL.
    os.environ["DATABASE_URL"] = database_url

    from app import app
    from models import (Region, Route, RouteStation, Station, TransportSystem,
                        db, region_transport_systems, route_regions,
                        station_connected_regions, station_nearby_stations)
    from sqlalchemy import delete, text

    repo_root = Path(__file__).resolve().parents[2]
    stations_path = resolve_output_path(repo_root, args.stations_file)
    routes_path = resolve_output_path(repo_root, args.routes_file)
    regions_path = resolve_output_path(repo_root, args.regions_file)

    stations_payload = load_json_list(stations_path)
    routes_payload = load_json_list(routes_path)
    regions_payload = load_json_list(regions_path)


    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    log_info(f"Using database: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    inserted = {"regions": 0, "routes": 0, "stations": 0}
    updated = {"regions": 0, "routes": 0, "stations": 0}

    with app.app_context():
        if args.clear:
            log_warn("Clearing existing data")
            db.session.execute(delete(RouteStation))
            db.session.execute(delete(route_regions))
            db.session.execute(delete(station_nearby_stations))
            db.session.execute(delete(station_connected_regions))
            db.session.execute(delete(region_transport_systems))
            db.session.execute(delete(Station))
            db.session.execute(delete(Route))
            db.session.execute(delete(TransportSystem))
            db.session.execute(delete(Region))
            db.session.commit()

        for table, col in [("regions", "id"), ("stations", "id"), ("routes", "id")]:
            db.session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), "
                    f"COALESCE((SELECT MAX({col}) FROM {table}), 1))"
                )
            )

        regions_by_code: dict[str, Region] = {}
        routes_by_name: dict[str, Route] = {}
        stations_by_code: dict[str, Station] = {}

        if not any(str(r.get("code", "")).upper() == "UNK" for r in regions_payload):
            regions_payload.append(
                {
                    "name": "Unknown",
                    "code": "UNK",
                    "population": "0",
                    "medianHouseholdIncome": "$0",
                    "noVehicleAvailable": "0.0%",
                    "povertyStatus": "0.0%",
                    "publicTransportationToWork": [],
                    "imageUrl": "",
                    "wikipediaUrl": "",
                    "tourismUrl": "",
                    "twitterUrl": None,
                    "railroadsOverview": "",
                    "numberOfAmtrakStations": 0,
                    "numberOfAmtrakRoutes": 0,
                }
            )

        for payload in regions_payload:
            code = str(payload.get("code", "")).strip().upper()
            if not code:
                continue

            region = Region.query.filter_by(code=code).first()
            created = region is None
            if region is None:
                region = Region(code=code)
                db.session.add(region)

            region.name = str(payload.get("name", code))
            region.population = parse_population_to_int(payload.get("population"))
            region.median_household_income = parse_currency_to_int(
                payload.get("medianHouseholdIncome")
            )
            region.no_vehicle_available_percent = parse_percent_to_float(
                payload.get("noVehicleAvailable")
            )
            region.poverty_rate_percent = parse_percent_to_float(payload.get("povertyStatus"))
            region.image_url = str(payload.get("imageUrl", "") or "")
            region.wikipedia_url = str(payload.get("wikipediaUrl", "") or "")
            region.tourism_url = str(payload.get("tourismUrl", "") or "")
            region.twitter_url = (
                str(payload["twitterUrl"]) if payload.get("twitterUrl") else None
            )
            region.railroads_overview = str(payload.get("railroadsOverview", "") or "")
            region.number_of_amtrak_stations = int(
                payload.get("numberOfAmtrakStations", 0) or 0
            )
            region.number_of_amtrak_routes = int(
                payload.get("numberOfAmtrakRoutes", 0) or 0
            )

            transport_names = [
                str(t).strip()
                for t in to_list(payload.get("publicTransportationToWork", []))
                if str(t).strip()
            ]
            transport_objs = []
            for tname in transport_names:
                ts = TransportSystem.query.filter_by(name=tname).first()
                if ts is None:
                    ts = TransportSystem(name=tname)
                    db.session.add(ts)
                transport_objs.append(ts)
            region.transport_systems = transport_objs

            regions_by_code[code] = region
            if created:
                inserted["regions"] += 1
            else:
                updated["regions"] += 1

        valid_region_codes = set(regions_by_code.keys())

        for payload in routes_payload:
            name = str(payload.get("name", "")).strip()
            if not name:
                continue

            route = Route.query.filter_by(name=name).first()
            created = route is None
            if route is None:
                route = Route(name=name)
                db.session.add(route)

            route.description = str(payload.get("description", "") or "")
            route.travel_time_in_hours = str(
                payload.get("travelTimeInHours", "Unknown") or "Unknown"
            )
            route.image_url = str(payload.get("imageUrl", "") or "")
            route.amtrak_url = str(payload.get("amtrakUrl", "") or "")
            route.wikipedia_url = str(payload.get("wikipediaUrl", "") or "")
            route.youtube_url = (
                str(payload["youtubeUrl"]) if payload.get("youtubeUrl") else None
            )
            menu = to_list(payload.get("menu", []))
            route.menu = [str(m) for m in menu] if menu else None

            routes_by_name[name] = route
            if created:
                inserted["routes"] += 1
            else:
                updated["routes"] += 1

        db.session.flush()

        for payload in routes_payload:
            name = str(payload.get("name", "")).strip()
            route = routes_by_name.get(name)
            if route is None:
                continue

            region_codes = parse_region_codes(
                payload.get("regionsSpanned", payload.get("regions_spanned", []))
            )
            route.regions_refs = [
                regions_by_code[c] for c in region_codes if c in regions_by_code
            ]

        for payload in stations_payload:
            code = str(payload.get("code", "")).strip().upper()
            if not code:
                continue

            region_code = str(
                payload.get("regionId", payload.get("regionCode", payload.get("region_id", "")))
            ).strip().upper()
            if region_code not in valid_region_codes:
                region_code = "UNK"
            region = regions_by_code.get(region_code)

            station = Station.query.filter_by(code=code).first()
            created = station is None
            if station is None:
                station = Station(code=code)
                db.session.add(station)

            station.name = str(payload.get("name", code))
            station.address = str(payload.get("address", "") or "")
            station.timezone = str(payload.get("timezone", "") or "")
            station.description = str(payload.get("description", "") or "")
            station.hours = str(payload.get("hours", "") or "")
            station.image_url = str(payload.get("imageUrl", "") or "")
            station.region_id = region.id if region else None
            station.routes_served_count = int(
                payload.get("routesServedCount", payload.get("routes_served_count", 0)) or 0
            )
            station.amtrak_url = str(payload.get("amtrakUrl", "") or "")
            station.wikipedia_url = str(payload.get("wikipediaUrl", "") or "")
            station.facebook_url = (
                str(payload["facebookUrl"]) if payload.get("facebookUrl") else None
            )
            station.twitter_url = (
                str(payload["twitterUrl"]) if payload.get("twitterUrl") else None
            )
            station.poi_image_url = str(payload.get("poiImageUrl", "") or "")
            station.poi_image_label = str(payload.get("poiImageLabel", "") or "")
            station.history = str(payload.get("history", "") or "")
            poi = to_list(payload.get("pointsOfInterest", []))
            station.points_of_interest = [str(p) for p in poi] if poi else None

            stations_by_code[code] = station
            if created:
                inserted["stations"] += 1
            else:
                updated["stations"] += 1

        db.session.flush()

        for payload in stations_payload:
            code = str(payload.get("code", "")).upper().strip()
            station = stations_by_code.get(code)
            if station is None:
                continue

            nearby_codes = []
            for entry in to_list(payload.get("nearbyStations", [])):
                c = parse_nearby_code(entry)
                if c and c != code and c in stations_by_code:
                    nearby_codes.append(c)

            station.nearby_station_refs = [
                stations_by_code[c] for c in nearby_codes
            ]

        for payload in stations_payload:
            code = str(payload.get("code", "")).upper().strip()
            station = stations_by_code.get(code)
            if station is None:
                continue

            region_codes = []
            for entry in to_list(payload.get("connectedDestinations", [])):
                c = parse_destination_region_code(entry)
                if c and c in regions_by_code:
                    region_codes.append(c)

            station.connected_regions_refs = [
                regions_by_code[c] for c in region_codes
            ]

        inferred_links = infer_station_route_links(stations_payload, routes_payload)
        db.session.execute(delete(RouteStation))
        db.session.flush()

        for payload in routes_payload:
            route_name = str(payload.get("name", "")).strip()
            route = routes_by_name.get(route_name)
            if route is None:
                continue

            major_stops = [
                str(s).strip().lower()
                for s in to_list(payload.get("majorStops", []))
                if str(s).strip()
            ]
            major_station_codes = parse_station_codes(
                payload.get("majorStationCodes", payload.get("major_station_codes", []))
            )
            major_station_order = {code: i for i, code in enumerate(major_station_codes)}

            added_station_ids: set[int] = set()
            for station_code, route_names in inferred_links.items():
                if route_name not in route_names:
                    continue
                s = stations_by_code.get(station_code)
                if s is None or s.id in added_station_ids:
                    continue

                is_major = False
                sort_order = None
                station_name_lower = s.name.lower()
                station_code_upper = str(s.code or "").upper()

                if station_code_upper in major_station_order:
                    is_major = True
                    sort_order = major_station_order[station_code_upper]

                for i, stop in enumerate(major_stops):
                    if stop in station_name_lower or station_name_lower in stop:
                        is_major = True
                        if sort_order is None:
                            sort_order = i
                        break

                db.session.add(
                    RouteStation(
                        route_id=route.id,
                        station_id=s.id,
                        is_major=is_major,
                        sort_order=sort_order,
                    )
                )
                added_station_ids.add(s.id)

        for station in stations_by_code.values():
            count = RouteStation.query.filter_by(station_id=station.id).count()
            station.routes_served_count = count

        for region in regions_by_code.values():
            region.number_of_amtrak_stations = Station.query.filter_by(
                region_id=region.id
            ).count()
            region.number_of_amtrak_routes = region.routes.count()

        if args.dry_run:
            log_info("Dry run complete; rolling back changes")
            db.session.rollback()
        else:
            db.session.commit()

    log_info(f"Regions: {inserted['regions']} inserted, {updated['regions']} updated")
    log_info(f"Routes: {inserted['routes']} inserted, {updated['routes']} updated")
    log_info(f"Stations: {inserted['stations']} inserted, {updated['stations']} updated")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log_error(str(error))
        raise
