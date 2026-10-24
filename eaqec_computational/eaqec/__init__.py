"""Reproducible computations for the EAQEC/AEAQEC constacyclic-code paper."""

from .constacyclic import RepeatedRootConstacyclicCode, hamming_distance_2_3
from .quantum import (
    AEAQECParameters,
    EAQECParameters,
    aeaqec_mds_s1,
    direct_constacyclic_pair,
    eaqec_s1,
    paper_3_4_reported,
    paper_3_20_reported,
)

__all__ = [
    "AEAQECParameters",
    "EAQECParameters",
    "RepeatedRootConstacyclicCode",
    "aeaqec_mds_s1",
    "direct_constacyclic_pair",
    "eaqec_s1",
    "hamming_distance_2_3",
    "paper_3_4_reported",
    "paper_3_20_reported",
]
