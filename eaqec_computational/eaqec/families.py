"""Parameter-family generation and CSV serialization for the paper examples."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Iterator, Literal, TextIO

from .linalg import validate_prime
from .quantum import (
    AEAQECParameters,
    EAQECParameters,
    aeaqec_mds_s1,
    eaqec_s1,
    paper_3_20_reported,
)


Orientation = Literal["natural", "swapped", "both"]


def nontrivial_pairs_s1(p: int) -> Iterator[tuple[int, int]]:
    """Pairs used in the displayed tables: 1 <= j < t <= p-1.

    These exclude k=0 and c=0 boundary cases, exactly as the examples do.
    """
    for j in range(1, p - 1):
        for t in range(j + 1, p):
            yield j, t


def eaqec_family(p: int, m: int = 1) -> Iterator[tuple[int, int, EAQECParameters]]:
    validate_prime(p)
    if m < 1:
        raise ValueError("m must be positive")
    for j, t in nontrivial_pairs_s1(p):
        yield j, t, eaqec_s1(p, m, j, t)


def aeaqec_family(
    p: int,
    m: int = 1,
    *,
    orientation: Orientation = "natural",
) -> Iterator[tuple[int, int, str, AEAQECParameters]]:
    """Generate matrix-consistent AEAQEC MDS families for s=1.

    ``natural`` uses C1=C_j, C2=C_t with j<t. ``swapped`` interchanges the
    constituents and hence swaps dz/dx. ``both`` emits both valid orientations.
    """
    validate_prime(p)
    if orientation not in ("natural", "swapped", "both"):
        raise ValueError("orientation must be natural, swapped, or both")
    labels = ("natural", "swapped") if orientation == "both" else (orientation,)
    for j, t in nontrivial_pairs_s1(p):
        for label in labels:
            yield (
                j,
                t,
                label,
                aeaqec_mds_s1(p, m, j, t, swap_constituents=(label == "swapped")),
            )


def paper_3_20_family(p: int, m: int = 1) -> Iterator[tuple[int, int, AEAQECParameters]]:
    """Literal Theorem 3.20/Table 34--36 formula output, for auditing only."""
    validate_prime(p)
    for t in range(1, p - 1):
        for j in range(t + 1, p):
            yield j, t, paper_3_20_reported(p, m, j, t)


def write_eaqec_csv(
    rows: Iterable[tuple[int, int, EAQECParameters]],
    destination: str | Path | TextIO,
) -> int:
    close = False
    if isinstance(destination, (str, Path)):
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("w", newline="", encoding="utf-8")
        close = True
    else:
        stream = destination
    count = 0
    try:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            [
                "j",
                "t",
                "q",
                "n",
                "k",
                "d",
                "c",
                "notation",
                "singleton_lhs_2d_plus_k",
                "singleton_rhs_n_plus_c_plus_2",
                "singleton_defect",
                "bound_condition_2d_le_n_plus_2",
            ]
        )
        for j, t, code in rows:
            writer.writerow(
                [
                    j,
                    t,
                    code.q,
                    code.n,
                    code.k,
                    code.d,
                    code.c,
                    code.notation(),
                    code.singleton_lhs,
                    code.singleton_rhs,
                    code.singleton_defect,
                    code.bound_condition,
                ]
            )
            count += 1
    finally:
        if close:
            stream.close()
    return count


def write_aeaqec_csv(
    rows: Iterable[tuple[int, int, str, AEAQECParameters]],
    destination: str | Path | TextIO,
) -> int:
    close = False
    if isinstance(destination, (str, Path)):
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("w", newline="", encoding="utf-8")
        close = True
    else:
        stream = destination
    count = 0
    try:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            [
                "j",
                "t",
                "orientation",
                "q",
                "n",
                "k",
                "dz",
                "dx",
                "d_min",
                "c",
                "notation",
                "singleton_lhs_dz_plus_dx",
                "singleton_rhs_n_minus_k_plus_c_plus_2",
                "singleton_defect",
                "mds",
            ]
        )
        for j, t, orientation, code in rows:
            writer.writerow(
                [
                    j,
                    t,
                    orientation,
                    code.q,
                    code.n,
                    code.k,
                    code.dz,
                    code.dx,
                    code.d,
                    code.c,
                    code.notation(),
                    code.singleton_lhs,
                    code.singleton_rhs,
                    code.singleton_defect,
                    code.is_mds(),
                ]
            )
            count += 1
    finally:
        if close:
            stream.close()
    return count


def write_paper_aeaqec_csv(
    rows: Iterable[tuple[int, int, AEAQECParameters]],
    destination: str | Path | TextIO,
) -> int:
    adapted = (
        (j, t, "paper-stated-unverified", code) for j, t, code in rows
    )
    return write_aeaqec_csv(adapted, destination)
