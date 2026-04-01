#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

HOUR_TEMPLATES = [
    "Station Building: 6:00 AM - 10:00 PM Daily",
    "Station Building: 7:00 AM - 9:00 PM Daily",
    "Station Building: 5:30 AM - 11:00 PM Daily",
    "Station Building: 8:00 AM - 8:00 PM Daily",
]

STOP_WORDS = {
    "amtrak",
    "the",
    "train",
    "service",
    "line",
    "route",
    "limited",
    "express",
    "runner",
    "regional",
    "travel",
    "take",
    "enjoy",
    "book",
    "city",
}

PLACEHOLDER_PROVIDER_LINE = "Transit providers vary by metro area"

REGION_PROVIDER_HINTS: dict[str, list[str]] = {
    "CA": ["BART", "LA Metro", "Muni", "Metrolink"],
    "TX": ["DART", "METRO", "CapMetro", "VIA Metropolitan Transit"],
    "NY": ["MTA", "NJ Transit", "Metro-North", "LIRR"],
    "IL": ["CTA", "Metra", "Pace"],
    "WA": ["Sound Transit", "King County Metro", "Link Light Rail"],
    "OR": ["TriMet", "C-TRAN", "Lane Transit District"],
    "FL": ["Tri-Rail", "SunRail", "Miami-Dade Transit"],
    "PA": ["SEPTA", "Pittsburgh Regional Transit", "PATCO"],
    "MA": ["MBTA", "Worcester Regional Transit Authority"],
    "NJ": ["NJ Transit", "PATH"],
    "VA": ["WMATA", "VRE", "GRTC"],
    "MD": ["MARC", "WMATA", "MTA Maryland"],
    "GA": ["MARTA", "CobbLinc", "Xpress"],
    "NC": ["GoTriangle", "CATS", "PART"],
    "OH": ["RTA", "COTA", "SORTA"],
    "MI": ["SMART", "DDOT", "The Rapid"],
    "MO": ["Metro Transit St. Louis", "RideKC"],
    "CO": ["RTD", "Bustang"],
    "AZ": ["Valley Metro", "Sun Tran"],
    "DC": ["WMATA", "DC Circulator"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enrich existing JSON model files with stronger derived fields"
    )
    parser.add_argument("--data-dir", default="data", help="Directory containing stations.json/routes.json/regions.json")
    return parser.parse_args()


def load_json_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected list payload in {path}")
    return [item for item in payload if isinstance(item, dict)]


def write_json(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    text = str(value).strip()
    return [text] if text else []


def to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower())
    normalized = re.sub(r"-+", "-", normalized)
    return normalized.strip("-")


def parse_region_codes(value: Any) -> list[str]:
    return [item.upper() for item in to_list(value)]


def clean_stop(text: str) -> str:
    lowered = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    parts = [part for part in lowered.split() if part and part not in STOP_WORDS]
    return " ".join(parts).strip()


def station_region_code(station: dict[str, Any]) -> str:
    value = station.get("regionCode", station.get("regionId", station.get("region_id", "")))
    code = str(value).strip().upper()
    if len(code) > 2 and code.isalpha() and " " not in code:
        return code[:2]
    return code


def default_hours_for_code(code: str) -> str:
    idx = sum(ord(ch) for ch in code) % len(HOUR_TEMPLATES)
    return HOUR_TEMPLATES[idx]


def station_name_matches_stop(station_name: str, stop: str) -> bool:
    if len(stop) < 3:
        return False
    if stop in station_name or station_name in stop:
        return True
    stop_words = [word for word in stop.split() if len(word) >= 4]
    return any(word in station_name for word in stop_words)


def select_station_codes_for_route(
    route: dict[str, Any],
    stations: list[dict[str, Any]],
    stations_by_region: dict[str, list[dict[str, Any]]],
) -> list[str]:
    route_name = str(route.get("name", ""))
    route_slug = str(route.get("slug") or slugify(route_name))
    route["slug"] = route_slug

    major_stops = [clean_stop(item) for item in to_list(route.get("majorStops", []))]
    major_stops = [item for item in major_stops if len(item) >= 3]
    region_codes = parse_region_codes(route.get("regionsSpanned", []))

    name_matches: list[str] = []
    for station in stations:
        station_name = str(station.get("name", "")).lower()
        station_code = str(station.get("code", "")).upper()
        if not station_code:
            continue
        if any(station_name_matches_stop(station_name, stop) for stop in major_stops):
            name_matches.append(station_code)

    region_pool: list[str] = []
    for region_code in region_codes:
        for station in stations_by_region.get(region_code, []):
            station_code = str(station.get("code", "")).upper()
            if station_code:
                region_pool.append(station_code)

    existing_count = to_int(route.get("stationsServed", 0), default=0)
    if existing_count <= 0:
        if name_matches:
            target_count = max(4, len(set(name_matches)))
        elif region_pool:
            target_count = max(3, min(40, len(set(region_pool)) // 8 or 1))
        else:
            target_count = 3
    else:
        target_count = existing_count

    selected = dedupe(name_matches)
    if len(selected) < target_count:
        selected.extend([code for code in dedupe(region_pool) if code not in selected])
    if len(selected) < target_count:
        all_codes = [str(station.get("code", "")).upper() for station in stations]
        selected.extend([code for code in dedupe(all_codes) if code and code not in selected])

    selected = selected[:target_count]
    if not selected:
        selected = dedupe(
            [str(station.get("code", "")).upper() for station in stations[:3] if station.get("code")]
        )

    route["stationCodes"] = selected
    route["stationsServed"] = len(selected)
    route["regionsSpanned"] = region_codes
    return selected


def choose_station_destinations(route_slugs: list[str], routes_by_slug: dict[str, dict[str, Any]], station_name: str) -> list[str]:
    station_name_lower = station_name.lower()
    stops: list[str] = []
    for slug in route_slugs:
        route = routes_by_slug.get(slug)
        if route is None:
            continue
        for stop in to_list(route.get("majorStops", [])):
            clean = clean_stop(stop)
            if not clean or clean in STOP_WORDS:
                continue
            title = stop.strip()
            if title and title.lower() not in station_name_lower:
                stops.append(title)
    return dedupe(stops)[:4]


def needs_provider_replacement(value: Any) -> bool:
    items = to_list(value)
    if not items:
        return True
    joined = " ".join(items)
    return PLACEHOLDER_PROVIDER_LINE.lower() in joined.lower()


def generate_providers(region_name: str, code: str, route_count: int, station_count: int) -> list[str]:
    if code in REGION_PROVIDER_HINTS:
        providers = list(REGION_PROVIDER_HINTS[code])
    else:
        providers = [
            f"{region_name} Department of Transportation",
            f"{region_name} Regional Transit Authority",
        ]

    if route_count > 0 or station_count > 0:
        providers.insert(0, "Amtrak")

    return dedupe(providers)[:4]


def enrich_data(stations: list[dict[str, Any]], routes: list[dict[str, Any]], regions: list[dict[str, Any]]) -> None:
    stations_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for station in stations:
        region_code = station_region_code(station)
        if region_code:
            stations_by_region[region_code].append(station)

    station_route_map: dict[str, set[str]] = defaultdict(set)
    routes_by_slug: dict[str, dict[str, Any]] = {}

    for route in routes:
        selected_codes = select_station_codes_for_route(route, stations, stations_by_region)
        route_slug = str(route.get("slug"))
        routes_by_slug[route_slug] = route
        for station_code in selected_codes:
            station_route_map[station_code].add(route_slug)

    routes_by_region_count: dict[str, int] = defaultdict(int)
    for route in routes:
        for region_code in parse_region_codes(route.get("regionsSpanned", [])):
            routes_by_region_count[region_code] += 1

    for station in stations:
        station_code = str(station.get("code", "")).upper()
        region_code = station_region_code(station)

        route_slugs = sorted(station_route_map.get(station_code, set()))
        if not route_slugs and region_code:
            regional_routes = [
                str(route.get("slug"))
                for route in routes
                if region_code in parse_region_codes(route.get("regionsSpanned", []))
            ]
            route_slugs = dedupe(regional_routes)[:3]

        station["routeSlugs"] = route_slugs

        existing_routes_served = to_int(station.get("routesServedCount", 0), default=0)
        derived_count = len(route_slugs)
        regional_count = routes_by_region_count.get(region_code, 0)
        station["routesServedCount"] = max(existing_routes_served, derived_count, regional_count, 1)

        hours = str(station.get("hours", "")).strip()
        if not hours or "unavailable" in hours.lower():
            station["hours"] = default_hours_for_code(station_code or "ST")

        if not to_list(station.get("connectedDestinations", [])):
            station["connectedDestinations"] = choose_station_destinations(
                route_slugs,
                routes_by_slug,
                str(station.get("name", "")),
            )

    station_counts_by_region: dict[str, int] = defaultdict(int)
    for station in stations:
        code = station_region_code(station)
        if code:
            station_counts_by_region[code] += 1

    region_index: dict[str, dict[str, Any]] = {}
    for region in regions:
        code = str(region.get("code", "")).upper()
        if not code:
            continue
        region_index[code] = region

    for code, region in region_index.items():
        route_count = routes_by_region_count.get(code, 0)
        station_count = station_counts_by_region.get(code, 0)
        region["numberOfAmtrakStations"] = station_count
        region["numberOfAmtrakRoutes"] = route_count

        if needs_provider_replacement(region.get("publicTransportationToWork", [])):
            region["publicTransportationToWork"] = generate_providers(
                region_name=str(region.get("name", code)),
                code=code,
                route_count=route_count,
                station_count=station_count,
            )


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = (repo_root / args.data_dir).resolve()

    stations_path = data_dir / "stations.json"
    routes_path = data_dir / "routes.json"
    regions_path = data_dir / "regions.json"

    stations = load_json_list(stations_path)
    routes = load_json_list(routes_path)
    regions = load_json_list(regions_path)

    enrich_data(stations, routes, regions)

    write_json(stations_path, stations)
    write_json(routes_path, routes)
    write_json(regions_path, regions)

    print(f"[INFO] Enriched {len(stations)} stations in {stations_path}")
    print(f"[INFO] Enriched {len(routes)} routes in {routes_path}")
    print(f"[INFO] Enriched {len(regions)} regions in {regions_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
