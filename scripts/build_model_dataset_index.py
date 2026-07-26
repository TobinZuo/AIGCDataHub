#!/usr/bin/env python3
"""Generate a repository-visible audit of every model dataset reference."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from catalog import ROOT, load_cards
from models import load_models


OUTPUT_PATH = ROOT / "MODEL_DATASET_INDEX.md"


def escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_index() -> str:
    datasets = {card["id"]: path.relative_to(ROOT).as_posix() for path, card in load_cards()}
    models = sorted(
        load_models(),
        key=lambda item: (item[1]["released_at"], item[1]["name"].lower()),
        reverse=True,
    )
    rows: list[str] = []
    linked = 0
    unresolved = 0
    for path, model in models:
        model_path = path.relative_to(ROOT).as_posix()
        references = model["data"]["datasets"]
        if not references:
            unresolved += 1
            rows.append(
                f"| [{escape(model['name'])}]({model_path}) | {model['released_at']} | — | undisclosed | "
                "— official sources name no dataset | — | The card records the full corpus as undisclosed. |"
            )
            continue
        for reference in references:
            catalog_id = reference["catalog_id"]
            if catalog_id:
                linked += 1
                resolution = f"[`{catalog_id}`]({datasets[catalog_id]})"
            else:
                unresolved += 1
                reason = {
                    "not-released": "publisher has not released it",
                    "undisclosed": "exact source is not disclosed",
                }.get(reference["availability"], "catalog card unavailable")
                resolution = f"— {reason}"
            rows.append(
                "| "
                f"[{escape(model['name'])}]({model_path}) | {model['released_at']} | "
                f"{escape(reference['name'])} | {reference['availability']} | {resolution} | "
                f"{reference['role']} | {escape(reference['notes'])} |"
            )

    lines = [
        "# Model ↔ Dataset reference index",
        "",
        "Generated from `models/**/*.yaml`. This is the audit view for every claimed model data reference: a public or gated named dataset must resolve to a catalog card; unreleased or undisclosed data must state why no card exists.",
        "",
        f"- Models: {len(models)}",
        f"- References linked to catalog cards: {linked}",
        f"- References without a card, with an explicit evidence boundary: {unresolved}",
        "- Ordering: model release date, newest first",
        "",
        "| Model | Released | Dataset or corpus named by source | Availability | Catalog resolution | Role | Evidence boundary |",
        "|---|---:|---|---|---|---|---|",
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
        print(f"model dataset index is current: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
