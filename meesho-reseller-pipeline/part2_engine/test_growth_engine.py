"""Part 2 tests - four Given-When-Then cases. Run: python -m unittest -v  (or pytest)."""
import os
import unittest

from growth_engine import is_flagged, mom_growth, validate_feed

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class TestGrowthEngine(unittest.TestCase):
    def test_1_ethnic_wear_april_to_may_is_flagged(self):
        # GIVEN April and May Ethnic Wear revenue
        previous, current = 104520.77, 185107.61
        # WHEN we compute MoM growth and flag it
        pct = mom_growth(previous, current)
        # THEN growth is 77.1% and the category is flagged
        self.assertEqual(pct, 77.1)
        self.assertEqual(is_flagged(pct), "flagged")

    def test_2_beauty_may_to_june_is_not_flagged(self):
        previous, current = 35542.11, 37559.07
        pct = mom_growth(previous, current)
        self.assertEqual(pct, 5.67)
        self.assertEqual(is_flagged(pct), "not_flagged")

    def test_3_exact_boundary_escalates(self):
        previous, current = 100000, 108000
        pct = mom_growth(previous, current)
        self.assertEqual(pct, 8.0)
        self.assertEqual(is_flagged(pct), "escalate_exact_boundary")

    def test_4_corrupted_feed_gives_exactly_three_errors_in_order(self):
        ok, errors = validate_feed(os.path.join(FIXTURES, "corrupted_feed.csv"))
        self.assertFalse(ok)
        self.assertEqual(
            errors,
            [
                "line 3: negative revenue (-4200.0) for category=Western Wear",
                "line 4: missing category (month=July)",
                "line 6: missing revenue (category=Home & Kitchen)",
            ],
        )

    # --- extra sanity checks (not required by the brief) ---
    def test_clean_feed_passes(self):
        ok, errors = validate_feed(os.path.join(FIXTURES, "monthly_category_revenue.csv"))
        self.assertEqual((ok, errors), (True, []))

    def test_is_flagged_never_returns_bool(self):
        for pct in (-23.6, 0.0, 8.0, 77.1):
            self.assertIsInstance(is_flagged(pct), str)


if __name__ == "__main__":
    unittest.main()
