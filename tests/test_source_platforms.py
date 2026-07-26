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
        platforms = load_source_platforms()
        self.assertEqual(len(platforms), 16)
        self.assertEqual(
            {item["id"] for item in platforms},
            {
                "youtube", "vimeo", "bilibili", "dailymotion", "netflix",
                "disney", "warner-bros", "paramount", "vcg", "shutterstock",
                "tuchong", "tiktok-shop", "amazon", "shopee", "temu", "shein",
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
        for private_phrase in ("淘金", "额外人力", "公司内"):
            self.assertNotIn(private_phrase, rendered)

    def test_generated_index_and_site_payload_include_source_platforms(self) -> None:
        self.assertEqual(OUTPUT_PATH.read_text(encoding="utf-8"), render_index())
        payload = build_payload()
        self.assertEqual(len(payload["source_platforms"]), 16)
        self.assertEqual(
            {item["category"] for item in payload["source_platforms"]},
            {"video-platform", "streaming-and-studio", "stock-media", "ecommerce"},
        )
        dataset_ids = {item["id"] for item in payload["datasets"]}
        self.assertTrue(dataset_ids.isdisjoint(item["id"] for item in payload["source_platforms"]))


if __name__ == "__main__":
    unittest.main()
