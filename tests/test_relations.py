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
        self.assertEqual(len(self.payload["dataset_relations"]), 25)
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
        self.assertIn(("celebv-hq", "talkingheadbench"), relation_pairs)
        self.assertIn(("koala-36m", "phantom-data"), relation_pairs)
        self.assertIn(("openhumanvid", "humoset"), relation_pairs)
        self.assertIn(("senorita-2m", "videocof-50k"), relation_pairs)
        self.assertIn(("videomatte240k", "vera-layered-video"), relation_pairs)
        self.assertIn(("co3d", "considvid"), relation_pairs)
        self.assertIn(("omniobject3d", "considvid"), relation_pairs)
        self.assertIn(("objectron", "considvid"), relation_pairs)
        self.assertIn(("mvimgnet-2-0", "considvid"), relation_pairs)
        self.assertIn(("celebv-hq", "celebv-dub"), relation_pairs)
        self.assertIn(("celebv-text", "celebv-dub"), relation_pairs)
        self.assertIn(("voxceleb2", "holidub-bench"), relation_pairs)
        self.assertIn(("celebv-dub", "holidub-bench"), relation_pairs)

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
        self.assertEqual(
            self.models["omnitryon"]["linked_dataset_ids"],
            ["tryany-bench"],
        )
        self.assertIn("omnitryon", self.datasets["tryany-bench"]["linked_model_ids"])
        self.assertEqual(
            set(self.models["itryon"]["linked_dataset_ids"]),
            {"vivid", "vvt-interact"},
        )
        self.assertIn("itryon", self.datasets["vivid"]["linked_model_ids"])
        self.assertIn("itryon", self.datasets["vvt-interact"]["linked_model_ids"])
        self.assertIn(
            "audiovisual-translation-dub",
            self.models["just-dub-it"]["linked_dataset_ids"],
        )
        self.assertIn(
            "just-dub-it",
            self.datasets["audiovisual-translation-dub"]["linked_model_ids"],
        )
        self.assertEqual(
            set(self.models["voicecraft-dub"]["linked_dataset_ids"]),
            {"lrs3", "celebv-dub", "voxceleb2"},
        )
        self.assertEqual(
            set(self.models["holidubber"]["linked_dataset_ids"]),
            {"emilia", "voxceleb2", "celebv-dub", "holidub-bench"},
        )
        self.assertIn("voicecraft-dub", self.datasets["lrs3"]["linked_model_ids"])
        self.assertEqual(
            set(self.datasets["celebv-dub"]["linked_model_ids"]),
            {"voicecraft-dub", "holidubber"},
        )
        self.assertIn("holidubber", self.datasets["holidub-bench"]["linked_model_ids"])
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
        self.assertIn(
            "seedance-1-pro-human-preference",
            self.models["seedance-1-0-pro"]["linked_dataset_ids"],
        )
        self.assertIn(
            "seedance-1-0-pro",
            self.datasets["seedance-1-pro-human-preference"]["linked_model_ids"],
        )
        self.assertEqual(
            self.models["videocof"]["linked_dataset_ids"],
            ["videocof-50k"],
        )
        self.assertEqual(
            set(self.models["humo-17b"]["linked_dataset_ids"]),
            {"phantom-data", "humoset"},
        )
        self.assertEqual(
            self.models["phantom-wan-14b"]["linked_dataset_ids"],
            ["panda-70m"],
        )
        self.assertIn("videocof", self.datasets["videocof-50k"]["linked_model_ids"])
        self.assertIn("humo-17b", self.datasets["phantom-data"]["linked_model_ids"])
        self.assertIn("humo-17b", self.datasets["humoset"]["linked_model_ids"])
        self.assertIn("phantom-wan-14b", self.datasets["panda-70m"]["linked_model_ids"])
        self.assertEqual(
            set(self.models["consid-gen"]["linked_dataset_ids"]),
            {"co3d", "omniobject3d", "objectron", "mvimgnet-2-0", "considvid"},
        )
        self.assertIn("consid-gen", self.datasets["considvid"]["linked_model_ids"])
        self.assertEqual(
            set(self.models["vera-14b"]["linked_dataset_ids"]),
            {"vera-layered-video", "videomatte240k"},
        )
        self.assertEqual(
            set(self.models["mova-720p"]["linked_dataset_ids"]),
            {
                "autorecap-xl", "chronomagic-pro", "acav100m", "openhumanvid",
                "speakervid-5m", "openvid-1m", "vggsound", "wavcaps",
                "jamendomaxcaps", "avgen-bench",
            },
        )
        self.assertEqual(
            set(self.datasets["avgen-bench"]["linked_model_ids"]),
            {
                "emu3-5", "gemini-3-1-flash-image", "hunyuanvideo-foley",
                "kling-2-6", "ltx-2", "ltx-2-3", "mova-720p", "ovi",
                "seedance-1-5-pro", "seedance-2-0", "sora-2", "veo-3-1",
                "wan-2-2", "wan-2-6",
            },
        )
        self.assertEqual(
            set(self.models["emu3-5"]["linked_dataset_ids"]),
            {
                "imagenet", "open-images-v7", "conceptual-captions-3m",
                "conceptual-12m", "laion-5b", "textatlas5m",
                "postercraft-public-corpora", "coyo-700m", "datacomp-1b",
                "journeydb", "infinity-instruct", "avgen-bench",
            },
        )

    def test_dataset_monitoring_is_joined_by_canonical_catalog_id(self) -> None:
        self.assertEqual(
            sum(dataset["monitoring"] is not None for dataset in self.datasets.values()),
            len(self.datasets),
        )
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
        self.assertEqual(self.datasets["graphvid-bench"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["vggsound"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["audioset"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["videoufo"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["talkingheadbench"]["monitoring"]["priority"], "critical")
        self.assertEqual(
            self.datasets["maven-multicultural-video"]["monitoring"]["priority"],
            "critical",
        )
        self.assertEqual(
            self.datasets["seedance-1-pro-human-preference"]["monitoring"]["priority"],
            "high",
        )
        self.assertEqual(self.datasets["videocof-50k"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["phantom-data"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["senorita-2m"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["spatialvid"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["avgen-bench"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["vera-layered-video"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["videomatte240k"]["monitoring"]["priority"], "high")
        self.assertEqual(self.datasets["jamendomaxcaps"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["voxceleb2"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["lrs3"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["celebv-dub"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.datasets["holidub-bench"]["monitoring"]["priority"], "critical")
        self.assertEqual(
            self.datasets["humoset"]["monitoring"]["source_url"],
            "https://modelscope.cn/api/v1/datasets/leoniuschen/HuMoSet",
        )
        self.assertEqual(
            self.datasets["flickr-5b"]["monitoring"],
            {
                "priority": "critical",
                "source_url": "https://huggingface.co/api/datasets/bigdata-pw/Flickr",
                "mode": "availability",
            },
        )
        linked_without_probe = {
            dataset_id
            for dataset_id, dataset in self.datasets.items()
            if dataset["linked_model_ids"] and dataset["monitoring"] is None
        }
        self.assertEqual(linked_without_probe, set())

    def test_model_monitoring_is_joined_by_canonical_model_id(self) -> None:
        self.assertEqual(
            sum(model["monitoring"] is not None for model in self.models.values()),
            len(self.models),
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
        self.assertEqual(self.models["skyreels-v4"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["veo-3-1"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["pixverse-v6"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["flux-2-max"]["monitoring"]["priority"], "critical")
        ranked_model_ids = {
            model_id
            for board in self.payload["rankings"]
            for entry in board["entries"]
            for model_id in entry["model_ids"]
        }
        self.assertEqual(len(ranked_model_ids), 49)
        self.assertEqual(
            {
                model_id
                for model_id in ranked_model_ids
                if self.models[model_id]["monitoring"] is None
            },
            set(),
        )
        self.assertEqual(self.models["gpt-image-2"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["gemini-omni-flash"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["seedance-2-0"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["seedance-1-0-pro"]["monitoring"]["priority"], "high")
        self.assertEqual(self.models["videocof"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["humo-17b"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["phantom-wan-14b"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["mova-720p"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["vera-14b"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["graphvid"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["consid-gen"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["voicecraft-dub"]["monitoring"]["priority"], "critical")
        self.assertEqual(self.models["holidubber"]["monitoring"]["priority"], "critical")
        self.assertEqual(
            self.models["openve-edit"]["monitoring"]["source_url"],
            "https://github.com/OpenVE-Team/OpenVE-3M/commits/main.atom",
        )


if __name__ == "__main__":
    unittest.main()
