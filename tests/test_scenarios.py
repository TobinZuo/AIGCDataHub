from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from build_site_data import build_payload, load_scenarios, scenario_ids


class ScenarioTaxonomyTests(unittest.TestCase):
    def test_requested_scenarios_have_models_and_datasets(self) -> None:
        payload = build_payload()
        expected = {
            "image-generation",
            "video-generation",
            "digital-human",
            "video-localization",
            "virtual-try-on",
        }
        self.assertEqual({item["id"] for item in payload["scenarios"]}, expected)

        for scenario_id in expected:
            with self.subTest(scenario=scenario_id):
                self.assertTrue(any(scenario_id in item["scenario_ids"] for item in payload["models"]))
                self.assertTrue(any(scenario_id in item["scenario_ids"] for item in payload["datasets"]))

    def test_scenario_lineage_for_requested_application_models(self) -> None:
        payload = build_payload()
        models = {item["id"]: item for item in payload["models"]}
        datasets = {item["id"]: item for item in payload["datasets"]}

        self.assertIn("digital-human", models["avatar-v"]["scenario_ids"])
        self.assertTrue(
            {"digital-human", "video-localization"}.issubset(models["just-dub-it"]["scenario_ids"])
        )
        self.assertIn("virtual-try-on", models["fit-vto"]["scenario_ids"])
        self.assertIn("virtual-try-on", models["flux-vto"]["scenario_ids"])
        self.assertIn("video-localization", datasets["audiovisual-translation-dub"]["scenario_ids"])
        self.assertIn("virtual-try-on", datasets["fit-vto-100k"]["scenario_ids"])

    def test_generated_assignments_come_from_task_matches(self) -> None:
        scenarios = load_scenarios()
        self.assertEqual(
            scenario_ids(["virtual-try-on", "text-to-image"], scenarios),
            ["image-generation", "virtual-try-on"],
        )


if __name__ == "__main__":
    unittest.main()
