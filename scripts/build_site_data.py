#!/usr/bin/env python3
"""Generate the static site catalog payload from the YAML source cards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from catalog import ROOT, compact_number, load_cards
from models import load_models


OUTPUT_PATH = ROOT / "site" / "app" / "catalog-data.json"
SCENARIO_PATH = ROOT / "sources" / "scenarios.yaml"
WATCHLIST_PATH = ROOT / "sources" / "watchlist.yaml"
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_scenarios() -> list[dict[str, Any]]:
    payload = yaml.safe_load(SCENARIO_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("sources/scenarios.yaml must use schema_version 1")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("sources/scenarios.yaml must contain at least one scenario")

    ids: set[str] = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("every scenario must be an object")
        required = {"id", "label", "short_label", "description", "tasks"}
        if set(scenario) != required:
            raise ValueError(f"scenario keys must be exactly {sorted(required)}")
        scenario_id = scenario["id"]
        if not isinstance(scenario_id, str) or not KEBAB_CASE.fullmatch(scenario_id) or scenario_id in ids:
            raise ValueError(f"invalid or duplicate scenario id: {scenario_id!r}")
        if not all(isinstance(scenario[key], str) and scenario[key] for key in ("label", "short_label", "description")):
            raise ValueError(f"scenario {scenario_id!r} requires non-empty labels and description")
        tasks = scenario["tasks"]
        if (
            not isinstance(tasks, list)
            or not tasks
            or not all(isinstance(task, str) and KEBAB_CASE.fullmatch(task) for task in tasks)
            or len(tasks) != len(set(tasks))
        ):
            raise ValueError(f"scenario {scenario_id!r} requires unique task matches")
        ids.add(scenario_id)
    return scenarios


def scenario_ids(tasks: list[str], scenarios: list[dict[str, Any]]) -> list[str]:
    task_set = set(tasks)
    return [scenario["id"] for scenario in scenarios if task_set.intersection(scenario["tasks"])]


def load_dataset_monitors() -> dict[str, dict[str, str]]:
    payload = yaml.safe_load(WATCHLIST_PATH.read_text(encoding="utf-8"))
    tracks = payload.get("tracks", []) if isinstance(payload, dict) else []
    track = next(
        (item for item in tracks if isinstance(item, dict) and item.get("id") == "important-dataset-updates"),
        None,
    )
    if track is None:
        raise ValueError("sources/watchlist.yaml must define important-dataset-updates")

    monitors: dict[str, dict[str, str]] = {}
    for source in track.get("official_sources", []):
        if not isinstance(source, dict):
            raise ValueError("important dataset watch sources must include url, catalog_id, and priority")
        source_url = source.get("url")
        catalog_id = source.get("catalog_id")
        priority = source.get("priority")
        if not all(isinstance(value, str) and value for value in (source_url, catalog_id, priority)):
            raise ValueError("important dataset watch sources require non-empty metadata")
        if not source_url.startswith("https://"):
            raise ValueError(f"dataset monitor requires an HTTPS url: {source_url!r}")
        if priority not in {"critical", "high", "standard"}:
            raise ValueError(f"dataset monitor has invalid priority: {priority!r}")
        if catalog_id in monitors:
            raise ValueError(f"duplicate dataset monitor catalog_id: {catalog_id!r}")
        monitors[catalog_id] = {"priority": priority, "source_url": source_url}
    return monitors


def strategy_profile(card: dict[str, Any]) -> dict[str, Any]:
    """Derive comparison fields without interpreting undisclosed evidence."""
    stages = card["data"]["stages"]
    data_references = card["data"]["datasets"]

    return {
        "stage_names": [stage["name"] for stage in stages],
        "source_types": list(
            dict.fromkeys(
                source_type
                for stage in stages
                for source_type in stage["source_types"]
            )
        ),
        "operations": list(
            dict.fromkeys(
                operation
                for stage in stages
                for operation in stage["operations"]
            )
        ),
        "data_reference_count": len(data_references),
        "linked_dataset_count": sum(
            reference["catalog_id"] is not None for reference in data_references
        ),
        "scale_disclosed_stage_count": sum(
            stage["scale_disclosed"] for stage in stages
        ),
        "stage_count": len(stages),
        "unknown_count": len(card["data"]["unknowns"]),
    }


def build_payload() -> dict[str, Any]:
    scenarios = load_scenarios()
    monitors = load_dataset_monitors()
    datasets = []
    for path, card in load_cards():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        item["scenario_ids"] = scenario_ids(card["tasks"], scenarios)
        item["scale_label"] = compact_number(
            card["scale"].get("samples"), card["scale"].get("approximate", False)
        )
        item["monitoring"] = monitors.get(card["id"])
        datasets.append(item)

    unknown_monitors = set(monitors) - {item["id"] for item in datasets}
    if unknown_monitors:
        raise ValueError(f"dataset monitors reference unknown catalog ids: {sorted(unknown_monitors)}")

    models = []
    for path, card in load_models():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        item["scenario_ids"] = scenario_ids(card["tasks"], scenarios)
        item["strategy_profile"] = strategy_profile(card)
        models.append(item)

    datasets.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    models.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    relations: list[dict[str, Any]] = []
    seen_relations: set[tuple[str, str, str]] = set()
    linked_models: dict[str, list[str]] = {item["id"]: [] for item in datasets}
    for model in models:
        linked_dataset_ids: list[str] = []
        for reference in model["data"]["datasets"]:
            dataset_id = reference["catalog_id"]
            if dataset_id is None:
                continue
            key = (model["id"], dataset_id, reference["role"])
            if key in seen_relations:
                raise ValueError(f"duplicate model-dataset relation: {key!r}")
            seen_relations.add(key)
            relations.append(
                {
                    "model_id": model["id"],
                    "dataset_id": dataset_id,
                    "role": reference["role"],
                    "availability": reference["availability"],
                    "scale": reference["scale"],
                    "reference_name": reference["name"],
                }
            )
            if dataset_id not in linked_dataset_ids:
                linked_dataset_ids.append(dataset_id)
            if model["id"] not in linked_models[dataset_id]:
                linked_models[dataset_id].append(model["id"])
        model["linked_dataset_ids"] = linked_dataset_ids

    for dataset in datasets:
        dataset["linked_model_ids"] = linked_models[dataset["id"]]

    relations.sort(key=lambda item: (item["model_id"], item["dataset_id"], item["role"]))
    verified_dates = [item["last_verified"] for item in [*datasets, *models]]

    return {
        "format_version": 6,
        "generated_from": [
            "catalog/**/*.yaml",
            "models/**/*.yaml",
            "sources/scenarios.yaml",
            "sources/watchlist.yaml",
        ],
        "last_verified": max(verified_dates),
        "scenarios": [
            {key: value for key, value in scenario.items() if key != "tasks"}
            for scenario in scenarios
        ],
        "datasets": datasets,
        "models": models,
        "relations": relations,
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
