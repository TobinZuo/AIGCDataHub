#!/usr/bin/env python3
"""Audit a JSONL or CSV multimodal manifest without fetching media."""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

from catalog import ROOT


TOOL_VERSION = "0.2.0"
ROW_SCHEMA_PATH = ROOT / "schemas" / "sample-manifest.schema.json"
REPORT_SCHEMA_PATH = ROOT / "schemas" / "audit-report.schema.json"
MAX_EXAMPLES = 5


@dataclass
class InputStats:
    format: str
    rows_seen: int = 0
    rows_parsed: int = 0
    blank_rows: int = 0
    parse_errors: int = 0
    parse_error_examples: list[dict[str, Any]] = field(default_factory=list)

    def add_error(self, line: int, error: str) -> None:
        self.parse_errors += 1
        if len(self.parse_error_examples) < MAX_EXAMPLES:
            self.parse_error_examples.append({"line": line, "error": error})


@dataclass(frozen=True)
class SelectedRow:
    line: int
    score: int
    value: dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def manifest_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    raise ValueError("manifest must use .jsonl, .ndjson, or .csv")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def coerce_csv_value(path: str, value: str) -> Any:
    integer_fields = {"media.bytes", "properties.width", "properties.height"}
    float_fields = {"properties.duration_seconds", "properties.fps"}
    if path in integer_fields:
        return int(value)
    if path in float_fields or path.startswith("quality."):
        return float(value)
    return value


def unflatten_csv_row(flat: dict[str, str | None]) -> dict[str, Any]:
    nested: dict[str, Any] = {}
    for raw_key, raw_value in flat.items():
        if raw_key is None:
            raise ValueError("row contains more values than the CSV header")
        key = raw_key.strip()
        value = raw_value.strip() if isinstance(raw_value, str) else ""
        if not key or not value:
            continue
        cursor = nested
        parts = key.split(".")
        for part in parts[:-1]:
            child = cursor.setdefault(part, {})
            if not isinstance(child, dict):
                raise ValueError(f"CSV columns conflict at {key!r}")
            cursor = child
        cursor[parts[-1]] = coerce_csv_value(key, value)
    return nested


def iter_jsonl(path: Path, stats: InputStats) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if not raw_line.strip():
                stats.blank_rows += 1
                continue
            stats.rows_seen += 1
            try:
                value = json.loads(raw_line)
                if not isinstance(value, dict):
                    raise ValueError("top-level JSON value must be an object")
            except (json.JSONDecodeError, ValueError) as exc:
                stats.add_error(line_number, str(exc))
                continue
            stats.rows_parsed += 1
            yield line_number, value


def iter_csv(path: Path, stats: InputStats) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV manifest has no header")
        for line_number, flat in enumerate(reader, start=2):
            stats.rows_seen += 1
            try:
                value = unflatten_csv_row(flat)
            except (TypeError, ValueError) as exc:
                stats.add_error(line_number, str(exc))
                continue
            stats.rows_parsed += 1
            yield line_number, value


def iter_manifest(path: Path, stats: InputStats) -> Iterator[tuple[int, dict[str, Any]]]:
    if stats.format == "jsonl":
        yield from iter_jsonl(path, stats)
    else:
        yield from iter_csv(path, stats)


def sampling_score(row: dict[str, Any], seed: int) -> int:
    canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    sample_id = row.get("sample_id")
    identity = f"{sample_id if isinstance(sample_id, str) else ''}\0{canonical}"
    digest = hashlib.sha256(f"{seed}\0{identity}".encode()).digest()
    return int.from_bytes(digest, "big")


def select_rows(
    path: Path, sample_size: int | None, seed: int
) -> tuple[list[SelectedRow], InputStats]:
    stats = InputStats(format=manifest_format(path))
    if sample_size is None:
        selected = [
            SelectedRow(line=line, score=sampling_score(row, seed), value=row)
            for line, row in iter_manifest(path, stats)
        ]
        return sorted(selected, key=lambda item: (item.score, item.line)), stats

    # The heap retains only the bottom-k hashes, keeping memory bounded by the
    # requested sample size even when scanning a very large manifest.
    heap: list[tuple[int, int, int, dict[str, Any]]] = []
    for line, row in iter_manifest(path, stats):
        score = sampling_score(row, seed)
        entry = (-score, -line, line, row)
        if len(heap) < sample_size:
            heapq.heappush(heap, entry)
        elif entry[:2] > heap[0][:2]:
            heapq.heapreplace(heap, entry)

    selected = [
        SelectedRow(line=line, score=-negative_score, value=row)
        for negative_score, _, line, row in heap
    ]
    return sorted(selected, key=lambda item: (item.score, item.line)), stats


