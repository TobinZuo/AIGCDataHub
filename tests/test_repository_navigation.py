from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RETIRED_HOST = "aigc-datahub-index.zuotongbin.chatgpt.site"


class RepositoryNavigationTests(unittest.TestCase):
    def test_readme_exposes_github_native_indexes_before_optional_pages(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        start_here = readme.index("## Start here on GitHub")
        dataset_index = readme.index("DATASET_ACCESS_INDEX.md")
        relationship_index = readme.index("MODEL_DATASET_INDEX.md")
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
