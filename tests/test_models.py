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
        self.assertGreaterEqual(len(cards), 11)
        self.assertTrue({"image", "video", "audio", "multimodal"}.issubset(modalities))

    def test_product_only_releases_are_representable(self) -> None:
        cards = [card for _, card in load_models()]
        self.assertTrue(any(card["access"]["status"] == "product-only" for card in cards))

    def test_every_model_records_unknowns(self) -> None:
        for _, card in load_models():
            with self.subTest(card=card["id"]):
                self.assertTrue(card["data"]["unknowns"])

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


if __name__ == "__main__":
    unittest.main()
