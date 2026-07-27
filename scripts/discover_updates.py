#!/usr/bin/env python3
"""Discover new generative image/video links from the official-source watchlist."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

from catalog import load_cards
from models import load_models
from source_platforms import load_source_platforms


SCHEMA_VERSION = 10
USER_AGENT = "AIGCDataHub-discovery/0.1 (+https://github.com/TobinZuo/AIGCDataHub)"
MEDIA_TERMS = (
    "image",
    "video",
    "visual",
    "text-to-image",
    "text to image",
    "image-to-video",
    "image to video",
    "text-to-video",
    "text to video",
    "diffusion",
    "digital human",
    "talking avatar",
    "talking head",
    "lip-sync",
    "lip sync",
    "lipsync",
    "video dubbing",
    "video translation",
    "video localization",
    "virtual try-on",
    "virtual try on",
    "vton",
    "生图",
    "文生图",
    "图生视频",
    "文生视频",
    "图像",
    "视频",
)
SIGNAL_TERMS = (
    "generat",
    "model",
    "dataset",
    "benchmark",
    "release",
    "launch",
    "introduc",
    "preview",
    "technical report",
    "paper",
    "training",
    "data strateg",
    "editing",
    "synthetic",
    "intelligence",
    "avatar",
    "dubbing",
    "translation",
    "localization",
    "try-on",
    "try on",
    "garment",
    "fashion",
)
STRONG_MEDIA_NAMES = (
    "flux",
    "midjourney",
    "stable diffusion",
    "seedance",
    "sora",
    "veo",
    "hunyuanvideo",
    "hunyuanimage",
    "qwen-image",
    "qwen image",
    "wan2",
    "wan 2",
    "muse image",
    "muse video",
    "ernie-image",
    "gemini omni",
    "nano banana",
    "avatar v",
    "hunyuanvideo-avatar",
    "just-dub-it",
    "musetalk",
    "fashn vton",
    "fit dataset",
)
ARTIFACT_TERMS = (
    "code",
    "data",
    "dataset",
    "download",
    "github",
    "hugging face",
    "model",
    "paper",
    "report",
    "weights",
)
CONTEXTUAL_TRACKS = {"digital-human-and-localization", "virtual-try-on-and-commerce"}
REVISION_ONLY_TRACKS = {
    "important-dataset-updates",
    "important-model-updates",
    "source-platform-updates",
}
INDEX_HOSTS = {"github.com", "huggingface.co"}
IGNORED_PATH_PARTS = (
    "/login",
    "/signup",
    "/search",
    "/privacy",
    "/terms",
    "/contact",
    "/about",
    "/careers",
    "/pricing",
    "/topics/",
    "/tags/",
    "/category/",
    "/categories/",
    "/actions",
    "/activity",
    "/branches",
    "/commits/",
    "/custom-properties",
    "/discussions",
    "/forks",
    "/graphs/",
    "/issues",
    "/projects",
    "/pulls",
    "/pulse",
    "/security",
    "/spaces/",
    "/stargazers",
    "/tags",
    "/tree/",
    "/blob/",
    "/bibtex",
    "/watchers",
)
IGNORED_EXTENSIONS = (
    ".css",
    ".js",
    ".json",
    ".xml",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".zip",
    ".tar",
    ".gz",
)
TRANSIENT_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}
RETRY_DELAYS = (0.5, 1.5, 4.0)


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str
    review_priority: str = "standard"
    priority_score: int = 0
    priority_signals: tuple[str, ...] = ()
    created_at: str | None = None
    downloads: int | None = None
    likes: int | None = None
    gated: bool | str | None = None


@dataclass(frozen=True)
class RankingEntry:
    rank: int
    creator: str
    model: str
    score: float
    confidence_interval: str
    samples: int | None
    released: str
    open_weights: bool
    license: str | None = None
    component_models: tuple[str, ...] = ()

    @property
    def elo(self) -> int:
        """Backward-compatible view for callers that still name AA scores Elo."""
        return round(self.score)


@dataclass(frozen=True, order=True)
class WatchSource:
    track_id: str
    source_url: str
    catalog_id: str | None = None
    priority: str | None = None
    model_id: str | None = None
    ranking_id: str | None = None
    ranking_limit: int | None = None
    ranking_provider: str | None = None
    ranking_label: str | None = None
    ranking_modality: str | None = None
    ranking_parser: str | None = None
    ranking_score_label: str | None = None
    ranking_date_label: str | None = None
    ranking_coverage_policy: str | None = None
    ranking_page_url: str | None = None
    platform_id: str | None = None
    revision_mode: str | None = None


@dataclass(frozen=True)
class SourceSnapshot:
    track_id: str
    source_url: str
    resolved_url: str | None
    status: int | None
    candidates: tuple[Candidate, ...]
    error: str | None
    revision: str | None = None
    revision_url: str | None = None
    catalog_id: str | None = None
    priority: str | None = None
    model_id: str | None = None
    ranking_id: str | None = None
    rankings: tuple[RankingEntry, ...] = ()
    ranking_provider: str | None = None
    ranking_label: str | None = None
    ranking_modality: str | None = None
    ranking_parser: str | None = None
    ranking_score_label: str | None = None
    ranking_date_label: str | None = None
    ranking_coverage_policy: str | None = None
    ranking_page_url: str | None = None
    platform_id: str | None = None
    revision_mode: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidates"] = [asdict(candidate) for candidate in self.candidates]
        payload["rankings"] = [asdict(entry) for entry in self.rankings]
        return payload


@dataclass(frozen=True)
class DiscoveryDiff:
    new_candidates: tuple[dict[str, Any], ...]
    source_updates: tuple[dict[str, Any], ...]
    failures: tuple[dict[str, Any], ...]
    recoveries: tuple[dict[str, Any], ...]
    ranking_updates: tuple[dict[str, Any], ...] = ()
    ranking_coverage_gaps: tuple[dict[str, Any], ...] = ()

    @property
    def has_updates(self) -> bool:
        return bool(
            self.new_candidates
            or self.source_updates
            or self.failures
            or self.recoveries
            or self.ranking_updates
            or self.ranking_coverage_gaps
        )


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._href: str | None = None
        self._text: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a" or self._href is not None:
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, normalize_text(" ".join(self._text))))
            self._href = None
            self._text = []


class TableParser(HTMLParser):
    """Collect visible table cells without depending on provider CSS classes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_row = False
        self._cell_depth = 0
        self._cell_text: list[str] = []
        self._row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        tag = tag.lower()
        if tag == "tr":
            self._in_row = True
            self._row = []
        elif self._in_row and tag in {"td", "th"}:
            self._cell_depth = 1
            self._cell_text = []
        elif self._cell_depth:
            self._cell_depth += 1

    def handle_data(self, data: str) -> None:
        if self._cell_depth:
            self._cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._cell_depth:
            self._cell_depth -= 1
            if self._cell_depth == 0:
                self._row.append(normalize_text(" ".join(self._cell_text)))
                self._cell_text = []
        if tag == "tr" and self._in_row:
            if self._row:
                self.rows.append(self._row)
            self._in_row = False
            self._row = []


