"""Shared catalog loading and formatting helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = ROOT / "catalog"
SCHEMA_PATH = ROOT / "schemas" / "dataset.schema.json"


def card_paths() -> list[Path]:
    return sorted(CATALOG_ROOT.glob("**/*.yaml"))


def load_card(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        card = yaml.safe_load(stream)
    if not isinstance(card, dict):
        raise ValueError("top-level YAML value must be an object")
    return card


def load_cards() -> list[tuple[Path, dict[str, Any]]]:
    return [(path, load_card(path)) for path in card_paths()]


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def compact_number(value: int | None, approximate: bool = False) -> str:
    if value is None:
        return "unknown"
    units: Iterable[tuple[int, str]] = (
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    )
    for divisor, suffix in units:
        if value >= divisor:
            number = value / divisor
            rendered = f"{number:.1f}".rstrip("0").rstrip(".")
            return f"{'~' if approximate else ''}{rendered}{suffix}"
    return f"{'~' if approximate else ''}{value:,}"

