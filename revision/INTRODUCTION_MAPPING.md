# Introduction rewrite — internal mapping

**Paper:** *Joint Code-Dimension and k-Galois-Hull Enumerators for Simple-Root
Constacyclic Codes over Square-Free Affine Algebras* (manuscript
`FINAL_SUBMISSION.tex`).
**Reference used as a style/structure model only:** Debnath & Prakash, *Average
dimensions of Galois hulls of constacyclic codes*, Adv. Math. Commun. 19(6)
(2025) 1569–1604 — the paper's own reference `debnathAverage2025`. Its
Introduction was read for structure (motivation → chronological literature →
finite-ring paragraph → "Motivated by the above works…" → contributions →
organisation). No sentence, phrase or wording was taken from it.

---

## 1. Mapping: existing statement → supporting reference → role

| # | Statement in the old Introduction | Reference | Role in the new Introduction |
|---|---|---|---|
| 1 | Hull is `C ∩ C^⊥`; its dimension matters in several constructions | — (definition) | ¶1, opening definition |
| 2 | LCD codes | `massey1992` | ¶2 (applications) |
| 3 | LCD codes meet the Gilbert–Varshamov bound | `sendrier2004` | ¶2 (applications) |
| 4 | Code automorphisms / permutation-equivalence algorithms | `sendrier1997` | ¶2 (applications) + ¶5 (mass formula) |
| 5 | Entanglement-assisted quantum codes | `brun2006` | ¶2 (applications) |
| 6 | Optimal entanglement formulas | `wildeBrun2008` | ¶2 (applications) |
| 7 | k-Galois hull; Euclidean and Hermitian are `k = 0` and `k = d/2` | `fanZhang2017` | ¶1 (concept) |
| 8 | Polynomial-quotient viewpoint for cyclic-type codes | `huffmanPless2003` | ¶1 (concept) |
| 9 | Complementary-dual criterion for cyclic codes | `yangMassey1994` | ¶3 (cyclic, 1994) |
| 10 | Average Euclidean hull of cyclic codes | `skersys2003` | ¶3 (2003) + ¶5 (first moments) |
| 11 | Hull dimensions and prescribed-hull-dimension counts, cyclic/negacyclic | `sangwisut2015` | ¶3 (2015) + ¶7 (answers (i),(ii)) + ¶10 (benchmarks) |
| 12 | Average Hermitian hull of constacyclic codes, square-order fields | `jitmanSangwisut2018` | ¶3 (2018) + ¶5 |
| 13 | k-Galois hull formulas + counts for constacyclic codes over fields | `debnathConstacyclic2023` | ¶3 (2023) + ¶7 |
| 14 | Correction to the above | `debnathCorrection2023` | ¶3 |
| 15 | Average Galois hull dimension of constacyclic codes | `debnathAverage2025` | ¶3 (2025) + ¶5 |
| 16 | Small Galois hull dimensions | `debnathSmall2026` | ¶3 |
| 17 | Galois hulls of general linear codes | `liuPan2020` | ¶4 |
| 18 | MDS codes with prescribed Galois hull dimension | `cao2021` | ¶2 (application) + ¶4 |
| 19 | Galois self-orthogonal constacyclic codes | `fuLiu2022` | ¶4 |
| 20 | Generator polynomial matrices of Galois hulls of multi-twisted codes | `eldinSole2026` | ¶4 |
| 21 | Generator matrices for `C ∩ C^{⊥_k}` | `eldinLeroy2026` | ¶4 |
| 22 | Double cyclic codes | `gao2023` | ¶5 |
| 23 | Double/four circulant codes with small hull dimension | `aliabadi2026` | ¶5 |
| 24 | Sequence of numbers of linear codes with increasing hull dimension | `bouyuklieva2026` | ¶5 + ¶7 (answers (iii) over fields) |
| 25 | Chain-ring structure theory (cyclic/negacyclic) | `dinhLopezPermouth2004` | ¶6 (rings background) |
| 26 | Hamming-distance theory over chain rings | `nortonSalagean2000` | ¶6 (rings background) |
| 27 | Hulls of cyclic serial codes over a chain ring | `talbi2022` | ¶6 |
| 28 | Hulls of cyclic codes over Z₄ | `jitmanZ4` | ¶6 |
| 29 | Oddly even length over Z₄ | `pathakZ4` | ¶6 |
| 30 | Constacyclic codes over a non-chain ring + quantum codes | `zhang2026` | ¶2 (application) + ¶6 |
| 31 | k-Galois hulls of constacyclic codes over affine algebra rings (closest work) | `debnathAffine2026` | ¶6 (end) + ¶7 (the only answered question) |
| 32 | Bijection code ↔ labeled factor selection | internal Lemmas `lem:complete`, `lem:global-code` | ¶8 |
| 33 | Compatibility condition `λ^{1+p^{d-k}} = 1` | internal `eq:compat` | ¶8/¶9 |
| 34 | Dual generator / reciprocal / orbit boundary / transfer matrix / closed form | internal Theorems & Propositions | ¶9 (compressed statements only) |
| 35 | Main enumerator `E(u,z) = ∏ tr(T_w^a)` | internal `thm:central` | ¶9, displayed |
| 36 | Marginals, LCD count, mean, variance, conditional distribution | internal corollaries | ¶9 |
| 37 | Exactness, validation in char. 2,3,5, `F_32`, `n=31`, scope | internal §5, §6 | ¶10 |
| 38 | Roadmap + workflow figure | internal | ¶10 |

