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
from source_platforms import load_source_platforms


OUTPUT_PATH = ROOT / "site" / "app" / "catalog-data.json"
SCENARIO_PATH = ROOT / "sources" / "scenarios.yaml"
WATCHLIST_PATH = ROOT / "sources" / "watchlist.yaml"
DISCOVERY_STATE_PATH = ROOT / "sources" / "discovery-state.json"
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


def load_monitors(track_id: str, id_key: str, entity_label: str) -> dict[str, dict[str, str]]:
    payload = yaml.safe_load(WATCHLIST_PATH.read_text(encoding="utf-8"))
    tracks = payload.get("tracks", []) if isinstance(payload, dict) else []
    track = next(
        (item for item in tracks if isinstance(item, dict) and item.get("id") == track_id),
        None,
    )
    if track is None:
        raise ValueError(f"sources/watchlist.yaml must define {track_id}")

    monitors: dict[str, dict[str, str]] = {}
    for source in track.get("official_sources", []):
        if not isinstance(source, dict):
            raise ValueError(f"important {entity_label} watch sources require structured metadata")
        source_url = source.get("url")
        entity_id = source.get(id_key)
        priority = source.get("priority")
        revision_mode = source.get("revision_mode")
        if not all(isinstance(value, str) and value for value in (source_url, entity_id, priority)):
            raise ValueError(f"important {entity_label} watch sources require non-empty metadata")
        if not source_url.startswith("https://"):
            raise ValueError(f"{entity_label} monitor requires an HTTPS url: {source_url!r}")
        if priority not in {"critical", "high", "standard"}:
            raise ValueError(f"{entity_label} monitor has invalid priority: {priority!r}")
        if revision_mode is not None and revision_mode not in {"content-revision", "availability"}:
            raise ValueError(f"{entity_label} monitor has invalid revision_mode: {revision_mode!r}")
        if entity_id in monitors:
            raise ValueError(f"duplicate {entity_label} monitor id: {entity_id!r}")
        monitor = {"priority": priority, "source_url": source_url}
        if revision_mode is not None:
            monitor["mode"] = revision_mode
        monitors[entity_id] = monitor
    return monitors


def load_dataset_monitors() -> dict[str, dict[str, str]]:
    return load_monitors("important-dataset-updates", "catalog_id", "dataset")


def load_model_monitors() -> dict[str, dict[str, str]]:
    return load_monitors("important-model-updates", "model_id", "model")


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
        "linked_dataset_count": len(
            {
                reference["catalog_id"]
                for reference in data_references
                if reference["catalog_id"] is not None
            }
        ),
        "scale_disclosed_stage_count": sum(
            stage["scale_disclosed"] for stage in stages
        ),
        "stage_count": len(stages),
        "unknown_count": len(card["data"]["unknowns"]),
    }


def load_rankings() -> list[dict[str, Any]]:
    if not DISCOVERY_STATE_PATH.exists():
        return []
    state = json.loads(DISCOVERY_STATE_PATH.read_text(encoding="utf-8"))
    boards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in state.get("sources", []):
        ranking_id = source.get("ranking_id")
        if not ranking_id:
            continue
        if ranking_id in seen:
            raise ValueError(f"duplicate ranking snapshot: {ranking_id!r}")
        seen.add(ranking_id)
        entries = source.get("rankings", [])
        ranks = [entry.get("rank") for entry in entries]
        if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
            raise ValueError(f"ranking snapshot is not strictly ordered: {ranking_id!r}")
        boards.append(
            {
                "id": ranking_id,
                "provider": source.get("ranking_provider") or "Unknown",
                "label": source.get("ranking_label") or ranking_id,
                "modality": source.get("ranking_modality") or "video",
                "score_label": source.get("ranking_score_label") or "Score",
                "date_label": source.get("ranking_date_label") or "快照",
                "coverage_policy": source.get("ranking_coverage_policy") or "monitor",
                "source_url": source.get("ranking_page_url") or source["source_url"],
                "fetch_url": source["source_url"],
                "entries": entries,
            }
        )
    return sorted(boards, key=lambda item: item["id"])


