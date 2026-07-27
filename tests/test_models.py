from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")

from models import load_models
from build_readme import render_model_table
from build_model_dataset_index import render_index
from validate_models import validate_models


class ModelCatalogTests(unittest.TestCase):
    def test_model_catalog_is_valid(self) -> None:
        self.assertEqual(validate_models(), [])

    def test_seedance_1_records_public_data_strategy_and_external_evaluation(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        seedance = cards["seedance-1-0-pro"]
        self.assertEqual(seedance["data"]["disclosure_level"], "high-level")
        self.assertFalse(seedance["data"]["exact_datasets_disclosed"])
        self.assertIn(
            "seedance-1-pro-human-preference",
            {item["catalog_id"] for item in seedance["data"]["datasets"]},
        )
        operations = {
            operation
            for stage in seedance["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertTrue(
            {
                "shot-boundary-detection",
                "dense-video-captioning",
                "video-rlhf",
                "trajectory-segmented-consistency-distillation",
            }.issubset(operations)
        )

    def test_representative_modalities_are_present(self) -> None:
        cards = [card for _, card in load_models()]
        modalities = {modality for card in cards for modality in card["modalities"]}
        self.assertGreaterEqual(len(cards), 58)
        self.assertTrue({"image", "video", "audio", "multimodal"}.issubset(modalities))

    def test_product_only_releases_are_representable(self) -> None:
        cards = [card for _, card in load_models()]
        self.assertTrue(any(card["access"]["status"] == "product-only" for card in cards))

    def test_top_ranked_open_and_closed_model_versions_are_cataloged(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        self.assertTrue(
            {
                "gpt-image-2",
                "reve-2-1",
                "mai-image-2-5",
                "gemini-3-1-flash-image",
                "gpt-image-1-5",
                "gemini-3-pro-image",
                "wan-2-7",
                "happyhorse-1-1",
                "happyhorse-1-0",
                "grok-imagine-video-1-5",
                "runway-aleph-2",
                "kling-3",
                "seedream-5-0-pro",
                "grok-imagine-image-quality",
                "hunyuanimage-3-instruct",
                "luma-uni-1-max",
                "hidream-o1-image-1-5",
                "cosmos3-super-text2image",
                "veo-3-1",
                "skyreels-v4",
                "grok-imagine-video",
                "grok-imagine-image",
                "kling-o1",
                "hidream-o1-image",
                "pixverse-v6",
                "vidu-q3-pro",
                "recraft-v4-1",
                "flux-2-max",
                "veo-3-1-lite",
                "videocof",
                "humo-17b",
                "phantom-wan-14b",
                "seedance-1-5-pro",
                "kling-2-6",
                "ltx-2",
                "emu3-5",
                "wan-2-2",
                "hunyuanvideo-foley",
                "ovi",
            }.issubset(cards)
        )
        self.assertIn("GPT Image 2 (high)", cards["gpt-image-2"]["ranking_names"])
        self.assertIn("HappyHorse-1.0", cards["happyhorse-1-0"]["ranking_names"])
        self.assertIn("Kling Image 3.0 Omni", cards["kling-3"]["ranking_names"])
        self.assertIn("Recraft V4.1 Utility Pro", cards["recraft-v4-1"]["ranking_names"])

    def test_phantom_wan_links_only_disclosed_training_sources(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        phantom = cards["phantom-wan-14b"]
        self.assertEqual(
            {item["catalog_id"] for item in phantom["data"]["datasets"]},
            {"panda-70m", None},
        )
        self.assertNotIn(
            "phantom-data",
            {item["catalog_id"] for item in phantom["data"]["datasets"]},
        )
        self.assertEqual(phantom["access"]["status"], "open-weights")
        self.assertEqual(phantom["architecture"]["parameters"], 14000000000)

    def test_skyreels_disclosed_public_data_resolves_to_download_cards(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        linked = {
            item["catalog_id"]
            for item in cards["skyreels-v4"]["data"]["datasets"]
            if item["catalog_id"]
        }
        self.assertEqual(
            linked,
            {
                "re-laion-5b",
                "flickr-5b",
                "webvid-10m",
                "koala-36m",
                "openhumanvid",
                "emilia",
                "audioset",
                "vggsound",
                "soundnet",
            },
        )

    def test_public_and_gated_named_data_always_resolve_to_catalog_cards(self) -> None:
        for _, card in load_models():
            for reference in card["data"]["datasets"]:
                if reference["availability"] in {"public", "gated"}:
                    with self.subTest(model=card["id"], dataset=reference["name"]):
                        self.assertIsNotNone(reference["catalog_id"])

    def test_repository_model_dataset_index_is_current_and_explains_missing_cards(self) -> None:
        rendered = render_index()
        self.assertEqual(rendered, Path("MODEL_DATASET_INDEX.md").read_text(encoding="utf-8"))
        self.assertIn("publisher has not released it", rendered)
        self.assertIn("exact source is not disclosed", rendered)
        self.assertIn("models/image/gpt-image-2.yaml", rendered)

    def test_readme_model_summary_deduplicates_multi_role_dataset_names(self) -> None:
        row = next(
            line for line in render_model_table().splitlines()
            if "[OmniTryOn](models/video/omnitryon.yaml)" in line
        )
        self.assertEqual(row.count("[TryAny-Bench](catalog/video/tryany-bench.yaml)"), 1)

    def test_every_model_records_unknowns(self) -> None:
        for _, card in load_models():
            with self.subTest(card=card["id"]):
                self.assertTrue(card["data"]["unknowns"])

    def test_current_image_and_video_models_record_data_operations(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        omni_ops = set(cards["gemini-omni-flash"]["data"]["stages"][0]["operations"])
        image_stages = cards["gemini-3-1-flash-lite-image"]["data"]["stages"]
        image_ops = {operation for stage in image_stages for operation in stage["operations"]}
        mage_ops = {
            operation
            for stage in cards["mage-flow"]["data"]["stages"]
            for operation in stage["operations"]
        }

        self.assertTrue({"multilevel-captioning", "semantic-deduplication"}.issubset(omni_ops))
        self.assertTrue({"dataset-filtering", "human-preference-alignment", "critic-feedback"}.issubset(image_ops))
        self.assertTrue({"multi-granularity-captioning", "concept-balanced-sampling", "diffusion-nft"}.issubset(mage_ops))

    def test_digital_human_and_video_localization_lineage(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        avatar_stages = {stage["name"] for stage in cards["avatar-v"]["data"]["stages"]}
        just_dub_it_ids = {item["catalog_id"] for item in cards["just-dub-it"]["data"]["datasets"]}
        talkverse_ids = {item["catalog_id"] for item in cards["talkverse-5b"]["data"]["datasets"]}
        voicecraft_ids = {item["catalog_id"] for item in cards["voicecraft-dub"]["data"]["datasets"]}
        holidubber_ids = {item["catalog_id"] for item in cards["holidubber"]["data"]["datasets"]}
        talkverse_ops = {
            operation
            for stage in cards["talkverse-5b"]["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertEqual(avatar_stages, {"pretraining", "fine-tuning", "distillation", "preference"})
        self.assertEqual(just_dub_it_ids, {None, "audiovisual-translation-dub"})
        self.assertEqual(talkverse_ids, {None, "talkverse"})
        self.assertEqual(voicecraft_ids, {None, "lrs3", "celebv-dub", "voxceleb2"})
        self.assertEqual(
            holidubber_ids,
            {None, "emilia", "voxceleb2", "celebv-dub", "holidub-bench"},
        )
        self.assertEqual(cards["voicecraft-dub"]["access"]["status"], "open-weights")
        self.assertEqual(cards["holidubber"]["access"]["status"], "announced")
        self.assertTrue(cards["holidubber"]["data"]["stages"][1]["scale_disclosed"])
        self.assertTrue(
            {
                "audio-video-sync-filtering",
                "audio-style-captioning",
                "pose-extraction",
                "roi-loss-weighting",
            }.issubset(talkverse_ops)
        )
        self.assertTrue(cards["talkverse-5b"]["data"]["stages"][1]["scale_disclosed"])

        self.assertEqual(
            {item["catalog_id"] for item in cards["diflowdubber"]["data"]["datasets"]},
            {"libritts", "chem", "grid"},
        )
        self.assertEqual(
            {item["catalog_id"] for item in cards["funcineforge"]["data"]["datasets"]},
            {"cinedub-cn", "v2c-animation", "chem", "grid"},
        )
        self.assertEqual(
            {item["catalog_id"] for item in cards["unisync"]["data"]["datasets"]},
            {"unisync-5k", "hdtf", "realworld-lipsync"},
        )
        self.assertEqual(cards["funcineforge"]["access"]["status"], "open-weights")
        self.assertEqual(cards["diflowdubber"]["access"]["status"], "announced")
        self.assertEqual(cards["unisync"]["access"]["status"], "announced")
        self.assertIn(
            "facodec-tokenization",
            cards["diflowdubber"]["data"]["stages"][0]["operations"],
        )
        self.assertIn(
            "multimodal-cot-correction",
            cards["funcineforge"]["data"]["stages"][0]["operations"],
        )
        self.assertIn(
            "pose-anchored-fidelity-training",
            cards["unisync"]["data"]["stages"][0]["operations"],
        )

        hunyuan_ids = {item["catalog_id"] for item in cards["hunyuanvideo-avatar"]["data"]["datasets"]}
        musetalk_ids = {item["catalog_id"] for item in cards["musetalk-1-5"]["data"]["datasets"]}
        self.assertEqual(hunyuan_ids, {None, "hdtf", "celebv-hq"})
        self.assertEqual(musetalk_ids, {None, "hdtf"})
        self.assertTrue(cards["hunyuanvideo-avatar"]["data"]["stages"][1]["scale_disclosed"])
        self.assertIn(
            "audio-video-sync-filtering",
            cards["hunyuanvideo-avatar"]["data"]["stages"][1]["operations"],
        )
        self.assertIn(
            "dynamic-margin-sampling",
            cards["musetalk-1-5"]["data"]["stages"][1]["operations"],
        )

    def test_virtual_try_on_records_disclosed_and_undisclosed_strategies(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        fit_ids = {item["catalog_id"] for item in cards["fit-vto"]["data"]["datasets"]}
        ctrlvton_ids = {item["catalog_id"] for item in cards["ctrlvton"]["data"]["datasets"]}
        tripvvt_ids = {item["catalog_id"] for item in cards["tripvvt"]["data"]["datasets"]}
        self.assertEqual(fit_ids, {None, "fit-vto-100k"})
        self.assertEqual(ctrlvton_ids, {None, "viton-hd-edit"})
        self.assertEqual(tripvvt_ids, {None, "tripvvt-10k"})
        self.assertEqual(cards["fit-vto"]["data"]["disclosure_level"], "partial")
        self.assertEqual(cards["ctrlvton"]["data"]["disclosure_level"], "partial")
        self.assertEqual(cards["tripvvt"]["data"]["disclosure_level"], "partial")
        self.assertEqual(cards["flux-vto"]["data"]["disclosure_level"], "undisclosed")
        self.assertEqual(cards["flux-vto"]["data"]["datasets"], [])
        self.assertEqual(
            {item["catalog_id"] for item in cards["fashn-vton-1-5"]["data"]["datasets"]},
            {None},
        )

        ctrlvton_ops = {
            operation
            for stage in cards["ctrlvton"]["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertTrue(
            {"vlm-screening", "human-review", "mask-conditioning"}.issubset(ctrlvton_ops)
        )
        self.assertEqual(
            [stage["scale_disclosed"] for stage in cards["tripvvt"]["data"]["stages"]],
            [False, True, True, True],
        )
        fashn_ops = {
            operation
            for stage in cards["fashn-vton-1-5"]["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertTrue({"synthetic-triplet-generation", "token-dropping"}.issubset(fashn_ops))
        self.assertTrue(all(stage["scale_disclosed"] for stage in cards["fashn-vton-1-5"]["data"]["stages"]))

    def test_released_dataset_lineage_is_resolved(self) -> None:
        omni2sound = next(card for card in [item for _, item in load_models()] if card["id"] == "omni2sound")
        linked_ids = {item["catalog_id"] for item in omni2sound["data"]["datasets"]}
        self.assertEqual(
            linked_ids,
            {
                "audiocaps-2-0",
                "wavcaps",
                "clotho-2-1",
                "audioset",
                "vggsound",
                "fsd50k",
                "million-song-dataset",
                "fma",
                "soundatlas",
                "vggsound-omni",
            },
        )

    def test_videocof_and_humo_resolve_their_public_training_data(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        self.assertEqual(
            {item["catalog_id"] for item in cards["videocof"]["data"]["datasets"]},
            {"videocof-50k"},
        )
        self.assertEqual(
            {item["catalog_id"] for item in cards["humo-17b"]["data"]["datasets"]},
            {"phantom-data", "humoset"},
        )
        self.assertTrue(cards["videocof"]["data"]["exact_mixture_disclosed"])
        self.assertEqual(cards["humo-17b"]["architecture"]["parameters"], 17000000000)

    def test_consid_gen_resolves_public_sources_and_preserves_private_boundaries(self) -> None:
        model = {card["id"]: card for _, card in load_models()}["consid-gen"]
        self.assertEqual(
            {item["catalog_id"] for item in model["data"]["datasets"]},
            {None, "co3d", "omniobject3d", "objectron", "mvimgnet-2-0", "considvid"},
        )
        self.assertEqual(model["access"]["status"], "open-weights")
        operations = {
            operation
            for stage in model["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertTrue(
            {
                "synthetic-video-generation",
                "hierarchical-video-captioning",
                "geometry-aware-conditioning",
            }.issubset(operations)
        )
        self.assertFalse(model["data"]["exact_mixture_disclosed"])

    def test_mova_and_vera_resolve_public_training_data_and_external_evaluation(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        mova = cards["mova-720p"]
        vera = cards["vera-14b"]
        mova_ids = {
            item["catalog_id"]
            for item in mova["data"]["datasets"]
            if item["catalog_id"]
        }
        self.assertEqual(
            mova_ids,
            {
                "autorecap-xl",
                "chronomagic-pro",
                "acav100m",
                "openhumanvid",
                "speakervid-5m",
                "openvid-1m",
                "vggsound",
                "wavcaps",
                "jamendomaxcaps",
                "avgen-bench",
            },
        )
        self.assertEqual(mova["architecture"]["parameters"], 32000000000)
        self.assertTrue(mova["data"]["exact_datasets_disclosed"])
        self.assertEqual(
            {item["catalog_id"] for item in vera["data"]["datasets"]},
            {None, "vera-layered-video", "videomatte240k"},
        )
        self.assertEqual(vera["architecture"]["parameters"], 42000000000)
        self.assertEqual(vera["access"]["status"], "research-preview")

    def test_emu35_named_public_sources_resolve_to_download_cards(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        emu = cards["emu3-5"]
        linked = {
            item["catalog_id"]
            for item in emu["data"]["datasets"]
            if item["availability"] in {"public", "gated"}
        }
        self.assertEqual(
            linked,
            {
                "imagenet", "open-images-v7", "conceptual-captions-3m",
                "conceptual-12m", "laion-5b", "textatlas5m",
                "postercraft-public-corpora", "coyo-700m", "datacomp-1b",
                "journeydb", "infinity-instruct", "avgen-bench",
            },
        )
        self.assertTrue(emu["data"]["exact_datasets_disclosed"])
        self.assertFalse(emu["data"]["exact_mixture_disclosed"])

    def test_avgen_ranked_models_distinguish_training_from_pipeline_evaluation(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        for model_id in (
            "seedance-1-5-pro", "kling-2-6", "ltx-2", "emu3-5",
            "wan-2-2", "hunyuanvideo-foley", "ovi",
        ):
            with self.subTest(model=model_id):
                avgen = next(
                    item for item in cards[model_id]["data"]["datasets"]
                    if item["catalog_id"] == "avgen-bench"
                )
                self.assertEqual(avgen["role"], "evaluation")

    def test_undisclosed_training_cards_can_link_public_evaluation_sets(self) -> None:
        cards = {card["id"]: card for _, card in load_models()}
        for model_id in ("seedance-2-0", "wan-2-6"):
            with self.subTest(model=model_id):
                card = cards[model_id]
                self.assertEqual(card["data"]["disclosure_level"], "undisclosed")
                self.assertEqual(card["data"]["datasets"][0]["role"], "evaluation")
                self.assertEqual(card["data"]["datasets"][0]["catalog_id"], "avgen-bench")

        cards = {card["id"]: card for _, card in load_models()}
        lens_ids = {item["catalog_id"] for item in cards["lens"]["data"]["datasets"]}
        self.assertEqual(lens_ids, {"lens-800m", "lens-rl-8k"})

        ernie_ids = {item["catalog_id"] for item in cards["ernie-image"]["data"]["datasets"]}
        self.assertEqual(ernie_ids, {None, "eria-1k"})

        graphvid_ids = {item["catalog_id"] for item in cards["graphvid"]["data"]["datasets"]}
        self.assertEqual(graphvid_ids, {None, "graphvid-bench"})


if __name__ == "__main__":
    unittest.main()
