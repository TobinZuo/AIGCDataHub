#!/usr/bin/env python3
"""Generate the static site catalog payload from the YAML source cards."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from catalog import ROOT, compact_number, load_cards
from models import load_models


OUTPUT_PATH = ROOT / "site" / "app" / "catalog-data.json"


def build_payload() -> dict[str, Any]:
    datasets = []
    for path, card in load_cards():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        item["scale_label"] = compact_number(
            card["scale"].get("samples"), card["scale"].get("approximate", False)
        )
        datasets.append(item)

    models = []
    for path, card in load_models():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        models.append(item)

    datasets.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    models.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    verified_dates = [item["last_verified"] for item in [*datasets, *models]]

    return {
        "format_version": 2,
        "generated_from": ["catalog/**/*.yaml", "models/**/*.yaml"],
        "last_verified": max(verified_dates),
        "datasets": datasets,
        "models": models,
    }


def render_payload() -> str:
    return json.dumps(build_payload(), ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the checked-in site payload is out of date",
    )
    args = parser.parse_args()
    rendered = render_payload()

    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != rendered:
            print(f"out of date: {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"site data is current: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
