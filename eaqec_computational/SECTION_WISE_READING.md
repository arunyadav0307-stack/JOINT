# Section-wise reading and computational map

## Source and notation

The attached 45-page paper studies entanglement-assisted quantum codes obtained from repeated-root constacyclic codes. Its main setting is

- p: an odd prime;
- q = p^m and the classical alphabet F_q;
- n = p^s: classical code length and quantum physical length;
- C_j = <(x-alpha0)^j> in F_q[x]/<x^(p^s)-alpha>, with alpha0^(p^s)=alpha;
- dim(C_j) = n-j;
- C_j^perp = <(x-alpha0^(-1))^(n-j)>.

For two classical codes with generator matrices G1,G2 and dimensions k1,k2, the entanglement quantity is

    c = rank(G1 G2^T) = k1 - dim(C1 intersect C2^perp),

and the constructed logical dimension is k = n-k1-k2+c. The asymmetric distances are computed from the two dual-code set differences in Theorem 2.6. Although the paper often says “qubits,” general F_q constructions are q-ary (qudit) codes.

---

## Section 1 — Introduction

### Content read

The section reviews quantum error correction, entanglement-assisted codes, hulls and relative hulls, GRS/matrix-product/LCD approaches, and asymmetric entanglement-assisted codes. It identifies three targets:

1. new EAQEC parameters at physical length p^s;
2. AEAQEC MDS constructions and comparisons;
3. extension of the pure-AEAQEC Singleton inequality to the general construction.

### Computational translation

The meaningful computational checks are therefore not merely table typing. They are:

- construct the classical constituent matrices;
- compute c independently by rank and by intersection dimension;
- recover k from n-k1-k2+c;
- compute or bound dz,dx;
- test the Singleton equality/defect;
- compare every generated row with reported small tables.

These are implemented in `eaqec/linalg.py`, `eaqec/constacyclic.py`, and `eaqec/quantum.py`.

---

## Section 2 — Preliminaries

### Lemma 2.1 and Theorem 2.2: ideal and dual structure

A linear constacyclic code is an ideal of the polynomial quotient. In the repeated-root setting the ideal has the form C_j=<(x-alpha0)^j>, with q^(n-j) codewords. The program forms the basis

    (x-alpha0)^j, x(x-alpha0)^j, ..., x^(n-j-1)(x-alpha0)^j

in coefficient coordinates. Since every basis polynomial has degree at most n-1, no modular reduction is needed in these rows.

**Code:** `RepeatedRootConstacyclicCode.generator_matrix()` and `dual_root_description()`.

**Check:** for every j=0,...,9 over F_3 with n=9, the dual obtained by nullspace linear algebra equals the explicitly generated root-inverse dual ideal. Additional dual checks cover every j over F_7.

### Theorem 2.3: Hamming distance

The piecewise distance formula is implemented literally, including its three regions and zero-code boundary.

**Code:** `hamming_distance_2_3(p,s,j)`.

**Independent check:** for p=3, s=2, all ten ideals C_j are exhaustively enumerated. Formula and direct distances agree:

| j | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| d | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 6 | 9 | 0 |

### Definitions 2.4–2.8: quantum parameters and purity

- EAQEC: [[n,k,d;c]]_q.
- AEAQEC: [[n,k,dz/dx;c]]_q.
- Purity requires both asymmetric set-difference distances to equal the corresponding full dual-code distances.

**Code:** `EAQECParameters`, `AEAQECParameters`, and `DirectPairResult.pure`.

### Theorems 2.6–2.10: c, intersections and distances

`direct_constacyclic_pair()` performs the following sequence without using the later closed distance formulas:

1. build C1 and C2;
2. compute C1^perp and C2^perp by nullspaces;
3. compute both intersections by a block-nullspace system;
4. evaluate rank(G1 G2^T);
5. check c = k1-dim(C1 intersect C2^perp);
6. enumerate the two dual codes and compute the minimum weights outside the prescribed intersections;
7. set k=n-k1-k2+c and d=min(dz,dx).

This is the central independent verification routine.

### Theorems 2.9, 2.11, 2.13 and Definition 2.12: bounds

The parameter classes expose:

- EAQEC: 2d+k <= n+c+2, with the separate d <= (n+2)/2 hypothesis flag;
- AEAQEC: dx+dz <= n-k+c+2;
- Singleton defect (right side minus left side);
- MDS equality tests.

The code does not silently assume the EAQEC bound hypothesis when recording a row; it stores the hypothesis flag separately.

---

## Section 3 — EAQEC and AEAQEC codes

### Theorems 3.1–3.3: ingredients

- Theorem 3.1 classifies MDS repeated-root constacyclic codes. The s=1 case gives d(C_j)=j+1 for 0<=j<=p-1.
- Theorem 3.2 supplies the intersection dimension under distinct twists and dimension sum greater than n.
- Theorem 3.3 converts the two classical constituents and their dual set differences into EAQEC parameters.

`is_mds_3_1()` records the classification, while explicit intersections and distances are handled by the Section 2 routines.

### Theorem 3.4, s=1: EAQEC family

For 0<=j<t<=p, direct computation gives

    k1 = p-j,                 k2 = p-t,
    dim(C1 intersect C2^perp) = t-j,
    c = p-t,                  k = j,
    dz = p-j+1,               dx = p-t+1.

Since j<t, the EAQEC minimum distance is d=dx=p-t+1. Hence

    [[p,j,p-t+1;p-t]]_q.

