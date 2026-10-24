import unittest

from eaqec.linalg import RowSpace, gram_matrix, nullspace, rank, rref


class LinearAlgebraTests(unittest.TestCase):
    def test_rref_rank_and_nullspace(self):
        matrix = [[1, 2, 3], [2, 4, 0]]
        reduced, pivots = rref(matrix, 5)
        self.assertEqual(pivots, [0, 2])
        self.assertEqual(rank(matrix, 5), 2)
        kernel = nullspace(matrix, 5)
        self.assertEqual(len(kernel), 1)
        for row in matrix:
            self.assertEqual(sum(x * y for x, y in zip(row, kernel[0])) % 5, 0)

    def test_row_space_membership_dual_and_intersection(self):
        a = RowSpace([[1, 0, 1], [0, 1, 1]], 3)
        b = RowSpace([[1, 1, 2], [0, 0, 1]], 3)
        self.assertEqual(a.dimension, 2)
        self.assertTrue(a.contains([1, 1, 2]))
        self.assertFalse(a.contains([1, 0, 0]))
        self.assertEqual(a.dual().dimension, 1)
        intersection = a.intersection(b)
        self.assertTrue(intersection.is_subspace_of(a))
        self.assertTrue(intersection.is_subspace_of(b))
        self.assertEqual(intersection.dimension, 1)

    def test_zero_and_full_spaces(self):
        zero = RowSpace.zero(4, 3)
        full = RowSpace.full(4, 3)
        self.assertEqual(zero.dimension, 0)
        self.assertEqual(zero.dual(), full)
        self.assertEqual(full.dual(), zero)
        self.assertEqual(zero.intersection(full), zero)
        self.assertEqual(zero.minimum_distance(), 0)

    def test_exhaustive_enumeration_is_unique(self):
        space = RowSpace([[1, 0, 1], [0, 1, 2]], 3)
        vectors = list(space.iter_vectors(max_codewords=9))
        self.assertEqual(len(vectors), 9)
        self.assertEqual(len(set(vectors)), 9)
        self.assertTrue(all(space.contains(vector) for vector in vectors))

    def test_gram_matrix(self):
        a = [[1, 2], [0, 1]]
        b = [[1, 0], [1, 1]]
        self.assertEqual(gram_matrix(a, b, 3), [[1, 0], [0, 1]])
        self.assertEqual(rank(gram_matrix(a, b, 3), 3), 2)


if __name__ == "__main__":
    unittest.main()
