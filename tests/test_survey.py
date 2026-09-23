"""Tests concern reported aggregate arithmetic, not unverifiable study conduct."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from blueshield import survey as s


class SurveyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = s.audit_survey(ROOT / "data")

    def test_all_demographic_totals_equal_125(self):
        for group in self.audit["demographics"]["groups"].values():
            self.assertEqual(group["count_total"], 125)
            self.assertTrue(group["reconciles"])

    def test_discipline_median_is_12_not_28(self):
        self.assertEqual(self.audit["demographics"]["discipline_count_median"], 12)

    def test_reported_favorable_totals_and_conditional_counts(self):
        rows = self.audit["perceptions"]
        self.assertEqual([r["favorable_pct"] for r in rows], [84, 86.4, 92])
        self.assertEqual([r["conditional_count_equivalent"] for r in rows], [105, 108, 115])
        self.assertTrue(all(r["count_status"] == "conditional_arithmetic_not_verified_observed_count" for r in rows))

    def test_noninteger_equivalent_is_not_silently_rounded(self):
        row = {"item": "test_fixture", "very_pct": "36.6", "somewhat_pct": "0", "assumed_denominator": "125"}
        result = s.audit_perceptions([row])[0]
        self.assertEqual(result["conditional_count_equivalent"], 45.75)
        self.assertFalse(result["compatible_with_integer_count"])

    def test_invalid_percentages_and_components(self):
        for very, somewhat in [("NaN", "0"), ("-1", "30"), ("80", "30")]:
            with self.subTest(very=very, somewhat=somewhat), self.assertRaises(ValueError):
                s.audit_perceptions([{"item": "fixture", "very_pct": very, "somewhat_pct": somewhat, "assumed_denominator": "125"}])

    def test_duplicate_and_inconsistent_demographics_rejected(self):
        row = {"group": "fixture", "category": "A", "count": "2", "denominator": "4"}
        with self.assertRaises(ValueError):
            s.audit_demographics([row, row])
        with self.assertRaises(ValueError):
            s.audit_demographics([row, {**row, "category": "B", "denominator": "5"}])

    def test_nonreconciling_total_reported_honestly(self):
        result = s.audit_demographics([{"group": "fixture", "category": "A", "count": "2", "denominator": "4"}])
        self.assertFalse(result["groups"]["fixture"]["reconciles"])

    def test_interviews_keep_six_distinct_overlapping_prompts(self):
        rows = self.audit["interviews"]["rows"]
        self.assertEqual([r["count"] for r in rows], [20, 15, 18, 22, 23, 22])
        self.assertTrue(all(r["denominator"] == 25 for r in rows))
        self.assertEqual(sum(r["count"] for r in rows), 120)
        self.assertIn("may overlap", self.audit["interviews"]["interpretation"])

    def test_impact_is_excluded_without_selection_or_chart_invention(self):
        self.assertEqual(self.audit["excluded_items"], ["anticipated_impact"])
        self.assertTrue(self.audit["impact_discrepancy"]["exclude_from_analysis"])
        self.assertIsNone(self.audit["impact_discrepancy"]["selected_distribution"])
        self.assertIsNone(self.audit["impact_discrepancy"]["original_pie_percentages"])
        self.assertNotIn("anticipated_impact", [r["item"] for r in self.audit["perceptions"]])

    def test_no_inference_or_synthetic_respondent_records(self):
        self.assertFalse(self.audit["inference_performed"])
        self.assertFalse(self.audit["respondent_records_generated"])
        self.assertEqual(self.audit["metadata"]["reported_sample_size"], 125)
        self.assertIn("respondent-level data", self.audit["metadata"]["unavailable"])

    def test_invalid_count_and_denominator(self):
        for value in [-1, 26, 2.5, "NaN"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                s.count_value(value, 25)
        for value in [0, -1, 1.5, "NaN", True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                s.positive_integer(value, "n")


if __name__ == "__main__":
    unittest.main()
