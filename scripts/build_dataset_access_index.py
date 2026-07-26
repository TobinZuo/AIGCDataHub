#!/usr/bin/env python3
"""Generate a repository-visible access index for every dataset card."""

from __future__ import annotations

import argparse
import sys

from catalog import ROOT, load_cards


OUTPUT_PATH = ROOT / "DATASET_ACCESS_INDEX.md"


def escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def access_label(card: dict) -> str:
    access = card["access"]
    labels = {
        "hosted": "Download / browse files",
        "urls": "Source URLs / downloader",
        "metadata": "Metadata / tooling",
        "request": "Request access",
        "none": "Availability notice",
    }
    return labels[access["type"]]


def render_index() -> str:
    cards = sorted(
        load_cards(),
        key=lambda item: (item[1]["released_at"], item[1]["name"].lower()),
        reverse=True,
    )
    status_counts: dict[str, int] = {}
    rows: list[str] = []
    for path, card in cards:
        access = card["access"]
        status_counts[access["status"]] = status_counts.get(access["status"], 0) + 1
        source_path = path.relative_to(ROOT).as_posix()
        action = f"[{access_label(card)}]({access['url']})"
        rows.append(
            "| "
            f"[{escape(card['name'])}]({source_path}) | {card['released_at']} | "
            f"{access['status'].replace('-', ' ')} | {access['type']} | {action} | "
            f"{'yes' if access['requires_account'] else 'no'} | {escape(access['notes'])} |"
        )

    summary = ", ".join(
        f"{status.replace('-', ' ')} {count}"
        for status, count in sorted(status_counts.items())
    )
    lines = [
        "# Dataset access and download index",
        "",
        "Generated from `catalog/**/*.yaml`, newest release first. Every row links to the publisher's current distribution, metadata/downloader, request form, or primary-source availability notice. A link here does not override the media rights recorded in the dataset card.",
        "",
        f"- Datasets: {len(cards)} ({summary})",
        "- `hosted`: downloadable or browsable files are distributed at the link",
        "- `urls`: the publisher distributes source URLs or a downloader, not a durable media archive",
        "- `metadata`: metadata or tooling only",
        "- `request`: access requires an application, agreement, or account approval",
        "- `none`: no dataset payload is currently distributed; the link documents that boundary",
        "",
        "| Dataset card | Released | Access status | Delivery | Get data / access evidence | Account | Access notes |",
        "|---|---:|---|---|---|:---:|---|",
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
        print(f"dataset access index is current: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
