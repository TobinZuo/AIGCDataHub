from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")

from discover_updates import (
    Candidate,
    SourceSnapshot,
    compare_snapshots,
    extract_candidate_links,
    extract_source_revision,
    load_watchlist,
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
        track_ids = {track_id for track_id, _ in sources}
        urls = {url for _, url in sources}
        self.assertTrue({"digital-human-and-localization", "virtual-try-on-and-commerce"}.issubset(track_ids))
        self.assertTrue(
            {
                "https://www.heygen.com/research/avatar-v-data",
                "https://justdubit.github.io/",
                "https://johannakarras.github.io/FIT/",
            }.issubset(urls)
        )
        self.assertIn("https://huggingface.co/api/datasets/nkp37/OpenVid-1M", urls)

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
            ),
        )
        diff = compare_snapshots(baseline, current, {"https://example.com/known"})
        self.assertEqual([item["url"] for item in diff.new_candidates], ["https://example.com/new"])
        self.assertEqual([item["error"] for item in diff.failures], ["HTTP 429"])
        self.assertEqual([item["previous_error"] for item in diff.recoveries], ["HTTP 503"])
        self.assertEqual(
            [item["url"] for item in diff.source_updates],
            ["https://huggingface.co/datasets/nkp37/OpenVid-1M"],
        )

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
