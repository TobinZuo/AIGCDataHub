from __future__ import annotations

import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "scripts")

from discover_updates import (
    Candidate,
    RankingEntry,
    SourceSnapshot,
    WatchSource,
    _fetch_source,
    compare_snapshots,
    content_revision,
    dataset_impact_index,
    extract_candidate_links,
    extract_arena_ranking_entries,
    extract_huggingface_dataset_candidates,
    extract_ranking_entries,
    extract_source_revision,
    load_watchlist,
    model_impact_index,
    model_ranking_aliases,
    normalize_url,
    render_report,
    report_payload,
)
from upsert_discovery_issue import issue_action, issue_body


class DiscoveryTests(unittest.TestCase):
    def test_fetch_source_isolates_connection_resets(self) -> None:
        class ResettingResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _max_bytes):
                raise ConnectionResetError("connection reset by peer")

        source = WatchSource(
            "important-model-updates",
            "https://api.github.com/repos/example/model/commits/main",
            priority="critical",
            model_id="example-model",
        )
        with (
            patch.dict("discover_updates.os.environ", {"GITHUB_TOKEN": "test-token"}, clear=True),
            patch(
                "discover_updates.urllib.request.urlopen", return_value=ResettingResponse()
            ) as urlopen,
        ):
            snapshot = _fetch_source(source, timeout=1, max_bytes=1024)

        self.assertEqual(snapshot.error, "network-ConnectionResetError")
        self.assertEqual(snapshot.model_id, "example-model")
        self.assertEqual(snapshot.priority, "critical")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(request.get_header("X-github-api-version"), "2022-11-28")

    def test_content_revision_is_stable_and_change_sensitive(self) -> None:
        self.assertEqual(content_revision(b"official page"), content_revision(b"official page"))
        self.assertNotEqual(content_revision(b"official page"), content_revision(b"updated page"))
        self.assertTrue(content_revision(b"official page").startswith("sha256:"))

    def test_content_revision_ignores_html_hydration_and_markup_noise(self) -> None:
        first = b"""<!doctype html><html><head><meta name='description' content='Model API'></head>
        <body class='build-a'><h1>Model API</h1><script>window.build='123'</script>
        <style>.a{color:red}</style><p>Stable documentation.</p></body></html>"""
        second = b"""<!doctype html><html><head><meta name='description' content='Model API'></head>
        <body class='build-b'><h1>Model API</h1><script>window.build='456'</script>
        <style>.a{color:blue}</style><p> Stable   documentation. </p></body></html>"""
        changed = second.replace(b"Stable   documentation", b"Updated documentation")
        self.assertEqual(content_revision(first), content_revision(second))
        self.assertNotEqual(content_revision(first), content_revision(changed))

    def test_platform_availability_treats_access_control_as_reachable(self) -> None:
        source = WatchSource(
            "source-platform-updates",
            "https://example.com/partner",
            priority="high",
            platform_id="example",
            revision_mode="availability",
        )
        error = urllib.error.HTTPError(
            source.source_url, 403, "Forbidden", {}, None
        )
        with patch("discover_updates.urllib.request.urlopen", side_effect=error):
            snapshot = _fetch_source(source, timeout=1, max_bytes=1024)
        self.assertIsNone(snapshot.error)
        self.assertEqual(snapshot.status, 403)
        self.assertEqual(snapshot.revision, "reachable")
        self.assertEqual(snapshot.platform_id, "example")

    def test_normalize_url_removes_tracking_and_fragment(self) -> None:
        self.assertEqual(
            normalize_url("http://Example.com/releases/model/?utm_source=x&version=2#details"),
            "https://example.com/releases/model?version=2",
        )

    def test_extracts_only_relevant_image_and_video_links(self) -> None:
        html = """
        <a href="/blog/new-video-generation-model?utm_source=nav">New video generation model</a>
        <a href="https://example.com/FLUX-4">FLUX 4</a>
        <a href="/blog/audio-dataset">Audio dataset</a>
        <a href="/privacy">Image privacy policy</a>
        <a href="/logo.png">Video generation logo</a>
        """
        candidates = extract_candidate_links(html, "https://example.com/blog/")
        self.assertEqual(
            [(candidate.title, candidate.url) for candidate in candidates],
            [
                ("FLUX 4", "https://example.com/FLUX-4"),
                ("New video generation model", "https://example.com/blog/new-video-generation-model"),
            ],
        )

    def test_extracts_arxiv_title_from_recent_listing(self) -> None:
        html = """
        <dt><a href ="/abs/2607.12345">arXiv:2607.12345</a></dt>
        <dd><div class="list-title mathjax"><span class="descriptor">Title:</span> A Video Generation Dataset</div></dd>
        """
        candidates = extract_candidate_links(html, "https://arxiv.org/list/cs.CV/recent")
        self.assertEqual(candidates, (Candidate("A Video Generation Dataset", "https://arxiv.org/abs/2607.12345"),))

    def test_extracts_hugging_face_dataset_revision(self) -> None:
        revision, url = extract_source_revision(
            '{"id":"nkp37/OpenVid-1M","sha":"abc123","lastModified":"2026-07-25T10:00:00Z"}',
            "https://huggingface.co/api/datasets/nkp37/OpenVid-1M",
        )
        self.assertEqual(revision, "2026-07-25T10:00:00Z@abc123")
        self.assertEqual(url, "https://huggingface.co/datasets/nkp37/OpenVid-1M")

    def test_extracts_hugging_face_model_revision(self) -> None:
        revision, url = extract_source_revision(
            '{"id":"tencent/HunyuanVideo-Avatar","sha":"def456",'
            '"lastModified":"2026-07-25T11:00:00Z"}',
            "https://huggingface.co/api/models/tencent/HunyuanVideo-Avatar",
        )
        self.assertEqual(revision, "2026-07-25T11:00:00Z@def456")
        self.assertEqual(url, "https://huggingface.co/tencent/HunyuanVideo-Avatar")

    def test_extracts_hugging_face_release_feed_candidates(self) -> None:
        candidates = extract_huggingface_dataset_candidates(
            '[{"id":"org/NewVideoSet"},{"id":"invalid"},{"id":"org/SecondSet"}]'
        )
        self.assertEqual([item.title for item in candidates], ["org/NewVideoSet", "org/SecondSet"])
        self.assertTrue(all(item.review_priority == "low" for item in candidates))

    def test_hugging_face_candidate_priority_is_transparent_and_non_filtering(self) -> None:
        payload = json.dumps([
            {
                "id": "lab/Strong-Text-to-Video-Dataset",
                "createdAt": "2026-07-26T00:00:00Z",
                "downloads": 500,
                "likes": 4,
                "gated": False,
                "tags": [
                    "modality:video", "license:cc-by-4.0", "size_categories:10K<n<100K",
                    "arxiv:2607.12345",
                ],
                "description": "A text-to-video generation dataset.",
                "cardData": {"dataset_info": {"splits": [{"name": "train"}]}},
            },
            {"id": "user/model.zip", "downloads": 0, "likes": 0, "tags": []},
        ])
        candidates = extract_huggingface_dataset_candidates(payload)
        self.assertEqual([item.title for item in candidates], [
            "lab/Strong-Text-to-Video-Dataset", "user/model.zip",
        ])
        self.assertEqual(candidates[0].review_priority, "high")
        self.assertGreaterEqual(candidates[0].priority_score, 7)
        self.assertIn("paper-linked", candidates[0].priority_signals)
        self.assertEqual(candidates[1].review_priority, "low")
        self.assertIn("archive-like-name", candidates[1].priority_signals)

    def test_extracts_arena_official_dataset_ranking(self) -> None:
        payload = json.dumps({"rows": [
            {"row": {
                "model_name": "gpt-image-2 (medium)", "organization": "openai",
                "license": "Proprietary", "rating": 1384.8, "rating_lower": 1379.7,
                "rating_upper": 1389.9, "vote_count": 60382, "rank": 1,
                "category": "overall", "leaderboard_publish_date": "2026-07-10",
            }},
            {"row": {
                "model_name": "open-image", "organization": "example", "license": "Apache 2.0",
                "rating": 1300.2, "rating_lower": 1290.0, "rating_upper": 1310.0,
                "vote_count": 1200, "rank": 2, "category": "overall",
                "leaderboard_publish_date": "2026-07-10",
            }},
            {"row": {"model_name": "other-category", "organization": "example",
                "license": "Proprietary", "rating": 1400, "rank": 1, "category": "portrait"}},
        ]})
        entries = extract_arena_ranking_entries(payload, limit=2)
        self.assertEqual([item.model for item in entries], ["gpt-image-2 (medium)", "open-image"])
        self.assertEqual(entries[0].score, 1384.8)
        self.assertEqual(entries[0].confidence_interval, "1380–1390")
        self.assertFalse(entries[0].open_weights)
        self.assertTrue(entries[1].open_weights)

    def test_extracts_top_ranking_entries_and_open_weight_status(self) -> None:
        html = """
        <table>
          <tr><th></th><th>Range</th><th>Creator</th><th>Model</th><th>Elo</th><th>95% CI</th><th>Samples</th><th>Released</th><th>Price</th></tr>
          <tr><td>1</td><td>1</td><td>OpenAI</td><td>GPT Image 2 (high)</td><td>1,338</td><td>-7/7</td><td>21,060</td><td>Apr 2026</td><td>$211</td></tr>
          <tr><td>2</td><td>2</td><td>NVIDIA</td><td>Cosmos3 Open Weights</td><td>1,218</td><td>-8/8</td><td>8,000</td><td>Jun 2026</td><td>-</td></tr>
        </table>
        """
        entries = extract_ranking_entries(html, limit=2)
        self.assertEqual([entry.model for entry in entries], ["GPT Image 2 (high)", "Cosmos3"])
        self.assertEqual(entries[0].elo, 1338)
        self.assertEqual(entries[0].samples, 21060)
        self.assertFalse(entries[0].open_weights)
        self.assertTrue(entries[1].open_weights)

    def test_extracts_github_repository_revision(self) -> None:
        revision, url = extract_source_revision(
            '{"sha":"abc123","html_url":"https://github.com/org/repo/commit/abc123",'
            '"commit":{"committer":{"date":"2026-07-25T10:00:00Z"}}}',
            "https://api.github.com/repos/org/repo/commits/main",
        )
        self.assertEqual(revision, "2026-07-25T10:00:00Z@abc123")
        self.assertEqual(url, "https://github.com/org/repo/commit/abc123")

    def test_extracts_relevant_sitemap_locations(self) -> None:
        xml = """
        <urlset>
          <url><loc>https://example.com/index/new-video-generation-model/</loc></url>
          <url><loc>https://example.com/index/company-news/</loc></url>
        </urlset>
        """
        candidates = extract_candidate_links(xml, "https://example.com/sitemap.xml/video/")
        self.assertEqual(
            candidates,
            (Candidate("new video generation model", "https://example.com/index/new-video-generation-model"),),
        )

    def test_detects_digital_human_translation_and_try_on_scenarios(self) -> None:
        html = """
        <a href="/avatar-v">Avatar V talking avatar model</a>
        <a href="/joint-dubbing">Video translation and lip-sync dataset</a>
        <a href="/fit-vton">Fit-aware virtual try-on benchmark</a>
        """
        titles = {candidate.title for candidate in extract_candidate_links(html, "https://example.com/research")}
        self.assertEqual(
            titles,
            {
                "Avatar V talking avatar model",
                "Video translation and lip-sync dataset",
                "Fit-aware virtual try-on benchmark",
            },
        )

    def test_contextual_project_pages_surface_new_artifacts(self) -> None:
        html = """
        <a href="https://huggingface.co/datasets/example/paired-clips">Dataset</a>
        <a href="https://example.com/team">Team</a>
        """
        candidates = extract_candidate_links(html, "https://example.com/avatar-project", contextual=True)
        self.assertEqual(
            candidates,
            (Candidate("Dataset", "https://huggingface.co/datasets/example/paired-clips"),),
        )

    def test_watchlist_includes_requested_application_tracks(self) -> None:
        _, sources = load_watchlist(Path("sources/watchlist.yaml"))
        track_ids = {source.track_id for source in sources}
        urls = {source.source_url for source in sources}
        self.assertEqual(
            sum(source.track_id == "important-dataset-updates" for source in sources),
            31,
        )
        self.assertEqual(
            sum(source.track_id == "important-model-updates" for source in sources),
            37,
        )
        self.assertEqual(
            sum(source.track_id == "source-platform-updates" for source in sources),
            16,
        )
        self.assertTrue(
            {
                "digital-human-and-localization",
                "virtual-try-on-and-commerce",
                "important-dataset-updates",
                "important-model-updates",
                "dataset-release-feeds",
                "industry-model-rankings",
                "source-platform-updates",
            }.issubset(track_ids)
        )
        self.assertEqual(sum(source.track_id == "dataset-release-feeds" for source in sources), 8)
        self.assertEqual(sum(source.track_id == "industry-model-rankings" for source in sources), 10)
        self.assertEqual(len(sources), 163)
        self.assertEqual(
            {source.ranking_id for source in sources if source.ranking_id},
            {
                "text-to-image", "image-editing", "text-to-video", "image-to-video", "video-editing",
                "arena-text-to-image", "arena-image-edit", "arena-text-to-video",
                "arena-image-to-video", "arena-video-edit",
            },
        )
        arena = next(source for source in sources if source.ranking_id == "arena-text-to-image")
        self.assertEqual(arena.ranking_provider, "Arena")
        self.assertEqual(arena.ranking_parser, "arena-hf-dataset")
        self.assertEqual(arena.ranking_coverage_policy, "required")
        self.assertEqual(arena.ranking_modality, "image")
        self.assertTrue(
            {
                "https://www.heygen.com/research/avatar-v-data",
                "https://justdubit.github.io/",
                "https://johannakarras.github.io/FIT/",
                "https://huggingface.co/api/datasets/NXN-Labs/VITON-HD-edit",
                "https://huggingface.co/api/datasets/TripVVT/TripVVT-10K",
                "https://zhenzhiwang.github.io/talkverse/",
                "https://github.com/snap-research/TalkVerse",
                "https://huggingface.co/api/datasets/zhenzhiwang/TalkVerse",
                "https://github.com/fudan-generative-vision/OpenHumanVid",
                "https://huggingface.co/api/datasets/Haosonnn/OpenHumanVid-Talking",
                "https://api.github.com/repos/fudan-generative-vision/OpenHumanVid/commits/main",
                "https://api.github.com/repos/snap-research/Panda-70M/commits/main",
                "https://huggingface.co/api/datasets/Koala-36M/Koala-36M-v1",
                "https://huggingface.co/api/datasets/wjwow/FreeMan",
                "https://api.github.com/repos/GAP-LAB-CUHK-SZ/MVHumanNet/commits/main",
                "https://api.github.com/repos/GAP-LAB-CUHK-SZ/MVHumanNet_plusplus/commits/main",
                "https://huggingface.co/api/datasets/common-canvas/commoncatalog-cc-by",
                "https://huggingface.co/api/datasets/ma-xu/fine-t2i",
                "https://huggingface.co/api/datasets/stanford-vision-lab/gpic",
                "https://huggingface.co/api/datasets/Lewandofski/OpenVE-3M",
                "https://huggingface.co/api/datasets/Lewandofski/OpenVE-Bench",
                "https://api.github.com/repos/MRzzm/HDTF/commits/main",
                "https://api.github.com/repos/CelebV-HQ/CelebV-HQ/commits/main",
                "https://huggingface.co/api/datasets/FreedomIntelligence/TalkVid",
                "https://huggingface.co/api/datasets/MV-Fashion/MV-Fashion",
                "https://huggingface.co/api/models/tencent/HunyuanVideo-Avatar",
                "https://huggingface.co/api/models/TMElyralab/MuseTalk",
                "https://huggingface.co/api/models/fashn-ai/fashn-vton-1.5",
                "https://huggingface.co/api/datasets/amphion/Emilia-Dataset",
                "https://projects.csail.mit.edu/soundnet/",
                "https://huggingface.co/api/models/tencent/HunyuanImage-3.0-Instruct",
                "https://huggingface.co/api/models/nvidia/Cosmos3-Super-Text2Image",
                "https://arxiv.org/abs/2602.21818",
                "https://docs.x.ai/developers/models/grok-imagine-image",
                "https://pixverse.ai/en/blog/pixverse-launches-v6-advancing-ai-video-generation",
                "https://platform.vidu.com/docs/update",
                "https://docs.bfl.ai/release-notes",
                "https://blog.google/innovation-and-ai/technology/ai/veo-3-1-lite/",
                "https://developers.google.com/youtube/v3/docs",
                "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction",
                "https://partner.temu.com/documentation",
            }.issubset(urls)
        )
        self.assertIn("https://huggingface.co/api/datasets/nkp37/OpenVid-1M", urls)
        openvid = next(source for source in sources if source.catalog_id == "openvid-1m")
        self.assertEqual(openvid, WatchSource(
            "important-dataset-updates",
            "https://huggingface.co/api/datasets/nkp37/OpenVid-1M",
            "openvid-1m",
            "high",
        ))
        hunyuan_avatar = next(source for source in sources if source.model_id == "hunyuanvideo-avatar")
        self.assertEqual(
            hunyuan_avatar,
            WatchSource(
                "important-model-updates",
                "https://huggingface.co/api/models/tencent/HunyuanVideo-Avatar",
                None,
                "critical",
                "hunyuanvideo-avatar",
            ),
        )

    def test_dataset_impact_index_uses_canonical_model_references(self) -> None:
        impacts = dataset_impact_index()
        self.assertEqual(impacts["fit-vto-100k"]["model_ids"], ("fit-vto",))
        self.assertEqual(impacts["viton-hd-edit"]["model_ids"], ("ctrlvton",))
        self.assertEqual(impacts["tripvvt-10k"]["model_ids"], ("tripvvt",))
        self.assertEqual(impacts["audiovisual-translation-dub"]["model_ids"], ("just-dub-it",))
        self.assertEqual(impacts["talkverse"]["model_ids"], ("talkverse-5b",))
        self.assertEqual(impacts["wavcaps"]["model_ids"], ("omni2sound",))
        self.assertEqual(impacts["commoncatalog"]["model_ids"], ("commoncanvas-xl-c",))
        self.assertEqual(impacts["gpic"]["model_ids"], ("gpic-baselines",))
        self.assertEqual(impacts["openve-bench"]["model_ids"], ("openve-edit",))

    def test_dataset_impact_index_propagates_through_dataset_lineage(self) -> None:
        impacts = dataset_impact_index()
        self.assertEqual(
            impacts["openhumanvid"]["dataset_ids"],
            ("openhumanvid-talking", "talkverse"),
        )
        self.assertEqual(impacts["openhumanvid"]["model_ids"], ("skyreels-v4", "talkverse-5b"))
        self.assertEqual(impacts["panda-70m"]["dataset_ids"], ("talkverse",))
        self.assertEqual(impacts["panda-70m"]["model_ids"], ("talkverse-5b",))
        self.assertEqual(
            impacts["audioset"]["dataset_ids"],
            ("audiocaps-2-0", "soundatlas", "wavcaps"),
        )
        self.assertEqual(impacts["audioset"]["model_ids"], ("omni2sound", "skyreels-v4"))
        self.assertEqual(impacts["yfcc100m"]["dataset_ids"], ("commoncatalog",))
        self.assertEqual(impacts["yfcc100m"]["model_ids"], ("commoncanvas-xl-c",))
        self.assertEqual(
            impacts["mvhumannet"]["dataset_ids"],
            ("mvhumannet-plus-plus",),
        )
        self.assertEqual(impacts["openve-3m"]["dataset_ids"], ("openve-bench",))
        self.assertEqual(impacts["openve-3m"]["model_ids"], ("openve-edit",))

    def test_model_impact_index_uses_direct_dataset_links(self) -> None:
        impacts = model_impact_index()
        self.assertEqual(
            impacts["hunyuanvideo-avatar"]["dataset_ids"],
            ("celebv-hq", "hdtf"),
        )
        self.assertEqual(impacts["hunyuanvideo-avatar"]["model_ids"], ("hunyuanvideo-avatar",))
        self.assertEqual(impacts["musetalk-1-5"]["dataset_ids"], ("hdtf",))
        self.assertEqual(impacts["fashn-vton-1-5"]["dataset_ids"], ())

    def test_compares_candidates_failures_recoveries_and_known_urls(self) -> None:
        baseline = {
            "sources": [
                {
                    "track_id": "image-generation",
                    "source_url": "https://example.com/blog",
                    "candidates": [{"title": "Old image model", "url": "https://example.com/old"}],
                    "error": None,
                },
                {
                    "track_id": "datasets",
                    "source_url": "https://example.com/datasets",
                    "candidates": [],
                    "error": "HTTP 503",
                },
                {
                    "track_id": "important-dataset-updates",
                    "source_url": "https://huggingface.co/api/datasets/nkp37/OpenVid-1M",
                    "candidates": [],
                    "revision": "2026-07-01T00:00:00Z@old",
                    "error": None,
                },
                {
                    "track_id": "important-model-updates",
                    "source_url": "https://huggingface.co/api/models/example/video-model",
                    "candidates": [],
                    "revision": "2026-07-01T00:00:00Z@old-model",
                    "error": None,
                },
            ]
        }
        current = (
            SourceSnapshot(
                "image-generation",
                "https://example.com/blog",
                "https://example.com/blog",
                200,
                (
                    Candidate("Old image model", "https://example.com/old"),
                    Candidate("New video model", "https://example.com/new"),
                    Candidate("Known model", "https://example.com/known"),
                ),
                None,
            ),
            SourceSnapshot(
                "datasets",
                "https://example.com/datasets",
                "https://example.com/datasets",
                200,
                (),
                None,
            ),
            SourceSnapshot(
                "video-and-audio-generation",
                "https://example.com/video",
                None,
                None,
                (),
                "HTTP 429",
            ),
            SourceSnapshot(
                "important-dataset-updates",
                "https://huggingface.co/api/datasets/nkp37/OpenVid-1M",
                "https://huggingface.co/api/datasets/nkp37/OpenVid-1M",
                200,
                (),
                None,
                "2026-07-25T10:00:00Z@new",
                "https://huggingface.co/datasets/nkp37/OpenVid-1M",
                "openvid-1m",
                "high",
            ),
            SourceSnapshot(
                track_id="important-model-updates",
                source_url="https://huggingface.co/api/models/example/video-model",
                resolved_url="https://huggingface.co/api/models/example/video-model",
                status=200,
                candidates=(),
                error=None,
                revision="2026-07-25T12:00:00Z@new-model",
                revision_url="https://huggingface.co/example/video-model",
                priority="critical",
                model_id="video-model",
            ),
        )
        diff = compare_snapshots(
            baseline,
            current,
            {"https://example.com/known"},
            {
                "openvid-1m": {
                    "dataset_ids": ("derived-video",),
                    "model_ids": ("video-model",),
                }
            },
            {
                "video-model": {
                    "dataset_ids": ("training-video",),
                    "model_ids": ("video-model",),
                }
            },
        )
        self.assertEqual([item["url"] for item in diff.new_candidates], ["https://example.com/new"])
        self.assertEqual([item["error"] for item in diff.failures], ["HTTP 429"])
        self.assertEqual([item["previous_error"] for item in diff.recoveries], ["HTTP 503"])
        self.assertEqual(
            [item["url"] for item in diff.source_updates],
            [
                "https://huggingface.co/datasets/nkp37/OpenVid-1M",
                "https://huggingface.co/example/video-model",
            ],
        )
        self.assertEqual(diff.source_updates[0]["catalog_id"], "openvid-1m")
        self.assertEqual(diff.source_updates[0]["entity_type"], "dataset")
        self.assertEqual(diff.source_updates[0]["priority"], "high")
        self.assertEqual(diff.source_updates[0]["impacted_dataset_ids"], ["derived-video"])
        self.assertEqual(diff.source_updates[0]["impacted_model_ids"], ["video-model"])
        self.assertEqual(diff.source_updates[1]["model_id"], "video-model")
        self.assertEqual(diff.source_updates[1]["entity_type"], "model")
        self.assertEqual(diff.source_updates[1]["impacted_dataset_ids"], ["training-video"])
        markdown = render_report(
            report_payload(diff, "2026-07-26T00:00:00Z", "Discovery", 2, ["video"])
        )
        self.assertIn("Important catalog revisions", markdown)
        self.assertIn("linked datasets: `training-video`", markdown)
        self.assertIn("**critical** model priority", markdown)

    def test_report_preserves_human_review_contract(self) -> None:
        baseline = {"sources": []}
        current = (
            SourceSnapshot(
                "image-generation",
                "https://example.com/blog",
                "https://example.com/blog",
                200,
                (Candidate("New image model", "https://example.com/new-image-model"),),
                None,
            ),
        )
        diff = compare_snapshots(baseline, current, set())
        report = report_payload(diff, "2026-07-26T00:00:00Z", "Discovery", 1, ["image", "video"])
        markdown = render_report(report)
        self.assertIn("New image model", markdown)
        self.assertIn("requires primary-source verification", markdown)
        self.assertIn("<!-- aigcdatahub-weekly-discovery -->", markdown)
        self.assertTrue(report["has_updates"])

    def test_platform_revision_has_a_platform_specific_review_signal(self) -> None:
        baseline = {
            "sources": [
                {
                    "track_id": "source-platform-updates",
                    "source_url": "https://example.com/developer",
                    "revision": "sha256:old",
                    "candidates": [],
                    "error": None,
                }
            ]
        }
        current = (
            SourceSnapshot(
                track_id="source-platform-updates",
                source_url="https://example.com/developer",
                resolved_url="https://example.com/developer",
                status=200,
                candidates=(),
                error=None,
                revision="sha256:new",
                revision_url="https://example.com/developer",
                priority="high",
                platform_id="example-platform",
                revision_mode="content-revision",
            ),
        )
        diff = compare_snapshots(baseline, current, set())
        self.assertEqual(diff.source_updates[0]["entity_type"], "source-platform")
        self.assertEqual(diff.source_updates[0]["platform_id"], "example-platform")
        markdown = render_report(
            report_payload(diff, "2026-07-27T00:00:00Z", "Discovery", 1, ["image"])
        )
        self.assertIn("source-platform access signal", markdown)

    def test_ranking_diff_tracks_membership_and_order_not_elo_noise(self) -> None:
        baseline = {
            "sources": [
                {
                    "track_id": "industry-model-rankings",
                    "source_url": "https://example.com/ranking",
                    "ranking_id": "text-to-image",
                    "rankings": [
                        {"rank": 1, "model": "Model A", "elo": 1300},
                        {"rank": 2, "model": "Model B", "elo": 1290},
                    ],
                    "candidates": [],
                    "error": None,
                }
            ]
        }
        entries = (
            RankingEntry(1, "Org B", "Model B", 1305, "-8/8", 1000, "Jul 2026", False),
            RankingEntry(2, "Org C", "Model C", 1280, "-9/9", 800, "Jul 2026", True),
        )
        current = (
            SourceSnapshot(
                track_id="industry-model-rankings",
                source_url="https://example.com/ranking",
                resolved_url="https://example.com/ranking",
                status=200,
                candidates=(),
                error=None,
                ranking_id="text-to-image",
                rankings=entries,
            ),
        )
        diff = compare_snapshots(baseline, current, set())
        self.assertEqual(len(diff.ranking_updates), 1)
        self.assertEqual(diff.ranking_updates[0]["ranking_id"], "text-to-image")
        self.assertEqual(
            diff.ranking_updates[0]["changes"],
            [
                {"model": "Model A", "previous_rank": 1, "rank": None},
                {"model": "Model B", "previous_rank": 2, "rank": 1},
                {"model": "Model C", "previous_rank": None, "rank": 2},
            ],
        )
        unchanged_order = (
            SourceSnapshot(
                track_id="industry-model-rankings",
                source_url="https://example.com/ranking",
                resolved_url="https://example.com/ranking",
                status=200,
                candidates=(),
                error=None,
                ranking_id="text-to-image",
                rankings=(
                    RankingEntry(1, "Org A", "Model A", 1400, "-1/1", 2000, "Jul 2026", False),
                    RankingEntry(2, "Org B", "Model B", 1390, "-1/1", 2000, "Jul 2026", False),
                ),
            ),
        )
        self.assertFalse(compare_snapshots(baseline, unchanged_order, set()).ranking_updates)

    def test_ranking_coverage_gaps_remain_in_the_review_queue(self) -> None:
        current = (
            SourceSnapshot(
                track_id="industry-model-rankings",
                source_url="https://example.com/api",
                resolved_url="https://example.com/api",
                status=200,
                candidates=(),
                error=None,
                ranking_id="arena-text-to-image",
                rankings=(RankingEntry(1, "Lab", "Unmapped Model", 1300, "", 100, "2026-07-10", False),),
                ranking_provider="Arena",
                ranking_coverage_policy="monitor",
                ranking_page_url="https://example.com/leaderboard",
            ),
        )
        diff = compare_snapshots({"sources": []}, current, set(), ranking_aliases=model_ranking_aliases())
        self.assertEqual(len(diff.ranking_coverage_gaps), 1)
        self.assertEqual(diff.ranking_coverage_gaps[0]["model"], "Unmapped Model")
        self.assertTrue(diff.has_updates)
        markdown = render_report(
            report_payload(diff, "2026-07-27T00:00:00Z", "Discovery", 1, ["image"])
        )
        self.assertIn("Ranked models awaiting catalog cards", markdown)

    def test_issue_body_links_to_the_actions_run(self) -> None:
        body = issue_body(
            "report\n<!-- aigcdatahub-weekly-discovery -->\n",
            "TobinZuo/AIGCDataHub",
            "123",
            "https://github.com",
        )
        self.assertIn("https://github.com/TobinZuo/AIGCDataHub/actions/runs/123", body)

    def test_issue_actions_are_idempotent(self) -> None:
        open_issue = {"number": 1, "state": "open"}
        closed_issue = {"number": 1, "state": "closed"}
        self.assertEqual(issue_action(True, None), "create")
        self.assertEqual(issue_action(True, closed_issue), "update")
        self.assertEqual(issue_action(False, open_issue), "close")
        self.assertEqual(issue_action(False, closed_issue), "none")
        self.assertEqual(issue_action(False, None), "none")

    def test_weekly_workflow_has_minimal_issue_permissions(self) -> None:
        workflow = Path(".github/workflows/discovery.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "41 1 * * 1"', workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("issues: write", workflow)
        self.assertIn("scripts/discover_updates.py", workflow)
        self.assertIn("scripts/upsert_discovery_issue.py", workflow)
        self.assertEqual(workflow.count("GITHUB_TOKEN: ${{ github.token }}"), 2)


if __name__ == "__main__":
    unittest.main()