class RevisionTextParser(HTMLParser):
    """Collect stable human-visible page text while excluding executable payloads."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}
    META_FIELDS = {
        "description",
        "og:title",
        "og:description",
        "twitter:title",
        "twitter:description",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skipped: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS:
            self._skipped.append(tag)
            return
        if self._skipped or tag != "meta":
            return
        attributes = {key.lower(): value for key, value in attrs if value is not None}
        field = (attributes.get("name") or attributes.get("property") or "").lower()
        content = attributes.get("content")
        if field in self.META_FIELDS and content:
            self.parts.append(content)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS and tag in self._skipped:
            reverse_index = self._skipped[::-1].index(tag)
            del self._skipped[len(self._skipped) - reverse_index - 1]

    def handle_data(self, data: str) -> None:
        if not self._skipped:
            self.parts.append(data)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_ranking_name(value: str) -> str:
    return normalize_text(value).casefold()


def normalize_url(value: str, base_url: str | None = None) -> str | None:
    absolute = urllib.parse.urljoin(base_url or value, value)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    scheme = "https" if parsed.scheme == "http" else parsed.scheme
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    netloc = hostname
    if port and not (scheme == "https" and port == 443):
        netloc = f"{hostname}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query_items = []
    for key, item in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in {"ref", "source", "tab", "trk"}:
            continue
        query_items.append((key, item))
    query = urllib.parse.urlencode(sorted(query_items))
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def is_relevant_candidate(title: str, url: str) -> bool:
    lowered_url = url.lower()
    parsed = urllib.parse.urlsplit(lowered_url)
    path = parsed.path
    if any(part in path for part in IGNORED_PATH_PARTS) or path.endswith(IGNORED_EXTENSIONS):
        return False
    social_share_paths = {
        "facebook.com": ("/sharer",),
        "www.facebook.com": ("/sharer",),
        "linkedin.com": ("/sharearticle",),
        "www.linkedin.com": ("/sharearticle",),
        "reddit.com": ("/submit",),
        "www.reddit.com": ("/submit",),
        "x.com": ("/intent/",),
        "twitter.com": ("/intent/",),
    }
    if any(path.startswith(prefix) for prefix in social_share_paths.get(parsed.hostname or "", ())):
        return False
    blob = f"{title} {urllib.parse.unquote(lowered_url)}".lower()
    if any(name in blob for name in STRONG_MEDIA_NAMES):
        return True
    return any(term in blob for term in MEDIA_TERMS) and any(term in blob for term in SIGNAL_TERMS)


def _strip_tags(fragment: str) -> str:
    return normalize_text(re.sub(r"<[^>]+>", " ", fragment))


def extract_source_revision(payload: str, source_url: str) -> tuple[str | None, str | None]:
    """Extract a stable revision from supported first-party repository APIs."""
    parsed_url = urllib.parse.urlsplit(source_url)
    if parsed_url.hostname == "export.arxiv.org" and parsed_url.path == "/api/query":
        try:
            root = ET.fromstring(payload)
        except ET.ParseError:
            return None, None
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        entries: list[tuple[str, str]] = []
        for entry in root.findall("atom:entry", namespace):
            entry_id = normalize_text(entry.findtext("atom:id", default="", namespaces=namespace))
            entry_updated = normalize_text(entry.findtext("atom:updated", default="", namespaces=namespace))
            if entry_id and entry_updated:
                entries.append((entry_id.replace("http://arxiv.org/", "https://arxiv.org/"), entry_updated))
        if not entries:
            return None, None
        stable_entries = sorted(entries)
        revision = "|".join(f"{entry_id}@{updated}" for entry_id, updated in stable_entries)
        revision_url = stable_entries[0][0]
        return revision, revision_url if len(stable_entries) == 1 else None
    try:
        metadata = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return None, None
    if not isinstance(metadata, dict):
        return None, None
    if parsed_url.hostname == "huggingface.co" and parsed_url.path.startswith("/api/datasets/"):
        dataset_id = metadata.get("id")
        sha = metadata.get("sha")
        modified = metadata.get("lastModified")
        if not isinstance(dataset_id, str) or not isinstance(sha, str) or not sha:
            return None, None
        revision = sha if not isinstance(modified, str) or not modified else f"{modified}@{sha}"
        return revision, f"https://huggingface.co/datasets/{dataset_id}"

    if parsed_url.hostname == "huggingface.co" and parsed_url.path.startswith("/api/models/"):
        model_id = metadata.get("id")
        sha = metadata.get("sha")
        modified = metadata.get("lastModified")
        if not isinstance(model_id, str) or not isinstance(sha, str) or not sha:
            return None, None
        revision = sha if not isinstance(modified, str) or not modified else f"{modified}@{sha}"
        return revision, f"https://huggingface.co/{model_id}"

    if parsed_url.hostname == "api.github.com" and re.fullmatch(
        r"/repos/[^/]+/[^/]+/commits/[^/]+", parsed_url.path
    ):
        sha = metadata.get("sha")
        html_url = metadata.get("html_url")
        commit = metadata.get("commit")
        committer = commit.get("committer") if isinstance(commit, dict) else None
        committed_at = committer.get("date") if isinstance(committer, dict) else None
        if not isinstance(sha, str) or not sha:
            return None, None
        revision = sha if not isinstance(committed_at, str) or not committed_at else f"{committed_at}@{sha}"
        return revision, html_url if isinstance(html_url, str) else None

    if parsed_url.hostname in {"zenodo.org", "www.zenodo.org"} and re.fullmatch(
        r"/api/records/\d+", parsed_url.path
    ):
        modified = metadata.get("modified")
        record_revision = metadata.get("revision")
        links = metadata.get("links")
        html_url = links.get("html") if isinstance(links, dict) else None
        doi_url = metadata.get("doi_url")
        if not isinstance(modified, str) or not modified:
            return None, None
        revision = modified
        if isinstance(record_revision, (int, str)) and str(record_revision):
            revision = f"{modified}@revision-{record_revision}"
        stable_url = html_url if isinstance(html_url, str) else doi_url if isinstance(doi_url, str) else None
        return revision, stable_url

    if parsed_url.hostname in {"modelscope.cn", "www.modelscope.cn"} and re.fullmatch(
        r"/api/v1/datasets/[^/]+/[^/]+", parsed_url.path
    ):
        dataset = metadata.get("Data")
        if not isinstance(dataset, dict):
            return None, None
        namespace = dataset.get("Namespace")
        name = dataset.get("Name")
        dataset_id = dataset.get("Id")
        # ModelScope's GmtModified can advance with counters such as downloads,
        # while LastUpdatedTime tracks the dataset artifact/card revision. Prefer
        # the latter so popularity changes do not create false content updates.
        modified = dataset.get("LastUpdatedTime") or dataset.get("GmtModified")
        if (
            not isinstance(namespace, str)
            or not namespace
            or not isinstance(name, str)
            or not name
            or not isinstance(dataset_id, (int, str))
            or not str(dataset_id)
            or not isinstance(modified, (int, str))
            or not str(modified)
        ):
            return None, None
        return (
            f"{modified}@dataset-{dataset_id}",
            f"https://modelscope.cn/datasets/{namespace}/{name}",
        )

    return None, None


def canonical_revision_payload(payload: bytes) -> bytes:
    """Remove transport and hydration noise before hashing official page content."""
    stripped = payload.lstrip()
    if stripped.startswith(b"%PDF"):
        return payload

    text = payload.decode("utf-8", errors="replace")
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        value = None
    if value is not None:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    lowered = stripped[:512].lower()
    if b"<html" in lowered or b"<!doctype html" in lowered:
        parser = RevisionTextParser()
        parser.feed(text)
        visible_text = normalize_text(" ".join(parser.parts))
        if visible_text:
            return visible_text.encode("utf-8")
    return payload


def content_revision(payload: bytes) -> str:
    """Return a stable revision for JSON, visible HTML content, and binary files."""
    canonical = canonical_revision_payload(payload)
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def extract_candidate_links(html: str, base_url: str, contextual: bool = False) -> tuple[Candidate, ...]:
    parser = AnchorParser()
    parser.feed(html)
    raw_links = list(parser.links)

    # arXiv listing anchors contain identifiers rather than titles, so retain
    # the title block paired with each /abs/ link.
    arxiv_pattern = re.compile(
        r'<dt>.*?href\s*=\s*["\'](?P<href>/abs/[^"\']+)["\'].*?</dt>\s*'
        r'<dd>.*?<div[^>]+class=["\'][^"\']*list-title[^"\']*["\'][^>]*>'
        r'(?P<title>.*?)</div>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in arxiv_pattern.finditer(html):
        title = re.sub(r"^Title:\s*", "", _strip_tags(match.group("title")), flags=re.IGNORECASE)
        raw_links.append((match.group("href"), title))

    # XML sitemaps are often more stable than bot-protected news indexes. The
    # canonical <loc> path supplies a conservative title for keyword triage.
    sitemap_pattern = re.compile(r"<loc>\s*(?P<url>https?://[^<]+)\s*</loc>", re.IGNORECASE)
    for match in sitemap_pattern.finditer(html):
        item_url = normalize_text(match.group("url"))
        slug = urllib.parse.urlsplit(item_url).path.rstrip("/").rsplit("/", 1)[-1]
        title = normalize_text(urllib.parse.unquote(slug).replace("-", " "))
        raw_links.append((item_url, title))

    source = normalize_url(base_url)
    candidates: dict[str, Candidate] = {}
    for href, title in raw_links:
        url = normalize_url(href, base_url)
        artifact_blob = f"{title} {urllib.parse.unquote(urllib.parse.urlsplit(url).path)}".lower() if url else ""
        artifact = contextual and any(term in artifact_blob for term in ARTIFACT_TERMS)
        if not url or url == source or not title or not (is_relevant_candidate(title, url) or artifact):
            continue
        current = candidates.get(url)
        candidate = Candidate(title=title[:240], url=url)
        if current is None or len(candidate.title) > len(current.title):
            candidates[url] = candidate
    return tuple(sorted(candidates.values(), key=lambda item: (item.url, item.title.lower())))


def extract_huggingface_dataset_candidates(payload: str) -> tuple[Candidate, ...]:
    """Turn a Hugging Face search response into ranked human-review candidates.

    The score prioritizes review effort; it is not a claim about dataset quality.
    Low-signal records remain in the queue so a new dataset is never hidden merely
    because it has not accumulated downloads or likes yet.
    """
    try:
        records = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return ()
    if not isinstance(records, list):
        return ()

    candidates: dict[str, Candidate] = {}
    for record in records:
        dataset_id = record.get("id") if isinstance(record, dict) else None
        if not isinstance(dataset_id, str) or not dataset_id or "/" not in dataset_id:
            continue
        url = normalize_url(f"https://huggingface.co/datasets/{dataset_id}")
        if not url:
            continue

        tags = record.get("tags") if isinstance(record.get("tags"), list) else []
        string_tags = [tag for tag in tags if isinstance(tag, str)]
        card_data = record.get("cardData") if isinstance(record.get("cardData"), dict) else {}
        dataset_info = card_data.get("dataset_info")
        description = record.get("description") if isinstance(record.get("description"), str) else ""
        blob = " ".join([dataset_id, description, *string_tags]).casefold()
        core_terms = (
            "text-to-image", "text to image", "image-generation", "image generation",
            "text-to-video", "text to video", "video-generation", "video generation",
            "image-to-video", "image to video", "talking-head", "talking head",
            "video-dubbing", "video dubbing", "virtual-try-on", "virtual try-on",
        )
        score = 0
        signals: list[str] = []
        if any(term in blob for term in core_terms):
            score += 4
            signals.append("explicit-generative-media-match")
        if any(tag in {"modality:image", "modality:video"} for tag in string_tags):
            score += 2
            signals.append("image-or-video-modality")
        if any(tag.startswith("arxiv:") for tag in string_tags):
            score += 2
            signals.append("paper-linked")
        if description.strip() or isinstance(dataset_info, dict):
            score += 2
            signals.append("dataset-card-metadata")
        if any(tag.startswith("license:") for tag in string_tags) or card_data.get("license"):
            score += 1
            signals.append("license-declared")
        if any(tag.startswith("size_categories:") for tag in string_tags) or (
            isinstance(dataset_info, dict) and dataset_info.get("splits")
        ):
            score += 1
            signals.append("size-declared")

        downloads = record.get("downloads") if isinstance(record.get("downloads"), int) else None
        likes = record.get("likes") if isinstance(record.get("likes"), int) else None
        if (downloads or 0) >= 100 or (likes or 0) >= 2:
            score += 1
            signals.append("usage-signal")
        if record.get("gated") not in {None, False}:
            signals.append("gated-access")
        if record.get("private") is True or record.get("disabled") is True:
            score -= 4
            signals.append("disabled-or-private")
        if not description.strip() and not isinstance(dataset_info, dict):
            score -= 2
            signals.append("thin-metadata")
        if re.search(r"\.(?:zip|tar|gz|7z)$", dataset_id, re.IGNORECASE):
            score -= 2
            signals.append("archive-like-name")

        priority = "high" if score >= 7 else "standard" if score >= 3 else "low"
        created_at = record.get("createdAt")
        candidates[url] = Candidate(
            title=dataset_id[:240],
            url=url,
            review_priority=priority,
            priority_score=score,
            priority_signals=tuple(signals),
            created_at=created_at if isinstance(created_at, str) else None,
            downloads=downloads,
            likes=likes,
            gated=record.get("gated") if isinstance(record.get("gated"), (bool, str)) else None,
        )
    priority_order = {"high": 0, "standard": 1, "low": 2}
    return tuple(
        sorted(
            candidates.values(),
            key=lambda item: (
                priority_order[item.review_priority],
                -item.priority_score,
                item.url.lower(),
            ),
        )
    )


def extract_ranking_entries(html: str, limit: int = 15) -> tuple[RankingEntry, ...]:
    """Parse Artificial Analysis leaderboard tables into a stable top-N snapshot."""
    parser = TableParser()
    parser.feed(html)
    entries: list[RankingEntry] = []
    for row in parser.rows:
        if len(row) < 8 or not re.fullmatch(r"\d+", row[0].replace(",", "")):
            continue
        rank = int(row[0].replace(",", ""))
        if rank > limit:
            continue
        try:
            elo = int(row[4].replace(",", ""))
        except ValueError:
            continue
        model_cell = row[3]
        open_weights = model_cell.endswith("Open Weights")
        model = re.sub(r"\s*Open Weights\s*$", "", model_cell).strip()
        sample_text = row[6].replace(",", "")
        samples = int(sample_text) if sample_text.isdigit() else None
        entries.append(
            RankingEntry(
                rank=rank,
                creator=row[2],
                model=model,
                score=elo,
                confidence_interval=row[5],
                samples=samples,
                released=row[7],
                open_weights=open_weights,
                license="Open weights" if open_weights else "Proprietary / service",
            )
        )
    return tuple(sorted(entries, key=lambda item: item.rank)[:limit])


def extract_arena_ranking_entries(payload: str, limit: int = 15) -> tuple[RankingEntry, ...]:
    """Parse Arena's official Hugging Face leaderboard dataset API."""
    try:
        response = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return ()
    rows = response.get("rows") if isinstance(response, dict) else None
    if not isinstance(rows, list):
        return ()

    entries: list[RankingEntry] = []
    for item in rows:
        row = item.get("row") if isinstance(item, dict) else None
        if not isinstance(row, dict) or row.get("category") != "overall":
            continue
        rank = row.get("rank")
        rating = row.get("rating")
        if not isinstance(rank, int) or rank < 1 or rank > limit or not isinstance(rating, (int, float)):
            continue
        model = row.get("model_name")
        creator = row.get("organization")
        license_name = row.get("license")
        if not isinstance(model, str) or not model or not isinstance(creator, str):
            continue
        lower = row.get("rating_lower")
        upper = row.get("rating_upper")
        confidence_interval = ""
        if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
            confidence_interval = f"{round(lower)}–{round(upper)}"
        samples = row.get("vote_count") if isinstance(row.get("vote_count"), int) else None
        released = row.get("leaderboard_publish_date")
        license_text = license_name if isinstance(license_name, str) and license_name else None
        open_weights = bool(license_text and license_text.casefold() != "proprietary")
        entries.append(
            RankingEntry(
                rank=rank,
                creator=creator,
                model=model,
                score=round(float(rating), 1),
                confidence_interval=confidence_interval,
                samples=samples,
                released=released if isinstance(released, str) else "",
                open_weights=open_weights,
                license=license_text,
            )
        )
    return tuple(sorted(entries, key=lambda item: item.rank)[:limit])