def deep_get(row: dict[str, Any], dotted_path: str) -> Any:
    value: Any = row
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def clean_number(value: float) -> int | float:
    rounded = round(value, 4)
    return int(rounded) if rounded.is_integer() else rounded


def percentile(values: list[float], quantile: float) -> int | float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return clean_number(ordered[lower])
    interpolated = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return clean_number(interpolated)


def numeric_stats(values: list[float]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "p50": None, "p95": None, "max": None, "mean": None}
    return {
        "count": len(values),
        "min": clean_number(min(values)),
        "p50": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
        "max": clean_number(max(values)),
        "mean": clean_number(sum(values) / len(values)),
    }


def sorted_counts(counter: Counter[str], limit: int | None = None) -> dict[str, int]:
    pairs = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    if limit is not None:
        pairs = pairs[:limit]
    return dict(pairs)


def duplicate_summary(values: list[str]) -> dict[str, Any]:
    counts = Counter(values)
    duplicates = [(value, count) for value, count in counts.items() if count > 1]
    duplicates.sort(key=lambda item: (-item[1], item[0]))
    return {
        "duplicate_values": len(duplicates),
        "excess_rows": sum(count - 1 for _, count in duplicates),
        "examples": [{"value": value, "rows": count} for value, count in duplicates[:MAX_EXAMPLES]],
    }


def numeric_values(rows: list[SelectedRow], path: str) -> list[float]:
    result: list[float] = []
    for selected in rows:
        value = deep_get(selected.value, path)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            result.append(float(value))
    return result


def field_coverage(rows: list[SelectedRow], path: str) -> dict[str, int | float]:
    present = sum(is_present(deep_get(selected.value, path)) for selected in rows)
    return {"present_rows": present, "rate": rate(present, len(rows))}


def count_values(rows: list[SelectedRow], path: str) -> Counter[str]:
    values: Counter[str] = Counter()
    for selected in rows:
        value = deep_get(selected.value, path)
        if is_present(value):
            values[str(value)] += 1
    return values


def url_distribution(rows: list[SelectedRow], path: str) -> tuple[Counter[str], Counter[str]]:
    schemes: Counter[str] = Counter()
    hosts: Counter[str] = Counter()
    for selected in rows:
        value = deep_get(selected.value, path)
        if not isinstance(value, str) or not value.strip():
            continue
        parsed = urlparse(value)
        schemes[parsed.scheme.lower() or "local"] += 1
        if parsed.hostname:
            hosts[parsed.hostname.lower()] += 1
    return schemes, hosts


def aspect_ratio_distribution(rows: list[SelectedRow]) -> Counter[str]:
    result: Counter[str] = Counter()
    for selected in rows:
        width = deep_get(selected.value, "properties.width")
        height = deep_get(selected.value, "properties.height")
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)) or height <= 0:
            continue
        ratio_value = width / height
        if ratio_value < 0.8:
            result["portrait"] += 1
        elif ratio_value <= 1.2:
            result["square"] += 1
        elif ratio_value <= 2.0:
            result["landscape"] += 1
        else:
            result["panoramic"] += 1
    return result


def quality_distributions(rows: list[SelectedRow]) -> dict[str, dict[str, int | float | None]]:
    keys: set[str] = set()
    for selected in rows:
        quality = selected.value.get("quality")
        if isinstance(quality, dict):
            keys.update(str(key) for key in quality)
    return {key: numeric_stats(numeric_values(rows, f"quality.{key}")) for key in sorted(keys)}


def validate_rows(rows: list[SelectedRow]) -> dict[str, Any]:
    validator = Draft202012Validator(load_json(ROW_SCHEMA_PATH), format_checker=FormatChecker())
    valid_rows = 0
    error_counts: Counter[str] = Counter()
    invalid_examples: list[dict[str, Any]] = []
    for selected in rows:
        issues = sorted(validator.iter_errors(selected.value), key=lambda issue: list(issue.path))
        if not issues:
            valid_rows += 1
            continue
        rendered: list[str] = []
        for issue in issues:
            location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
            error_counts[location] += 1
            rendered.append(f"{location}: {issue.message}")
        if len(invalid_examples) < MAX_EXAMPLES:
            invalid_examples.append({"line": selected.line, "errors": rendered})
    invalid_rows = len(rows) - valid_rows
    return {
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "valid_rate": rate(valid_rows, len(rows)),
        "error_counts": sorted_counts(error_counts),
        "invalid_examples": invalid_examples,
    }