def ranking_key(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def build_payload() -> dict[str, Any]:
    scenarios = load_scenarios()
    source_platforms = load_source_platforms()
    scenario_id_set = {item["id"] for item in scenarios}
    for platform in source_platforms:
        unknown_scenarios = set(platform["relevant_scenarios"]) - scenario_id_set
        if unknown_scenarios:
            raise ValueError(
                f"source platform {platform['id']!r} references unknown scenarios: "
                f"{sorted(unknown_scenarios)}"
            )
    source_platforms.sort(key=lambda item: (item["category"], item["name"].lower()))
    dataset_monitors = load_dataset_monitors()
    model_monitors = load_model_monitors()
    datasets = []
    for path, card in load_cards():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        item["scenario_ids"] = scenario_ids(card["tasks"], scenarios)
        item["scale_label"] = compact_number(
            card["scale"].get("samples"), card["scale"].get("approximate", False)
        )
        item["monitoring"] = dataset_monitors.get(card["id"])
        datasets.append(item)

    unknown_monitors = set(dataset_monitors) - {item["id"] for item in datasets}
    if unknown_monitors:
        raise ValueError(f"dataset monitors reference unknown catalog ids: {sorted(unknown_monitors)}")

    models = []
    for path, card in load_models():
        item = dict(card)
        item["source_path"] = path.relative_to(ROOT).as_posix()
        item["scenario_ids"] = scenario_ids(card["tasks"], scenarios)
        item["strategy_profile"] = strategy_profile(card)
        item["monitoring"] = model_monitors.get(card["id"])
        item["ranking_positions"] = []
        models.append(item)

    unknown_model_monitors = set(model_monitors) - {item["id"] for item in models}
    if unknown_model_monitors:
        raise ValueError(f"model monitors reference unknown model ids: {sorted(unknown_model_monitors)}")

    datasets.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    models.sort(key=lambda item: (item["released_at"], item["name"].lower()), reverse=True)
    model_aliases: dict[str, str] = {}
    for model in models:
        for alias in [model["name"], *model.get("ranking_names", [])]:
            key = ranking_key(alias)
            previous = model_aliases.get(key)
            if previous and previous != model["id"]:
                raise ValueError(f"ranking alias {alias!r} maps to multiple models")
            model_aliases[key] = model["id"]

    rankings = load_rankings()
    model_by_id = {item["id"]: item for item in models}
    for board in rankings:
        for entry in board["entries"]:
            component_names = [
                value
                for value in entry.get("component_models", [])
                if isinstance(value, str) and value
            ] or [entry["model"]]
            components = [
                {
                    "name": name,
                    "model_id": model_aliases.get(ranking_key(name)),
                }
                for name in component_names
            ]
            model_ids = list(dict.fromkeys(
                component["model_id"]
                for component in components
                if component["model_id"]
            ))
            primary_model_id = model_aliases.get(ranking_key(entry["model"]))
            if primary_model_id and primary_model_id not in model_ids:
                model_ids.insert(0, primary_model_id)
            entry["components"] = components
            entry["model_ids"] = model_ids
            entry["model_id"] = primary_model_id or (model_ids[0] if model_ids else None)
            for model_id in model_ids:
                model_by_id[model_id]["ranking_positions"].append(
                    {
                        "ranking_id": board["id"],
                        "provider": board["provider"],
                        "rank": entry["rank"],
                        "score": entry.get("score", entry.get("elo")),
                        "score_label": board["score_label"],
                        "entry_model": entry["model"],
                        "component_count": len(components),
                    }
                )
    dataset_by_id = {item["id"]: item for item in datasets}
    dataset_relations: list[dict[str, Any]] = []
    seen_dataset_relations: set[tuple[str, str]] = set()
    upstream_datasets: dict[str, list[str]] = {item["id"]: [] for item in datasets}
    downstream_datasets: dict[str, list[str]] = {item["id"]: [] for item in datasets}
    for dataset in datasets:
        for reference in dataset.get("derived_from", []):
            source_dataset_id = reference["catalog_id"]
            key = (source_dataset_id, dataset["id"])
            if source_dataset_id not in dataset_by_id:
                raise ValueError(
                    f"dataset lineage references unknown catalog id: {source_dataset_id!r}"
                )
            if source_dataset_id == dataset["id"]:
                raise ValueError(f"dataset cannot derive from itself: {dataset['id']!r}")
            if key in seen_dataset_relations:
                raise ValueError(f"duplicate dataset lineage relation: {key!r}")
            seen_dataset_relations.add(key)
            dataset_relations.append(
                {
                    "source_dataset_id": source_dataset_id,
                    "derived_dataset_id": dataset["id"],
                    "relationship": reference["relationship"],
                    "contribution": reference["contribution"],
                    "notes": reference["notes"],
                }
            )
            upstream_datasets[dataset["id"]].append(source_dataset_id)
            downstream_datasets[source_dataset_id].append(dataset["id"])

    for dataset in datasets:
        dataset["upstream_dataset_ids"] = upstream_datasets[dataset["id"]]
        dataset["downstream_dataset_ids"] = downstream_datasets[dataset["id"]]

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
    dataset_relations.sort(
        key=lambda item: (
            item["source_dataset_id"],
            item["derived_dataset_id"],
            item["relationship"],
        )
    )
    verified_dates = [item["last_verified"] for item in [*datasets, *models]]

    return {
        "format_version": 15,
        "generated_from": [
            "catalog/**/*.yaml",
            "models/**/*.yaml",
            "sources/scenarios.yaml",
            "sources/source-platforms.yaml",
            "sources/watchlist.yaml",
            "sources/discovery-state.json",
        ],
        "last_verified": max(verified_dates),
        "scenarios": [
            {key: value for key, value in scenario.items() if key != "tasks"}
            for scenario in scenarios
        ],
        "source_platforms": source_platforms,
        "datasets": datasets,
        "models": models,
        "relations": relations,
        "dataset_relations": dataset_relations,
        "rankings": rankings,
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
