import unittest

from eaqec.verify import run_verification


class VerificationIntegrationTest(unittest.TestCase):
    def test_quick_verification_suite(self):
        result = run_verification(deep=False)
        self.assertTrue(result["pass"])
        self.assertTrue(result["distance_formula"]["pass"])
        self.assertTrue(result["swapped_orientation"]["pass"])
        self.assertEqual(result["scope"]["s1_pair_cases"], 12)
        for finding in result["discrepancies"].values():
            self.assertTrue(finding["pass"])


if __name__ == "__main__":
    unittest.main()
