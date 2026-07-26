"""Shared candidate content-source platform loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from catalog import ROOT


SOURCE_PLATFORM_PATH = ROOT / "sources" / "source-platforms.yaml"
SOURCE_PLATFORM_SCHEMA_PATH = ROOT / "schemas" / "source-platform.schema.json"


def load_source_platform_registry() -> dict[str, Any]:
    payload = yaml.safe_load(SOURCE_PLATFORM_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("sources/source-platforms.yaml must contain an object")
    return payload


def load_source_platforms() -> list[dict[str, Any]]:
    platforms = load_source_platform_registry().get("platforms")
    if not isinstance(platforms, list):
        raise ValueError("sources/source-platforms.yaml must contain platforms")
    return platforms


def load_source_platform_schema() -> dict[str, Any]:
    return json.loads(SOURCE_PLATFORM_SCHEMA_PATH.read_text(encoding="utf-8"))
