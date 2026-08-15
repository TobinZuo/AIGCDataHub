from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")

from build_readme import (
    END,
    METRICS_END,
    METRICS_START,
    MODEL_END,
    MODEL_START,
    START,
    generated_readme,
    render_dataset_table,
    render_model_table,
    render_project_metrics,
)
from build_dataset_access_index import render_index as render_access_index
from build_site_data import build_payload
from catalog import compact_number, load_cards
from validate_catalog import validate


class CatalogTests(unittest.TestCase):
    def test_catalog_is_valid(self) -> None:
        self.assertEqual(validate(), [])

    def test_cards_are_present(self) -> None:
        self.assertGreaterEqual(len(load_cards()), 55)

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
                "hdtf",
                "celebv-hq",
                "talkvid",
                "mv-fashion",
                "videocof-50k",
                "phantom-data",
                "humoset",
                "senorita-2m",
                "spatialvid",
                "voxceleb2",
                "lrs3",
                "celebv-text",
                "celebv-dub",
                "holidub-bench",
                "libritts",
                "grid",
                "chem",
                "v2c-animation",
                "cinedub-cn",
                "cinedub-example",
                "unisync-5k",
                "realworld-lipsync",
                "davis-2017",
                "elasticttt-video-editing",
                "worldweaver-minecraft-126h",
                "solaris-training-dataset",
                "solaris-eval-datasets",
                "vpt-contractor-demonstrations",
                "sana-video-2-progressive-training-pools",
                "sana-video-2-preference-pairs",
                "mage-flow-curated-image-text",
                "mage-flow-edit-triples",
                "mage-flow-rl-prompt-pools",
                "innotext-30k",
                "agenthoi-mixed-source-corpus",
                "fmri-face",
                "thuman2-0",
                "culturevidbench",
                "mie-bench",
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
        self.assertEqual(cards["openhumanvid-talking"]["scale"]["samples"], 8989)
        self.assertEqual(cards["talkvid"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["talkvid"]["scale"]["samples"], 500)
        self.assertEqual(cards["mv-fashion"]["scale"]["samples"], 52020529)
        self.assertEqual(cards["mv-fashion"]["access"]["status"], "gated")
        self.assertIn("audio-driven-avatar", cards["hdtf"]["tasks"])
        self.assertEqual(cards["celebv-hq"]["access"]["type"], "urls")
        self.assertEqual(cards["videocof-50k"]["scale"]["samples"], 49177)
        self.assertEqual(cards["phantom-data"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["humoset"]["scale"]["samples"], 670000)
        self.assertEqual(cards["humoset"]["access"]["type"], "hosted")
        self.assertEqual(cards["senorita-2m"]["scale"]["samples"], 1950021)
        self.assertEqual(cards["senorita-2m"]["access"]["status"], "open")
        self.assertEqual(cards["spatialvid"]["scale"]["hours"], 7089)
        self.assertEqual(cards["spatialvid"]["access"]["status"], "gated")
        self.assertEqual(cards["davis-2017"]["scale"]["samples"], 10459)
        self.assertEqual(cards["davis-2017"]["scale"]["source_items"], 150)
        self.assertEqual(cards["davis-2017"]["access"]["status"], "open")
        self.assertEqual(cards["elasticttt-video-editing"]["scale"]["samples"], 125)
        self.assertEqual(cards["elasticttt-video-editing"]["scale"]["source_items"], 25)
        self.assertEqual(cards["elasticttt-video-editing"]["access"]["status"], "open")
        self.assertEqual(
            cards["elasticttt-video-editing"]["derived_from"][0]["catalog_id"],
            "davis-2017",
        )
        self.assertEqual(cards["worldweaver-minecraft-126h"]["access"]["status"], "unavailable")
        self.assertEqual(cards["worldweaver-minecraft-126h"]["scale"]["hours"], 126)
        self.assertEqual(cards["solaris-training-dataset"]["access"]["status"], "open")
        self.assertEqual(cards["solaris-training-dataset"]["scale"]["samples"], 12640000)
        self.assertEqual(cards["solaris-training-dataset"]["scale"]["source_items"], 9240)
        self.assertEqual(cards["solaris-eval-datasets"]["scale"]["samples"], 1280)
        self.assertEqual(cards["vpt-contractor-demonstrations"]["access"]["type"], "urls")
        self.assertEqual(cards["sana-video-2-progressive-training-pools"]["scale"]["samples"], 30000000)
        self.assertEqual(cards["sana-video-2-progressive-training-pools"]["access"]["status"], "unavailable")
        self.assertIsNone(cards["sana-video-2-preference-pairs"]["scale"]["samples"])
        self.assertEqual(cards["mage-flow-curated-image-text"]["scale"]["samples"], 1300000000)
        self.assertEqual(cards["mage-flow-curated-image-text"]["scale"]["source_items"], 10000000000)
        self.assertEqual(cards["mage-flow-edit-triples"]["scale"]["samples"], 45000000)
        self.assertEqual(cards["mage-flow-edit-triples"]["scale"]["source_items"], 90000000)
        self.assertEqual(cards["mage-flow-rl-prompt-pools"]["scale"]["samples"], 50000)
        self.assertEqual(cards["innotext-30k"]["scale"]["samples"], 30000)
        self.assertEqual(cards["agenthoi-mixed-source-corpus"]["scale"]["samples"], 108000)
        self.assertEqual(cards["agenthoi-mixed-source-corpus"]["scale"]["source_items"], 10000000)
        self.assertEqual(cards["fmri-face"]["scale"]["samples"], 62856)
        self.assertEqual(cards["thuman2-0"]["access"]["status"], "gated")
        self.assertEqual(cards["thuman2-0"]["scale"]["samples"], 500)
        self.assertEqual(cards["culturevidbench"]["access"]["status"], "unavailable")
        self.assertEqual(cards["culturevidbench"]["scale"]["samples"], 1000)
        self.assertEqual(cards["mie-bench"]["access"]["status"], "unavailable")
        self.assertEqual(cards["mie-bench"]["scale"]["samples"], 3000)
        self.assertEqual(cards["fmri-face"]["scale"]["source_items"], 2174)
        self.assertEqual(cards["voxceleb2"]["access"]["status"], "unavailable")
        self.assertEqual(cards["lrs3"]["access"]["status"], "unavailable")
        self.assertEqual(cards["celebv-text"]["access"]["type"], "urls")
        self.assertEqual(cards["celebv-dub"]["access"]["type"], "hosted")
        self.assertEqual(cards["holidub-bench"]["access"]["status"], "unavailable")
        self.assertEqual(cards["emilia"]["access"]["status"], "gated")
        self.assertEqual(cards["libritts"]["access"]["type"], "hosted")
        self.assertEqual(cards["grid"]["scale"]["samples"], 34000)
        self.assertEqual(cards["chem"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["v2c-animation"]["access"]["type"], "urls")
        self.assertEqual(cards["cinedub-cn"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["cinedub-example"]["access"]["status"], "gated")
        self.assertEqual(cards["unisync-5k"]["access"]["status"], "unavailable")
        self.assertEqual(cards["realworld-lipsync"]["scale"]["samples"], 495)

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

    def test_release_feed_promotions_have_downloads_and_review_boundaries(self) -> None:
        cards = {card["id"]: card for _, card in load_cards()}
        self.assertTrue(
            {
                "videoufo",
                "talkingheadbench",
                "maven-multicultural-video",
                "seedance-1-pro-human-preference",
            }.issubset(cards)
        )
        self.assertEqual(cards["videoufo"]["scale"]["samples"], 1091712)
        self.assertEqual(cards["videoufo"]["access"]["type"], "hosted")
        self.assertEqual(cards["talkingheadbench"]["scale"]["samples"], 5306)
        self.assertEqual(cards["talkingheadbench"]["license"]["commercial_use"], "review-required")
        self.assertEqual(cards["maven-multicultural-video"]["scale"]["samples"], 972)
        self.assertEqual(cards["seedance-1-pro-human-preference"]["scale"]["samples"], 198)

    def test_joint_audio_video_and_layered_editing_datasets_are_actionable(self) -> None:
        cards = {card["id"]: card for _, card in load_cards()}
        expected = {
            "avgen-bench",
            "vera-layered-video",
            "videomatte240k",
            "chronomagic-pro",
            "acav100m",
            "speakervid-5m",
            "autorecap-xl",
            "jamendomaxcaps",
        }
        self.assertTrue(expected.issubset(cards))
        self.assertEqual(cards["avgen-bench"]["scale"]["samples"], 3009)
        self.assertEqual(cards["vera-layered-video"]["access"]["type"], "hosted")
        self.assertEqual(cards["videomatte240k"]["scale"]["samples"], 240709)
        self.assertEqual(cards["chronomagic-pro"]["access"]["type"], "hosted")
        self.assertEqual(cards["acav100m"]["access"]["status"], "metadata-only")
        self.assertEqual(cards["speakervid-5m"]["access"]["type"], "metadata")
        self.assertEqual(cards["autorecap-xl"]["access"]["type"], "metadata")
        self.assertEqual(cards["jamendomaxcaps"]["access"]["type"], "hosted")

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
        self.assertEqual(
            cards["talkingheadbench"]["derived_from"][0]["catalog_id"],
            "celebv-hq",
        )
        self.assertEqual(
            cards["phantom-data"]["derived_from"][0]["catalog_id"],
            "koala-36m",
        )
        self.assertEqual(
            cards["humoset"]["derived_from"][0]["catalog_id"],
            "openhumanvid",
        )
        self.assertEqual(
            cards["videocof-50k"]["derived_from"][0]["catalog_id"],
            "senorita-2m",
        )
        self.assertEqual(
            cards["vera-layered-video"]["derived_from"][0]["catalog_id"],
            "videomatte240k",
        )
        self.assertEqual(
            {item["catalog_id"] for item in cards["considvid"]["derived_from"]},
            {"co3d", "omniobject3d", "objectron", "mvimgnet-2-0"},
        )
        self.assertEqual(cards["considvid"]["scale"]["samples"], 8298)
        self.assertEqual(cards["considvid"]["access"]["type"], "hosted")
        self.assertIn("license", cards["considvid"]["license"]["notes"].lower())

    def test_site_catalog_orders_datasets_by_release_date(self) -> None:
        datasets = build_payload()["datasets"]
        dates = [card["released_at"] for card in datasets]
        self.assertEqual(dates, sorted(dates, reverse=True))
        newest_date = dates[0]
        newest_ids = {card["id"] for card in datasets if card["released_at"] == newest_date}
        self.assertEqual(
            newest_ids,
            {"td-v2a-freesound-corpus"},
        )

    def test_site_catalog_orders_models_by_release_date(self) -> None:
        models = build_payload()["models"]
        dates = [card["released_at"] for card in models]
        self.assertEqual(dates, sorted(dates, reverse=True))
        newest_date = dates[0]
        newest_ids = {card["id"] for card in models if card["released_at"] == newest_date}
        self.assertEqual(
            newest_ids,
            {"evoke", "jogg-avatar-v2v", "ltx-2-5", "scope"},
        )

    def test_every_ranking_top_fifteen_entry_maps_to_a_model_card(self) -> None:
        rankings = build_payload()["rankings"]
        self.assertEqual(len(rankings), 11)
        self.assertEqual(
            {board["provider"] for board in rankings},
            {"Artificial Analysis", "Arena", "AVGen-Bench"},
        )
        required_boards = [board for board in rankings if board["coverage_policy"] == "required"]
        self.assertEqual(len(required_boards), 8)
        self.assertEqual(
            {
                board["id"]
                for board in rankings
                if board["coverage_policy"] == "monitor"
            },
            {"image-editing", "image-to-video", "text-to-image"},
        )
        for board in required_boards:
            with self.subTest(board=board["id"]):
                required = min(15, len(board["entries"]))
                self.assertGreaterEqual(required, 6)
                self.assertTrue(all(entry["model_id"] for entry in board["entries"][:required]))
                self.assertTrue(all(
                    component["model_id"]
                    for entry in board["entries"][:required]
                    for component in entry["components"]
                ))

        avgen = next(board for board in rankings if board["id"] == "avgen-text-to-audio-video")
        pipeline = next(entry for entry in avgen["entries"] if entry["model"] == "Wan2.2 + HunyuanVideo-Foley")
        self.assertEqual(
            pipeline["components"],
            [
                {"name": "Wan2.2", "model_id": "wan-2-2"},
                {"name": "HunyuanVideo-Foley", "model_id": "hunyuanvideo-foley"},
            ],
        )
        self.assertEqual(pipeline["model_ids"], ["wan-2-2", "hunyuanvideo-foley"])

    def test_compact_number(self) -> None:
        self.assertEqual(compact_number(70_723_513), "70.7M")
        self.assertEqual(compact_number(1_000_000, approximate=True), "~1M")
        self.assertEqual(compact_number(None), "unknown")

    def test_readme_generation_is_idempotent(self) -> None:
        source = (
            f"before\n{METRICS_START}\nstale metrics\n{METRICS_END}\n"
            f"{MODEL_START}\nstale models\n{MODEL_END}\n"
            f"middle\n{START}\nstale datasets\n{END}\nafter\n"
        )
        once = generated_readme(source)
        self.assertEqual(generated_readme(once), once)
        self.assertIn("| Models | Datasets |", render_project_metrics())
        self.assertIn("| 模型 | 数据集 |", render_project_metrics("zh"))
        self.assertIn("| Dataset | Organization | Modality | Released |", render_dataset_table())
        self.assertIn("[download / browse (open)](https://", render_dataset_table())
        self.assertIn("| Model | Organization |", render_model_table())

    def test_repository_dataset_access_index_is_current_and_has_every_card(self) -> None:
        rendered = render_access_index()
        self.assertEqual(rendered, Path("DATASET_ACCESS_INDEX.md").read_text(encoding="utf-8"))
        self.assertEqual(rendered.count("\n| ["), len(load_cards()))
        self.assertIn("Get data / access evidence", rendered)
        self.assertIn("Download / browse files", rendered)


if __name__ == "__main__":
    unittest.main()
