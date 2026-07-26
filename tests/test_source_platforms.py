from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from build_site_data import build_payload
from build_source_platform_index import OUTPUT_PATH, render_index
from source_platforms import load_source_platform_registry, load_source_platforms
from validate_source_platforms import validate_source_platforms


class SourcePlatformTests(unittest.TestCase):
    def test_registry_is_valid_and_contains_all_reference_platforms(self) -> None:
        self.assertEqual(validate_source_platforms(), [])
        self.assertEqual(load_source_platform_registry()["schema_version"], 2)
        platforms = load_source_platforms()
        self.assertEqual(len(platforms), 18)
        self.assertEqual(
            {item["id"] for item in platforms},
            {
                "youtube", "vimeo", "bilibili", "dailymotion", "netflix",
                "disney", "warner-bros", "paramount", "vcg", "shutterstock",
                "tuchong", "pexels", "mixkit", "tiktok-shop", "amazon", "shopee", "temu", "shein",
            },
        )

    def test_registry_preserves_dataset_and_publication_boundaries(self) -> None:
        registry = load_source_platform_registry()
        rendered = render_index()
        self.assertIn("not dataset releases", registry["policy"]["boundary"])
        self.assertIn("not provide a dataset download link", rendered)
        for platform in registry["platforms"]:
            self.assertEqual(platform["access_boundary"], "source-platform-not-dataset")
            self.assertEqual(platform["rights_review"], "required")
            self.assertEqual(
                platform["data_access"]["training_rights"],
                "not-granted-by-interface",
            )
            self.assertIn(platform["monitoring"]["mode"], {"content-revision", "availability"})
        for private_phrase in ("淘金", "额外人力", "公司内"):
            self.assertNotIn(private_phrase, rendered)

    def test_actionable_official_access_interfaces_are_cataloged(self) -> None:
        platforms = {item["id"]: item for item in load_source_platforms()}
        self.assertEqual(
            platforms["youtube"]["data_access"]["interface_url"],
            "https://developers.google.com/youtube/v3/docs",
        )
        self.assertEqual(
            platforms["amazon"]["data_access"]["interface_name"],
            "Amazon Creators API",
        )
        self.assertEqual(
            platforms["tuchong"]["data_access"]["status"],
            "licensed-service",
        )
        self.assertEqual(
            platforms["pexels"]["data_access"]["interface_name"],
            "Pexels API",
        )
        self.assertIn(
            "explicit Pexels permission",
            platforms["pexels"]["data_access"]["requirements"],
        )
        self.assertEqual(platforms["mixkit"]["data_access"]["status"], "licensed-service")
        self.assertIn("Free or Restricted", platforms["mixkit"]["data_access"]["requirements"])
        self.assertEqual(
            platforms["netflix"]["data_access"]["status"],
            "partner-portal",
        )
        self.assertIsNone(platforms["disney"]["data_access"]["interface_url"])

    def test_generated_index_and_site_payload_include_source_platforms(self) -> None:
        self.assertEqual(OUTPUT_PATH.read_text(encoding="utf-8"), render_index())
        payload = build_payload()
        self.assertEqual(len(payload["source_platforms"]), 18)
        self.assertEqual(
            {item["category"] for item in payload["source_platforms"]},
            {"video-platform", "streaming-and-studio", "stock-media", "ecommerce"},
        )
        dataset_ids = {item["id"] for item in payload["datasets"]}
        self.assertTrue(dataset_ids.isdisjoint(item["id"] for item in payload["source_platforms"]))


if __name__ == "__main__":
    unittest.main()
