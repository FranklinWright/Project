#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from python.common import log_error, log_info, resolve_output_path

DEFAULT_STATIONS = "data/raw/stations.json"
DEFAULT_ROUTES = "data/raw/routes.json"
DEFAULT_REGIONS = "data/raw/regions.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate scraped RailReach data files")
    parser.add_argument("--stations-file", default=DEFAULT_STATIONS)
    parser.add_argument("--routes-file", default=DEFAULT_ROUTES)
    parser.add_argument("--regions-file", default=DEFAULT_REGIONS)
    return parser.parse_args()


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list in {path}")

    return [item for item in payload if isinstance(item, dict)]


def assert_required_fields(records: list[dict[str, Any]], required_fields: list[str], label: str) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records):
        for field in required_fields:
            value = record.get(field)
            if value in (None, ""):
                errors.append(f"{label}[{index}] missing required field '{field}'")
    return errors


def assert_unique_field(records: list[dict[str, Any]], field: str, label: str) -> list[str]:
    errors: list[str] = []
    seen: dict[str, int] = {}

    for index, record in enumerate(records):
        value = str(record.get(field, "")).strip()
        if not value:
            continue
        if value in seen:
            errors.append(
                f"{label}[{index}] duplicate {field}='{value}' (first seen at index {seen[value]})"
            )
        else:
            seen[value] = index

    return errors


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]

    stations_file = resolve_output_path(repo_root, args.stations_file)
    routes_file = resolve_output_path(repo_root, args.routes_file)
    regions_file = resolve_output_path(repo_root, args.regions_file)

    stations = load_json_list(stations_file)
    routes = load_json_list(routes_file)
    regions = load_json_list(regions_file)

    errors: list[str] = []
    errors.extend(assert_required_fields(stations, ["name", "code", "regionId"], "stations"))
    errors.extend(assert_required_fields(routes, ["name", "amtrakUrl"], "routes"))
    errors.extend(assert_required_fields(regions, ["name", "code"], "regions"))

    errors.extend(assert_unique_field(stations, "code", "stations"))
    errors.extend(assert_unique_field(routes, "name", "routes"))
    errors.extend(assert_unique_field(regions, "code", "regions"))

    if len(stations) < 100:
        errors.append(f"Expected at least 100 stations, found {len(stations)}")
    if len(routes) < 20:
        errors.append(f"Expected at least 20 routes, found {len(routes)}")
    if len(regions) < 50:
        errors.append(f"Expected at least 50 regions, found {len(regions)}")

    if errors:
        for error in errors:
            log_error(error)
        return 1

    log_info(f"stations.json records: {len(stations)}")
    log_info(f"routes.json records: {len(routes)}")
    log_info(f"regions.json records: {len(regions)}")
    log_info("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
