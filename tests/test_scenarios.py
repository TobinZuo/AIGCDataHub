from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from build_site_data import build_payload, load_scenarios, scenario_ids, strategy_profile


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
        self.assertTrue(
            {"video-generation", "digital-human", "video-localization"}.issubset(
                models["talkverse-5b"]["scenario_ids"]
            )
        )
        self.assertIn("virtual-try-on", models["fit-vto"]["scenario_ids"])
        self.assertIn("virtual-try-on", models["flux-vto"]["scenario_ids"])
        self.assertIn("virtual-try-on", models["ctrlvton"]["scenario_ids"])
        self.assertIn("virtual-try-on", models["tripvvt"]["scenario_ids"])
        self.assertIn("video-localization", datasets["audiovisual-translation-dub"]["scenario_ids"])
        self.assertIn("virtual-try-on", datasets["fit-vto-100k"]["scenario_ids"])
        self.assertIn("virtual-try-on", datasets["viton-hd-edit"]["scenario_ids"])
        self.assertIn("virtual-try-on", datasets["tripvvt-10k"]["scenario_ids"])
        self.assertTrue(
            {"video-generation", "digital-human"}.issubset(
                datasets["talkverse"]["scenario_ids"]
            )
        )
        self.assertIn("video-generation", datasets["openhumanvid"]["scenario_ids"])
        self.assertTrue(
            {"video-generation", "digital-human"}.issubset(
                datasets["openhumanvid-talking"]["scenario_ids"]
            )
        )

    def test_generated_assignments_come_from_task_matches(self) -> None:
        scenarios = load_scenarios()
        self.assertEqual(
            scenario_ids(["virtual-try-on", "text-to-image"], scenarios),
            ["image-generation", "virtual-try-on"],
        )

    def test_strategy_profiles_are_derived_from_model_cards(self) -> None:
        payload = build_payload()
        self.assertEqual(payload["format_version"], 11)
        models = {item["id"]: item for item in payload["models"]}

        for model in models.values():
            with self.subTest(model=model["id"]):
                self.assertEqual(model["strategy_profile"], strategy_profile(model))

    def test_strategy_profile_preserves_disclosure_boundaries(self) -> None:
        models = {item["id"]: item for item in build_payload()["models"]}

        fit_vto = models["fit-vto"]["strategy_profile"]
        self.assertEqual(fit_vto["stage_names"], ["pretraining", "fine-tuning"])
        self.assertEqual(
            fit_vto["source_types"],
            ["undisclosed", "synthetic", "public-dataset"],
        )
        self.assertEqual(fit_vto["data_reference_count"], 3)
        self.assertEqual(fit_vto["linked_dataset_count"], 1)
        self.assertEqual(fit_vto["scale_disclosed_stage_count"], 1)
        self.assertEqual(fit_vto["stage_count"], 2)

        flux_vto = models["flux-vto"]["strategy_profile"]
        self.assertEqual(flux_vto["source_types"], ["undisclosed"])
        self.assertEqual(flux_vto["data_reference_count"], 0)
        self.assertEqual(flux_vto["linked_dataset_count"], 0)
        self.assertEqual(flux_vto["scale_disclosed_stage_count"], 0)
        self.assertEqual(flux_vto["stage_count"], 2)

        ctrlvton = models["ctrlvton"]["strategy_profile"]
        self.assertEqual(ctrlvton["linked_dataset_count"], 1)
        self.assertEqual(ctrlvton["stage_count"], 4)
        self.assertTrue(
            {"source-mixing", "vlm-screening", "mask-conditioning"}.issubset(
                ctrlvton["operations"]
            )
        )

        tripvvt = models["tripvvt"]["strategy_profile"]
        self.assertEqual(tripvvt["linked_dataset_count"], 1)
        self.assertEqual(tripvvt["scale_disclosed_stage_count"], 3)
        self.assertTrue(
            {"synthetic-triplet-generation", "mixed-resolution-training"}.issubset(
                tripvvt["operations"]
            )
        )

        avatar_v = models["avatar-v"]["strategy_profile"]
        self.assertEqual(
            avatar_v["stage_names"],
            ["pretraining", "fine-tuning", "distillation", "preference"],
        )
        self.assertEqual(
            avatar_v["source_types"],
            ["public-web", "proprietary", "human-feedback", "synthetic"],
        )


if __name__ == "__main__":
    unittest.main()
