#!/usr/bin/env python3
"""Generate the repository-visible candidate source-platform index."""

from __future__ import annotations

import argparse
import sys

from catalog import ROOT
from source_platforms import load_source_platform_registry, load_source_platforms


OUTPUT_PATH = ROOT / "SOURCE_PLATFORM_INDEX.md"
CATEGORY_LABELS = {
    "video-platform": "Video platform",
    "streaming-and-studio": "Streaming / studio",
    "stock-media": "Stock media",
    "ecommerce": "E-commerce",
}
ACCESS_LABELS = {
    "documented-api": "Documented API",
    "partner-api": "Partner API",
    "partner-portal": "Partner portal",
    "licensed-service": "Licensed service",
    "not-cataloged": "No interface cataloged",
}


def escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_index() -> str:
    registry = load_source_platform_registry()
    platforms = sorted(
        load_source_platforms(), key=lambda item: (item["category"], item["name"].lower())
    )
    policy = registry["policy"]
    rows = []
    for item in platforms:
        access = item["data_access"]
        monitoring = item["monitoring"]
        interface = (
            f"[{escape(access['interface_name'])}]({access['interface_url']})"
            if access["interface_url"]
            else "Not cataloged"
        )
        rows.append(
            "| "
            f"[{escape(item['name'])}]({item['homepage']}) | "
            f"{CATEGORY_LABELS[item['category']]} | {', '.join(item['modalities'])} | "
            f"{', '.join(item['relevant_scenarios'])} | "
            f"{ACCESS_LABELS[access['status']]} | {interface} | "
            f"{escape(access['scope'])} | {escape(access['requirements'])} | "
            f"[{monitoring['mode']}]({monitoring['url']}) / {monitoring['priority']} | "
            f"{item['last_reviewed']} |"
        )
    lines = [
        "# Candidate content-source platform index",
        "",
        "This registry keeps potential acquisition surfaces separate from released datasets. It does not provide a dataset download link or imply permission to crawl, train on, redistribute, or commercialize platform content.",
        "",
        f"- Platforms: {len(platforms)}",
        f"- Catalog boundary: {policy['boundary']}",
        f"- Rights boundary: {policy['rights']}",
        f"- Publication boundary: {policy['internal_notes']}",
        "- Interface boundary: an API, portal, or licensed service exposes only its documented scope; it does not grant model-training or redistribution rights.",
        "",
        "| Platform | Category | Modalities | Relevant scenarios | Data access | Official interface | Accessible scope | Requirements | Monitoring | Reviewed |",
        "|---|---|---|---|---|---|---|---|---|---:|",
        *rows,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_index()
    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != rendered:
            print(f"out of date: {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"source platform index is current: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
