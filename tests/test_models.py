from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from models import load_models
from validate_models import validate_models


class ModelCatalogTests(unittest.TestCase):
    def test_model_catalog_is_valid(self) -> None:
        self.assertEqual(validate_models(), [])

    def test_representative_modalities_are_present(self) -> None:
        cards = [card for _, card in load_models()]
        modalities = {modality for card in cards for modality in card["modalities"]}
        self.assertGreaterEqual(len(cards), 23)
        self.assertTrue({"image", "video", "audio", "multimodal"}.issubset(modalities))

    def test_product_only_releases_are_representable(self) -> None:
        cards = [card for _, card in load_models()]
        self.assertTrue(any(card["access"]["status"] == "product-only" for card in cards))

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
        talkverse_ops = {
            operation
            for stage in cards["talkverse-5b"]["data"]["stages"]
            for operation in stage["operations"]
        }
        self.assertEqual(avatar_stages, {"pretraining", "fine-tuning", "distillation", "preference"})
        self.assertEqual(just_dub_it_ids, {None, "audiovisual-translation-dub"})
        self.assertEqual(talkverse_ids, {None, "talkverse"})
        self.assertTrue(
            {
                "audio-video-sync-filtering",
                "audio-style-captioning",
                "pose-extraction",
                "roi-loss-weighting",
            }.issubset(talkverse_ops)
        )
        self.assertTrue(cards["talkverse-5b"]["data"]["stages"][1]["scale_disclosed"])

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

        cards = {card["id"]: card for _, card in load_models()}
        lens_ids = {item["catalog_id"] for item in cards["lens"]["data"]["datasets"]}
        self.assertEqual(lens_ids, {"lens-800m", "lens-rl-8k"})

        ernie_ids = {item["catalog_id"] for item in cards["ernie-image"]["data"]["datasets"]}
        self.assertEqual(ernie_ids, {None, "eria-1k"})

        graphvid_ids = {item["catalog_id"] for item in cards["graphvid"]["data"]["datasets"]}
        self.assertEqual(graphvid_ids, {None, "graphvid-bench"})


if __name__ == "__main__":
    unittest.main()
