#!/usr/bin/env python3
"""Generate the static site changelog payload from updates/*.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPDATES_DIR = ROOT / "updates"
OUTPUT_PATH = ROOT / "site" / "app" / "changelog-data.json"
DATE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def _flush_paragraph(blocks: list[dict[str, Any]], lines: list[str]) -> None:
    if lines:
        blocks.append({"type": "paragraph", "text": " ".join(lines)})
        lines.clear()


def _flush_list(blocks: list[dict[str, Any]], items: list[str]) -> None:
    if items:
        blocks.append({"type": "list", "items": list(items)})
        items.clear()


def _flush_table(blocks: list[dict[str, Any]], rows: list[list[str]]) -> None:
    if rows:
        if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
            rows.pop(1)
        blocks.append({"type": "table", "rows": [list(row) for row in rows]})
        rows.clear()


def _table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_blocks(lines: list[str]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    items: list[str] = []
    table: list[list[str]] = []

    def flush_all() -> None:
        _flush_paragraph(blocks, paragraph)
        _flush_list(blocks, items)
        _flush_table(blocks, table)

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_all()
            continue
        if line.startswith("### "):
            flush_all()
            blocks.append({"type": "subheading", "text": line[4:].strip()})
            continue
        if line.startswith("| ") and line.endswith("|"):
            _flush_paragraph(blocks, paragraph)
            _flush_list(blocks, items)
            table.append(_table_row(line))
            continue
        if line.startswith("- "):
            _flush_paragraph(blocks, paragraph)
            _flush_table(blocks, table)
            items.append(line[2:].strip())
            continue
        if items:
            items[-1] = f"{items[-1]} {line}"
        elif table:
            _flush_table(blocks, table)
            paragraph.append(line)
        else:
            paragraph.append(line)

    flush_all()
    return blocks


def parse_update(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = path.stem
    intro_lines: list[str] = []
    sections: list[dict[str, Any]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("# ") and title == path.stem:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current_title is not None:
                sections.append({"title": current_title, "blocks": parse_blocks(current_lines)})
            elif current_lines:
                intro_lines = current_lines
            current_title = line[3:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_title is not None:
        sections.append({"title": current_title, "blocks": parse_blocks(current_lines)})
    elif current_lines:
        intro_lines = current_lines

    match = DATE_NAME.fullmatch(path.name)
    if not match:
        raise ValueError(f"update filename must be YYYY-MM-DD.md: {path.name}")
    return {
        "date": match.group(1),
        "title": title,
        "intro": parse_blocks(intro_lines),
        "sections": sections,
        "source_path": path.relative_to(ROOT).as_posix(),
    }


def build_payload() -> dict[str, Any]:
    entries = [
        parse_update(path)
        for path in UPDATES_DIR.glob("*.md")
        if DATE_NAME.fullmatch(path.name)
    ]
    entries.sort(key=lambda entry: entry["date"], reverse=True)
    return {
        "format_version": 1,
        "generated_from": "updates/*.md",
        "entries": entries,
    }


def render_payload() -> str:
    return json.dumps(build_payload(), ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_payload()

    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != rendered:
            print(f"out of date: {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"changelog data is current: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
