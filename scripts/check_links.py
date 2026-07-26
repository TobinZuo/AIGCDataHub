#!/usr/bin/env python3
"""Check primary-source URLs declared by dataset and model cards."""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

from catalog import load_cards
from models import load_models


@dataclass(frozen=True)
class Link:
    entity_id: str
    field: str
    url: str


def links() -> list[Link]:
    result: set[Link] = set()
    for _, card in load_cards():
        result.add(Link(card["id"], "release_date_source", card["release_date_source"]))
        result.add(Link(card["id"], "access.url", card["access"]["url"]))
        result.add(Link(card["id"], "evidence.homepage", card["evidence"]["homepage"]))
        if card["evidence"]["paper"]:
            result.add(Link(card["id"], "evidence.paper", card["evidence"]["paper"]))
    for _, card in load_models():
        for field_name in ("release_url", "weights_url", "api_url"):
            if card["access"][field_name]:
                result.add(Link(card["id"], f"access.{field_name}", card["access"][field_name]))
        for field_name in ("release", "technical_report", "repository"):
            if card["evidence"][field_name]:
                result.add(Link(card["id"], f"evidence.{field_name}", card["evidence"][field_name]))
    return sorted(result, key=lambda item: (item.url, item.entity_id, item.field))


def check(link: Link, timeout: float) -> tuple[Link, str | None]:
    headers = {"User-Agent": "AIGCDataHub-link-checker/0.1"}
    request = urllib.request.Request(link.url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status < 400:
                return link, None
    except urllib.error.HTTPError as exc:
        # An authentication challenge proves that a gated resource exists. We
        # are checking address validity here, not bypassing access controls.
        if exc.code == 401:
            return link, None
        if exc.code not in {403, 405, 429}:
            return link, f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return link, str(exc)

    # Some hosts reject HEAD requests. Retry with a one-byte GET.
    headers["Range"] = "bytes=0-0"
    request = urllib.request.Request(link.url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status < 400:
                return link, None
            return link, f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return link, None
        return link, f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return link, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    declared = links()
    failures: list[tuple[Link, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(check, link, args.timeout) for link in declared]
        for future in concurrent.futures.as_completed(futures):
            link, error = future.result()
            if error:
                failures.append((link, error))

    if failures:
        print(f"Link check failed for {len(failures)} declaration(s):", file=sys.stderr)
        for link, error in sorted(failures, key=lambda item: item[0].url):
            print(
                f"- {link.entity_id}.{link.field}: {link.url} ({error})",
                file=sys.stderr,
            )
        return 1

    print(f"Checked {len(declared)} link declaration(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
