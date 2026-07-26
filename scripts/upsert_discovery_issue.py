#!/usr/bin/env python3
"""Create, update, reopen, or close the weekly discovery issue."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


MARKER = "<!-- aigcdatahub-weekly-discovery -->"


class GitHubClient:
    def __init__(self, repository: str, token: str, api_url: str = "https://api.github.com") -> None:
        self.repository = repository
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.api_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "AIGCDataHub-discovery/0.1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {path} failed with HTTP {exc.code}: {detail}") from exc

    def find_issue(self, title: str) -> dict[str, Any] | None:
        query = urllib.parse.urlencode({"state": "all", "per_page": 100, "sort": "updated", "direction": "desc"})
        issues = self.request("GET", f"/repos/{self.repository}/issues?{query}")
        for issue in issues:
            if "pull_request" not in issue and issue.get("title") == title and MARKER in issue.get("body", ""):
                return issue
        return None

    def create_issue(self, title: str, body: str) -> dict[str, Any]:
        return self.request("POST", f"/repos/{self.repository}/issues", {"title": title, "body": body})

    def update_issue(self, number: int, body: str, state: str) -> dict[str, Any]:
        return self.request(
            "PATCH", f"/repos/{self.repository}/issues/{number}", {"body": body, "state": state}
        )


def issue_body(markdown: str, repository: str, run_id: str | None, server_url: str) -> str:
    body = markdown.rstrip() + "\n"
    if run_id:
        body += f"\nRun: {server_url}/{repository}/actions/runs/{run_id}\n"
    return body


def issue_action(has_updates: bool, existing: dict[str, Any] | None) -> str:
    """Choose the idempotent issue mutation for the current report."""
    if has_updates:
        return "update" if existing else "create"
    if existing and existing.get("state") == "open":
        return "close"
    return "none"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    markdown = args.markdown.read_text(encoding="utf-8")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    body = issue_body(
        markdown,
        repository,
        os.environ.get("GITHUB_RUN_ID"),
        os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
    )
    if args.dry_run:
        print(json.dumps({"title": report["issue_title"], "has_updates": report["has_updates"], "body": body}))
        return 0
    if not repository or not token:
        raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN are required")

    client = GitHubClient(repository, token, os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    existing = client.find_issue(report["issue_title"])
    action = issue_action(report["has_updates"], existing)
    if action == "update":
        issue = client.update_issue(existing["number"], body, "open")
        print(f"Updated discovery issue #{issue['number']}: {issue['html_url']}")
    elif action == "create":
        issue = client.create_issue(report["issue_title"], body)
        print(f"Created discovery issue #{issue['number']}: {issue['html_url']}")
    elif action == "close":
        issue = client.update_issue(existing["number"], body, "closed")
        print(f"Closed discovery issue #{issue['number']}: no unresolved source changes")
    else:
        print("No unresolved source changes and no open discovery issue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