def recommendations(
    stats: InputStats,
    validation: dict[str, Any],
    coverage: dict[str, dict[str, int | float]],
    duplicates: dict[str, dict[str, Any]],
) -> list[str]:
    result: list[str] = []
    if stats.parse_errors:
        result.append("Fix manifest parse errors before relying on downstream counts.")
    if validation["valid_rate"] < 1:
        result.append("Resolve canonical row schema violations or document a schema mapping step.")
    if coverage["provenance.core"]["rate"] < 1:
        result.append("Preserve dataset ID, source URL, license, and takedown identity for every sample.")
    if coverage["caption.text"]["rate"] < 1:
        result.append("Separate missing captions from empty captions and define a recaptioning policy.")
    if duplicates["sample_id"]["excess_rows"]:
        result.append("Make sample IDs unique before deterministic splitting or sharding.")
    if duplicates["media.sha256"]["excess_rows"]:
        result.append("Review exact media duplicates and decide whether repeated captions are intentional.")
    if not result:
        result.append("No manifest-level issues triggered; proceed to media access and decode probes.")
    return result


def audit_manifest(path: Path, sample_size: int | None, seed: int) -> dict[str, Any]:
    rows, stats = select_rows(path, sample_size, seed)
    selected_count = len(rows)
    validation = validate_rows(rows)

    coverage_paths = [
        "sample_id",
        "media.uri",
        "media.sha256",
        "media.mime_type",
        "caption.text",
        "caption.source",
        "caption.language",
        "provenance.dataset_id",
        "provenance.source_url",
        "provenance.license",
        "provenance.takedown_id",
        "provenance.collected_at",
        "properties.width",
        "properties.height",
        "properties.duration_seconds",
        "properties.fps",
    ]
    coverage = {path_name: field_coverage(rows, path_name) for path_name in coverage_paths}
    core_provenance_fields = (
        "provenance.dataset_id",
        "provenance.source_url",
        "provenance.license",
        "provenance.takedown_id",
    )
    core_count = sum(
        all(is_present(deep_get(selected.value, path_name)) for path_name in core_provenance_fields)
        for selected in rows
    )
    coverage["provenance.core"] = {"present_rows": core_count, "rate": rate(core_count, selected_count)}

    duplicate_fields = {
        "sample_id": "sample_id",
        "media.uri": "media.uri",
        "media.sha256": "media.sha256",
    }
    duplicates = {
        name: duplicate_summary(
            [
                str(value)
                for selected in rows
                if is_present(value := deep_get(selected.value, path_name))
            ]
        )
        for name, path_name in duplicate_fields.items()
    }

    media_schemes, media_hosts = url_distribution(rows, "media.uri")
    source_schemes, source_hosts = url_distribution(rows, "provenance.source_url")
    caption_lengths = [
        float(len(value))
        for selected in rows
        if isinstance(value := deep_get(selected.value, "caption.text"), str)
    ]

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "tool": {"name": "aigcdatahub-manifest-audit", "version": TOOL_VERSION},
        "input": {
            "path": path.as_posix(),
            "format": stats.format,
            "sha256": file_sha256(path),
            "rows_seen": stats.rows_seen,
            "rows_parsed": stats.rows_parsed,
            "blank_rows": stats.blank_rows,
            "parse_errors": stats.parse_errors,
            "parse_error_examples": stats.parse_error_examples,
        },
        "sampling": {
            "algorithm": "sha256-bottom-k-v1",
            "seed": seed,
            "requested_rows": sample_size,
            "selected_rows": selected_count,
        },
        "validation": validation,
        "coverage": coverage,
        "duplicates": duplicates,
        "distributions": {
            "modality": sorted_counts(count_values(rows, "modality")),
            "caption_source": sorted_counts(count_values(rows, "caption.source")),
            "caption_language": sorted_counts(count_values(rows, "caption.language")),
            "caption_characters": numeric_stats(caption_lengths),
            "media_scheme": sorted_counts(media_schemes),
            "media_host": sorted_counts(media_hosts, limit=20),
            "source_scheme": sorted_counts(source_schemes),
            "source_host": sorted_counts(source_hosts, limit=20),
            "license": sorted_counts(count_values(rows, "provenance.license")),
            "width": numeric_stats(numeric_values(rows, "properties.width")),
            "height": numeric_stats(numeric_values(rows, "properties.height")),
            "aspect_ratio_bucket": sorted_counts(aspect_ratio_distribution(rows)),
            "duration_seconds": numeric_stats(numeric_values(rows, "properties.duration_seconds")),
            "fps": numeric_stats(numeric_values(rows, "properties.fps")),
            "media_bytes": numeric_stats(numeric_values(rows, "media.bytes")),
            "quality": quality_distributions(rows),
        },
        "recommendations": [],
    }
    report["recommendations"] = recommendations(stats, validation, coverage, duplicates)

    report_validator = Draft202012Validator(load_json(REPORT_SCHEMA_PATH), format_checker=FormatChecker())
    report_validator.validate(report)
    return report


