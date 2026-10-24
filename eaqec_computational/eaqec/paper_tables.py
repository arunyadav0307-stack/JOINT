"""Small reported tables transcribed for exact, reproducible comparisons.

The large families are generated from formulas rather than copied.  Tables 22
and 34 are short enough to transcribe and provide useful regression checks.
"""

from __future__ import annotations

from collections import Counter

from .families import eaqec_family, paper_3_20_family
from .quantum import AEAQECParameters, EAQECParameters


TABLE_22_REPORTED = [
    EAQECParameters(7, 1, 6, 5, 7),
    EAQECParameters(7, 1, 5, 4, 7),
    EAQECParameters(7, 1, 4, 3, 7),
    EAQECParameters(7, 1, 3, 2, 7),
    EAQECParameters(7, 1, 2, 1, 7),
    EAQECParameters(7, 2, 5, 4, 7),
    EAQECParameters(7, 2, 4, 3, 7),
    EAQECParameters(7, 2, 3, 2, 7),
    EAQECParameters(7, 2, 2, 1, 7),
    EAQECParameters(7, 3, 4, 3, 7),
    EAQECParameters(7, 3, 3, 2, 7),
    EAQECParameters(7, 3, 2, 1, 7),
    EAQECParameters(7, 4, 3, 2, 7),
    EAQECParameters(7, 4, 2, 1, 7),
    EAQECParameters(7, 5, 2, 1, 7),
]


TABLE_34_REPORTED = [
    AEAQECParameters(7, 2, 7, 6, 6, 7),
    AEAQECParameters(7, 3, 7, 5, 6, 7),
    AEAQECParameters(7, 4, 7, 4, 6, 7),
    AEAQECParameters(7, 5, 7, 3, 6, 7),
    AEAQECParameters(7, 6, 7, 2, 6, 7),
    AEAQECParameters(7, 3, 6, 5, 5, 7),
    AEAQECParameters(7, 4, 6, 4, 5, 7),
    AEAQECParameters(7, 5, 6, 3, 5, 7),
    AEAQECParameters(7, 6, 6, 2, 5, 7),
    AEAQECParameters(7, 4, 5, 4, 4, 7),
    AEAQECParameters(7, 5, 5, 3, 4, 7),
    AEAQECParameters(7, 4, 5, 4, 4, 7),
    AEAQECParameters(7, 5, 5, 3, 4, 7),
    AEAQECParameters(7, 6, 5, 2, 4, 7),
    AEAQECParameters(7, 5, 4, 3, 2, 7),
    AEAQECParameters(7, 6, 4, 2, 1, 7),
    AEAQECParameters(7, 6, 3, 2, 1, 7),
]


def compare_table_22() -> dict[str, object]:
    generated = [code for _, _, code in eaqec_family(7)]
    return {
        "reported_rows": len(TABLE_22_REPORTED),
        "generated_rows": len(generated),
        "exact_ordered_match": generated == TABLE_22_REPORTED,
        "pass": generated == TABLE_22_REPORTED,
    }


def compare_table_34() -> dict[str, object]:
    """Compare the printed table with its own displayed Theorem 3.20 formula.

    This is an internal consistency check only.  A separate explicit-matrix
    counterexample in ``verify.py`` checks the actual constacyclic construction.
    """
    literal = [code for _, _, code in paper_3_20_family(7)]
    counts = Counter(TABLE_34_REPORTED)
    duplicates = sorted(
        (code.notation(), count) for code, count in counts.items() if count > 1
    )
    missing = [code.notation() for code in literal if code not in counts]
    mismatches = []
    for index, reported in enumerate(TABLE_34_REPORTED, start=1):
        # For the displayed formula, k=j and dz=p-t+1.
        j = reported.k
        t = 7 - reported.dz + 1
        if not 1 <= t < j <= 6:
            continue
        expected = next(
            code for jj, tt, code in paper_3_20_family(7) if (jj, tt) == (j, t)
        )
        if reported != expected:
            mismatches.append(
                {
                    "row": index,
                    "reported": reported.notation(),
                    "literal_formula": expected.notation(),
                }
            )
    return {
        "reported_rows": len(TABLE_34_REPORTED),
        "literal_formula_rows": len(literal),
        "duplicates": duplicates,
        "missing_literal_formula_rows": missing,
        "row_mismatches": mismatches,
        "pass": not duplicates and not missing and not mismatches,
    }
