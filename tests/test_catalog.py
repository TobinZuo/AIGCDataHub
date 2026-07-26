from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from build_readme import END, MODEL_END, MODEL_START, START, generated_readme, render_dataset_table, render_model_table
from build_site_data import build_payload
from catalog import compact_number, load_cards
from validate_catalog import validate


class CatalogTests(unittest.TestCase):
    def test_catalog_is_valid(self) -> None:
        self.assertEqual(validate(), [])

    def test_cards_are_present(self) -> None:
        self.assertGreaterEqual(len(load_cards()), 44)

    def test_audio_and_3d_coverage_is_present(self) -> None:
        modalities = {card["modality"] for _, card in load_cards()}
        self.assertTrue({"audio", "3d"}.issubset(modalities))

    def test_audio_lineage_datasets_are_present(self) -> None:
        ids = {card["id"] for _, card in load_cards()}
        self.assertTrue(
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
            }.issubset(ids)
        )

    def test_image_model_lineage_datasets_are_present(self) -> None:
        ids = {card["id"] for _, card in load_cards()}
        self.assertTrue({"lens-800m", "lens-rl-8k", "eria-1k", "gensyn10"}.issubset(ids))

    def test_application_scenario_datasets_are_present(self) -> None:
        cards = {card["id"]: card for _, card in load_cards()}
        self.assertTrue(
            {
                "audiovisual-translation-dub",
                "fit-vto-100k",
                "viton-hd-edit",
                "tripvvt-10k",
                "talkverse",
                "openhumanvid",
                "openhumanvid-talking",
            }.issubset(cards)
        )
        self.assertIn("video-dubbing", cards["audiovisual-translation-dub"]["tasks"])
        self.assertIn("virtual-try-on", cards["fit-vto-100k"]["tasks"])
        self.assertIn("controllable-virtual-try-on", cards["viton-hd-edit"]["tasks"])
        self.assertIn("video-virtual-try-on", cards["tripvvt-10k"]["tasks"])
        self.assertIn("audio-driven-avatar", cards["talkverse"]["tasks"])
        self.assertEqual(cards["talkverse"]["access"]["type"], "metadata")
        self.assertIn("text-to-video", cards["openhumanvid"]["tasks"])
        self.assertEqual(cards["openhumanvid"]["access"]["status"], "gated")
        self.assertIn("talking-head-generation", cards["openhumanvid-talking"]["tasks"])
        self.assertEqual(cards["openhumanvid-talking"]["scale"]["samples"], 32176)

    def test_reference_wiki_candidates_are_backed_by_public_sources(self) -> None:
        cards = {card["id"]: card for _, card in load_cards()}
        self.assertTrue(
            {
                "koala-36m",
                "freeman",
                "mvhumannet",
                "mvhumannet-plus-plus",
                "yfcc100m",
                "commoncatalog",
                "fine-t2i",
                "gpic",
                "openve-3m",
                "openve-bench",
            }.issubset(cards)
        )
        self.assertEqual(cards["koala-36m"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["freeman"]["license"]["commercial_use"], "noncommercial")
        self.assertEqual(cards["gpic"]["scale"]["samples"], 101200000)
        self.assertEqual(cards["openve-bench"]["scale"]["samples"], 431)

    def test_dataset_lineage_uses_canonical_catalog_ids(self) -> None:
        cards = {card["id"]: card for _, card in load_cards()}
        self.assertEqual(
            {item["catalog_id"] for item in cards["talkverse"]["derived_from"]},
            {"openhumanvid", "panda-70m"},
        )
        self.assertEqual(
            cards["openhumanvid-talking"]["derived_from"][0]["relationship"],
            "filtered-subset",
        )
        self.assertEqual(
            cards["vggsound-omni"]["derived_from"][0]["catalog_id"],
            "vggsound",
        )
        self.assertEqual(
            cards["commoncatalog"]["derived_from"][0]["catalog_id"],
            "yfcc100m",
        )
        self.assertEqual(
            cards["mvhumannet-plus-plus"]["derived_from"][0]["catalog_id"],
            "mvhumannet",
        )
        self.assertEqual(
            cards["openve-bench"]["derived_from"][0]["catalog_id"],
            "openve-3m",
        )

    def test_site_catalog_orders_datasets_by_release_date(self) -> None:
        datasets = build_payload()["datasets"]
        dates = [card["released_at"] for card in datasets]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual(datasets[0]["id"], "graphvid-bench")

    def test_compact_number(self) -> None:
        self.assertEqual(compact_number(70_723_513), "70.7M")
        self.assertEqual(compact_number(1_000_000, approximate=True), "~1M")
        self.assertEqual(compact_number(None), "unknown")

    def test_readme_generation_is_idempotent(self) -> None:
        source = (
            f"before\n{MODEL_START}\nstale models\n{MODEL_END}\n"
            f"middle\n{START}\nstale datasets\n{END}\nafter\n"
        )
        once = generated_readme(source)
        self.assertEqual(generated_readme(once), once)
        self.assertIn("| Dataset | Organization | Modality | Released |", render_dataset_table())
        self.assertIn("| Model | Organization |", render_model_table())


if __name__ == "__main__":
    unittest.main()
