from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "scripts")

from check_links import is_hard_failure


class LinkCheckTests(unittest.TestCase):
    def test_only_confirmed_missing_responses_are_hard_failures(self) -> None:
        self.assertTrue(is_hard_failure("HTTP 404"))
        self.assertTrue(is_hard_failure("HTTP 410"))
        self.assertFalse(is_hard_failure("HTTP 403"))
        self.assertFalse(is_hard_failure("HTTP 429"))
        self.assertFalse(is_hard_failure("<urlopen error connection reset>"))


if __name__ == "__main__":
    unittest.main()
