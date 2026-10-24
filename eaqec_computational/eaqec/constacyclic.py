"""Repeated-root constacyclic codes used in Sections 2 and 3 of the paper.

Over a prime field ``F_p``, every nonzero ``alpha0`` satisfies
``alpha0^(p^s) = alpha0``.  Consequently

    x^(p^s) - alpha = (x - alpha0)^(p^s),   alpha = alpha0,

so the ideals ``C_j = <(x-alpha0)^j>`` have explicit generator matrices.
The implementation builds those matrices directly in coefficient coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass

from .linalg import Matrix, RowSpace, validate_prime


def trim_polynomial(coefficients: list[int], p: int) -> list[int]:
    result = [int(x) % p for x in coefficients]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def multiply_polynomials(a: list[int], b: list[int], p: int) -> list[int]:
    product = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            product[i + j] = (product[i + j] + x * y) % p
    return trim_polynomial(product, p)


def binomial_power(root: int, exponent: int, p: int) -> list[int]:
    """Return coefficients of ``(x-root)^exponent``, low degree first."""
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    result = [1]
    base = [(-root) % p, 1]
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = multiply_polynomials(result, base, p)
        base = multiply_polynomials(base, base, p)
        remaining >>= 1
    return result


def hamming_distance_2_3(p: int, s: int, j: int) -> int:
    """Evaluate the piecewise Hamming-distance formula in Theorem 2.3."""
    validate_prime(p)
    if s < 1:
        raise ValueError("s must be positive")
    n = p**s
    if not 0 <= j <= n:
        raise ValueError(f"j must satisfy 0 <= j <= {n}")
    if j == 0:
        return 1
    if j == n:
        return 0

    for beta in range(p - 1):
        lower = beta * p ** (s - 1) + 1
        upper = (beta + 1) * p ** (s - 1)
        if lower <= j <= upper:
            return beta + 2

    for k in range(1, s):
        for t in range(1, p):
            lower = n - p ** (s - k) + (t - 1) * p ** (s - k - 1) + 1
            upper = n - p ** (s - k) + t * p ** (s - k - 1)
            if lower <= j <= upper:
                return (t + 1) * p**k

    raise ArithmeticError(f"Theorem 2.3 cases did not cover p={p}, s={s}, j={j}")


def is_mds_3_1(p: int, s: int, j: int) -> bool:
    """Classification of nontrivial MDS constacyclic codes in Theorem 3.1."""
    n = p**s
    if not 0 <= j <= n:
        raise ValueError(f"j must satisfy 0 <= j <= {n}")
    if j == 0:
        return True
    if s == 1:
        return j <= p - 1
    return j == 1 or j == n - 1


@dataclass(frozen=True)
class RepeatedRootConstacyclicCode:
    """The ideal ``<(x-root)^j>`` of length ``p^s`` over ``F_p``."""

    p: int
    s: int
    root: int
    j: int

    def __post_init__(self) -> None:
        validate_prime(self.p)
        if self.s < 1:
            raise ValueError("s must be positive")
        object.__setattr__(self, "root", self.root % self.p)
        if self.root == 0:
            raise ValueError("root must be nonzero in F_p")
        if not 0 <= self.j <= self.n:
            raise ValueError(f"j must satisfy 0 <= j <= {self.n}")

    @property
    def n(self) -> int:
        return self.p**self.s

    @property
    def twist(self) -> int:
        return pow(self.root, self.n, self.p)

    @property
    def dimension(self) -> int:
        return self.n - self.j

    def generator_polynomial(self) -> list[int]:
        return binomial_power(self.root, self.j, self.p)

    def generator_matrix(self) -> Matrix:
        """Rows are x^i*(x-root)^j for i=0,...,n-j-1.

        Every row has degree at most n-1, so no quotient-ring reduction is
        needed.  The zero code is represented by a zero-row generator matrix.
        """
        polynomial = self.generator_polynomial()
        rows: Matrix = []
        for shift in range(self.dimension):
            row = [0] * shift + polynomial
            row += [0] * (self.n - len(row))
            rows.append(row)
        return rows

    def row_space(self) -> RowSpace:
        return RowSpace(self.generator_matrix(), self.p, self.n)

    def theoretical_distance(self) -> int:
        return hamming_distance_2_3(self.p, self.s, self.j)

    def direct_distance(self, *, max_codewords: int = 2_000_000) -> int:
        return self.row_space().minimum_distance(max_codewords=max_codewords)

    def dual_root_description(self) -> "RepeatedRootConstacyclicCode":
        """Return the dual ideal stated in Theorem 2.2.

        C_j^perp = <(x-root^(-1))^(n-j)>.
        """
        inverse_root = pow(self.root, -1, self.p)
        return RepeatedRootConstacyclicCode(self.p, self.s, inverse_root, self.n - self.j)
