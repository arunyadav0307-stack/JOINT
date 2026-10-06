# JOINT — complete handover inventory

Generated: 2026-10-06 (Asia/Calcutta) · Repo `/home/user/JOINT` · branch `arena/f97c74b1-joint` · base commit `9918239`

Everything the agent currently holds in the workspace, in one place.

## What is in this bundle

| Folder | What | Files |
|---|---|---|
| `01_repo_archives/` | The 5 archives exactly as committed in git (unchanged since commit 9918239; git tracks these as SHA-1 blobs, the md5s here are for your own integrity check) | 5 |
| `02_audit3_package_extracted/` | Audit-3 zip unpacked: manuscript (.tex/.bbl/.pdf/.bib/.bst), supplementary Python+CSV, reports, author notes | 28 |
| `03_repo_revision_folder/` | Repo's tracked `revision/` folder: NEW_INTRODUCTION.tex, mapping, preview HTML, build scripts, figure | 10 |
| `04_this_session_zips/` | Zips produced this session: repacked complete package + untouched copy of the Audit-3 original | 2 |

## Top-level workspace files

| File | Bytes | MD5 |
|---|---:|---|
| `Audit 2 Joint Code Dimension and k Galois Hull Enumerators for Simple Root Constacyclic Codes over Square Free Affine Algebras.zip` | 656,814 | `e0ce99530ef0d6cdbf4c467df5ee211f` |
| `Audit 3 JOINT_Paper_Source_and_Supplementary_Files.zip` | 1,946,764 | `a7131987735eb40b3f680b1e052682cf` |
| `Audit 3 JOINT_Paper_Source_and_Supplementary_Files_COPY.zip` | 1,946,764 | `a7131987735eb40b3f680b1e052682cf` |
| `FINAL_SUBMISSION_READY.zip` | 2,435,150 | `55480fbaa4bb2d4637e8f082a7679f00` |
| `Galois_Hull_Revision.zip` | 307,596 | `ee1021deb278fb2698bf007789fbec7c` |
| `JOINT_Paper_Package_COMPLETE.zip` | 1,946,764 | `aa1a43b2e32cc3b41d1ed4f3df3eaa64` |
| `Joint Code Dimension and k Galois Hull Enumerators for Simple Root Constacyclic Codes over Square Free Affine Algebras.zip` | 502,209 | `ffc147e460990a833dac45ab41ec9f0c` |
| `README.md` | 23 | `e49215ab24c7bc325104b271d7aac0b2` |

## Tracked in git (16 files)

```
Audit 2 Joint Code Dimension and k Galois Hull Enumerators for Simple Root Constacyclic Codes over Square Free Affine Algebras.zip
Audit 3 JOINT_Paper_Source_and_Supplementary_Files.zip
FINAL_SUBMISSION_READY.zip
Galois_Hull_Revision.zip
Joint Code Dimension and k Galois Hull Enumerators for Simple Root Constacyclic Codes over Square Free Affine Algebras.zip
README.md
revision/.gitignore
revision/FINAL_SUBMISSION.tex
revision/INTRODUCTION_MAPPING.md
revision/Introduction_revised.pdf
revision/NEW_INTRODUCTION.tex
revision/NEW_INTRODUCTION_preview.html
revision/README.md
revision/build_pdf.py
revision/build_preview.py
revision/figure1_workflow.png
```

## `revision/` folder

| File | Bytes | MD5 |
|---|---:|---|
| `revision/.gitignore` | 72 | `4ff3a7c8d0ec979b4a1caf61678780fb` |
| `revision/FINAL_SUBMISSION.tex` | 116,588 | `c2577c2d96a3c2354623cc4b7171c70b` |
| `revision/INTRODUCTION_MAPPING.md` | 7,174 | `d400ad9f0f526773feb674af351a5cff` |
| `revision/Introduction_revised.pdf` | 204,299 | `946ac822bb8f541206d44d080de3695e` |
| `revision/NEW_INTRODUCTION.tex` | 11,465 | `72403465afdbec7846b0c72614751eb2` |
| `revision/NEW_INTRODUCTION_preview.html` | 22,438 | `3b63224d574ffbfd2a9ec57a9dbbb72b` |
| `revision/README.md` | 2,940 | `80a1aaa81004bd687c27fcb22611dcbf` |
| `revision/build_pdf.py` | 16,398 | `344760d30a27c8e666eb4cc03e80ba99` |
| `revision/build_preview.py` | 12,765 | `4c199ead21fd094ecf0f8647508a5c31` |
| `revision/figure1_workflow.png` | 46,794 | `c86320666e41ef0b628e6ef4ecfef859` |

## Checks actually run this session

- `unzip -t` on the Audit-3 zip → **No errors detected in compressed data**
- Audit-3 is a real blob, not an LFS pointer: `git cat-file -s 3a71bb1f` = 1946764 = on-disk size; no `.gitattributes` present
- `python3 run_examples.py --output generated` → exit 0; regenerated 5 joint-CSVs + summary.json
- regenerated CSVs vs shipped `supplementary/data/*.csv` → **5/5 exact MATCH**
- repacked `JOINT_Paper_Package_COMPLETE.zip` vs original zip → `diff -r` **byte-identical content, 0 differences** (34 files, 2,219,225 bytes)
- first repack accidentally included the 9 scratch `generated/` artifacts (43 files); rebuilt with `-x` filters → back to 34

## Known issues (from the package's own README — not fixed here)

1. `manuscript/FINAL_SUBMISSION.pdf` is the **pre-Phase-3 build**; it does not contain the rewritten Introduction. Recompile from `.tex`.
2. The 3 `reports/*.pdf` and `author_notes/Introduction_revised_reading_copy.pdf` refer to the **old citation numbers** `[1]`–`[32]`, which the `.bbl` reorder changed.
3. Corresponding-author email still missing; some 2026 reference metadata and the cited theorem/version of `debnathAffine2026` need checking (`author_notes/SCIENTIFIC_ISSUES_TO_REVIEW.md`).
4. **Unverified:** `hull_check.py` / `checked_hull_check.py` were never executed — they need `galois==0.4.11`, `numpy==2.3.5`, `numba==0.66.0` (not installed).
5. Nothing new was committed to git this session; the two new zips and the scratch folder are untracked.

## Verify this bundle

From inside the unpacked `JOINT_EVERYTHING_2026-10-06/` folder:

```sh
md5sum -c CHECKSUMS.md5      # expected: 46 lines, all "OK"
```

Run and confirmed during packaging: **46/46 OK, 0 failures.**
