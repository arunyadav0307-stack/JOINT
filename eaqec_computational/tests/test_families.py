import io
import unittest

from eaqec.families import (
    aeaqec_family,
    eaqec_family,
    paper_3_20_family,
    write_eaqec_csv,
)
from eaqec.paper_tables import compare_table_22, compare_table_34


class FamilyAndTableTests(unittest.TestCase):
    def test_eaqec_family_size_and_boundaries(self):
        rows = list(eaqec_family(7))
        self.assertEqual(len(rows), 15)
        self.assertEqual(rows[0][2].notation(), "[[7,1,6;5]]_7")
        self.assertEqual(rows[-1][2].notation(), "[[7,5,2;1]]_7")
        self.assertEqual(sum(1 for _ in eaqec_family(11)), 45)
        self.assertEqual(sum(1 for _ in eaqec_family(167)), 13695)
        self.assertTrue(all(row[2].satisfies_singleton_bound() for row in rows))

    def test_valid_aeaqec_both_orientations(self):
        rows = list(aeaqec_family(7, orientation="both"))
        self.assertEqual(len(rows), 30)
        self.assertTrue(all(row[3].is_mds() for row in rows))
        self.assertTrue(all(row[3].satisfies_singleton_bound() for row in rows))

    def test_paper_formula_family_is_separate(self):
        rows = list(paper_3_20_family(7))
        self.assertEqual(len(rows), 15)
        self.assertEqual(rows[0][2].notation(), "[[7,2,7/6;6]]_7")

    def test_csv_serialization(self):
        stream = io.StringIO()
        count = write_eaqec_csv(eaqec_family(3), stream)
        lines = stream.getvalue().strip().splitlines()
        self.assertEqual(count, 1)
        self.assertEqual(len(lines), 2)
        self.assertIn("[[3,1,2;1]]_3", lines[1])

    def test_reported_table_22_exact_match(self):
        comparison = compare_table_22()
        self.assertTrue(comparison["pass"])
        self.assertEqual(comparison["reported_rows"], 15)

    def test_reported_table_34_internal_issues(self):
        comparison = compare_table_34()
        self.assertFalse(comparison["pass"])
        self.assertEqual(comparison["reported_rows"], 17)
        self.assertEqual(comparison["literal_formula_rows"], 15)
        self.assertEqual(len(comparison["duplicates"]), 2)
        self.assertEqual(len(comparison["row_mismatches"]), 3)
        self.assertEqual(len(comparison["missing_literal_formula_rows"]), 3)


if __name__ == "__main__":
    unittest.main()
