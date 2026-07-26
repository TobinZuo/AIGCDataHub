#!/usr/bin/env python3
"""Validate AIGC model cards and their dataset references."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from catalog import ROOT, load_cards
from models import load_model_schema, load_models


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def validate_models() -> list[str]:
    errors: list[str] = []
    try:
        models = load_models()
    except Exception as exc:
        return [str(exc)]
    if not models:
        return ["models contains no model cards"]

    dataset_ids = {card["id"] for _, card in load_cards()}
    validator = Draft202012Validator(load_model_schema(), format_checker=FormatChecker())
    ids: list[str] = []
    ranking_aliases: list[str] = []

    for path, model in models:
        path_name = relative(path)
        model_id = model.get("id")
        if isinstance(model_id, str):
            ids.append(model_id)
            if path.stem != model_id:
                errors.append(f"{path_name}: file name must match id {model_id!r}")
        ranking_aliases.extend(model.get("ranking_names", []))

        modalities = model.get("modalities", [])
        expected_parent = "multimodal" if "multimodal" in modalities else (modalities[0] if modalities else None)
        if expected_parent and path.parent.name != expected_parent:
            errors.append(f"{path_name}: parent directory must be {expected_parent!r}")

        for issue in sorted(validator.iter_errors(model), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
            errors.append(f"{path_name}:{location}: {issue.message}")

        data = model.get("data", {})
        for index, dataset in enumerate(data.get("datasets", [])):
            catalog_id = dataset.get("catalog_id")
            if catalog_id and catalog_id not in dataset_ids:
                errors.append(
                    f"{path_name}:data.datasets.{index}.catalog_id: unknown dataset {catalog_id!r}"
                )
            if dataset.get("availability") in {"public", "gated"} and not catalog_id:
                errors.append(
                    f"{path_name}:data.datasets.{index}.catalog_id: public or gated named data requires a catalog card"
                )

        training_references = [
            reference
            for reference in data.get("datasets", [])
            if reference.get("role") != "evaluation"
        ]
        if data.get("exact_datasets_disclosed") and not training_references:
            errors.append(f"{path_name}: exact_datasets_disclosed requires at least one dataset")
        if data.get("disclosure_level") == "undisclosed" and training_references:
            errors.append(f"{path_name}: undisclosed data must not claim named training datasets")

        try:
            released = date.fromisoformat(model["released_at"])
            verified = date.fromisoformat(model["last_verified"])
            if verified < released:
                errors.append(f"{path_name}: last_verified cannot precede released_at")
        except (KeyError, TypeError, ValueError):
            pass

    for model_id, count in sorted(Counter(ids).items()):
        if count > 1:
            errors.append(f"duplicate model id: {model_id}")
    for alias, count in sorted(Counter(ranking_aliases).items()):
        if count > 1:
            errors.append(f"duplicate ranking alias: {alias}")
    return errors


def main() -> int:
    errors = validate_models()
    if errors:
        print(f"Model validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(load_models())} model card(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
