import unittest

from eaqec.constacyclic import (
    RepeatedRootConstacyclicCode,
    binomial_power,
    hamming_distance_2_3,
)


class ConstacyclicTests(unittest.TestCase):
    def test_binomial_generator_polynomial(self):
        self.assertEqual(binomial_power(3, 2, 7), [2, 1, 1])

    def test_generator_matrix_and_dimension(self):
        code = RepeatedRootConstacyclicCode(7, 1, 3, 2)
        matrix = code.generator_matrix()
        self.assertEqual(code.n, 7)
        self.assertEqual(code.dimension, 5)
        self.assertEqual(len(matrix), 5)
        self.assertEqual(matrix[0][:3], [2, 1, 1])
        self.assertEqual(matrix[1][1:4], [2, 1, 1])
        self.assertEqual(code.row_space().dimension, 5)

    def test_dual_root_description(self):
        for j in range(8):
            code = RepeatedRootConstacyclicCode(7, 1, 3, j)
            self.assertEqual(code.row_space().dual(), code.dual_root_description().row_space())

    def test_distance_formula_length_three(self):
        expected = [1, 2, 3, 0]
        self.assertEqual([hamming_distance_2_3(3, 1, j) for j in range(4)], expected)

    def test_distance_formula_repeated_root_length_nine(self):
        expected = [1, 2, 2, 2, 3, 3, 3, 6, 9, 0]
        self.assertEqual([hamming_distance_2_3(3, 2, j) for j in range(10)], expected)

    def test_invalid_root_and_prime(self):
        with self.assertRaises(ValueError):
            RepeatedRootConstacyclicCode(7, 1, 0, 1)
        with self.assertRaises(ValueError):
            RepeatedRootConstacyclicCode(9, 1, 1, 1)


if __name__ == "__main__":
    unittest.main()
