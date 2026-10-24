# EAQEC/AEAQEC computational supplement

Reproducible computational work for the attached paper:

> Hai Q. Dinh et al., *Asymmetric entanglement-assisted quantum error-correcting MDS codes of physical qubits p^s over F_{p^m}*, EPJ Quantum Technology 13, 90 (2026). DOI: 10.1140/epjqt/s40507-026-00503-0.

**Hinglish summary:** Paper ki s=1 parameter families generate karne ke saath, yeh package chhote cases mein explicit generator matrices, duals, intersections, entanglement rank aur exhaustive Hamming distances se independent verification karta hai. Paper-stated formulas aur matrix-verified outputs ko alag rakha gaya hai; computational discrepancies bhi report mein documented hain.

## Quick start

Python 3.10+ is sufficient. There are **no third-party dependencies**.

```bash
cd eaqec_computational

# 24 regression/integration tests
python3 -m unittest discover -s tests -v

# Generate every CSV/JSON output and run deep exact verification
python3 run_all.py
```

The main human-readable result is [`results/VERIFICATION_REPORT.md`](results/VERIFICATION_REPORT.md). The section-by-section reading and theorem-to-code map is in [`SECTION_WISE_READING.md`](SECTION_WISE_READING.md).

## What the program computes

1. **Repeated-root constacyclic codes**
   - ideals C_j = <(x-alpha0)^j> of length p^s over a prime field;
   - explicit generator matrices and dimensions;
   - Euclidean duals and the root-inverse dual description;
   - Theorem 2.3 Hamming-distance formula and exhaustive small-code distances.

2. **Exact finite-field linear algebra**
   - RREF, rank, nullspace and canonical row-space membership;
   - C1 intersect C2^perp and C2 intersect C1^perp;
   - c = rank(G1 G2^T) and its intersection-dimension identity;
   - exhaustive wt(C1^perp \ ...) and wt(C2^perp \ ...) for small dual codes.

3. **Quantum-code parameters**
   - EAQEC [[n,k,d;c]]_q and AEAQEC [[n,k,dz/dx;c]]_q records;
   - the verified s=1 EAQEC family from Theorem 3.4;
   - two matrix-consistent AEAQEC MDS orientations for j<t;
   - EAQEC/AEAQEC Singleton-bound, defect, purity and MDS checks.

4. **Reproduction and auditing**
   - all displayed EAQEC example sizes p = 7, 11, 19, 23, 29, 31 and the additional p = 59, 167 comparisons;
   - AEAQEC families for p = 7, 11, 19;
   - exact Table 22 comparison and internal Table 34 comparison;
   - explicit counterexamples for the s>=2 statement and Theorem 3.20 ordering, as printed.

## Command-line examples

Run these from `eaqec_computational/`.

### Generate a formula family

```bash
# Validated s=1 EAQEC parameters, CSV on stdout
python3 -m eaqec family eaqec --p 7

# Matrix-consistent AEAQEC MDS codes, both dz/dx orientations
python3 -m eaqec family aeaqec --p 7 --orientation both --output /tmp/aeaqec_p7.csv

# Literal Theorem 3.20 output, clearly separated for auditing only
python3 -m eaqec family paper --p 7 --output /tmp/paper_3_20_p7.csv
```

`--m M` sets q=p^M in the closed s=1 parameter formulas. Explicit matrix verification currently uses prime fields (M=1).

### Compute one pair directly

```bash
python3 -m eaqec direct \
  --p 3 --s 2 --j 1 --t 2 --root1 1 --root2 2
```

This returns JSON containing both generator-code dimensions, both intersection dimensions, rank(G1 G2^T), k, dz, dx, c, purity, Singleton data, and the EAQEC/AEAQEC notation.

For the paper's F_7 roots, use `--root1 3 --root2 2`. Roots must be nonzero and twists distinct. Exhaustive enumeration is guarded by `--max-codewords` (default 2,000,000).

### Verification only

```bash
python3 -m eaqec verify --deep --output /tmp/verification.json
```

## Output layout

After `python3 run_all.py`:

```text
results/
├── summary.json
├── verification.json
├── VERIFICATION_REPORT.md
└── tables/
    ├── eaqec_p7.csv
    ├── eaqec_p11.csv
    ├── ...                         # p=19,23,29,31,59,167
    ├── aeaqec_mds/
    │   ├── aeaqec_mds_p7.csv       # natural and swapped, j<t
    │   ├── aeaqec_mds_p11.csv
    │   └── aeaqec_mds_p19.csv
    └── paper_stated/
        ├── paper_3_20_p7.csv        # unverified literal reproduction
        ├── paper_3_20_p11.csv
        └── paper_3_20_p19.csv
```

The `paper_stated/` files are **not** presented as validated quantum codes. They exist so that the printed formulas can be compared mechanically with explicit computations.

## Important computational findings

- The s=1 EAQEC formula `[[p,j,p-t+1;p-t]]_q` agrees with all tested explicit pairs, including every nontrivial pair over F_7.
- Table 22 matches the generated 15 rows exactly and in order.
- The printed Table 23 row `[[11,4,15;14]]_11` is impossible for the stated length-11 family because d>n and c>n.
- For p=3, s=2, j=1, t=2, explicit matrices give `[[9,1,6;7]]_3`, not the universally printed s>=2 result `[[9,2,1;1]]_3`.
- For the Table 34 input j=2, t=1 over F_7, direct computation gives c=5 and k=1, not c=6 and k=2. The corresponding direct AEAQEC result is `[[7,1,6/7;5]]_7`.

See the generated report for exact dimensions and the section-wise notes for the valid j<t formulas.

## Verification scope

This is a reproducible computational supplement, not a claim that every theorem in the 45-page paper has been formally proved by software. Large-p tables come from closed formulas; exhaustive distance checks are performed only in declared small cases. Literature novelty claims are not independently searched or certified. No external datasets are used.
