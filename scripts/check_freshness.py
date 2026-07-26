#!/usr/bin/env python3
"""Enforce verification-age policies for living dataset and model cards."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from catalog import load_cards
from models import load_models


CATALOG_TIMEZONE = ZoneInfo("Asia/Shanghai")


def catalog_today(now: datetime | None = None) -> date:
    """Return the catalog's editorial date independent of the host timezone."""
    instant = now or datetime.now(tz=CATALOG_TIMEZONE)
    if instant.tzinfo is None:
        raise ValueError("catalog_today requires a timezone-aware datetime")
    return instant.astimezone(CATALOG_TIMEZONE).date()


@dataclass(frozen=True)
class FreshnessIssue:
    kind: str
    item_id: str
    last_verified: date
    age_days: int
    limit_days: int
    reason: str


def freshness_issues(
    today: date,
    dataset_days: int = 90,
    model_days: int = 45,
    watch_days: int = 14,
) -> list[FreshnessIssue]:
    issues: list[FreshnessIssue] = []
    for _, card in load_cards():
        verified = date.fromisoformat(card["last_verified"])
        age = (today - verified).days
        if age < 0:
            issues.append(
                FreshnessIssue("dataset", card["id"], verified, age, dataset_days, "verification date is in the future")
            )
        elif age > dataset_days:
            issues.append(FreshnessIssue("dataset", card["id"], verified, age, dataset_days, "stale"))

    for _, card in load_models():
        verified = date.fromisoformat(card["last_verified"])
        limit = watch_days if card["status"] == "watch" else model_days
        age = (today - verified).days
        if age < 0:
            issues.append(
                FreshnessIssue("model", card["id"], verified, age, limit, "verification date is in the future")
            )
        elif age > limit:
            issues.append(FreshnessIssue("model", card["id"], verified, age, limit, "stale"))
    return sorted(issues, key=lambda issue: (issue.kind, issue.item_id))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--today", type=date.fromisoformat, default=catalog_today())
    parser.add_argument("--dataset-days", type=int, default=90)
    parser.add_argument("--model-days", type=int, default=45)
    parser.add_argument("--watch-days", type=int, default=14)
    args = parser.parse_args()
    for name in ("dataset_days", "model_days", "watch_days"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be at least 1")
    return args


def main() -> int:
    args = parse_args()
    issues = freshness_issues(args.today, args.dataset_days, args.model_days, args.watch_days)
    if issues:
        print(f"Freshness check failed with {len(issues)} issue(s):", file=sys.stderr)
        for issue in issues:
            print(
                f"- {issue.kind} {issue.item_id}: {issue.reason}; "
                f"last verified {issue.last_verified.isoformat()}, age {issue.age_days}d, limit {issue.limit_days}d",
                file=sys.stderr,
            )
        return 1
    print(
        f"Freshness check passed for {len(load_cards())} dataset card(s) "
        f"and {len(load_models())} model card(s) as of {args.today.isoformat()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
