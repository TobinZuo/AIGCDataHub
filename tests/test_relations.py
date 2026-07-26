from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from build_site_data import build_payload


class ModelDatasetRelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = build_payload()
        self.models = {item["id"]: item for item in self.payload["models"]}
        self.datasets = {item["id"]: item for item in self.payload["datasets"]}

    def test_relation_index_contains_every_resolved_model_reference(self) -> None:
        expected = sum(
            reference["catalog_id"] is not None
            for model in self.payload["models"]
            for reference in model["data"]["datasets"]
        )
        self.assertEqual(len(self.payload["relations"]), expected)

    def test_model_and_dataset_backlinks_are_symmetric(self) -> None:
        relation_pairs = {
            (relation["model_id"], relation["dataset_id"])
            for relation in self.payload["relations"]
        }
        for model_id, dataset_id in relation_pairs:
            with self.subTest(model=model_id, dataset=dataset_id):
                self.assertIn(dataset_id, self.models[model_id]["linked_dataset_ids"])
                self.assertIn(model_id, self.datasets[dataset_id]["linked_model_ids"])

    def test_representative_scenario_relations_are_navigable(self) -> None:
        self.assertIn("graphvid-bench", self.models["graphvid"]["linked_dataset_ids"])
        self.assertIn("graphvid", self.datasets["graphvid-bench"]["linked_model_ids"])
        self.assertIn("fit-vto-100k", self.models["fit-vto"]["linked_dataset_ids"])
        self.assertIn("fit-vto", self.datasets["fit-vto-100k"]["linked_model_ids"])
        self.assertIn("viton-hd-edit", self.models["ctrlvton"]["linked_dataset_ids"])
        self.assertIn("ctrlvton", self.datasets["viton-hd-edit"]["linked_model_ids"])
        self.assertIn("tripvvt-10k", self.models["tripvvt"]["linked_dataset_ids"])
        self.assertIn("tripvvt", self.datasets["tripvvt-10k"]["linked_model_ids"])
        self.assertIn(
            "audiovisual-translation-dub",
            self.models["just-dub-it"]["linked_dataset_ids"],
        )
        self.assertIn(
            "just-dub-it",
            self.datasets["audiovisual-translation-dub"]["linked_model_ids"],
        )

    def test_dataset_monitoring_is_joined_by_canonical_catalog_id(self) -> None:
        self.assertEqual(
            self.datasets["fit-vto-100k"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/Yuanhao-Harry-Wang/fitvto-100k",
            },
        )
        self.assertEqual(
            self.datasets["viton-hd-edit"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/NXN-Labs/VITON-HD-edit",
            },
        )
        self.assertEqual(
            self.datasets["tripvvt-10k"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/TripVVT/TripVVT-10K",
            },
        )
        self.assertEqual(self.datasets["finevideo"]["monitoring"]["priority"], "high")
        self.assertIsNone(self.datasets["graphvid-bench"]["monitoring"])


if __name__ == "__main__":
    unittest.main()
