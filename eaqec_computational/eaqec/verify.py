"""Independent finite-case verification and reproducible discrepancy checks."""

from __future__ import annotations

from typing import Iterable, Optional

from .constacyclic import RepeatedRootConstacyclicCode
from .quantum import (
    AEAQECParameters,
    EAQECParameters,
    DirectPairResult,
    aeaqec_mds_s1,
    direct_constacyclic_pair,
    eaqec_s1,
    paper_3_4_reported,
    paper_3_20_reported,
)


DEFAULT_MAX_CODEWORDS = 2_000_000


def verify_distance_formula_p3_s2(*, max_codewords: int = DEFAULT_MAX_CODEWORDS) -> dict[str, object]:
    """Exhaustively check Theorem 2.3 and the dual description for n=9, p=3."""
    cases = []
    for j in range(10):
        code = RepeatedRootConstacyclicCode(3, 2, 1, j)
        formula = code.theoretical_distance()
        direct = code.direct_distance(max_codewords=max_codewords)
        dual_matches = code.row_space().dual() == code.dual_root_description().row_space()
        cases.append(
            {
                "j": j,
                "dimension": code.dimension,
                "formula_distance": formula,
                "direct_distance": direct,
                "distance_match": formula == direct,
                "dual_root_description_match": dual_matches,
                "pass": formula == direct and dual_matches,
            }
        )
    return {
        "description": "Theorem 2.3 distances and Theorem 2.2 duals over F_3, length 9",
        "cases": cases,
        "pass": all(case["pass"] for case in cases),
    }


def _case_result(
    direct: DirectPairResult,
    expected_eaqec: EAQECParameters,
    expected_aeaqec: AEAQECParameters,
    *,
    require_pure_mds: bool,
) -> dict[str, object]:
    comparisons = {
        "eaqec_parameters_match": direct.symmetric == expected_eaqec,
        "aeaqec_parameters_match": direct.asymmetric == expected_aeaqec,
        "rank_intersection_c_match": direct.rank_gram == direct.c_from_intersection,
        "k_dimension_identity_match": direct.asymmetric.k == direct.k_from_dimensions,
        "aeaqec_singleton_bound": direct.asymmetric.satisfies_singleton_bound(),
        "eaqec_singleton_bound": direct.symmetric.satisfies_singleton_bound(),
    }
    if require_pure_mds:
        comparisons["pure"] = direct.pure
        comparisons["aeaqec_mds"] = direct.asymmetric.is_mds()
    return {
        "j": direct.j,
        "t": direct.t,
        "root1": direct.root1,
        "root2": direct.root2,
        "expected_eaqec": expected_eaqec.notation(),
        "direct_eaqec": direct.symmetric.notation(),
        "expected_aeaqec": expected_aeaqec.notation(),
        "direct_aeaqec": direct.asymmetric.notation(),
        "comparisons": comparisons,
        "direct_data": direct.as_dict(),
        "pass": all(comparisons.values()),
    }


def verify_s1_cases(
    p: int,
    *,
    pairs: Optional[Iterable[tuple[int, int]]] = None,
    root1: int = 1,
    root2: int = 2,
    max_codewords: int = DEFAULT_MAX_CODEWORDS,
) -> dict[str, object]:
    """Check Theorem 3.4(s=1), Theorem 2.7 and Theorem 3.21 case by case."""
    if pairs is None:
        pairs = ((j, t) for j in range(1, p - 1) for t in range(j + 1, p))
    cases = []
    for j, t in pairs:
        direct = direct_constacyclic_pair(
            p,
            1,
            j,
            t,
            root1=root1,
            root2=root2,
            max_codewords=max_codewords,
        )
        cases.append(
            _case_result(
                direct,
                eaqec_s1(p, 1, j, t),
                aeaqec_mds_s1(p, 1, j, t),
                require_pure_mds=True,
            )
        )
    return {
        "description": f"Explicit generator-matrix verification over F_{p}, s=1",
        "p": p,
        "cases": cases,
        "pass": all(case["pass"] for case in cases),
    }


