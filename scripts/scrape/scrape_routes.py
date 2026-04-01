#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, unquote

from python.common import (
    fetch_text,
    log_info,
    log_warn,
    normalize_whitespace,
    resolve_output_path,
    safe_int,
    slugify,
    wikipedia_best_effort,
    write_json,
)

DEFAULT_OUTPUT = "data/raw/routes.json"
ROUTES_PAGE = "https://www.amtrak.com/train-routes"
DEFAULT_STATIONS = "data/raw/stations.json"

DEFAULT_MENU = [
    "Signature Flat Iron Steak",
    "Pan Roasted Chicken Breast",
    "Atlantic Salmon",
    "Railroad French Toast",
]

CITY_TO_STATE_CODE = {
    "albany": "NY",
    "albuquerque": "NM",
    "atlanta": "GA",
    "austin": "TX",
    "boston": "MA",
    "chicago": "IL",
    "cincinnati": "OH",
    "cleveland": "OH",
    "dallas": "TX",
    "denver": "CO",
    "detroit": "MI",
    "houston": "TX",
    "kansas city": "MO",
    "los angeles": "CA",
    "miami": "FL",
    "milwaukee": "WI",
    "new orleans": "LA",
    "new york": "NY",
    "oakland": "CA",
    "oklahoma city": "OK",
    "philadelphia": "PA",
    "phoenix": "AZ",
    "portland": "OR",
    "sacramento": "CA",
    "salt lake city": "UT",
    "san antonio": "TX",
    "san diego": "CA",
    "san francisco": "CA",
    "seattle": "WA",
    "st louis": "MO",
    "washington": "DC",
        "greensboro": "NC",
        "greenboro": "NC",
        "hartford": "CT",
        "montreal": "QC",
        "new haven": "CT",
        "new york city": "NY",
        "northampton": "MA",
        "raleigh": "NC",
        "springfield": "MA",
        "charlotte": "NC",
        "durham": "NC",
}

STATE_NAME_TO_CODE = {
    "alabama": "AL",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "district of columbia": "DC",
    "florida": "FL",
    "georgia": "GA",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}

ROUTE_NAME_REGION_FALLBACK = {
    "northeast regional": "CT, DC, DE, MA, MD, NC, NJ, NY, PA, RI, SC, VA",
    "northeast regional train": "CT, DC, DE, MA, MD, NC, NJ, NY, PA, RI, SC, VA",
}

