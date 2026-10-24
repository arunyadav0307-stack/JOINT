import unittest

from eaqec.quantum import (
    aeaqec_mds_s1,
    direct_constacyclic_pair,
    eaqec_s1,
    paper_3_4_reported,
    paper_3_20_reported,
)


class QuantumConstructionTests(unittest.TestCase):
    def test_s1_closed_parameters(self):
        code = eaqec_s1(7, 1, 1, 2)
        self.assertEqual(code.notation(), "[[7,1,6;5]]_7")
        self.assertTrue(code.satisfies_singleton_bound())
        asymmetric = aeaqec_mds_s1(7, 1, 1, 2)
        self.assertEqual(asymmetric.notation(), "[[7,1,7/6;5]]_7")
        self.assertTrue(asymmetric.is_mds())
        self.assertTrue(asymmetric.satisfies_singleton_bound())

    def test_direct_s1_pair(self):
        result = direct_constacyclic_pair(7, 1, 1, 2, root1=3, root2=2)
        self.assertEqual(result.symmetric, eaqec_s1(7, 1, 1, 2))
        self.assertEqual(result.asymmetric, aeaqec_mds_s1(7, 1, 1, 2))
        self.assertEqual(result.rank_gram, 5)
        self.assertEqual(result.c_from_intersection, 5)
        self.assertTrue(result.pure)
        self.assertTrue(result.asymmetric.is_mds())

    def test_direct_repeated_root_counterexample(self):
        result = direct_constacyclic_pair(3, 2, 1, 2, root1=1, root2=2)
        printed = paper_3_4_reported(3, 1, 2, 1, 2)
        self.assertEqual(printed.notation(), "[[9,2,1;1]]_3")
        self.assertEqual(result.symmetric.notation(), "[[9,1,6;7]]_3")
        self.assertEqual(result.asymmetric.notation(), "[[9,1,9/6;7]]_3")
        self.assertEqual(result.rank_gram, 7)
        self.assertNotEqual(result.symmetric, printed)

    def test_table_34_first_row_counterexample(self):
        reported = paper_3_20_reported(7, 1, 2, 1)
        direct = direct_constacyclic_pair(7, 1, 2, 1, root1=3, root2=2)
        self.assertEqual(reported.notation(), "[[7,2,7/6;6]]_7")
        self.assertEqual(direct.asymmetric.notation(), "[[7,1,6/7;5]]_7")
        self.assertEqual(direct.rank_gram, 5)

    def test_swapped_constituents(self):
        direct = direct_constacyclic_pair(7, 1, 4, 2, root1=2, root2=3)
        expected = aeaqec_mds_s1(7, 1, 2, 4, swap_constituents=True)
        self.assertEqual(direct.asymmetric, expected)
        self.assertEqual(expected.notation(), "[[7,2,4/6;3]]_7")

    def test_invalid_pair_order(self):
        with self.assertRaises(ValueError):
            eaqec_s1(7, 1, 2, 1)
        with self.assertRaises(ValueError):
            direct_constacyclic_pair(7, 1, 1, 2, root1=1, root2=1)


if __name__ == "__main__":
    unittest.main()
