"""EAQEC/AEAQEC parameters and independent matrix-level computation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .constacyclic import RepeatedRootConstacyclicCode
from .linalg import RowSpace, gram_matrix, rank, validate_prime


@dataclass(frozen=True)
class EAQECParameters:
    n: int
    k: int
    d: int
    c: int
    q: int

    def notation(self) -> str:
        return f"[[{self.n},{self.k},{self.d};{self.c}]]_{self.q}"

    @property
    def singleton_lhs(self) -> int:
        return 2 * self.d + self.k

    @property
    def singleton_rhs(self) -> int:
        return self.n + self.c + 2

    @property
    def singleton_defect(self) -> int:
        return self.singleton_rhs - self.singleton_lhs

    @property
    def bound_condition(self) -> bool:
        # Theorem 2.11 states this hypothesis for the EAQEC bound.
        return 2 * self.d <= self.n + 2

    def satisfies_singleton_bound(self) -> bool:
        return self.singleton_lhs <= self.singleton_rhs

    def is_mds(self) -> bool:
        return self.singleton_defect == 0


@dataclass(frozen=True)
class AEAQECParameters:
    n: int
    k: int
    dz: int
    dx: int
    c: int
    q: int

    @property
    def d(self) -> int:
        return min(self.dz, self.dx)

    def notation(self) -> str:
        return f"[[{self.n},{self.k},{self.dz}/{self.dx};{self.c}]]_{self.q}"

    @property
    def singleton_lhs(self) -> int:
        return self.dx + self.dz

    @property
    def singleton_rhs(self) -> int:
        return self.n - self.k + self.c + 2

    @property
    def singleton_defect(self) -> int:
        return self.singleton_rhs - self.singleton_lhs

    def satisfies_singleton_bound(self) -> bool:
        """Check the AEAQEC bound proved in Theorem 3.21."""
        return self.singleton_lhs <= self.singleton_rhs

    def is_mds(self) -> bool:
        return self.singleton_defect == 0

    def to_eaqec(self) -> EAQECParameters:
        return EAQECParameters(self.n, self.k, self.d, self.c, self.q)


@dataclass(frozen=True)
class DirectPairResult:
    """Fully explicit computation for a pair of repeated-root codes."""

    p: int
    s: int
    root1: int
    root2: int
    j: int
    t: int
    asymmetric: AEAQECParameters
    rank_gram: int
    intersection_dimension_1_2dual: int
    intersection_dimension_2_1dual: int
    dimension_c1: int
    dimension_c2: int
    dual_distance_1: int
    dual_distance_2: int
    pure: bool

    @property
    def symmetric(self) -> EAQECParameters:
        return self.asymmetric.to_eaqec()

    @property
    def c_from_intersection(self) -> int:
        return self.dimension_c1 - self.intersection_dimension_1_2dual

    @property
    def k_from_dimensions(self) -> int:
        return (
            self.asymmetric.n
            - self.dimension_c1
            - self.dimension_c2
            + self.asymmetric.c
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "p": self.p,
            "s": self.s,
            "q": self.asymmetric.q,
            "n": self.asymmetric.n,
            "root1": self.root1,
            "root2": self.root2,
            "j": self.j,
            "t": self.t,
            "dimension_c1": self.dimension_c1,
            "dimension_c2": self.dimension_c2,
            "dim_C1_intersection_C2dual": self.intersection_dimension_1_2dual,
            "dim_C2_intersection_C1dual": self.intersection_dimension_2_1dual,
            "rank_G1_G2_transpose": self.rank_gram,
            "c_from_rank": self.asymmetric.c,
            "c_from_intersection": self.c_from_intersection,
            "k": self.asymmetric.k,
            "k_from_dimensions": self.k_from_dimensions,
            "dz": self.asymmetric.dz,
            "dx": self.asymmetric.dx,
            "d": self.asymmetric.d,
            "dual_distance_1": self.dual_distance_1,
            "dual_distance_2": self.dual_distance_2,
            "pure": self.pure,
            "aeaqec_singleton_lhs": self.asymmetric.singleton_lhs,
            "aeaqec_singleton_rhs": self.asymmetric.singleton_rhs,
            "aeaqec_mds": self.asymmetric.is_mds(),
            "eaqec": self.symmetric.notation(),
            "aeaqec": self.asymmetric.notation(),
        }


def _required_distance(value: Optional[int], label: str) -> int:
    if value is None:
        raise ValueError(f"{label}: the relevant set difference has no nonzero vector")
    return value


def direct_constacyclic_pair(
    p: int,
    s: int,
    j: int,
    t: int,
    *,
    root1: int = 1,
    root2: int = 2,
    max_codewords: int = 2_000_000,
) -> DirectPairResult:
    """Compute Theorem 2.6/3.3 parameters without using distance formulas.

    Steps are deliberately independent of the paper's closed parameter
    formulas: build generator matrices, compute both Euclidean duals, form both
    intersections, evaluate ``rank(G1*G2.T)``, and exhaustively enumerate the
    two dual-code set differences.  It is therefore a genuine finite-case
    verification, although exhaustive distances are only feasible for small
    dual dimensions.
    """
    validate_prime(p)
    if (root1 - root2) % p == 0:
        raise ValueError("Theorem 3.2 requires distinct nonzero twists")
    c1_definition = RepeatedRootConstacyclicCode(p, s, root1, j)
    c2_definition = RepeatedRootConstacyclicCode(p, s, root2, t)
    c1 = c1_definition.row_space()
    c2 = c2_definition.row_space()
    c1_dual = c1.dual()
    c2_dual = c2.dual()

    intersection_1_2dual = c1.intersection(c2_dual)
    intersection_2_1dual = c2.intersection(c1_dual)
    gram = gram_matrix(c1.matrix(), c2.matrix(), p)
    c = rank(gram, p) if gram else 0
    c_intersection = c1.dimension - intersection_1_2dual.dimension
    if c != c_intersection:
        raise ArithmeticError(
            f"Theorem 2.7 rank/intersection mismatch: {c} != {c_intersection}"
        )

    n = p**s
    k = n - c1.dimension - c2.dimension + c
    dz = _required_distance(
        c1_dual.minimum_weight_outside(
            intersection_2_1dual, max_codewords=max_codewords
        ),
        "dz",
    )
    dx = _required_distance(
        c2_dual.minimum_weight_outside(
            intersection_1_2dual, max_codewords=max_codewords
        ),
        "dx",
    )
    dual_distance_1 = c1_dual.minimum_distance(max_codewords=max_codewords)
    dual_distance_2 = c2_dual.minimum_distance(max_codewords=max_codewords)
    pure = dz == dual_distance_1 and dx == dual_distance_2
    asymmetric = AEAQECParameters(n, k, dz, dx, c, p)
    return DirectPairResult(
        p=p,
        s=s,
        root1=c1_definition.root,
        root2=c2_definition.root,
        j=j,
        t=t,
        asymmetric=asymmetric,
        rank_gram=c,
        intersection_dimension_1_2dual=intersection_1_2dual.dimension,
        intersection_dimension_2_1dual=intersection_2_1dual.dimension,
        dimension_c1=c1.dimension,
        dimension_c2=c2.dimension,
        dual_distance_1=dual_distance_1,
        dual_distance_2=dual_distance_2,
        pure=pure,
    )


def eaqec_s1(p: int, m: int, j: int, t: int) -> EAQECParameters:
    """The independently checked ``s=1`` branch of Theorem 3.4.

    Requires ``0 <= j < t <= p``.  Setting ``t=p`` gives the zero-entanglement
    boundary; the paper's displayed tables normally omit that boundary.
    """
    validate_prime(p)
    if m < 1:
        raise ValueError("m must be positive")
    if not 0 <= j < t <= p:
        raise ValueError(f"require 0 <= j < t <= p; received j={j}, t={t}")
    return EAQECParameters(p, j, p - t + 1, p - t, p**m)


def paper_3_4_reported(p: int, m: int, s: int, j: int, t: int) -> EAQECParameters:
    """Literal two-branch output of Theorem 3.4, including its disputed s>=2 branch.

    This function is for transcription/auditing only.  Use :func:`eaqec_s1`
    for the independently verified construction or
    :func:`direct_constacyclic_pair` for an explicit general-s computation.
    """
    validate_prime(p)
    if m < 1 or s < 1:
        raise ValueError("m and s must be positive")
    n = p**s
    if not 0 <= j < t <= n:
        raise ValueError(f"require 0 <= j < t <= {n}; received j={j}, t={t}")
    if s == 1:
        return eaqec_s1(p, m, j, t)
    return EAQECParameters(n, 2, 1, 1, p**m)


def aeaqec_mds_s1(
    p: int,
    m: int,
    j: int,
    t: int,
    *,
    swap_constituents: bool = False,
) -> AEAQECParameters:
    """Valid MDS pair for ``0 <= j < t <= p`` over ``F_(p^m)``.

    With C1=C_j and C2=C_t, Theorem 2.6 gives
    ``dz=p-j+1`` and ``dx=p-t+1``.  Swapping the two constituents swaps these
    two distances while leaving n,k,c unchanged.  Both orientations are
    included because the paper's later formulas interchange the roles in
    different places.
    """
    validate_prime(p)
    if m < 1:
        raise ValueError("m must be positive")
    if not 0 <= j < t <= p:
        raise ValueError(f"require 0 <= j < t <= p; received j={j}, t={t}")
    dz, dx = p - j + 1, p - t + 1
    if swap_constituents:
        dz, dx = dx, dz
    return AEAQECParameters(p, j, dz, dx, p - t, p**m)


def paper_3_20_reported(p: int, m: int, j: int, t: int) -> AEAQECParameters:
    """Literal output of Theorem 3.20's displayed formula (not endorsed).

    The proof prints ``j>t`` while its entanglement calculation requires the
    opposite dimension ordering.  This function exists only to reproduce the
    paper-stated tables and compare them with explicit matrices.  Use
    :func:`direct_constacyclic_pair` or :func:`aeaqec_mds_s1` for validated
    constructions.
    """
    validate_prime(p)
    if m < 1:
        raise ValueError("m must be positive")
    if not 1 <= t < j <= p - 1:
        raise ValueError("paper-table mode uses 1 <= t < j <= p-1")
    return AEAQECParameters(p, j, p - t + 1, p - j + 1, p - t, p**m)
