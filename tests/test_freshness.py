from __future__ import annotations

import sys
import unittest
from datetime import date

sys.path.insert(0, "scripts")

from check_freshness import freshness_issues


class FreshnessTests(unittest.TestCase):
    def test_current_catalog_is_fresh_on_reference_date(self) -> None:
        self.assertEqual(freshness_issues(date(2026, 7, 26)), [])

    def test_watch_cards_expire_quickly(self) -> None:
        issues = freshness_issues(date(2026, 8, 11))
        stale_ids = {issue.item_id for issue in issues}
        self.assertIn("flux-3", stale_ids)
        self.assertIn("seedance-2-0", stale_ids)


if __name__ == "__main__":
    unittest.main()

