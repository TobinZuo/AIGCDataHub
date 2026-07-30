import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_changelog_data", ROOT / "scripts" / "build_changelog_data.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BuildChangelogDataTests(unittest.TestCase):
    def test_builds_newest_first_structured_history(self):
        payload = MODULE.build_payload()
        entries = payload["entries"]

        self.assertGreaterEqual(len(entries), 3)
        self.assertEqual([entry["date"] for entry in entries], sorted(
            (entry["date"] for entry in entries), reverse=True
        ))
        latest = entries[0]
        self.assertEqual(latest["date"], "2026-07-30")
        self.assertIn("排行榜变化", [section["title"] for section in latest["sections"]])
        self.assertIn("https://arxiv.org/abs/2607.21694", str(latest))

    def test_preserves_tables_and_subheadings(self):
        entries = MODULE.build_payload()["entries"]
        blocks = [
            block
            for entry in entries
            for section in entry["sections"]
            for block in section["blocks"]
        ]

        self.assertTrue(any(block["type"] == "table" for block in blocks))
        self.assertTrue(any(block["type"] == "subheading" for block in blocks))


if __name__ == "__main__":
    unittest.main()
