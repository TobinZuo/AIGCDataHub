"""Shared model-card loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from catalog import ROOT


MODELS_ROOT = ROOT / "models"
MODEL_SCHEMA_PATH = ROOT / "schemas" / "model.schema.json"


def model_paths() -> list[Path]:
    return sorted(MODELS_ROOT.glob("**/*.yaml"))


def load_model(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        model = yaml.safe_load(stream)
    if not isinstance(model, dict):
        raise ValueError("top-level YAML value must be an object")
    return model


def load_models() -> list[tuple[Path, dict[str, Any]]]:
    return [(path, load_model(path)) for path in model_paths()]


def load_model_schema() -> dict[str, Any]:
    with MODEL_SCHEMA_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)

