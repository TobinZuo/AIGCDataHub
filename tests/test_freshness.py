from __future__ import annotations

import sys
import unittest
from datetime import date, datetime, timezone

sys.path.insert(0, "scripts")

from check_freshness import catalog_today, freshness_issues


class FreshnessTests(unittest.TestCase):
    def test_catalog_date_uses_shanghai_timezone_on_utc_runner(self) -> None:
        utc_runner_time = datetime(2026, 7, 26, 16, 36, tzinfo=timezone.utc)
        self.assertEqual(catalog_today(utc_runner_time), date(2026, 7, 27))

    def test_catalog_date_rejects_naive_datetimes(self) -> None:
        with self.assertRaises(ValueError):
            catalog_today(datetime(2026, 7, 27, 0, 36))

    def test_current_catalog_is_fresh_on_reference_date(self) -> None:
        self.assertEqual(freshness_issues(date(2026, 8, 18)), [])

    def test_watch_cards_expire_quickly(self) -> None:
        issues = freshness_issues(date(2026, 8, 31))
        stale_ids = {issue.item_id for issue in issues}
        self.assertIn("flux-3", stale_ids)
        self.assertIn("seedance-2-0", stale_ids)


if __name__ == "__main__":
    unittest.main()
