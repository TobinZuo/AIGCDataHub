#!/usr/bin/env python3
"""Generate a Chinese, reader-facing changelog from updates/*.md summaries."""

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
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https://tobinzuo\.github\.io/AIGCDataHub/#[^)]+)\)")
PUBLIC_ORIGIN = "https://tobinzuo.github.io/AIGCDataHub"
TARGET_PREFIX = "页面定位："
SUMMARY_TITLE = "中文摘要"
SUMMARY_DIMENSIONS = (
    ("models", "模型"),
    ("datasets", "数据集"),
    ("relations", "数据关系"),
    ("rankings", "排行榜"),
    ("monitoring", "监控"),
    ("unknowns", "未披露"),
)


def extract_summary(lines: list[str], path: Path) -> list[dict[str, Any]]:
    expected_labels = [label for _, label in SUMMARY_DIMENSIONS]
    values: dict[str, dict[str, Any]] = {}
    in_summary = False
    current_label: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_label
        if current_label is not None:
            target_lines = [
                line.strip()
                for line in current_lines
                if line.strip().startswith(TARGET_PREFIX)
            ]
            if len(target_lines) != 1:
                raise ValueError(
                    f"{path.name} summary dimension {current_label!r} requires one 页面定位 line"
                )
            links = [
                {"label": label, "href": href.removeprefix(PUBLIC_ORIGIN)}
                for label, href in MARKDOWN_LINK.findall(target_lines[0])
            ]
            if not links:
                raise ValueError(
                    f"{path.name} summary dimension {current_label!r} has no valid page target"
                )
            text = " ".join(
                line.strip()
                for line in current_lines
                if line.strip() and not line.strip().startswith(TARGET_PREFIX)
            )
            if not text:
                raise ValueError(f"{path.name} summary dimension {current_label!r} is empty")
            values[current_label] = {"text": text, "links": links}
        current_label = None
        current_lines.clear()

    for line in lines:
        if line == f"## {SUMMARY_TITLE}":
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            flush()
            break
        if not in_summary:
            continue
        if line.startswith("### "):
            flush()
            current_label = line[4:].strip()
            if current_label not in expected_labels:
                raise ValueError(
                    f"{path.name} has unsupported summary dimension: {current_label!r}"
                )
            if current_label in values:
                raise ValueError(f"{path.name} repeats summary dimension: {current_label!r}")
            continue
        current_lines.append(line)
    else:
        if in_summary:
            flush()

    if not in_summary:
        raise ValueError(f"{path.name} must contain a {SUMMARY_TITLE!r} section")
    missing = [label for label in expected_labels if label not in values]
    if missing:
        raise ValueError(f"{path.name} is missing summary dimensions: {missing}")

    return [
        {"id": dimension_id, "label": label, **values[label]}
        for dimension_id, label in SUMMARY_DIMENSIONS
    ]


def parse_update(path: Path) -> dict[str, Any]:
    match = DATE_NAME.fullmatch(path.name)
    if not match:
        raise ValueError(f"update filename must be YYYY-MM-DD.md: {path.name}")
    date = match.group(1)
    lines = path.read_text(encoding="utf-8").splitlines()
    return {
        "date": date,
        "title": f"{date} 更新",
        "summary": extract_summary(lines, path),
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
        "format_version": 2,
        "generated_from": "updates/*.md 中的中文摘要",
        "dimensions": [
            {"id": dimension_id, "label": label}
            for dimension_id, label in SUMMARY_DIMENSIONS
        ],
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
