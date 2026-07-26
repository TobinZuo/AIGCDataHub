from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")

from discover_updates import (
    Candidate,
    SourceSnapshot,
    WatchSource,
    compare_snapshots,
    dataset_impact_index,
    extract_candidate_links,
    extract_source_revision,
    load_watchlist,
    model_impact_index,
    normalize_url,
    render_report,
    report_payload,
)
from upsert_discovery_issue import issue_action, issue_body


class DiscoveryTests(unittest.TestCase):
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
            29,
        )
        self.assertEqual(
            sum(source.track_id == "important-model-updates" for source in sources),
            13,
        )
        self.assertTrue(
            {
                "digital-human-and-localization",
                "virtual-try-on-and-commerce",
                "important-dataset-updates",
                "important-model-updates",
            }.issubset(track_ids)
        )
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
        self.assertEqual(impacts["openhumanvid"]["model_ids"], ("talkverse-5b",))
        self.assertEqual(impacts["panda-70m"]["dataset_ids"], ("talkverse",))
        self.assertEqual(impacts["panda-70m"]["model_ids"], ("talkverse-5b",))
        self.assertEqual(
            impacts["audioset"]["dataset_ids"],
            ("audiocaps-2-0", "soundatlas", "wavcaps"),
        )
        self.assertEqual(impacts["audioset"]["model_ids"], ("omni2sound",))
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


if __name__ == "__main__":
    unittest.main()
