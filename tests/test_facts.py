"""Unit tests for the Python-computed Level 2 facts (synthetic data, no network, no API key)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from competition.facts import all_facts, history_facts  # noqa: E402

HIST = [("2025-10", 100), ("2025-11", 80), ("2025-12", 60), ("2026-01", 50), ("2026-02", 55), ("2026-03", 90),
        ("2026-04", 120), ("2026-05", 200), ("2026-06", 300), ("2026-07", 350), ("2026-08", 330), ("2026-09", 250)]
CLEAN = {"bill_month": "2026-09", "units_consumed": 250,
         "usage_history": [{"month": m, "units": u, "bill_amount": u * 10.0} for m, u in HIST]}
L1 = {"bill_month": "2026-09", "units_consumed": 250, "current_bill": 2500, "payable_within_due_date": 2500,
      "payable_after_due_date": 2625, "total_taxes": 400, "charges": [{"type": "fpa", "amount": 12.5}]}


class Facts(unittest.TestCase):
    def test_core(self):
        t = all_facts(CLEAN, L1)
        self.assertIn("Jul 2026 with 350", t)                      # highest month
        self.assertIn("Average units over the 12 history months: 165.42", t)
        self.assertIn("(summer - winter): +271.67", t)               # 980/3 - 165/3
    def test_yoy_missing(self):
        self.assertIn("NOT in the printed history", "\n".join(history_facts(CLEAN)))
    def test_surcharge(self):
        self.assertIn("= 125", all_facts(CLEAN, L1))
    def test_no_history_is_not_guessed(self):
        t = history_facts({"bill_month": "2026-09", "units_consumed": 10, "usage_history": []})[0]
        self.assertIn("NOT available", t)
    def test_trend_down(self):
        c = dict(CLEAN, usage_history=[{"month": m, "units": u, "bill_amount": None} for m, u in [("2026-07", 350), ("2026-08", 330), ("2026-09", 250)]])
        self.assertIn("-> down", "\n".join(history_facts(c)))


if __name__ == "__main__":
    unittest.main()
