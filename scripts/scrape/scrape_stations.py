#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from python.common import (
    log_info,
    log_warn,
    normalize_whitespace,
    pick_first,
    resolve_output_path,
    safe_int,
    slugify,
    to_list,
    try_fetch_json,
    wikipedia_best_effort,
    write_json,
)

DEFAULT_OUTPUT = "data/raw/stations.json"
SOURCE_URLS = [
    "https://v2.amtraker.com/v3/stations",
    "https://api-v3.amtraker.com/v3/stations",
]

DEFAULT_FACEBOOK_URL = "https://www.facebook.com/Amtrak/"
DEFAULT_TWITTER_URL = "https://twitter.com/Amtrak"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape station data for RailReach")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout seconds")
    parser.add_argument(
        "--no-wikipedia",
        action="store_true",
        help="Skip Wikipedia enrichment lookups",
    )
    parser.add_argument(
        "--wikipedia-max",
        type=int,
        default=1000,
        help="Maximum number of station records to enrich using Wikipedia lookups",
    )
    return parser.parse_args()


def fallback_station_image(code: str) -> str:
    return f"https://picsum.photos/seed/railreach-station-{slugify(code)}/1600/900"


def fallback_poi_image(code: str) -> str:
    return f"https://picsum.photos/seed/railreach-poi-{slugify(code)}/1200/675"


def title_from_wikipedia_url(url: str) -> str:
    if not url:
        return ""
    title = url.rstrip("/").split("/")[-1]
    return unquote(title).replace("_", " ").strip()


def infer_region_id(address: str, state: str, code: str) -> str:
    if state and len(state) == 2:
        return state.upper()

    if address:
        match = re.search(r",\s*([A-Z]{2})\b", address.upper())
        if match:
            return match.group(1)

    if code and len(code) >= 2:
        return code[:2].upper()

    return "UNK"


def normalize_station(raw: dict[str, Any]) -> dict[str, Any]:
    code = str(pick_first(raw, ["code", "Code", "stationCode", "station_code", "id"], "UNK")).upper()
    name = normalize_whitespace(
        str(pick_first(raw, ["name", "Name", "stationName", "station_name"], f"Station {code}"))
    )
    state = str(pick_first(raw, ["state", "State", "abbr"], "")).upper()

    address = normalize_whitespace(
        str(
            pick_first(
                raw,
                ["address", "Address", "fullAddress", "location"],
                "",
            )
        )
    )
    if not address:
        address_parts = [
            str(pick_first(raw, ["street", "address1"], "")).strip(),
            str(pick_first(raw, ["city"], "")).strip(),
            state,
            str(pick_first(raw, ["zip", "zipcode", "postalCode"], "")).strip(),
        ]
        address = normalize_whitespace(", ".join(part for part in address_parts if part)) or "Address unavailable"

    routes = to_list(pick_first(raw, ["routes", "routeNames"], []))
    nearby = to_list(pick_first(raw, ["nearbyStations", "nearby_stations"], []))
    points_of_interest = to_list(pick_first(raw, ["pointsOfInterest", "points_of_interest"], []))
    destinations = to_list(pick_first(raw, ["connectedDestinations", "destinations"], []))

    region_id = infer_region_id(address=address, state=state, code=code)

    return {
        "name": name,
        "code": code,
        "address": address,
        "timezone": str(pick_first(raw, ["timezone", "tz", "timeZone"], "Unknown")),
        "description": str(
            pick_first(raw, ["description", "desc", "info"], "Description unavailable")
        ),
        "hours": str(pick_first(raw, ["hours", "stationHours"], "Hours unavailable")),
        "nearbyStations": [str(item) for item in nearby],
        "pointsOfInterest": [str(item) for item in points_of_interest],
        "connectedDestinations": [str(item) for item in destinations],
        "routesServedCount": safe_int(
            pick_first(raw, ["routesServedCount", "routeCount"], len(routes)),
            default=len(routes),
        ),
        "imageUrl": str(pick_first(raw, ["imageUrl", "image", "photoUrl"], "")),
        "regionId": region_id,
        "amtrakUrl": str(
            pick_first(raw, ["amtrakUrl", "stationUrl"], f"https://www.amtrak.com/stations/{code.lower()}")
        ),
        "wikipediaUrl": str(pick_first(raw, ["wikipediaUrl", "wikipedia"], "")),
        "facebookUrl": str(pick_first(raw, ["facebookUrl", "facebook"], "")) or DEFAULT_FACEBOOK_URL,
        "twitterUrl": str(pick_first(raw, ["twitterUrl", "twitter"], "")) or DEFAULT_TWITTER_URL,
        "poiImageUrl": str(pick_first(raw, ["poiImageUrl"], "")),
        "poiImageLabel": str(pick_first(raw, ["poiImageLabel"], "")),
        "history": str(pick_first(raw, ["history"], "")),
    }


