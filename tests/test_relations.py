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
        self.assertGreaterEqual(len(self.payload["relations"]), 26)

    def test_model_and_dataset_backlinks_are_symmetric(self) -> None:
        relation_pairs = {
            (relation["model_id"], relation["dataset_id"])
            for relation in self.payload["relations"]
        }
        for model_id, dataset_id in relation_pairs:
            with self.subTest(model=model_id, dataset=dataset_id):
                self.assertIn(dataset_id, self.models[model_id]["linked_dataset_ids"])
                self.assertIn(model_id, self.datasets[dataset_id]["linked_model_ids"])

    def test_dataset_lineage_index_and_backlinks_are_symmetric(self) -> None:
        self.assertEqual(len(self.payload["dataset_relations"]), 12)
        relation_pairs = {
            (relation["source_dataset_id"], relation["derived_dataset_id"])
            for relation in self.payload["dataset_relations"]
        }
        self.assertIn(("openhumanvid", "talkverse"), relation_pairs)
        self.assertIn(("panda-70m", "talkverse"), relation_pairs)
        self.assertIn(("openhumanvid", "openhumanvid-talking"), relation_pairs)
        self.assertIn(("audioset", "soundatlas"), relation_pairs)
        self.assertIn(("vggsound", "vggsound-omni"), relation_pairs)
        self.assertIn(("yfcc100m", "commoncatalog"), relation_pairs)
        self.assertIn(("mvhumannet", "mvhumannet-plus-plus"), relation_pairs)
        self.assertIn(("openve-3m", "openve-bench"), relation_pairs)

        for source_id, derived_id in relation_pairs:
            with self.subTest(source=source_id, derived=derived_id):
                self.assertIn(derived_id, self.datasets[source_id]["downstream_dataset_ids"])
                self.assertIn(source_id, self.datasets[derived_id]["upstream_dataset_ids"])

    def test_dataset_lineage_preserves_relationship_evidence(self) -> None:
        relation = next(
            item
            for item in self.payload["dataset_relations"]
            if item["source_dataset_id"] == "openhumanvid"
            and item["derived_dataset_id"] == "openhumanvid-talking"
        )
        self.assertEqual(relation["relationship"], "filtered-subset")
        self.assertIn("parts 001 through 040", relation["contribution"])
        self.assertIn("speech-active", relation["notes"])

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
        self.assertIn("talkverse", self.models["talkverse-5b"]["linked_dataset_ids"])
        self.assertIn("talkverse-5b", self.datasets["talkverse"]["linked_model_ids"])
        self.assertIn(
            "commoncatalog",
            self.models["commoncanvas-xl-c"]["linked_dataset_ids"],
        )
        self.assertIn(
            "commoncanvas-xl-c",
            self.datasets["commoncatalog"]["linked_model_ids"],
        )
        self.assertIn("gpic", self.models["gpic-baselines"]["linked_dataset_ids"])
        self.assertIn("gpic-baselines", self.datasets["gpic"]["linked_model_ids"])
        self.assertEqual(
            set(self.models["openve-edit"]["linked_dataset_ids"]),
            {"openve-3m", "openve-bench"},
        )
        self.assertEqual(
            set(self.models["hunyuanvideo-avatar"]["linked_dataset_ids"]),
            {"hdtf", "celebv-hq"},
        )
        self.assertIn("hunyuanvideo-avatar", self.datasets["celebv-hq"]["linked_model_ids"])
        self.assertIn("musetalk-1-5", self.datasets["hdtf"]["linked_model_ids"])

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
        self.assertEqual(
            self.datasets["talkverse"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/zhenzhiwang/TalkVerse",
            },
        )
        self.assertEqual(
            self.datasets["openhumanvid-talking"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/Haosonnn/OpenHumanVid-Talking",
            },
        )
        self.assertEqual(self.datasets["finevideo"]["monitoring"]["priority"], "high")
        self.assertEqual(self.datasets["koala-36m"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["freeman"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["commoncatalog"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["fine-t2i"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["gpic"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["openve-3m"]["monitoring"]["priority"], "critical")
        self.assertIsNone(self.datasets["graphvid-bench"]["monitoring"])

    def test_model_monitoring_is_joined_by_canonical_model_id(self) -> None:
        self.assertEqual(
            sum(model["monitoring"] is not None for model in self.models.values()),
            13,
        )
        self.assertEqual(
            self.models["hunyuanvideo-avatar"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/models/tencent/HunyuanVideo-Avatar",
            },
        )
        self.assertEqual(self.models["musetalk-1-5"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["fashn-vton-1-5"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["ltx-2-3"]["monitoring"]["priority"], "high")
        self.assertIsNone(self.models["graphvid"]["monitoring"])


if __name__ == "__main__":
    unittest.main()
