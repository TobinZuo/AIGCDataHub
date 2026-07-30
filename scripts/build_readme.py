#!/usr/bin/env python3
"""Generate dataset and model tables embedded in README.md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from catalog import ROOT, compact_number, load_cards
from models import load_models


README_PATH = ROOT / "README.md"
ZH_README_PATH = ROOT / "README.zh-CN.md"
START = "<!-- BEGIN DATASET CATALOG -->"
END = "<!-- END DATASET CATALOG -->"
MODEL_START = "<!-- BEGIN MODEL CATALOG -->"
MODEL_END = "<!-- END MODEL CATALOG -->"
METRICS_START = "<!-- BEGIN PROJECT METRICS -->"
METRICS_END = "<!-- END PROJECT METRICS -->"
STATUS = {"verified": "✅", "partial": "🟡", "archived": "🗄️"}
MODEL_STATUS = {"verified": "✅", "partial": "🟡", "watch": "👀"}


def dataset_access_label(card: dict) -> str:
    access = card["access"]
    actions = {
        "hosted": "download / browse",
        "urls": "URLs / downloader",
        "metadata": "metadata / tooling",
        "request": "request access",
        "none": "availability notice",
    }
    return f"{actions[access['type']]} ({access['status'].replace('-', ' ')})"


def render_dataset_table() -> str:
    rows = [
        "| Dataset | Organization | Modality | Released | Tasks | Scale | Access | Commercial use | Status |",
        "|---|---|---|---|---|---:|---|---|:---:|",
    ]
    ordered = sorted(load_cards(), key=lambda item: (item[1]["released_at"], item[1]["name"]), reverse=True)
    for path, card in ordered:
        relative_path = path.relative_to(ROOT).as_posix()
        name = f"[{card['name']}]({relative_path})"
        tasks = ", ".join(task.replace("-", " ") for task in card["tasks"])
        scale = compact_number(card["scale"]["samples"], card["scale"]["approximate"])
        access = f"[{dataset_access_label(card)}]({card['access']['url']})"
        commercial = card["license"]["commercial_use"].replace("-", " ")
        rows.append(
            f"| {name} | {card['organization']} | {card['modality']} | {card['released_at']} | "
            f"{tasks} | {scale} | {access} | {commercial} | {STATUS[card['status']]} |"
        )
    return "\n".join(rows)


def render_model_table() -> str:
    dataset_paths = {card["id"]: path for path, card in load_cards()}
    rows = [
        "| Model | Organization | Modalities | Released | Access | Data disclosure | Named datasets | Status |",
        "|---|---|---|---|---|---|---|:---:|",
    ]
    ordered = sorted(load_models(), key=lambda item: (item[1]["released_at"], item[1]["name"]), reverse=True)
    for path, model in ordered:
        model_path = path.relative_to(ROOT).as_posix()
        name = f"[{model['name']}]({model_path})"
        modalities = ", ".join(item for item in model["modalities"] if item != "multimodal")
        named_datasets: list[str] = []
        seen_dataset_labels: set[str] = set()
        for dataset in model["data"]["datasets"]:
            catalog_id = dataset["catalog_id"]
            if catalog_id and catalog_id in dataset_paths:
                target = dataset_paths[catalog_id].relative_to(ROOT).as_posix()
                label = f"[{dataset['name']}]({target})"
            else:
                label = dataset["name"]
            if label not in seen_dataset_labels:
                named_datasets.append(label)
                seen_dataset_labels.add(label)
        rows.append(
            "| "
            + " | ".join(
                [
                    name,
                    model["organization"],
                    modalities or "multimodal",
                    model["released_at"],
                    model["access"]["status"].replace("-", " "),
                    model["data"]["disclosure_level"].replace("-", " "),
                    ", ".join(named_datasets) or "not disclosed",
                    MODEL_STATUS[model["status"]],
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def render_project_metrics(locale: str = "en") -> str:
    cards = [card for _, card in load_cards()]
    models = [model for _, model in load_models()]
    model_relations = sum(
        1
        for model in models
        for dataset in model["data"]["datasets"]
        if dataset["catalog_id"] is not None
    )
    dataset_relations = sum(len(card.get("derived_from", [])) for card in cards)
    open_datasets = sum(card["access"]["status"] == "open" for card in cards)
    update_dates = [path.stem for path in (ROOT / "updates").glob("*.md")]
    latest_update = max(update_dates)

    if locale == "zh":
        headers = ["模型", "数据集", "模型与数据关系", "数据集衍生关系", "公开可访问", "最新核验"]
    else:
        headers = ["Models", "Datasets", "Model–dataset links", "Dataset lineage", "Open access", "Latest review"]
    values = [
        str(len(models)),
        str(len(cards)),
        str(model_relations),
        str(dataset_relations),
        str(open_datasets),
        latest_update,
    ]
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "|" + "|".join(":---:" for _ in headers) + "|",
            "| " + " | ".join(values) + " |",
        ]
    )


def replace_block(current: str, start: str, end: str, rendered: str) -> str:
    if start not in current or end not in current:
        raise ValueError(f"README.md must contain {start!r} and {end!r}")
    before, remainder = current.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{rendered}\n{end}{after}"


def generated_readme(current: str, locale: str = "en", catalogs: bool = True) -> str:
    with_metrics = replace_block(
        current,
        METRICS_START,
        METRICS_END,
        render_project_metrics(locale),
    )
    if not catalogs:
        return with_metrics
    with_datasets = replace_block(with_metrics, START, END, render_dataset_table())
    return replace_block(with_datasets, MODEL_START, MODEL_END, render_model_table())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if README.md is not up to date instead of writing it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = README_PATH.read_text(encoding="utf-8")
    expected = generated_readme(current)
    current_zh = ZH_README_PATH.read_text(encoding="utf-8")
    expected_zh = generated_readme(current_zh, locale="zh", catalogs=False)
    if args.check:
        if current != expected or current_zh != expected_zh:
            print("README files are stale; run `make readme`.", file=sys.stderr)
            return 1
        print("README files are up to date.")
        return 0

    README_PATH.write_text(expected, encoding="utf-8")
    ZH_README_PATH.write_text(expected_zh, encoding="utf-8")
    print(
        f"Updated README.md with {len(load_cards())} dataset card(s) "
        f"and {len(load_models())} model card(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