def enrich_station(
    station: dict[str, Any],
    timeout: int,
    use_wikipedia: bool,
    wiki_cache: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    name = str(station.get("name", "")).strip()
    code = str(station.get("code", "UNK")).strip().upper()

    station["facebookUrl"] = station.get("facebookUrl") or DEFAULT_FACEBOOK_URL
    station["twitterUrl"] = station.get("twitterUrl") or DEFAULT_TWITTER_URL

    if use_wikipedia and name:
        cache_key = name.lower()
        summary = wiki_cache.get(cache_key)
        if cache_key not in wiki_cache:
            url_title = title_from_wikipedia_url(str(station.get("wikipediaUrl", "")))
            title_candidates = [
                url_title,
                f"{name} station (Amtrak)",
                f"{name} station",
                name,
            ]
            summary = wikipedia_best_effort(
                title_candidates=title_candidates,
                search_query=f"{name} Amtrak station",
                timeout=timeout,
            )
            wiki_cache[cache_key] = summary

        if summary:
            extract = normalize_whitespace(str(summary.get("extract", "")))
            summary_image = (
                (summary.get("originalimage") or {}).get("source")
                or (summary.get("thumbnail") or {}).get("source")
                or ""
            )
            page_url = (summary.get("content_urls") or {}).get("desktop", {}).get("page", "")

            if extract and (
                not station.get("description")
                or station.get("description") == "Description unavailable"
            ):
                station["description"] = extract

            if extract and not station.get("history"):
                station["history"] = extract

            if summary_image and not station.get("imageUrl"):
                station["imageUrl"] = summary_image

            if summary_image and not station.get("poiImageUrl"):
                station["poiImageUrl"] = summary_image
                station["poiImageLabel"] = station.get("poiImageLabel") or "Station area"

            if page_url and not station.get("wikipediaUrl"):
                station["wikipediaUrl"] = page_url

    if not station.get("imageUrl"):
        station["imageUrl"] = fallback_station_image(code)

    if not station.get("poiImageUrl"):
        station["poiImageUrl"] = fallback_poi_image(code)
        station["poiImageLabel"] = station.get("poiImageLabel") or "Nearby area"

    if not station.get("history"):
        station["history"] = station.get("description") or "Historical details unavailable."

    return station


def station_records_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            return [item for item in payload["data"] if isinstance(item, dict)]

        if isinstance(payload.get("features"), list):
            records: list[dict[str, Any]] = []
            for feature in payload["features"]:
                if not isinstance(feature, dict):
                    continue
                properties = feature.get("properties") if isinstance(feature.get("properties"), dict) else feature
                if isinstance(properties, dict):
                    records.append(properties)
            return records

        records = []
        for code, value in payload.items():
            if not isinstance(value, dict):
                continue
            record = dict(value)
            if "code" not in record and "Code" not in record:
                record["code"] = code
            records.append(record)
        return records

    return []


def fallback_stations() -> list[dict[str, Any]]:
    log_warn("Using fallback stations data (network source unavailable)")
    return [
        {
            "name": "Austin Station",
            "code": "AUS",
            "address": "250 North Lamar Boulevard, Austin, TX 78703",
            "timezone": "America/Chicago",
            "description": "Amtrak station in Austin, Texas.",
            "hours": "Station Building: 9:00 AM - 7:00 PM Daily",
            "nearbyStations": ["San Marcos, TX (SMC)", "Taylor, TX (TAY)"],
            "pointsOfInterest": ["Lady Bird Lake", "Texas State Capitol"],
            "connectedDestinations": ["Chicago, IL", "San Antonio, TX"],
            "routesServedCount": 1,
            "imageUrl": fallback_station_image("AUS"),
            "regionId": "TX",
            "amtrakUrl": "https://www.amtrak.com/stations/aus",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/Austin_station_(Amtrak)",
            "facebookUrl": "https://www.facebook.com/Amtrak/",
            "twitterUrl": "https://twitter.com/Amtrak",
            "poiImageUrl": fallback_poi_image("AUS"),
            "poiImageLabel": "Nearby area",
            "history": "Austin Station serves long-distance Amtrak service and regional connections.",
        },
        {
            "name": "Sacramento Valley Station",
            "code": "SAC",
            "address": "401 I Street, Sacramento, CA 95814",
            "timezone": "America/Los_Angeles",
            "description": "Major Amtrak station in Sacramento, California.",
            "hours": "Station Building: 5:00 AM - 11:59 PM Daily",
            "nearbyStations": ["Davis, CA (DAV)", "Roseville, CA (RSV)"],
            "pointsOfInterest": ["Old Sacramento", "State Railroad Museum"],
            "connectedDestinations": ["San Francisco, CA", "Los Angeles, CA"],
            "routesServedCount": 4,
            "imageUrl": fallback_station_image("SAC"),
            "regionId": "CA",
            "amtrakUrl": "https://www.amtrak.com/stations/sac",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/Sacramento_Valley_Station",
            "facebookUrl": "https://www.facebook.com/Amtrak/",
            "twitterUrl": "https://twitter.com/Amtrak",
            "poiImageUrl": fallback_poi_image("SAC"),
            "poiImageLabel": "Nearby area",
            "history": "Sacramento Valley Station is a major rail hub for California intercity travel.",
        },
        {
            "name": "Chicago Union Station",
            "code": "CHI",
            "address": "255 South Clinton Street, Chicago, IL 60606",
            "timezone": "America/Chicago",
            "description": "Major Amtrak station in Chicago, Illinois.",
            "hours": "Station Building: 5:30 AM - 11:59 PM Daily",
            "nearbyStations": ["Homewood, IL (HMW)", "Dyer, IN (DYE)"],
            "pointsOfInterest": ["Willis Tower", "Millennium Park"],
            "connectedDestinations": ["New York, NY", "Los Angeles, CA"],
            "routesServedCount": 16,
            "imageUrl": fallback_station_image("CHI"),
            "regionId": "IL",
            "amtrakUrl": "https://www.amtrak.com/stations/chi",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/Chicago_Union_Station",
            "facebookUrl": "https://www.facebook.com/Amtrak/",
            "twitterUrl": "https://twitter.com/Amtrak",
            "poiImageUrl": fallback_poi_image("CHI"),
            "poiImageLabel": "Nearby area",
            "history": "Chicago Union Station is one of the busiest Amtrak hubs in the United States.",
        },
    ]


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    output_path = resolve_output_path(repo_root, args.output)

    wiki_cache: dict[str, dict[str, Any] | None] = {}
    wikipedia_calls_used = 0

    try:
        payload, source_url = try_fetch_json(SOURCE_URLS, timeout=args.timeout)
        raw_records = station_records_from_payload(payload)
        log_info(f"Fetched {len(raw_records)} raw station records from {source_url}")
        stations = [normalize_station(record) for record in raw_records]
        stations = [station for station in stations if station["code"] != "UNK"]
    except RuntimeError as error:
        log_warn(str(error))
        stations = fallback_stations()

    deduped: dict[str, dict[str, Any]] = {}
    for station in stations:
        should_use_wikipedia = not args.no_wikipedia and wikipedia_calls_used < args.wikipedia_max
        station = enrich_station(
            station,
            timeout=args.timeout,
            use_wikipedia=should_use_wikipedia,
            wiki_cache=wiki_cache,
        )
        if should_use_wikipedia:
            wikipedia_calls_used += 1
        deduped[station["code"]] = station

    final_stations = [deduped[code] for code in sorted(deduped.keys())]
    write_json(output_path, final_stations)
    log_info(f"Wrote {len(final_stations)} station records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