def extract_avgen_ranking_entries(payload: str, limit: int = 15) -> tuple[RankingEntry, ...]:
    """Parse the compact leaderboard in AVGen-Bench's official Markdown README."""
    compact_table = re.search(
        r"\|\s*Model\s*\|\s*Components\s*\|\s*Total\s*\|"
        r"(?P<body>.*?)"
        r"(?:\n\s*<details>|\n\s*Full per-metric results|\n\s*##\s+)",
        payload,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if compact_table is None:
        return ()

    entries: list[RankingEntry] = []
    for line in compact_table.group("body").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or set(cells[0]) <= {"-", ":"}:
            continue
        model, components, total = cells
        model = re.sub(r"[*_`]", "", model).strip()
        components = re.sub(r"[*_`]", "", components).strip()
        total = re.sub(r"[*_`]", "", total).strip()
        try:
            score = float(total)
        except ValueError:
            continue
        has_open = "(open-source)" in components.casefold()
        has_proprietary = "(proprietary)" in components.casefold()
        if has_open and has_proprietary:
            license_name = "Mixed pipeline"
            open_weights = False
        elif has_open:
            license_name = "Open-source"
            open_weights = True
        else:
            license_name = "Proprietary"
            open_weights = False
        entries.append(
            RankingEntry(
                rank=len(entries) + 1,
                creator=components,
                model=model,
                score=score,
                confidence_interval="",
                samples=None,
                released="",
                open_weights=open_weights,
                license=license_name,
                component_models=tuple(
                    re.sub(
                        r"\s*\((?:open-source|proprietary)\)\s*$",
                        "",
                        component,
                        flags=re.IGNORECASE,
                    ).strip()
                    for component in re.split(r"\s+\+\s+", components)
                    if component.strip()
                ),
            )
        )
        if len(entries) >= limit:
            break
    return tuple(entries)


def _fetch_source_once(source: WatchSource, timeout: float, max_bytes: int) -> SourceSnapshot:
    track_id = source.track_id
    source_url = source.source_url
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json,application/json,text/html;q=0.9,*/*;q=0.5",
    }
    hostname = (urllib.parse.urlsplit(source_url).hostname or "").lower()
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if hostname == "api.github.com" and github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    request = urllib.request.Request(source_url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                return SourceSnapshot(
                    track_id,
                    source_url,
                    response.url,
                    response.status,
                    (),
                    "response-too-large",
                    catalog_id=source.catalog_id,
                    priority=source.priority,
                    model_id=source.model_id,
                    ranking_id=source.ranking_id,
                    ranking_provider=source.ranking_provider,
                    ranking_label=source.ranking_label,
                    ranking_modality=source.ranking_modality,
                    ranking_parser=source.ranking_parser,
                    ranking_score_label=source.ranking_score_label,
                    ranking_date_label=source.ranking_date_label,
                    ranking_coverage_policy=source.ranking_coverage_policy,
                    ranking_page_url=source.ranking_page_url,
                    platform_id=source.platform_id,
                    revision_mode=source.revision_mode,
                )
            charset = response.headers.get_content_charset() or "utf-8"
            html = payload.decode(charset, errors="replace")
            hostname = (urllib.parse.urlsplit(response.url).hostname or "").lower()
            revision, revision_url = extract_source_revision(html, response.url)
            if source.revision_mode == "availability":
                revision = "reachable" if track_id == "source-platform-updates" else f"http-{response.status}"
                revision_url = normalize_url(response.url)
            elif revision is None and track_id in {
                "important-dataset-updates",
                "important-model-updates",
            }:
                revision = content_revision(payload)
                revision_url = normalize_url(response.url)
            elif track_id == "source-platform-updates":
                revision = (
                    content_revision(payload)
                    if source.revision_mode == "content-revision"
                    else "reachable"
                )
                revision_url = normalize_url(response.url)
            if track_id in REVISION_ONLY_TRACKS:
                rankings = ()
                candidates = ()
            elif source.ranking_id:
                ranking_extractors = {
                    "artificial-analysis-html": extract_ranking_entries,
                    "arena-hf-dataset": extract_arena_ranking_entries,
                    "avgen-markdown": extract_avgen_ranking_entries,
                }
                rankings = ranking_extractors[source.ranking_parser or "artificial-analysis-html"](
                    html, source.ranking_limit or 15
                )
                candidates: tuple[Candidate, ...] = ()
                if not rankings:
                    raise ValueError("ranking-table-empty")
            elif hostname == "huggingface.co" and urllib.parse.urlsplit(response.url).path == "/api/datasets":
                rankings = ()
                candidates = extract_huggingface_dataset_candidates(html)
            else:
                rankings = ()
                candidates = extract_candidate_links(
                    html,
                    response.url,
                    contextual=track_id in CONTEXTUAL_TRACKS and hostname not in INDEX_HOSTS,
                )
            return SourceSnapshot(
                track_id=track_id,
                source_url=source_url,
                resolved_url=normalize_url(response.url),
                status=response.status,
                candidates=candidates,
                error=None,
                revision=revision,
                revision_url=revision_url,
                catalog_id=source.catalog_id,
                priority=source.priority,
                model_id=source.model_id,
                ranking_id=source.ranking_id,
                rankings=rankings,
                ranking_provider=source.ranking_provider,
                ranking_label=source.ranking_label,
                ranking_modality=source.ranking_modality,
                ranking_parser=source.ranking_parser,
                ranking_score_label=source.ranking_score_label,
                ranking_date_label=source.ranking_date_label,
                ranking_coverage_policy=source.ranking_coverage_policy,
                ranking_page_url=source.ranking_page_url,
                platform_id=source.platform_id,
                revision_mode=source.revision_mode,
            )
    except urllib.error.HTTPError as exc:
        if source.revision_mode == "availability" and exc.code in {401, 403, 405, 429}:
            return SourceSnapshot(
                track_id=track_id,
                source_url=source_url,
                resolved_url=normalize_url(exc.url),
                status=exc.code,
                candidates=(),
                error=None,
                revision="reachable" if track_id == "source-platform-updates" else f"http-{exc.code}",
                revision_url=normalize_url(exc.url),
                catalog_id=source.catalog_id,
                priority=source.priority,
                model_id=source.model_id,
                platform_id=source.platform_id,
                revision_mode=source.revision_mode,
            )
        error = f"HTTP {exc.code}"
    except TimeoutError:
        error = "timeout"
    except urllib.error.URLError as exc:
        error = f"network-{type(exc.reason).__name__}"
    except OSError as exc:
        error = f"network-{type(exc).__name__}"
    except (UnicodeError, ValueError) as exc:
        error = f"parse-{type(exc).__name__}"
    return SourceSnapshot(
        track_id,
        source_url,
        None,
        None,
        (),
        error,
        catalog_id=source.catalog_id,
        priority=source.priority,
        model_id=source.model_id,
        ranking_id=source.ranking_id,
        ranking_provider=source.ranking_provider,
        ranking_label=source.ranking_label,
        ranking_modality=source.ranking_modality,
        ranking_parser=source.ranking_parser,
        ranking_score_label=source.ranking_score_label,
        ranking_date_label=source.ranking_date_label,
        ranking_coverage_policy=source.ranking_coverage_policy,
        ranking_page_url=source.ranking_page_url,
        platform_id=source.platform_id,
        revision_mode=source.revision_mode,
    )


def _is_transient_fetch_error(error: str | None) -> bool:
    if not error:
        return False
    if error == "timeout" or error.startswith("network-"):
        return True
    if error.startswith("HTTP "):
        try:
            return int(error.removeprefix("HTTP ")) in TRANSIENT_HTTP_CODES
        except ValueError:
            return False
    return False


def _fetch_source(
    source: WatchSource,
    timeout: float,
    max_bytes: int,
    retry_delays: tuple[float, ...] = RETRY_DELAYS,
) -> SourceSnapshot:
    """Fetch one source and retry only transport or retryable HTTP failures."""
    snapshot = _fetch_source_once(source, timeout, max_bytes)
    for delay in retry_delays:
        if not _is_transient_fetch_error(snapshot.error):
            break
        time.sleep(delay)
        snapshot = _fetch_source_once(source, timeout, max_bytes)
    return snapshot


def load_watchlist(path: Path) -> tuple[dict[str, Any], list[WatchSource]]:
    watchlist = yaml.safe_load(path.read_text(encoding="utf-8"))
    discovery = watchlist.get("discovery", {})
    included = set(discovery.get("included_tracks", []))
    excluded = {normalize_url(url) or url for url in discovery.get("excluded_sources", [])}
    dataset_ids = {card["id"] for _, card in load_cards()}
    model_ids = {card["id"] for _, card in load_models()}
    sources: list[WatchSource] = []
    seen_urls: set[str] = set()
    for track in watchlist["tracks"]:
        track_id = track["id"]
        if included and track_id not in included:
            continue
        for source in track["official_sources"]:
            catalog_id = None
            priority = None
            model_id = None
            ranking_id = None
            ranking_limit = None
            ranking_provider = None
            ranking_label = None
            ranking_modality = None
            ranking_parser = None
            ranking_score_label = None
            ranking_date_label = None
            ranking_coverage_policy = None
            ranking_page_url = None
            revision_mode = None
            if isinstance(source, dict):
                unexpected = set(source) - {
                    "url",
                    "catalog_id",
                    "model_id",
                    "priority",
                    "ranking_id",
                    "ranking_limit",
                    "ranking_provider",
                    "ranking_label",
                    "ranking_modality",
                    "ranking_parser",
                    "ranking_score_label",
                    "ranking_date_label",
                    "ranking_coverage_policy",
                    "ranking_page_url",
                    "revision_mode",
                }
                if unexpected:
                    raise ValueError(f"watch source has unsupported keys: {sorted(unexpected)}")
                url = source.get("url")
                catalog_id = source.get("catalog_id")
                priority = source.get("priority")
                model_id = source.get("model_id")
                ranking_id = source.get("ranking_id")
                ranking_limit = source.get("ranking_limit")
                ranking_provider = source.get("ranking_provider")
                ranking_label = source.get("ranking_label")
                ranking_modality = source.get("ranking_modality")
                ranking_parser = source.get("ranking_parser")
                ranking_score_label = source.get("ranking_score_label")
                ranking_date_label = source.get("ranking_date_label")
                ranking_coverage_policy = source.get("ranking_coverage_policy")
                ranking_page_url = source.get("ranking_page_url")
                revision_mode = source.get("revision_mode")
            else:
                url = source
            if not isinstance(url, str) or not url.startswith("https://"):
                raise ValueError(f"watch source requires an HTTPS url: {url!r}")
            if catalog_id is not None and catalog_id not in dataset_ids:
                raise ValueError(f"watch source references unknown dataset catalog_id: {catalog_id!r}")
            if model_id is not None and model_id not in model_ids:
                raise ValueError(f"watch source references unknown model model_id: {model_id!r}")
            if priority is not None and priority not in {"critical", "high", "standard"}:
                raise ValueError(f"watch source has invalid priority: {priority!r}")
            if revision_mode is not None and (
                track_id not in {"important-dataset-updates", "important-model-updates"}
                or revision_mode not in {"content-revision", "availability"}
            ):
                raise ValueError(
                    "revision_mode is only valid for important dataset/model sources and must be "
                    "content-revision or availability"
                )
            if ranking_id is not None and (
                not isinstance(ranking_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ranking_id)
            ):
                raise ValueError(f"watch source has invalid ranking_id: {ranking_id!r}")
            if ranking_limit is not None and (
                not isinstance(ranking_limit, int) or not 1 <= ranking_limit <= 100
            ):
                raise ValueError(f"watch source has invalid ranking_limit: {ranking_limit!r}")
            ranking_metadata = {
                "ranking_provider": ranking_provider,
                "ranking_label": ranking_label,
                "ranking_modality": ranking_modality,
                "ranking_parser": ranking_parser,
                "ranking_score_label": ranking_score_label,
                "ranking_date_label": ranking_date_label,
                "ranking_coverage_policy": ranking_coverage_policy,
                "ranking_page_url": ranking_page_url,
            }
            if track_id == "important-dataset-updates":
                if catalog_id is None or priority is None or model_id is not None:
                    raise ValueError(
                        "important dataset watch sources require catalog_id and priority only"
                    )
            if track_id == "important-model-updates":
                if model_id is None or priority is None or catalog_id is not None:
                    raise ValueError(
                        "important model watch sources require model_id and priority only"
                    )
            if track_id == "industry-model-rankings":
                if (
                    ranking_id is None
                    or ranking_limit is None
                    or not all(isinstance(value, str) and value for value in ranking_metadata.values())
                    or catalog_id is not None
                    or model_id is not None
                    or priority is not None
                ):
                    raise ValueError(
                        "ranking watch sources require ranking_id and ranking_limit only"
                    )
                if ranking_modality not in {"image", "video"}:
                    raise ValueError(f"ranking source has invalid modality: {ranking_modality!r}")
                if ranking_parser not in {
                    "artificial-analysis-html",
                    "arena-hf-dataset",
                    "avgen-markdown",
                }:
                    raise ValueError(f"ranking source has invalid parser: {ranking_parser!r}")
                if ranking_coverage_policy not in {"required", "monitor"}:
                    raise ValueError(
                        f"ranking source has invalid coverage policy: {ranking_coverage_policy!r}"
                    )
                if not ranking_page_url.startswith("https://"):
                    raise ValueError(f"ranking page requires an HTTPS url: {ranking_page_url!r}")
            elif ranking_id is not None or ranking_limit is not None or any(
                value is not None for value in ranking_metadata.values()
            ):
                raise ValueError("ranking metadata is only valid for industry-model-rankings")
            normalized = normalize_url(url) or url
            if normalized in seen_urls or normalized in excluded:
                continue
            seen_urls.add(normalized)
            sources.append(
                WatchSource(
                    track_id,
                    url,
                    catalog_id,
                    priority,
                    model_id,
                    ranking_id,
                    ranking_limit,
                    ranking_provider,
                    ranking_label,
                    ranking_modality,
                    ranking_parser,
                    ranking_score_label,
                    ranking_date_label,
                    ranking_coverage_policy,
                    ranking_page_url,
                    revision_mode=revision_mode,
                )
            )
    if not included or "source-platform-updates" in included:
        platform_ids: set[str] = set()
        for platform in load_source_platforms():
            platform_id = platform["id"]
            monitoring = platform["monitoring"]
            url = monitoring["url"]
            normalized = normalize_url(url) or url
            if platform_id in platform_ids:
                raise ValueError(f"duplicate source platform monitor id: {platform_id!r}")
            if normalized in excluded:
                continue
            if normalized in seen_urls:
                raise ValueError(
                    f"source platform monitor duplicates another watch URL: {url!r}"
                )
            platform_ids.add(platform_id)
            seen_urls.add(normalized)
            sources.append(
                WatchSource(
                    track_id="source-platform-updates",
                    source_url=url,
                    priority=monitoring["priority"],
                    platform_id=platform_id,
                    revision_mode=monitoring["mode"],
                )
            )
    return watchlist, sorted(sources)


def scan_sources(
    sources: list[WatchSource], timeout: float, max_bytes: int, workers: int
) -> tuple[SourceSnapshot, ...]:
    snapshots: list[SourceSnapshot] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_fetch_source, source, timeout, max_bytes): source
            for source in sources
        }
        for future in concurrent.futures.as_completed(futures):
            snapshots.append(future.result())
    return tuple(sorted(snapshots, key=lambda item: (item.track_id, item.source_url)))


def declared_urls(watchlist: dict[str, Any] | None = None) -> set[str]:
    urls: set[str] = set()
    for _, card in load_cards():
        values = [
            card["release_date_source"],
            card["access"]["url"],
            card["evidence"]["homepage"],
            card["evidence"]["paper"],
        ]
        urls.update(url for value in values if value and (url := normalize_url(value)))
    for _, card in load_models():
        values = list(card["access"].values()) + list(card["evidence"].values())
        urls.update(url for value in values if isinstance(value, str) and (url := normalize_url(value)))
    for platform in load_source_platforms():
        values = [
            platform["homepage"],
            platform["data_access"]["interface_url"],
            platform["monitoring"]["url"],
        ]
        urls.update(url for value in values if value and (url := normalize_url(value)))
    if watchlist is not None:
        excluded = watchlist.get("discovery", {}).get("excluded_sources", [])
        urls.update(url for value in excluded if (url := normalize_url(value)))
    return urls


def snapshot_payload(snapshots: tuple[SourceSnapshot, ...], generated_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "sources": [snapshot.to_dict() for snapshot in snapshots],
    }


def dataset_impact_index() -> dict[str, dict[str, tuple[str, ...]]]:
    cards = {card["id"]: card for _, card in load_cards()}
    direct_models: dict[str, set[str]] = {card_id: set() for card_id in cards}
    for _, model in load_models():
        for reference in model["data"]["datasets"]:
            catalog_id = reference["catalog_id"]
            if catalog_id is not None:
                direct_models.setdefault(catalog_id, set()).add(model["id"])

    children: dict[str, set[str]] = {card_id: set() for card_id in cards}
    for child_id, card in cards.items():
        for reference in card.get("derived_from", []):
            parent_id = reference["catalog_id"]
            if parent_id in children:
                children[parent_id].add(child_id)

    impacts: dict[str, dict[str, tuple[str, ...]]] = {}
    for source_id in sorted(cards):
        downstream: set[str] = set()
        queue = list(children[source_id])
        while queue:
            child_id = queue.pop()
            if child_id in downstream:
                continue
            downstream.add(child_id)
            queue.extend(children[child_id])
        model_ids = set(direct_models.get(source_id, set()))
        for dataset_id in downstream:
            model_ids.update(direct_models.get(dataset_id, set()))
        impacts[source_id] = {
            "dataset_ids": tuple(sorted(downstream)),
            "model_ids": tuple(sorted(model_ids)),
        }
    return impacts


def model_impact_index() -> dict[str, dict[str, tuple[str, ...]]]:
    """Map a model revision to its directly linked canonical datasets."""
    impacts: dict[str, dict[str, tuple[str, ...]]] = {}
    for _, model in load_models():
        dataset_ids = {
            reference["catalog_id"]
            for reference in model["data"]["datasets"]
            if reference["catalog_id"] is not None
        }
        impacts[model["id"]] = {
            "dataset_ids": tuple(sorted(dataset_ids)),
            "model_ids": (model["id"],),
        }
    return impacts


def model_ranking_aliases() -> set[str]:
    aliases: set[str] = set()
    for _, model in load_models():
        for value in [model["name"], *model.get("ranking_names", [])]:
            aliases.add(normalize_ranking_name(value))
    return aliases


def source_entity_payload(
    source: SourceSnapshot,
    dataset_impacts: dict[str, dict[str, tuple[str, ...]]],
    model_impacts: dict[str, dict[str, tuple[str, ...]]],
) -> dict[str, Any]:
    if source.catalog_id:
        impact = dataset_impacts.get(source.catalog_id, {})
        return {
            "entity_type": "dataset",
            "entity_id": source.catalog_id,
            "catalog_id": source.catalog_id,
            "model_id": None,
            "priority": source.priority or "standard",
            "impacted_dataset_ids": list(impact.get("dataset_ids", ())),
            "impacted_model_ids": list(impact.get("model_ids", ())),
        }
    if source.model_id:
        impact = model_impacts.get(source.model_id, {})
        return {
            "entity_type": "model",
            "entity_id": source.model_id,
            "catalog_id": None,
            "model_id": source.model_id,
            "priority": source.priority or "standard",
            "impacted_dataset_ids": list(impact.get("dataset_ids", ())),
            "impacted_model_ids": list(impact.get("model_ids", (source.model_id,))),
        }
    if source.platform_id:
        return {
            "entity_type": "source-platform",
            "entity_id": source.platform_id,
            "catalog_id": None,
            "model_id": None,
            "platform_id": source.platform_id,
            "priority": source.priority or "standard",
            "impacted_dataset_ids": [],
            "impacted_model_ids": [],
        }
    return {}


def compare_snapshots(
    baseline: dict[str, Any],
    current: tuple[SourceSnapshot, ...],
    known_urls: set[str],
    dataset_impacts: dict[str, dict[str, tuple[str, ...]]] | None = None,
    model_impacts: dict[str, dict[str, tuple[str, ...]]] | None = None,
    ranking_aliases: set[str] | None = None,
) -> DiscoveryDiff:
    baseline_sources = {
        (item["track_id"], item["source_url"]): item for item in baseline.get("sources", [])
    }
    new_candidates: list[dict[str, Any]] = []
    source_updates: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    recoveries: list[dict[str, Any]] = []
    ranking_updates: list[dict[str, Any]] = []
    ranking_coverage_gaps: list[dict[str, Any]] = []
    dataset_impacts = dataset_impacts or {}
    model_impacts = model_impacts or {}

    for source in current:
        key = (source.track_id, source.source_url)
        previous = baseline_sources.get(key, {})
        previous_urls = {item["url"] for item in previous.get("candidates", [])}
        for candidate in source.candidates:
            if candidate.url in previous_urls or candidate.url in known_urls:
                continue
            new_candidates.append({
                "track_id": source.track_id,
                "source_url": source.source_url,
                **asdict(candidate),
            })
        previous_revision = previous.get("revision")
        if (
            not source.error
            and previous_revision
            and source.revision
            and source.revision != previous_revision
        ):
            source_updates.append(
                {
                    "track_id": source.track_id,
                    "source_url": source.source_url,
                    "url": source.revision_url or source.resolved_url or source.source_url,
                    "previous_revision": previous_revision,
                    "revision": source.revision,
                    **source_entity_payload(source, dataset_impacts, model_impacts),
                }
            )
        previous_error = previous.get("error")
        if source.error and source.error != previous_error:
            failure: dict[str, Any] = {
                "track_id": source.track_id,
                "source_url": source.source_url,
                "error": source.error,
            }
            failure.update(source_entity_payload(source, dataset_impacts, model_impacts))
            failures.append(failure)
        elif not source.error and previous_error:
            recovery: dict[str, Any] = {
                "track_id": source.track_id,
                "source_url": source.source_url,
                "previous_error": previous_error,
            }
            recovery.update(source_entity_payload(source, dataset_impacts, model_impacts))
            recoveries.append(recovery)

        if source.ranking_id and not source.error and previous.get("rankings"):
            previous_names = [item["model"] for item in previous["rankings"]]
            current_names = [item.model for item in source.rankings]
            if previous_names != current_names:
                previous_positions = {
                    name: index for index, name in enumerate(previous_names, start=1)
                }
                current_positions = {
                    name: index for index, name in enumerate(current_names, start=1)
                }
                changes = []
                for name in sorted(set(previous_positions) | set(current_positions)):
                    before = previous_positions.get(name)
                    after = current_positions.get(name)
                    if before != after:
                        changes.append({"model": name, "previous_rank": before, "rank": after})
                ranking_updates.append(
                    {
                        "ranking_id": source.ranking_id,
                        "ranking_provider": source.ranking_provider,
                        "source_url": source.ranking_page_url or source.source_url,
                        "changes": changes,
                        "current": [asdict(entry) for entry in source.rankings],
                    }
                )

        if source.ranking_id and not source.error and ranking_aliases is not None:
            for entry in source.rankings:
                component_models = entry.component_models or (entry.model,)
                for component_model in component_models:
                    if normalize_ranking_name(component_model) in ranking_aliases:
                        continue
                    ranking_coverage_gaps.append(
                        {
                            "ranking_id": source.ranking_id,
                            "ranking_provider": source.ranking_provider,
                            "coverage_policy": source.ranking_coverage_policy,
                            "rank": entry.rank,
                            "model": component_model,
                            "ranking_entry": entry.model,
                            "creator": entry.creator,
                            "source_url": source.ranking_page_url or source.source_url,
                        }
                    )

    priority_order = {"high": 0, "standard": 1, "low": 2}
    return DiscoveryDiff(
        new_candidates=tuple(sorted(
            new_candidates,
            key=lambda item: (
                priority_order.get(item.get("review_priority", "standard"), 1),
                -item.get("priority_score", 0),
                item["track_id"],
                item["url"],
            ),
        )),
        source_updates=tuple(
            sorted(source_updates, key=lambda item: (item["track_id"], item["source_url"]))
        ),
        failures=tuple(sorted(failures, key=lambda item: (item["track_id"], item["source_url"]))),
        recoveries=tuple(sorted(recoveries, key=lambda item: (item["track_id"], item["source_url"]))),
        ranking_updates=tuple(
            sorted(ranking_updates, key=lambda item: item["ranking_id"])
        ),
        ranking_coverage_gaps=tuple(
            sorted(
                ranking_coverage_gaps,
                key=lambda item: (item["ranking_id"], item["rank"], item["model"]),
            )
        ),
    )


def report_payload(
    diff: DiscoveryDiff,
    generated_at: str,
    issue_title: str,
    source_count: int,
    focus: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "issue_title": issue_title,
        "focus": focus,
        "source_count": source_count,
        "has_updates": diff.has_updates,
        "new_candidates": list(diff.new_candidates),
        "source_updates": list(diff.source_updates),
        "failures": list(diff.failures),
        "recoveries": list(diff.recoveries),
        "ranking_updates": list(diff.ranking_updates),
        "ranking_coverage_gaps": list(diff.ranking_coverage_gaps),
    }


def render_report(report: dict[str, Any], limit: int = 100) -> str:
    date = report["generated_at"][:10]
    lines = [
        f"# Daily generative-media discovery — {date}",
        "",
        "Automated triage only: every candidate still requires primary-source verification before a card or `last_verified` value changes.",
        "",
        f"- Focus: {', '.join(report['focus'])}",
        f"- Watched sources checked: {report['source_count']}",
        f"- New candidate links: {len(report['new_candidates'])}",
        f"- Important catalog revisions: {len(report['source_updates'])}",
        f"- New source failures: {len(report['failures'])}",
        f"- Source recoveries: {len(report['recoveries'])}",
        f"- Ranking boards changed: {len(report['ranking_updates'])}",
        f"- Ranked models awaiting a verified catalog card: {len(report['ranking_coverage_gaps'])}",
        "",
    ]
    if report["ranking_updates"]:
        lines.extend(["## Ranking changes", ""])
        for board in report["ranking_updates"]:
            lines.append(f"### `{board['ranking_id']}`")
            lines.append("")
            for change in board["changes"]:
                before = change["previous_rank"] if change["previous_rank"] is not None else "outside"
                after = change["rank"] if change["rank"] is not None else "outside"
                lines.append(f"- {change['model']}: {before} → {after}")
            lines.append(f"- [Current leaderboard]({board['source_url']})")
            lines.append("")
    if report["new_candidates"]:
        lines.extend(["## Candidate links", ""])
        shown = report["new_candidates"][:limit]
        for priority in ("high", "standard", "low"):
            group = [item for item in shown if item.get("review_priority", "standard") == priority]
            if not group:
                continue
            lines.extend([f"### {priority.title()} review priority", ""])
            for item in group:
                metadata = []
                if item.get("created_at"):
                    metadata.append(f"created {item['created_at'][:10]}")
                if item.get("downloads") is not None:
                    metadata.append(f"{item['downloads']:,} downloads")
                if item.get("priority_signals"):
                    metadata.append(", ".join(item["priority_signals"]))
                suffix = f"; {'; '.join(metadata)}" if metadata else ""
                lines.append(
                    f"- [ ] [{item['title']}]({item['url']}) — score {item.get('priority_score', 0)}; "
                    f"`{item['track_id']}` via [watch source]({item['source_url']}){suffix}"
                )
            lines.append("")
        if len(report["new_candidates"]) > limit:
            lines.append(f"- … {len(report['new_candidates']) - limit} additional candidates are available in the JSON artifact.")
        lines.append("")
    if report["ranking_coverage_gaps"]:
        lines.extend(["## Ranked models awaiting catalog cards", ""])
        lines.append(
            "These models remain monitored even when a first-party model card has not yet been verified."
        )
        lines.append("")
        for item in report["ranking_coverage_gaps"]:
            lines.append(
                f"- [ ] #{item['rank']} {item['model']} ({item['creator']}) — "
                f"`{item['ranking_id']}` / {item.get('ranking_provider') or 'ranking provider'}; "
                f"[leaderboard]({item['source_url']})"
            )
        lines.append("")
    if report["source_updates"]:
        lines.extend(["## Important catalog revisions", ""])
        for item in report["source_updates"]:
            if item["entity_type"] == "source-platform":
                lines.append(
                    f"- [ ] [`{item['entity_id']}`]({item['url']}) — **{item['priority']}** "
                    f"source-platform access signal; `{item['previous_revision']}` → `{item['revision']}`"
                )
                continue
            empty_dataset_impact = (
                "no linked catalog dataset"
                if item["entity_type"] == "model"
                else "no downstream catalog dataset"
            )
            dataset_impact = ", ".join(
                f"`{dataset_id}`" for dataset_id in item["impacted_dataset_ids"]
            ) or empty_dataset_impact
            impact = ", ".join(f"`{model_id}`" for model_id in item["impacted_model_ids"]) or "no catalog-linked model"
            dataset_label = "linked datasets" if item["entity_type"] == "model" else "downstream datasets"
            lines.append(
                f"- [ ] [`{item['entity_id']}`]({item['url']}) — **{item['priority']}** "
                f"{item['entity_type']} priority; `{item['previous_revision']}` → `{item['revision']}`; "
                f"{dataset_label}: {dataset_impact}; impacted models: {impact}"
            )
        lines.append("")
    if report["failures"]:
        lines.extend(["## Source failures", ""])
        for item in report["failures"]:
            entity = f" `{item['entity_id']}` ({item['priority']}) —" if item.get("entity_id") else ""
            lines.append(f"-{entity} `{item['error']}` — [{item['source_url']}]({item['source_url']})")
        lines.append("")
    if report["recoveries"]:
        lines.extend(["## Recovered sources", ""])
        for item in report["recoveries"]:
            lines.append(
                f"- [{item['source_url']}]({item['source_url']}) — previously `{item['previous_error']}`"
            )
        lines.append("")
    if not report["has_updates"]:
        lines.extend(["## Result", "", "No unresolved source changes were found relative to the reviewed baseline.", ""])
    lines.extend(
        [
            "## Review contract",
            "",
            "1. Open the primary source and confirm the exact release date and media-generation scope.",
            "2. Record only explicitly disclosed datasets, processing operations, access, and licensing.",
            "3. Add unknowns instead of inferring data from model capabilities.",
            "4. After accepting or rejecting every candidate, refresh the reviewed discovery baseline in the same PR.",
            "",
            "<!-- aigcdatahub-daily-discovery -->",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watchlist", type=Path, default=Path("sources/watchlist.yaml"))
    parser.add_argument("--state", type=Path, default=Path("sources/discovery-state.json"))
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--accept-current", action="store_true")
    parser.add_argument(
        "--allow-failures",
        action="store_true",
        help="Allow --accept-current to store source failures in the reviewed baseline.",
    )
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=4_000_000)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def ensure_acceptable_baseline(
    snapshots: tuple[SourceSnapshot, ...], allow_failures: bool = False
) -> None:
    """Fail closed so a transient outage cannot become an invisible baseline."""
    failures = [snapshot for snapshot in snapshots if snapshot.error]
    if failures and not allow_failures:
        examples = ", ".join(snapshot.source_url for snapshot in failures[:3])
        raise SystemExit(
            f"refusing to accept baseline with {len(failures)} source failure(s): {examples}; "
            "rerun after recovery or pass --allow-failures explicitly"
        )


def main() -> int:
    args = parse_args()
    if args.workers < 1 or args.timeout <= 0 or args.max_bytes < 1024:
        raise SystemExit("workers and timeout must be positive; max-bytes must be at least 1024")
    watchlist, sources = load_watchlist(args.watchlist)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    snapshots = scan_sources(sources, args.timeout, args.max_bytes, args.workers)
    current_state = snapshot_payload(snapshots, generated_at)

    if args.accept_current:
        ensure_acceptable_baseline(snapshots, args.allow_failures)
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(json.dumps(current_state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        baseline = current_state
    elif args.state.exists():
        baseline = json.loads(args.state.read_text(encoding="utf-8"))
    else:
        raise SystemExit(f"reviewed discovery baseline is missing: {args.state}")

    diff = compare_snapshots(
        baseline,
        snapshots,
        declared_urls(watchlist),
        dataset_impact_index(),
        model_impact_index(),
        model_ranking_aliases(),
    )
    discovery = watchlist.get("discovery", {})
    report = report_payload(
        diff=diff,
        generated_at=generated_at,
        issue_title=discovery.get("issue_title", "[Auto] Daily generative-media discovery"),
        source_count=len(sources),
        focus=discovery.get("focus_modalities", ["image", "video"]),
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_out.write_text(render_report(report), encoding="utf-8")
    print(
        f"Checked {len(sources)} watched source(s): {len(diff.new_candidates)} new candidate(s), "
        f"{len(diff.source_updates)} important catalog revision(s), {len(diff.failures)} new failure(s), "
        f"{len(diff.recoveries)} recovery/recoveries, {len(diff.ranking_updates)} ranking board change(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
