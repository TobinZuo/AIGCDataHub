#!/usr/bin/env python3
"""Validate all dataset cards against the repository schema and conventions."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from catalog import ROOT, load_cards, load_schema


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def validate() -> list[str]:
    errors: list[str] = []
    try:
        cards = load_cards()
    except Exception as exc:  # report malformed YAML without a traceback
        return [str(exc)]

    if not cards:
        errors.append("catalog contains no dataset cards")
        return errors

    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    ids: list[str] = []

    for path, card in cards:
        path_name = relative(path)
        card_id = card.get("id")
        if isinstance(card_id, str):
            ids.append(card_id)
            if path.stem != card_id:
                errors.append(f"{path_name}: file name must match id {card_id!r}")

        modality = card.get("modality")
        if isinstance(modality, str) and path.parent.name != modality:
            errors.append(
                f"{path_name}: parent directory must match modality {modality!r}"
            )

        for issue in sorted(validator.iter_errors(card), key=lambda err: list(err.path)):
            location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
            errors.append(f"{path_name}:{location}: {issue.message}")

        try:
            released = date.fromisoformat(card["released_at"])
            verified = date.fromisoformat(card["last_verified"])
            if verified < released:
                errors.append(f"{path_name}: last_verified cannot precede released_at")
        except (KeyError, TypeError, ValueError):
            pass

    duplicates = [card_id for card_id, count in Counter(ids).items() if count > 1]
    for card_id in sorted(duplicates):
        errors.append(f"duplicate dataset id: {card_id}")

    cards_by_id = {
        card["id"]: (path, card)
        for path, card in cards
        if isinstance(card.get("id"), str)
    }
    lineage_graph: dict[str, list[str]] = {card_id: [] for card_id in cards_by_id}
    for child_id, (path, card) in cards_by_id.items():
        seen_parents: set[str] = set()
        for reference in card.get("derived_from", []):
            if not isinstance(reference, dict):
                continue
            parent_id = reference.get("catalog_id")
            if not isinstance(parent_id, str):
                continue
            if parent_id in seen_parents:
                errors.append(
                    f"{relative(path)}: duplicate derived_from catalog_id {parent_id!r}"
                )
                continue
            seen_parents.add(parent_id)
            if parent_id == child_id:
                errors.append(f"{relative(path)}: dataset cannot derive from itself")
                continue
            if parent_id not in cards_by_id:
                errors.append(
                    f"{relative(path)}: derived_from references unknown catalog id {parent_id!r}"
                )
                continue
            lineage_graph[child_id].append(parent_id)

    visiting: list[str] = []
    state: dict[str, int] = {}
    reported_cycles: set[tuple[str, ...]] = set()

    def visit(card_id: str) -> None:
        state[card_id] = 1
        visiting.append(card_id)
        for parent_id in lineage_graph[card_id]:
            if state.get(parent_id, 0) == 0:
                visit(parent_id)
            elif state.get(parent_id) == 1:
                start = visiting.index(parent_id)
                cycle = tuple([*visiting[start:], parent_id])
                if cycle not in reported_cycles:
                    reported_cycles.add(cycle)
                    errors.append(f"dataset lineage cycle: {' -> '.join(cycle)}")
        visiting.pop()
        state[card_id] = 2

    for card_id in sorted(lineage_graph):
        if state.get(card_id, 0) == 0:
            visit(card_id)

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"Catalog validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(load_cards())} dataset card(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
