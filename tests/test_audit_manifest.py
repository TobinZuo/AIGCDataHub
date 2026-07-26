from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")

from audit_manifest import audit_manifest, render_markdown, select_rows, unflatten_csv_row
from catalog import ROOT


EXAMPLE = ROOT / "examples" / "manifests" / "tiny-multimodal.jsonl"


class ManifestAuditTests(unittest.TestCase):
    def test_example_report_is_complete(self) -> None:
        report = audit_manifest(EXAMPLE.relative_to(ROOT), sample_size=8, seed=20260726)
        self.assertEqual(report["input"]["rows_parsed"], 8)
        self.assertEqual(report["validation"]["valid_rate"], 1.0)
        self.assertEqual(report["coverage"]["provenance.core"]["rate"], 1.0)
        self.assertEqual(report["duplicates"]["sample_id"]["excess_rows"], 0)
        self.assertIn("Schema-valid rows: 100.0%", render_markdown(report))

    def test_bottom_k_sampling_is_independent_of_input_order(self) -> None:
        lines = EXAMPLE.read_text(encoding="utf-8").splitlines()
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.jsonl"
            second = Path(directory) / "second.jsonl"
            first.write_text("\n".join(lines) + "\n", encoding="utf-8")
            second.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
            rows_a, _ = select_rows(first, sample_size=3, seed=7)
            rows_b, _ = select_rows(second, sample_size=3, seed=7)
        ids_a = {row.value["sample_id"] for row in rows_a}
        ids_b = {row.value["sample_id"] for row in rows_b}
        self.assertEqual(ids_a, ids_b)

    def test_invalid_rows_are_reported_not_dropped(self) -> None:
        invalid = {"sample_id": "broken", "modality": "image"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.jsonl"
            path.write_text(json.dumps(invalid) + "\n", encoding="utf-8")
            report = audit_manifest(path, sample_size=None, seed=1)
        self.assertEqual(report["validation"]["invalid_rows"], 1)
        self.assertTrue(
            any("Resolve canonical row schema violations" in item for item in report["recommendations"])
        )

    def test_csv_dotted_fields_are_coerced(self) -> None:
        row = unflatten_csv_row(
            {
                "sample_id": "x",
                "properties.width": "1024",
                "properties.duration_seconds": "4.5",
                "quality.alignment": "0.91",
            }
        )
        self.assertEqual(row["properties"]["width"], 1024)
        self.assertEqual(row["properties"]["duration_seconds"], 4.5)
        self.assertEqual(row["quality"]["alignment"], 0.91)


if __name__ == "__main__":
    unittest.main()
