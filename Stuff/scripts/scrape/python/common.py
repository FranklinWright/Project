from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

DEFAULT_HEADERS = {
    "User-Agent": "RailReachDataPipeline/1.0 (+https://railreach.me)",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        charset = "utf-8"
        if "charset=" in content_type.lower():
            for part in content_type.split(";"):
                part = part.strip()
                if part.lower().startswith("charset="):
                    charset = part.split("=", 1)[1].strip().strip('"')
                    break
        return response.read().decode(charset, errors="replace")


def fetch_json(url: str, timeout: int = 30) -> Any:
    text = fetch_text(url, timeout=timeout)
    return json.loads(text)


def ensure_parent_dir(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def write_json(file_path: Path, payload: Any) -> None:
    ensure_parent_dir(file_path)
    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def to_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def pick_first(record: dict[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return default


def slugify(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"[^a-z0-9\s-]", "", lowered)
    lowered = re.sub(r"[\s_-]+", "-", lowered)
    return lowered.strip("-")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_warn(message: str) -> None:
    print(f"[WARN] {message}")


def log_error(message: str) -> None:
    print(f"[ERROR] {message}")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def format_percent(numerator: float, denominator: float) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{(numerator / denominator) * 100:.1f}%"


def format_population(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} million"
    return f"{value:,}"


def format_currency(value: int) -> str:
    return f"${value:,}"


def parse_population_to_int(value: Any) -> int:
    """Parse scraped population string (e.g. '31.7 million', '128,000') to int."""
    s = str(value or "").strip().replace(",", "")
    if not s:
        return 0
    s_lower = s.lower()
    if "million" in s_lower:
        try:
            return int(float(s_lower.replace("million", "").strip()) * 1_000_000)
        except (TypeError, ValueError):
            return 0
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def parse_currency_to_int(value: Any) -> int:
    """Parse scraped currency string (e.g. '$73,000') to int."""
    s = str(value or "").strip().replace("$", "").replace(",", "")
    if not s:
        return 0
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def parse_percent_to_float(value: Any) -> float:
    """Parse scraped percent string (e.g. '5.3%', '0.0%') to float."""
    s = str(value or "").strip().replace("%", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def resolve_output_path(root: Path, relative_or_absolute: str) -> Path:
    path = Path(relative_or_absolute)
    if path.is_absolute():
        return path
    return root / path


def try_fetch_json(urls: Iterable[str], timeout: int = 30) -> tuple[Any, str]:
    last_error: Exception | None = None
    for url in urls:
        try:
            payload = fetch_json(url, timeout=timeout)
            return payload, url
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as error:
            last_error = error
            log_warn(f"Failed to fetch {url}: {error}")

    if last_error is None:
        raise RuntimeError("No source URLs were provided")
    raise RuntimeError(f"All source URLs failed. Last error: {last_error}")


def safe_fetch_json(url: str, timeout: int = 30) -> Any | None:
    try:
        return fetch_json(url, timeout=timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return None


def wikipedia_summary(title: str, timeout: int = 30) -> dict[str, Any] | None:
    encoded_title = quote(title.replace(" ", "_"), safe="")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    payload = safe_fetch_json(url, timeout=timeout)
    if not isinstance(payload, dict):
        return None
    if payload.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
        return None
    return payload


def wikipedia_search_first_title(query: str, timeout: int = 30) -> str | None:
    encoded_query = quote(query)
    url = (
        "https://en.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={encoded_query}&format=json&srlimit=1"
    )
    payload = safe_fetch_json(url, timeout=timeout)
    if not isinstance(payload, dict):
        return None
    search_results = payload.get("query", {}).get("search", [])
    if not isinstance(search_results, list) or not search_results:
        return None
    top = search_results[0]
    if not isinstance(top, dict):
        return None
    title = top.get("title")
    return str(title).strip() if title else None


def wikipedia_best_effort(
    title_candidates: Iterable[str],
    search_query: str | None = None,
    timeout: int = 30,
) -> dict[str, Any] | None:
    for title in title_candidates:
        normalized = normalize_whitespace(title)
        if not normalized:
            continue
        summary = wikipedia_summary(normalized, timeout=timeout)
        if summary:
            return summary

    if search_query:
        discovered_title = wikipedia_search_first_title(search_query, timeout=timeout)
        if discovered_title:
            return wikipedia_summary(discovered_title, timeout=timeout)

    return None
