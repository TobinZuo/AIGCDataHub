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
        self.assertEqual(latest["date"], "2026-08-18")
        self.assertEqual(payload["format_version"], 3)
        self.assertEqual(
            [dimension["label"]["zh"] for dimension in latest["summary"]],
            ["模型", "数据集", "数据关系", "排行榜", "监控", "未披露"],
        )
        self.assertEqual(
            [dimension["label"]["en"] for dimension in latest["summary"]],
            ["Models", "Datasets", "Data relations", "Rankings", "Monitoring", "Undisclosed"],
        )
        self.assertIn("Marionette", latest["summary"][0]["text"]["zh"])
        self.assertIn("Marionette", latest["summary"][0]["text"]["en"])
        self.assertEqual(
            latest["summary"][0]["links"][0],
            {
                "href": "/#model-marionette",
                "label": {"zh": "Marionette", "en": "Marionette"},
            },
        )
        self.assertTrue(all(dimension["links"] for dimension in latest["summary"]))
        self.assertTrue(all(
            link["href"].startswith("/#") and set(link["label"]) == {"zh", "en"}
            for dimension in latest["summary"]
            for link in dimension["links"]
        ))

    def test_public_payload_contains_only_reader_summary_and_source_path(self):
        entries = MODULE.build_payload()["entries"]

        self.assertTrue(all(set(entry) == {"date", "title", "summary", "source_path"} for entry in entries))
        self.assertNotIn("Review window", str(entries))
        self.assertNotIn("Accepted changes", str(entries))


if __name__ == "__main__":
    unittest.main()
