#!/usr/bin/env python3
"""
Post-build step: inject Jinja placeholders into dist/index.html for Flask SSR rendering.
Overwrites dist/index.html in place.
"""
from pathlib import Path

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_INDEX = PROJECT_ROOT / "dist" / "index.html"

SSR_CONTENT_PLACEHOLDER = "{{ ssr_content | safe }}"
DEHYDRATED_STATE_PLACEHOLDER = "window.__REACT_QUERY_STATE__={{ dehydrated_state | tojson }}"


def main() -> None:
    if not DIST_INDEX.exists():
        raise SystemExit("dist/index.html not found. Run make build-frontend first.")

    soup = BeautifulSoup(DIST_INDEX.read_text(encoding="utf-8"), "html.parser")

    root = soup.find("div", id="root")
    if root:
        root.clear()
        root.append(SSR_CONTENT_PLACEHOLDER)

    body = soup.find("body")
    if body:
        script = soup.new_tag("script")
        script.string = DEHYDRATED_STATE_PLACEHOLDER
        body.append(script)

    DIST_INDEX.write_text(str(soup), encoding="utf-8")
    print(f"Wrote {DIST_INDEX.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