**Verification status:** this formula passes every nontrivial explicit pair over F_3 and F_5 and, in deep mode, all 15 nontrivial pairs over F_7. The root choices used for the F_7 checks are the paper's alpha0=3 and gamma0=2.

### Theorem 3.4, s>=2: statement requiring caution

As printed, the theorem assigns [[p^s,2,1;1]]_q without restricting j,t beyond 0<=j<t<=p^s. This is not compatible with the dimension identity k=j and c=p-t used in its own proof.

An explicit valid counterexample computed by the program is:

    p=3, s=2, n=9, j=1, t=2, roots 1 and 2
    k1=8, k2=7, dim(C1 intersect C2^perp)=1
    c=7, k=1, dz=9, dx=6
    direct EAQEC = [[9,1,6;7]]_3
    direct AEAQEC = [[9,1,9/6;7]]_3.

Therefore the package does **not** label the universal s>=2 formula as verified. It generates the closed EAQEC families only for s=1 and retains the s>=2 case in the discrepancy report.

### Examples 3.5–3.16 and Remark 3.17: EAQEC tables

The examples use length-p codes over F_p, normally with 3- and 2-constacyclic constituents. The generator covers the nontrivial rows 1<=j<t<=p-1 (k>0,c>0).

| p | Generated nontrivial rows | Paper location |
|---:|---:|---|
| 7 | 15 | Example 3.5 / Table 22 |
| 11 | 45 | Example 3.7 / Table 23 |
| 19 | 153 | Example 3.9 / Table 24 |
| 23 | 231 | Example 3.11 / Table 25 |
| 29 | 378 | Example 3.13 / Table 26 |
| 31 | 435 | Example 3.15 / Table 27 |
| 59 | 1653 | Remark 3.17 comparisons |
| 167 | 13695 | Remark 3.17 comparisons |

Table 22 is an exact ordered match. Table 23 includes the anomalous printed row [[11,4,15;14]]_11; it has d>n and c>n and is not produced by the theorem formula.

The numerous remarks compare n,k,d,c with earlier references. This package checks arithmetic and family parameters; it does not independently repeat the paper's complete literature search or novelty claim.

### Theorems 3.18–3.19: general AEAQEC parameter mechanism

The useful dimension computation is the same as above. For arbitrary classical dimensions with k1>=k2, Theorem 3.19 uses

    c = k2,       k = n-k1.

For the repeated-root pair C1=C_j,C2=C_t, k1>=k2 means j<=t. With j<t this yields c=p-t and k=j. This ordering is important for the computational implementation.

### Theorem 3.20 and Examples 3.23, 3.25, 3.27

For the matrix-consistent ordering j<t, two valid orientations follow directly from Theorem 2.6:

| Constituents | Parameters |
|---|---|
| C1=C_j, C2=C_t | [[p,j,(p-j+1)/(p-t+1);p-t]]_q |
| C1=C_t, C2=C_j | [[p,j,(p-t+1)/(p-j+1);p-t]]_q |

Both have the same n,k,c and Singleton sum, and both are MDS in the checked s=1 cases. The package writes both orientations to `results/tables/aeaqec_mds/`.

The proof of Theorem 3.20 as printed instead says j>t while retaining c=p-t. The explicit input j=2,t=1 over F_7 gives:

    paper/Table 34: [[7,2,7/6;6]]_7
    direct rank: c=5
    direct dimensions: k=1
    direct AEAQEC: [[7,1,6/7;5]]_7.

Thus the printed ordering cannot simply be used for validated generation. Literal outputs are still reproducible under `results/tables/paper_stated/`, with an explicit unverified label.

The transcription check of Table 34 also finds two duplicated rows and three rows whose c values differ from the displayed Theorem 3.20 formula itself. These are separate internal-table issues in addition to the matrix-level ordering problem.

### Theorem 3.21: AEAQEC Singleton bound

The program tests

    dx+dz <= n-k+c+2

for every explicit pair, including the s>=2 counterexample. The inequality holds in all computed cases. This is finite-case evidence for the bound, not a software proof of the general theorem.

### Theorem 3.22: MDS condition

For s=1 repeated-root constituents, direct computation confirms purity and

    dx+dz = n-k+c+2

for all tested pairs, including the swapped orientation. The full dual distances and the two set-difference distances are separately enumerated to check purity rather than inferred only from the Singleton equality.

### Remarks 3.24–3.29 and Tables 28–36

The paper compares its AEAQEC distances with previously published asymmetric codes. The program supplies generated tables and exact Singleton data for p=7,11,19. Because of the ordering discrepancy above, users should compare the matrix-verified tables, not assume that every printed Table 34–36 row has been computationally certified.

---

## Section 4 — Conclusion

The conclusion summarizes new EAQEC parameters, AEAQEC MDS examples, comparisons with earlier codes, and the general AEAQEC Singleton bound. The computational supplement supports the s=1 parameter mechanism and bound checks, while identifying specific statements/tables that need author review before reuse.

## What is and is not certified here

**Computed exactly:**

- small prime-field generator matrices, ranks, duals, intersections and distances;
- all declared small-case comparisons;
- every generated CSV row and its Singleton arithmetic;
- exact Table 22 and internal Table 34 comparisons.

**Not claimed:**

- a formal proof of every theorem;
- exhaustive large-p minimum-distance computation;
- explicit extension-field matrix verification (closed formulas still accept q=p^m);
- independent verification of every literature comparison or novelty statement.