def format_rate(value: Any) -> str:
    return f"{float(value) * 100:.1f}%"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Manifest audit report",
        "",
        f"- Input: `{report['input']['path']}`",
        f"- SHA-256: `{report['input']['sha256']}`",
        f"- Rows parsed: {report['input']['rows_parsed']:,} / {report['input']['rows_seen']:,}",
        f"- Rows selected: {report['sampling']['selected_rows']:,}",
        f"- Sampling: `{report['sampling']['algorithm']}` with seed `{report['sampling']['seed']}`",
        f"- Schema-valid rows: {format_rate(report['validation']['valid_rate'])}",
        "",
        "## Field coverage",
        "",
        "| Field | Present | Coverage |",
        "|---|---:|---:|",
    ]
    for field_name, values in report["coverage"].items():
        lines.append(
            f"| `{field_name}` | {values['present_rows']:,} | {format_rate(values['rate'])} |"
        )

    lines.extend(["", "## Duplicates", "", "| Identity | Duplicate values | Excess rows |", "|---|---:|---:|"])
    for field_name, values in report["duplicates"].items():
        lines.append(f"| `{field_name}` | {values['duplicate_values']:,} | {values['excess_rows']:,} |")

    lines.extend(["", "## Key distributions", ""])
    for name in ("modality", "caption_source", "caption_language", "media_scheme", "license"):
        values = report["distributions"][name]
        rendered = ", ".join(f"{key}={count:,}" for key, count in values.items()) or "none"
        lines.append(f"- **{name.replace('_', ' ').title()}:** {rendered}")

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.extend(
        [
            "",
            "This report covers manifest metadata only. It does not prove media availability,",
            "decode integrity, safety, semantic alignment, or legal fitness for use.",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_check(path: Path, content: str, check: bool) -> bool:
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if declared output files are stale")
    parser.add_argument("--fail-on-invalid", action="store_true")
    parser.add_argument("--min-provenance-coverage", type=float)
    args = parser.parse_args()
    if args.sample_size is not None and args.sample_size < 1:
        parser.error("--sample-size must be at least 1")
    if args.check and not (args.json_out or args.markdown_out):
        parser.error("--check requires --json-out and/or --markdown-out")
    if args.min_provenance_coverage is not None and not 0 <= args.min_provenance_coverage <= 1:
        parser.error("--min-provenance-coverage must be between 0 and 1")
    return args


def main() -> int:
    args = parse_args()
    try:
        report = audit_manifest(args.manifest, args.sample_size, args.seed)
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1

    json_content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    markdown_content = render_markdown(report)
    outputs_current = True
    if args.json_out:
        outputs_current &= write_or_check(args.json_out, json_content, args.check)
    if args.markdown_out:
        outputs_current &= write_or_check(args.markdown_out, markdown_content, args.check)
    if not args.json_out and not args.markdown_out:
        print(json_content, end="")
    elif args.check and not outputs_current:
        print("Audit output is stale; regenerate it without --check.", file=sys.stderr)
        return 1
    else:
        action = "Checked" if args.check else "Wrote"
        print(f"{action} manifest audit for {report['sampling']['selected_rows']} selected row(s).")

    policy_failed = False
    if args.fail_on_invalid and (
        report["input"]["parse_errors"] or report["validation"]["invalid_rows"]
    ):
        print("Policy failed: manifest contains parse or schema errors.", file=sys.stderr)
        policy_failed = True
    if args.min_provenance_coverage is not None:
        actual = report["coverage"]["provenance.core"]["rate"]
        if actual < args.min_provenance_coverage:
            print(
                f"Policy failed: provenance coverage {actual:.4f} is below "
                f"{args.min_provenance_coverage:.4f}.",
                file=sys.stderr,
            )
            policy_failed = True
    return 2 if policy_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