## 2. Statements kept unchanged

Every mathematical claim, citation and internal cross-reference of the old
Introduction is retained somewhere in the new one. No reference is added,
removed or re-attributed; no theorem, definition, lemma or corollary is renamed
or renumbered; the workflow figure (Fig. 1) and its caption are unchanged.

## 3. Statements rewritten, and why

| Old formulation | Problem | New formulation |
|---|---|---|
| Applications compressed into one long first sentence ("...in the classical setting these include ... ; in the quantum setting, ...") | Two paragraphs' worth of material in one sentence; hard to read | ¶2 lists the applications in one short sentence each, each with its own reference |
| Literature split by "two strands" (family-level vs. individual-code) | Topical split hides the historical order; cyclic → constacyclic → Galois → rings progression is not visible | ¶3 (cyclic/negacyclic → constacyclic), ¶4 (Galois hulls of general codes), ¶5 (distribution/ counting studies), ¶6 (rings → affine algebras), each in chronological order internally |
| Gap explained in two places (end of the second strand paragraph and the "three counting problems" paragraph) | The reader meets the gap twice, once implicitly | ¶7 states the gap once: what results of each kind give, the three questions, what is answered where, and why the joint question is open here |
| Results (i)–(iv) written as a dense technical list | Machinery (orbit weights, transfer matrices) presented before the reader has seen Section 2 | ¶9 keeps the four results but in compressed form, keeps only the main product formula on display, and labels (i)–(iii) explicitly as assembling established descriptions |
| Method announced inside the contributions paragraph | Method appears before the gap is stated | Method appears in ¶8, after the gap, in three lines only |
| "(29) study k-Galois hulls of constacyclic codes over square-free affine algebras" | The cited work is stated as being over *affine algebra rings* in the bibliography; the square-free hypothesis is the present paper's | ¶6 says "affine algebra rings"; ¶8 states that the present paper works in the square-free case with labeled field components |

## 4. What was deliberately **not** changed

* The research problem, hypotheses, notation (`κ`, `η_k`, `w_O = m_s d_O`), and
  all labels/theorem numbers.
* The abstract, keywords, MSC line, all sections after the Introduction, the
  figures, table, appendix and statements.
* The honesty statements of the original: no "first"/priority claim, and the
  explicit sentence that items (i)–(iii) assemble established descriptions while
  (iv) is the paper's result.
