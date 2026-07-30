from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RETIRED_HOST = "aigc-datahub-index.zuotongbin.chatgpt.site"


class RepositoryNavigationTests(unittest.TestCase):
    def test_readme_leads_with_value_proof_and_bilingual_entry_points(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertLess(readme.index("site/public/og.png"), readme.index("## Start here on GitHub"))
        self.assertLess(readme.index("## Why AIGCDataHub"), readme.index("## Scope"))
        self.assertIn("Use the data in 60 seconds", readme)
        self.assertIn("README.zh-CN.md", readme)
        self.assertIn("从生成式 AI 模型，一路追到它的数据源头", chinese)
        self.assertIn("60 秒使用数据", chinese)
        self.assertIn("<!-- BEGIN PROJECT METRICS -->", readme)
        self.assertIn("<!-- BEGIN PROJECT METRICS -->", chinese)

    def test_readme_does_not_embed_stale_inventory_counts(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertNotIn("Fifty-four of the 55", readme)
        self.assertNotIn("All 40 distinct model cards", readme)
        self.assertNotIn("all 16 candidate source platforms", readme)
        self.assertNotIn("updates/2026-07-27.md", readme)
        self.assertNotIn("physical-AI models", readme)
        self.assertNotIn("Physical AI", chinese)

    def test_repository_exposes_community_health_and_citation_files(self) -> None:
        for name in ("CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md"):
            self.assertTrue((ROOT / name).is_file(), name)

        citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        self.assertEqual(citation["title"], "AIGCDataHub")
        self.assertEqual(citation["version"], "0.1.0")
        self.assertEqual(citation["license"], "Apache-2.0")

    def test_readme_exposes_github_native_indexes_before_optional_pages(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        start_here = readme.index("## Start here on GitHub")
        dataset_index = readme.index("DATASET_ACCESS_INDEX.md", start_here)
        relationship_index = readme.index("MODEL_DATASET_INDEX.md", start_here)
        optional_pages = readme.index("optional [interactive GitHub Pages view]")

        self.assertLess(start_here, dataset_index)
        self.assertLess(dataset_index, optional_pages)
        self.assertLess(relationship_index, optional_pages)

    def test_retired_preview_is_never_an_active_link(self) -> None:
        active_surfaces = [
            ROOT / "README.md",
            ROOT / "site" / "README.md",
            ROOT / "site" / "app" / "layout.tsx",
            ROOT / "site" / "app" / "catalog-explorer.tsx",
            ROOT / ".github" / "workflows" / "pages.yml",
        ]

        for path in active_surfaces:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(f"https://{RETIRED_HOST}", text, path)
            self.assertNotIn(f"http://{RETIRED_HOST}", text, path)

    def test_pages_metadata_and_workflow_use_the_github_origin(self) -> None:
        origin = "https://tobinzuo.github.io/AIGCDataHub"
        layout = (ROOT / "site" / "app" / "layout.tsx").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(f'const origin = "{origin}"', layout)
        self.assertIn("alternates: { canonical: origin }", layout)
        self.assertIn("actions/deploy-pages@v4", workflow)
        self.assertIn("branches:\n      - master", workflow)


if __name__ == "__main__":
    unittest.main()