def verify_swapped_orientation(
    *,
    max_codewords: int = DEFAULT_MAX_CODEWORDS,
) -> dict[str, object]:
    """Verify the second valid AEAQEC orientation by swapping constituents."""
    j, t = 2, 4
    # Natural constituents are (root 3, exponent j) and (root 2, exponent t).
    # Swapping the codes also swaps their roots.
    direct = direct_constacyclic_pair(
        7,
        1,
        t,
        j,
        root1=2,
        root2=3,
        max_codewords=max_codewords,
    )
    expected = aeaqec_mds_s1(7, 1, j, t, swap_constituents=True)
    comparisons = {
        "parameters_match": direct.asymmetric == expected,
        "singleton_bound": direct.asymmetric.satisfies_singleton_bound(),
        "mds": direct.asymmetric.is_mds(),
        "pure": direct.pure,
    }
    return {
        "description": "Swapped constituent orientation over F_7",
        "expected": expected.notation(),
        "direct": direct.asymmetric.notation(),
        "direct_data": direct.as_dict(),
        "comparisons": comparisons,
        "pass": all(comparisons.values()),
    }


def discrepancy_counterexamples(
    *, max_codewords: int = DEFAULT_MAX_CODEWORDS
) -> dict[str, object]:
    """Compute explicit counterexamples to two statements as printed.

    These mismatches are expected audit findings, not failures of the test
    suite.  Every assertion below checks the independently computed values.
    """
    general = direct_constacyclic_pair(
        3,
        2,
        1,
        2,
        root1=1,
        root2=2,
        max_codewords=max_codewords,
    )
    printed_general = paper_3_4_reported(3, 1, 2, 1, 2)
    general_checks = {
        "direct_n_k_d_c": (general.symmetric.n, general.symmetric.k, general.symmetric.d, general.symmetric.c)
        == (9, 1, 6, 7),
        "printed_parameters_differ": general.symmetric != printed_general,
        "rank_intersection_identity": general.rank_gram == general.c_from_intersection,
    }

    reported = paper_3_20_reported(7, 1, 2, 1)
    direct = direct_constacyclic_pair(
        7,
        1,
        2,
        1,
        root1=3,
        root2=2,
        max_codewords=max_codewords,
    )
    asymmetric_checks = {
        "paper_row_is_table_34_first_row": reported.notation() == "[[7,2,7/6;6]]_7",
        "direct_n_k_dz_dx_c": (
            direct.asymmetric.n,
            direct.asymmetric.k,
            direct.asymmetric.dz,
            direct.asymmetric.dx,
            direct.asymmetric.c,
        )
        == (7, 1, 6, 7, 5),
        "paper_c_differs_from_rank": reported.c != direct.rank_gram,
        "paper_parameters_differ": reported != direct.asymmetric,
    }
    return {
        "theorem_3_4_s_ge_2": {
            "input": {"p": 3, "s": 2, "j": 1, "t": 2, "root1": 1, "root2": 2},
            "printed": printed_general.notation(),
            "direct_eaqec": general.symmetric.notation(),
            "direct_aeaqec": general.asymmetric.notation(),
            "direct_data": general.as_dict(),
            "checks": general_checks,
            "pass": all(general_checks.values()),
        },
        "theorem_3_20_table_34": {
            "input": {"p": 7, "s": 1, "j": 2, "t": 1, "root1": 3, "root2": 2},
            "printed": reported.notation(),
            "direct_eaqec": direct.symmetric.notation(),
            "direct_aeaqec": direct.asymmetric.notation(),
            "direct_data": direct.as_dict(),
            "checks": asymmetric_checks,
            "pass": all(asymmetric_checks.values()),
        },
    }


def run_verification(*, deep: bool = False) -> dict[str, object]:
    """Run deterministic checks; ``deep`` adds every nontrivial F_7 pair."""
    distance = verify_distance_formula_p3_s2()
    prime3 = verify_s1_cases(3)
    prime5 = verify_s1_cases(5)
    if deep:
        prime7 = verify_s1_cases(7, root1=3, root2=2)
    else:
        prime7 = verify_s1_cases(
            7,
            pairs=[(1, 2), (2, 3), (2, 6), (4, 5), (5, 6)],
            root1=3,
            root2=2,
        )
    swapped = verify_swapped_orientation()
    discrepancies = discrepancy_counterexamples()
    components = [distance, prime3, prime5, prime7, swapped]
    components.extend(discrepancies.values())
    s1_case_count = sum(len(component.get("cases", [])) for component in (prime3, prime5, prime7))
    return {
        "scope": {
            "deep": deep,
            "method": "exact prime-field linear algebra and exhaustive codeword enumeration",
            "max_codewords_per_enumeration": DEFAULT_MAX_CODEWORDS,
            "s1_pair_cases": s1_case_count,
        },
        "distance_formula": distance,
        "s1_verification": {"F_3": prime3, "F_5": prime5, "F_7": prime7},
        "swapped_orientation": swapped,
        "discrepancies": discrepancies,
        "pass": all(component["pass"] for component in components),
    }
