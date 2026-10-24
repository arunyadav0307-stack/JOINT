"""Exact finite-prime-field linear algebra used by the verification suite.

Elements of ``F_p`` are represented by integers modulo ``p``.  No floating
point arithmetic or third-party dependency is used.  A ``RowSpace`` is stored
in reduced row-echelon form, which makes membership and equality canonical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, Sequence


Vector = list[int]
Matrix = list[list[int]]


class ComputationLimit(RuntimeError):
    """Raised before an exhaustive enumeration exceeds its declared budget."""


def validate_prime(p: int, *, allow_two: bool = False) -> None:
    if not isinstance(p, int) or p < 2:
        raise ValueError("p must be an integer prime")
    if p == 2 and not allow_two:
        raise ValueError("the paper assumes an odd prime p")
    if any(p % d == 0 for d in range(2, int(p**0.5) + 1)):
        raise ValueError(f"p={p} is not prime")


def _matrix_shape(matrix: Sequence[Sequence[int]], n: Optional[int] = None) -> tuple[int, int]:
    rows = len(matrix)
    if rows == 0:
        if n is None:
            raise ValueError("the number of columns is required for an empty matrix")
        return 0, n
    columns = len(matrix[0])
    if n is not None and columns != n:
        raise ValueError(f"expected {n} columns, received {columns}")
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix rows must all have the same length")
    return rows, columns


def rref(matrix: Sequence[Sequence[int]], p: int, n: Optional[int] = None) -> tuple[Matrix, list[int]]:
    """Return reduced row-echelon form and pivot columns over ``F_p``."""
    validate_prime(p, allow_two=True)
    _, columns = _matrix_shape(matrix, n)
    a: Matrix = [
        [int(x) % p for x in row]
        for row in matrix
        if any(int(x) % p for x in row)
    ]
    if not a:
        return [], []
    pivot_columns: list[int] = []
    pivot_row = 0
    for col in range(columns):
        selected = next((r for r in range(pivot_row, len(a)) if a[r][col] != 0), None)
        if selected is None:
            continue
        a[pivot_row], a[selected] = a[selected], a[pivot_row]
        inverse = pow(a[pivot_row][col], -1, p)
        a[pivot_row] = [(inverse * x) % p for x in a[pivot_row]]
        for r in range(len(a)):
            if r == pivot_row or a[r][col] == 0:
                continue
            factor = a[r][col]
            a[r] = [(x - factor * y) % p for x, y in zip(a[r], a[pivot_row])]
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == len(a):
            break
    return a[:pivot_row], pivot_columns


def rank(matrix: Sequence[Sequence[int]], p: int, n: Optional[int] = None) -> int:
    return len(rref(matrix, p, n)[1])


def nullspace(matrix: Sequence[Sequence[int]], p: int, n: Optional[int] = None) -> Matrix:
    """Return a row basis for ``{x : matrix * x = 0}`` over ``F_p``."""
    _, columns = _matrix_shape(matrix, n)
    reduced, pivots = rref(matrix, p, n)
    free_columns = [c for c in range(columns) if c not in pivots]
    basis: Matrix = []
    for free in free_columns:
        vector = [0] * columns
        vector[free] = 1
        for row, pivot in zip(reduced, pivots):
            vector[pivot] = (-row[free]) % p
        basis.append(vector)
    return basis


def identity(n: int, p: int) -> Matrix:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def gram_matrix(a: Sequence[Sequence[int]], b: Sequence[Sequence[int]], p: int) -> Matrix:
    """Compute ``a * b.T`` for two matrices with the same row length."""
    if not a or not b:
        return []
    if len(a[0]) != len(b[0]):
        raise ValueError("generator matrices must have the same row length")
    return [
        [sum(x * y for x, y in zip(row_a, row_b)) % p for row_b in b]
        for row_a in a
    ]


@dataclass(frozen=True)
class RowSpace:
    """A linear row space over a prime field, canonically stored in RREF."""

    p: int
    n: int
    rows: tuple[tuple[int, ...], ...]

    def __init__(self, matrix: Sequence[Sequence[int]], p: int, n: Optional[int] = None):
        validate_prime(p, allow_two=True)
        _, columns = _matrix_shape(matrix, n)
        reduced, _ = rref(matrix, p, columns)
        object.__setattr__(self, "p", p)
        object.__setattr__(self, "n", columns)
        object.__setattr__(self, "rows", tuple(tuple(row) for row in reduced))

    @classmethod
    def zero(cls, n: int, p: int) -> "RowSpace":
        return cls([], p, n)

    @classmethod
    def full(cls, n: int, p: int) -> "RowSpace":
        return cls(identity(n, p), p, n)

    @property
    def dimension(self) -> int:
        return len(self.rows)

    @property
    def size(self) -> int:
        return self.p**self.dimension

    def matrix(self) -> Matrix:
        return [list(row) for row in self.rows]

    def dual(self) -> "RowSpace":
        return RowSpace(nullspace(self.matrix(), self.p, self.n), self.p, self.n)

    def contains(self, vector: Sequence[int]) -> bool:
        if len(vector) != self.n:
            raise ValueError(f"expected a vector of length {self.n}")
        work = [int(x) % self.p for x in vector]
        # RREF rows are ordered by increasing pivot column.  Eliminating in
        # that order never reintroduces a previously cleared pivot.
        for row in self.rows:
            pivot = next(i for i, value in enumerate(row) if value != 0)
            factor = work[pivot]
            if factor:
                work = [(x - factor * y) % self.p for x, y in zip(work, row)]
        return not any(work)

    def intersection(self, other: "RowSpace") -> "RowSpace":
        """Compute ``self ∩ other`` using a block-nullspace system.

        If (u,v) satisfies self.rows.T*u + other.rows.T*v = 0, then
        self.rows.T*u belongs to both row spaces.  The nullspace basis thus
        maps directly to a generating set for the intersection.
        """
        if self.p != other.p or self.n != other.n:
            raise ValueError("row spaces must have the same field and ambient length")
        if self.dimension == 0 or other.dimension == 0:
            return RowSpace.zero(self.n, self.p)
        a, b = self.matrix(), other.matrix()
        da, db = len(a), len(b)
        block = [
            [a[r][col] for r in range(da)] + [b[r][col] for r in range(db)]
            for col in range(self.n)
        ]
        relations = nullspace(block, self.p, da + db)
        generators: Matrix = []
        for relation in relations:
            vector = [
                sum(relation[r] * a[r][col] for r in range(da)) % self.p
                for col in range(self.n)
            ]
            generators.append(vector)
        return RowSpace(generators, self.p, self.n)

    def is_subspace_of(self, other: "RowSpace") -> bool:
        return all(other.contains(row) for row in self.rows)

    def iter_vectors(self, *, max_codewords: Optional[int] = None) -> Iterator[tuple[int, ...]]:
        """Enumerate every vector exactly once, using incremental recursion."""
        if max_codewords is not None and self.size > max_codewords:
            raise ComputationLimit(
                f"enumeration of q^k={self.p}^{self.dimension}={self.size:,} "
                f"exceeds the limit {max_codewords:,}"
            )
        vector = [0] * self.n
        rows = self.rows
        p = self.p

        def visit(depth: int) -> Iterator[tuple[int, ...]]:
            if depth == len(rows):
                yield tuple(vector)
                return
            row = rows[depth]
            for coefficient in range(p):
                if coefficient:
                    # Increase this row's coefficient by one.  After the last
                    # branch, one further addition restores the parent vector.
                    for col, value in enumerate(row):
                        if value:
                            vector[col] = (vector[col] + value) % p
                yield from visit(depth + 1)
            for col, value in enumerate(row):
                if value:
                    vector[col] = (vector[col] + value) % p

        yield from visit(0)

    def minimum_distance(self, *, max_codewords: Optional[int] = 2_000_000) -> int:
        """Exhaustive Hamming minimum distance; the zero code has distance 0."""
        if self.dimension == 0:
            return 0
        best = self.n + 1
        for vector in self.iter_vectors(max_codewords=max_codewords):
            weight = sum(value != 0 for value in vector)
            if weight and weight < best:
                best = weight
                if best == 1:
                    break
        return best

    def minimum_weight_outside(
        self,
        excluded: "RowSpace",
        *,
        max_codewords: Optional[int] = 2_000_000,
    ) -> Optional[int]:
        """Return ``wt(self \\ excluded)`` by exhaustive enumeration.

        ``None`` means that the set difference contains no nonzero vector.
        The zero vector is irrelevant because it belongs to every subspace.
        """
        if self.p != excluded.p or self.n != excluded.n:
            raise ValueError("row spaces must have the same field and ambient length")
        best: Optional[int] = None
        for vector in self.iter_vectors(max_codewords=max_codewords):
            if not any(vector) or excluded.contains(vector):
                continue
            weight = sum(value != 0 for value in vector)
            if best is None or weight < best:
                best = weight
                if best == 1:
                    break
        return best
