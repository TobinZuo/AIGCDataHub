#!/usr/bin/env python3
"""Validate the candidate content-source platform registry."""

from __future__ import annotations

import sys
from collections import Counter

from jsonschema import Draft202012Validator, FormatChecker

from source_platforms import (
    load_source_platform_registry,
    load_source_platform_schema,
    load_source_platforms,
)


def validate_source_platforms() -> list[str]:
    errors: list[str] = []
    try:
        registry = load_source_platform_registry()
    except Exception as exc:
        return [str(exc)]

    validator = Draft202012Validator(
        load_source_platform_schema(), format_checker=FormatChecker()
    )
    for issue in sorted(validator.iter_errors(registry), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
        errors.append(f"sources/source-platforms.yaml:{location}: {issue.message}")

    platforms = registry.get("platforms", [])
    for field in ("id", "homepage"):
        values = [item.get(field) for item in platforms if isinstance(item, dict)]
        for value, count in sorted(Counter(values).items(), key=lambda item: str(item[0])):
            if value is not None and count > 1:
                errors.append(f"duplicate source platform {field}: {value}")
    return errors


def main() -> int:
    errors = validate_source_platforms()
    if errors:
        print(f"Source-platform validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(load_source_platforms())} candidate source platform(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
