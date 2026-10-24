#!/usr/bin/env python3
"""Generate the complete computational supplement with exact deep checks."""

from pathlib import Path

from eaqec.reproduce import reproduce


if __name__ == "__main__":
    destination = Path(__file__).resolve().parent / "results"
    manifest = reproduce(destination, deep=True)
    verification = manifest["verification"]
    print("=" * 68)
    print("EAQEC/AEAQEC COMPUTATIONAL SUPPLEMENT")
    print("=" * 68)
    print(f"Verification: {'PASS' if verification['pass'] else 'FAIL'}")
    print(f"Direct s=1 pair cases: {verification['s1_pair_cases']}")
    print(f"Output: {destination}")
    print(f"Report: {destination / 'VERIFICATION_REPORT.md'}")
