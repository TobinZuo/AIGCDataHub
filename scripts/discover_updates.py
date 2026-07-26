#!/usr/bin/env python3
"""Discover new generative image/video links from the official-source watchlist."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

from catalog import load_cards
from models import load_models


SCHEMA_VERSION = 5
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


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str


@dataclass(frozen=True, order=True)
class WatchSource:
    track_id: str
    source_url: str
    catalog_id: str | None = None
    priority: str | None = None
    model_id: str | None = None


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

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidates"] = [asdict(candidate) for candidate in self.candidates]
        return payload


@dataclass(frozen=True)
class DiscoveryDiff:
    new_candidates: tuple[dict[str, Any], ...]
    source_updates: tuple[dict[str, Any], ...]
    failures: tuple[dict[str, Any], ...]
    recoveries: tuple[dict[str, Any], ...]

    @property
    def has_updates(self) -> bool:
        return bool(self.new_candidates or self.source_updates or self.failures or self.recoveries)


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


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


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
    path = urllib.parse.urlsplit(lowered_url).path
    if any(part in path for part in IGNORED_PATH_PARTS) or path.endswith(IGNORED_EXTENSIONS):
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

    return None, None


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


def _fetch_source(source: WatchSource, timeout: float, max_bytes: int) -> SourceSnapshot:
    track_id = source.track_id
    source_url = source.source_url
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json,application/json,text/html;q=0.9,*/*;q=0.5",
    }
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
                )
            charset = response.headers.get_content_charset() or "utf-8"
            html = payload.decode(charset, errors="replace")
            hostname = (urllib.parse.urlsplit(response.url).hostname or "").lower()
            revision, revision_url = extract_source_revision(html, response.url)
            return SourceSnapshot(
                track_id=track_id,
                source_url=source_url,
                resolved_url=normalize_url(response.url),
                status=response.status,
                candidates=extract_candidate_links(
                    html,
                    response.url,
                    contextual=track_id in CONTEXTUAL_TRACKS and hostname not in INDEX_HOSTS,
                ),
                error=None,
                revision=revision,
                revision_url=revision_url,
                catalog_id=source.catalog_id,
                priority=source.priority,
                model_id=source.model_id,
            )
    except urllib.error.HTTPError as exc:
        error = f"HTTP {exc.code}"
    except TimeoutError:
        error = "timeout"
    except urllib.error.URLError as exc:
        error = f"network-{type(exc.reason).__name__}"
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
    )


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
            if isinstance(source, dict):
                unexpected = set(source) - {"url", "catalog_id", "model_id", "priority"}
                if unexpected:
                    raise ValueError(f"watch source has unsupported keys: {sorted(unexpected)}")
                url = source.get("url")
                catalog_id = source.get("catalog_id")
                priority = source.get("priority")
                model_id = source.get("model_id")
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
            normalized = normalize_url(url) or url
            if normalized in seen_urls or normalized in excluded:
                continue
            seen_urls.add(normalized)
            sources.append(WatchSource(track_id, url, catalog_id, priority, model_id))
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


def declared_urls() -> set[str]:
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
    return {}


def compare_snapshots(
    baseline: dict[str, Any],
    current: tuple[SourceSnapshot, ...],
    known_urls: set[str],
    dataset_impacts: dict[str, dict[str, tuple[str, ...]]] | None = None,
    model_impacts: dict[str, dict[str, tuple[str, ...]]] | None = None,
) -> DiscoveryDiff:
    baseline_sources = {
        (item["track_id"], item["source_url"]): item for item in baseline.get("sources", [])
    }
    new_candidates: list[dict[str, Any]] = []
    source_updates: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    recoveries: list[dict[str, Any]] = []
    dataset_impacts = dataset_impacts or {}
    model_impacts = model_impacts or {}

    for source in current:
        key = (source.track_id, source.source_url)
        previous = baseline_sources.get(key, {})
        previous_urls = {item["url"] for item in previous.get("candidates", [])}
        for candidate in source.candidates:
            if candidate.url in previous_urls or candidate.url in known_urls:
                continue
            new_candidates.append(
                {
                    "track_id": source.track_id,
                    "source_url": source.source_url,
                    "title": candidate.title,
                    "url": candidate.url,
                }
            )
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

    return DiscoveryDiff(
        new_candidates=tuple(sorted(new_candidates, key=lambda item: (item["track_id"], item["url"]))),
        source_updates=tuple(
            sorted(source_updates, key=lambda item: (item["track_id"], item["source_url"]))
        ),
        failures=tuple(sorted(failures, key=lambda item: (item["track_id"], item["source_url"]))),
        recoveries=tuple(sorted(recoveries, key=lambda item: (item["track_id"], item["source_url"]))),
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
    }


def render_report(report: dict[str, Any], limit: int = 100) -> str:
    date = report["generated_at"][:10]
    lines = [
        f"# Weekly generative-media discovery — {date}",
        "",
        "Automated triage only: every candidate still requires primary-source verification before a card or `last_verified` value changes.",
        "",
        f"- Focus: {', '.join(report['focus'])}",
        f"- Watched sources checked: {report['source_count']}",
        f"- New candidate links: {len(report['new_candidates'])}",
        f"- Important catalog revisions: {len(report['source_updates'])}",
        f"- New source failures: {len(report['failures'])}",
        f"- Source recoveries: {len(report['recoveries'])}",
        "",
    ]
    if report["new_candidates"]:
        lines.extend(["## Candidate links", ""])
        for item in report["new_candidates"][:limit]:
            lines.append(
                f"- [ ] [{item['title']}]({item['url']}) — `{item['track_id']}` via [watch source]({item['source_url']})"
            )
        if len(report["new_candidates"]) > limit:
            lines.append(f"- … {len(report['new_candidates']) - limit} additional candidates are available in the JSON artifact.")
        lines.append("")
    if report["source_updates"]:
        lines.extend(["## Important catalog revisions", ""])
        for item in report["source_updates"]:
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
            "<!-- aigcdatahub-weekly-discovery -->",
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
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=4_000_000)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1 or args.timeout <= 0 or args.max_bytes < 1024:
        raise SystemExit("workers and timeout must be positive; max-bytes must be at least 1024")
    watchlist, sources = load_watchlist(args.watchlist)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    snapshots = scan_sources(sources, args.timeout, args.max_bytes, args.workers)
    current_state = snapshot_payload(snapshots, generated_at)

    if args.accept_current:
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
        declared_urls(),
        dataset_impact_index(),
        model_impact_index(),
    )
    discovery = watchlist.get("discovery", {})
    report = report_payload(
        diff=diff,
        generated_at=generated_at,
        issue_title=discovery.get("issue_title", "[Auto] Weekly generative-media discovery"),
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
        f"{len(diff.recoveries)} recovery/recoveries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