YOUTUBE_VIDEO_PATTERN = re.compile(r'"videoId":"([A-Za-z0-9_-]{11})"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape route data for RailReach")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout seconds")
    parser.add_argument("--max-routes", type=int, default=60, help="Max route pages to crawl")
    parser.add_argument(
        "--stations-file",
        default=DEFAULT_STATIONS,
        help="Optional stations JSON to infer regions spanned",
    )
    parser.add_argument(
        "--no-wikipedia",
        action="store_true",
        help="Skip Wikipedia enrichment lookups",
    )
    return parser.parse_args()


def fallback_route_image(slug: str) -> str:
    return f"https://picsum.photos/seed/railreach-route-{slugify(slug)}/1600/900"


def title_from_wikipedia_url(url: str) -> str:
    if not url:
        return ""
    title = url.rstrip("/").split("/")[-1]
    return unquote(title).replace("_", " ").strip()


def normalize_text(value: str) -> str:
    lowered = normalize_whitespace(str(value)).lower()
    return re.sub(r"\s+", " ", lowered).strip()


def extract_first_youtube_video_url(html: str) -> str:
    for video_id in YOUTUBE_VIDEO_PATTERN.findall(html):
        return f"https://www.youtube.com/watch?v={video_id}"
    return ""


def youtube_search_first_video_url(query: str, timeout: int) -> str:
    encoded_query = quote_plus(normalize_whitespace(query))
    if not encoded_query:
        return ""

    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    try:
        html = fetch_text(search_url, timeout=timeout)
    except Exception:  # noqa: BLE001
        return ""
    return extract_first_youtube_video_url(html)


def resolve_route_youtube_url(
    route_name: str,
    timeout: int,
    youtube_cache: dict[str, str],
) -> str:
    cache_key = normalize_text(route_name)
    if not cache_key:
        return ""
    if cache_key in youtube_cache:
        return youtube_cache[cache_key]

    queries = [
        f"Amtrak {route_name} train",
        f"{route_name} train ride",
    ]
    for query in queries:
        video_url = youtube_search_first_video_url(query, timeout=timeout)
        if video_url:
            youtube_cache[cache_key] = video_url
            return video_url

    default_key = "__default__"
    if default_key not in youtube_cache:
        youtube_cache[default_key] = youtube_search_first_video_url("Amtrak train ride", timeout=timeout)
    youtube_cache[cache_key] = youtube_cache.get(default_key, "")
    return youtube_cache[cache_key]


def is_probable_image_url(url: str) -> bool:
    if not url:
        return False
    lower = url.strip().lower()
    if not lower.startswith("http"):
        return False

    path_without_query = lower.split("?", 1)[0]
    if path_without_query.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif")):
        return True

    return any(token in lower for token in ("/content/dam/", "/image/", "/images/", "imagerendition"))


def extract_route_links(html: str) -> list[str]:
    href_pattern = re.compile(r'href="([^"]+)"', flags=re.IGNORECASE)
    links: list[str] = []
    for raw_href in href_pattern.findall(html):
        href = raw_href.strip()
        if not href:
            continue

        lower_href = href.lower()
        if "javascript:" in lower_href or lower_href.startswith("mailto:"):
            continue
        if "deals-discounts" in lower_href or "vacation" in lower_href:
            continue
        if "-train" not in lower_href:
            continue
        if "amtrak.com" in lower_href and not lower_href.startswith("http"):
            continue

        if href.startswith("/"):
            href = f"https://www.amtrak.com{href}"
        elif href.startswith("http") and "amtrak.com" not in href:
            continue

        href = href.split("#")[0].split("?")[0]
        if href not in links:
            links.append(href)

    return links


def extract_meta(html: str, key: str) -> str:
    patterns = [
        rf'<meta[^>]+property="{re.escape(key)}"[^>]+content="([^"]*)"',
        rf'<meta[^>]+name="{re.escape(key)}"[^>]+content="([^"]*)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return normalize_whitespace(match.group(1))
    return ""


def route_name_from_html(html: str, url: str) -> str:
    def route_name_from_url(route_url: str) -> str:
        slug = route_url.rstrip("/").split("/")[-1].strip().lower()
        if not slug:
            return ""
        slug = re.sub(r"-trains?$", "", slug)
        return normalize_whitespace(slug.replace("-", " ")).title()

    def clean_route_name(raw_name: str) -> str:
        cleaned = normalize_whitespace(raw_name)
        cleaned = re.sub(r"\btrains?\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -:,")
        return cleaned

    name_from_url = route_name_from_url(url)
    if name_from_url:
        return name_from_url

    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if title_match:
        title = normalize_whitespace(title_match.group(1))
        if "|" in title:
            title = title.split("|")[0].strip()
        if "-" in title and "train" in title.lower():
            title = title.split("-")[0].strip()
        if title:
            return clean_route_name(title)

    slug = url.rstrip("/").split("/")[-1]
    return clean_route_name(slug.replace("-", " ").title())


def extract_travel_time(text: str) -> str:
    match = re.search(r"(\d+\s+hours?(?:\s+\d+\s+minutes?)?)", text, flags=re.IGNORECASE)
    if match:
        return normalize_whitespace(match.group(1))
    return "Unknown"


def extract_stations_served(text: str) -> int:
    match = re.search(r"(\d+)\s+stations?", text, flags=re.IGNORECASE)
    if match:
        return safe_int(match.group(1), default=0)
    return 0


def extract_major_stops(description: str) -> list[str]:
    candidates = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", description)
    banned = {
        "Amtrak",
        "Train",
        "Route",
        "Daily",
        "Between",
        "North",
        "South",
        "East",
        "West",
    }
    stops: list[str] = []
    for candidate in candidates:
        if candidate in banned:
            continue
        if candidate not in stops:
            stops.append(candidate)
        if len(stops) >= 6:
            break
    return stops


def normalize_route(url: str, html: str) -> dict[str, Any]:
    name = route_name_from_html(html, url)
    description = extract_meta(html, "description")
    if not description:
        description = "Route description unavailable"

    image_url = extract_meta(html, "og:image") or extract_meta(html, "twitter:image")
    if not is_probable_image_url(image_url):
        image_url = ""
    travel_time = extract_travel_time(html)
    stations_served = extract_stations_served(html)
    major_stops = extract_major_stops(description)

    return {
        "name": name,
        "majorStops": major_stops,
        "description": description,
        "menu": DEFAULT_MENU,
        "travelTimeInHours": travel_time,
        "regionsSpanned": [],
        "stationsServed": stations_served,
        "imageUrl": image_url,
        "amtrakUrl": url,
        "wikipediaUrl": f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}",
        "youtubeUrl": None,
        "slug": slugify(name),
    }


def load_station_payloads(stations_file: Path) -> list[dict[str, Any]]:
    if not stations_file.exists():
        return []
    try:
        payload = json.loads(stations_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        log_warn(f"Could not parse stations file for route enrichment: {error}")
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def infer_regions_for_route(route: dict[str, Any], _stations: list[dict[str, Any]]) -> list[str]:
    major_stops = [str(stop).strip().lower() for stop in route.get("majorStops", []) if str(stop).strip()]

    region_codes: set[str] = set()
    for stop in major_stops:
        mapped = CITY_TO_STATE_CODE.get(stop)
        if mapped:
            region_codes.add(mapped)
            continue
        for city, state_code in CITY_TO_STATE_CODE.items():
            if city in stop:
                region_codes.add(state_code)

    description = normalize_text(str(route.get("description", "")))
    has_dc_phrase = bool(re.search(r"\bwashington\s+d\.?c\.?\b", description))
    if has_dc_phrase:
        region_codes.add("DC")
    for state_name, state_code in sorted(STATE_NAME_TO_CODE.items(), key=lambda item: len(item[0]), reverse=True):
        if state_name == "washington" and has_dc_phrase:
            continue
        if re.search(rf"\b{re.escape(state_name)}\b", description):
            region_codes.add(state_code)

    route_name = str(route.get("name", "")).strip().lower()
    if not region_codes and route_name in ROUTE_NAME_REGION_FALLBACK:
        fallback = ROUTE_NAME_REGION_FALLBACK[route_name]
        return [c.strip().upper() for c in fallback.split(",") if c.strip()]

    if not region_codes:
        existing = route.get("regionsSpanned", [])
        if isinstance(existing, list):
            return [str(c).strip().upper() for c in existing if c]
        return [c.strip().upper() for c in str(existing).split(",") if c.strip()]
    return sorted(region_codes)


def enrich_route_with_wikipedia(
    route: dict[str, Any],
    timeout: int,
    use_wikipedia: bool,
    wiki_cache: dict[str, dict[str, Any] | None],
    youtube_cache: dict[str, str],
) -> dict[str, Any]:
    name = str(route.get("name", "")).strip()
    slug = str(route.get("slug", slugify(name)))

    if use_wikipedia and name:
        cache_key = name.lower()
        summary = wiki_cache.get(cache_key)
        if cache_key not in wiki_cache:
            url_title = title_from_wikipedia_url(str(route.get("wikipediaUrl", "")))
            summary = wikipedia_best_effort(
                title_candidates=[url_title, name, f"{name} train"],
                search_query=f"{name} Amtrak",
                timeout=timeout,
            )
            wiki_cache[cache_key] = summary

        if summary:
            summary_image = (
                (summary.get("originalimage") or {}).get("source")
                or (summary.get("thumbnail") or {}).get("source")
                or ""
            )
            extract = normalize_whitespace(str(summary.get("extract", "")))
            page_url = (summary.get("content_urls") or {}).get("desktop", {}).get("page", "")

            if extract and (
                not route.get("description")
                or route.get("description") == "Route description unavailable"
            ):
                route["description"] = extract

            if summary_image and not route.get("imageUrl"):
                route["imageUrl"] = summary_image

            if page_url and not route.get("wikipediaUrl"):
                route["wikipediaUrl"] = page_url

    if not route.get("imageUrl"):
        route["imageUrl"] = fallback_route_image(slug)

    if not route.get("menu"):
        route["menu"] = DEFAULT_MENU

    if not route.get("youtubeUrl") and name:
        route["youtubeUrl"] = resolve_route_youtube_url(
            route_name=name,
            timeout=timeout,
            youtube_cache=youtube_cache,
        )

    return route


def fallback_routes() -> list[dict[str, Any]]:
    log_warn("Using fallback routes data (network source unavailable)")
    return [
        {
            "name": "Texas Eagle",
            "majorStops": ["Chicago", "St. Louis", "Dallas", "Austin", "San Antonio"],
            "description": "Amtrak route between Chicago and San Antonio with thruway service beyond.",
            "menu": DEFAULT_MENU,
            "travelTimeInHours": "32 hours 25 minutes",
            "regionsSpanned": ["TX", "CA", "IL"],
            "stationsServed": 43,
            "imageUrl": fallback_route_image("texas-eagle"),
            "amtrakUrl": "https://www.amtrak.com/texas-eagle-train",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/Texas_Eagle",
            "youtubeUrl": None,
            "slug": "texas-eagle",
        },
        {
            "name": "California Zephyr",
            "majorStops": ["Chicago", "Denver", "Salt Lake City", "Sacramento"],
            "description": "Scenic route between Chicago and Northern California.",
            "menu": DEFAULT_MENU,
            "travelTimeInHours": "51 hours 20 minutes",
            "regionsSpanned": ["IL", "CA"],
            "stationsServed": 34,
            "imageUrl": fallback_route_image("california-zephyr"),
            "amtrakUrl": "https://www.amtrak.com/california-zephyr-train",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/California_Zephyr",
            "youtubeUrl": None,
            "slug": "california-zephyr",
        },
        {
            "name": "Coast Starlight",
            "majorStops": ["Seattle", "Portland", "Sacramento", "Los Angeles"],
            "description": "Daily route linking major West Coast cities.",
            "menu": DEFAULT_MENU,
            "travelTimeInHours": "35 hours",
            "regionsSpanned": ["CA"],
            "stationsServed": 30,
            "imageUrl": fallback_route_image("coast-starlight"),
            "amtrakUrl": "https://www.amtrak.com/coast-starlight-train",
            "wikipediaUrl": "https://en.wikipedia.org/wiki/Coast_Starlight",
            "youtubeUrl": None,
            "slug": "coast-starlight",
        },
    ]


def scrape_routes(
    timeout: int,
    max_routes: int,
    stations_file: Path,
    use_wikipedia: bool,
) -> list[dict[str, Any]]:
    routes_page_html = fetch_text(ROUTES_PAGE, timeout=timeout)
    route_links = extract_route_links(routes_page_html)
    if not route_links:
        raise RuntimeError("No route links found on train routes page")

    log_info(f"Discovered {len(route_links)} candidate route links")
    normalized_routes: list[dict[str, Any]] = []
    stations = load_station_payloads(stations_file)
    wiki_cache: dict[str, dict[str, Any] | None] = {}
    youtube_cache: dict[str, str] = {}

    for link in route_links[:max_routes]:
        try:
            html = fetch_text(link, timeout=timeout)
            route = normalize_route(link, html)
            route["regionsSpanned"] = infer_regions_for_route(route, stations)
            route = enrich_route_with_wikipedia(
                route,
                timeout=timeout,
                use_wikipedia=use_wikipedia,
                wiki_cache=wiki_cache,
                youtube_cache=youtube_cache,
            )
            normalized_routes.append(route)
        except Exception as error:  # noqa: BLE001
            log_warn(f"Skipping {link}: {error}")

    deduped: dict[str, dict[str, Any]] = {}
    for route in normalized_routes:
        slug = route.get("slug") or slugify(str(route.get("name", "")))
        route["slug"] = slug
        deduped[str(slug)] = route

    routes = [deduped[key] for key in sorted(deduped.keys())]
    if not routes:
        raise RuntimeError("No route pages could be parsed")

    return routes


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    output_path = resolve_output_path(repo_root, args.output)
    stations_file = resolve_output_path(repo_root, args.stations_file)

    try:
        routes = scrape_routes(
            timeout=args.timeout,
            max_routes=args.max_routes,
            stations_file=stations_file,
            use_wikipedia=not args.no_wikipedia,
        )
        log_info(f"Scraped {len(routes)} routes from {ROUTES_PAGE}")
    except Exception as error:  # noqa: BLE001
        log_warn(f"Route scraping failed: {error}")
        routes = fallback_routes()

    write_json(output_path, routes)
    log_info(f"Wrote {len(routes)} route records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
