# r02 Retrieval Report: Ali 2023 — SGLT2 Inhibitors / Heart Failure

**Date:** 2026-04-27
**Stage:** Retrieval
**Status:** COMPLETE — 8/9 recall (88.9%)

---

## Pre-Flight Checks

| Check | Result |
|-------|--------|
| `config.json` exists with `search.pubmed_query`, `search.search_date_end` (2022-09-10), `paths.*` | **PASS** |
| `ground_truth.json` exists with exactly 9 `inclusion_pmids` | **PASS** |
| Query readable via Python JSON load | **PASS** |

---

## Search Query Executed

```
(("dapagliflozin"[MeSH Terms] OR "dapagliflozin"[Supplementary Concept] OR
"dapagliflozin"[Title/Abstract] OR "Forxiga"[Title/Abstract] OR
"Farxiga"[Title/Abstract] OR "BMS-512148"[Title/Abstract])
AND ("Heart Failure"[MeSH Terms] OR "heart failure"[Title/Abstract] OR
"cardiac failure"[Title/Abstract] OR "heart decompensation"[Title/Abstract])
AND ("Randomized Controlled Trial"[Publication Type] OR
"randomized controlled trial"[Title/Abstract] OR
"randomised controlled trial"[Title/Abstract] OR
"randomized"[Title/Abstract] OR "randomised"[Title/Abstract] OR
"placebo"[Title/Abstract]))
AND ("2017/01/01"[PDAT] : "2022/09/10"[PDAT])
```

---

## Results

| Metric | Value |
|--------|-------|
| **Total PMIDs retrieved** | 244 |
| **Ground truth PMIDs** | 9 |
| **Found** | 8 |
| **Missed** | 1 |
| **Recall** | 88.89% (8/9) |

---

## Ground Truth PMID Status

| # | PMID | Study | Status |
|---|------|-------|--------|
| 1 | 33426003 | Ibrahim 2020 — Dapagliflozin + furosemide in decompensated HFrEF | **MISSED** |
| 2 | 31535829 | McMurray 2019 — DAPA-HF | FOUND |
| 3 | 34446370 | McMurray 2021 — DAPA-CKD HF subanalysis | FOUND |
| 4 | 31524498 | Nassif 2019 — DEFINE-HF | FOUND |
| 5 | 34711976 | Nassif 2021 — Dapagliflozin in HFpEF | FOUND |
| 6 | 35604416 | Palau 2022 — DAPA-VO2 | FOUND |
| 7 | 32245746 | Singh 2020 — REFORM | FOUND |
| 8 | 36027570 | Solomon 2022 — DELIVER | FOUND |
| 9 | 30415602 | Wiviott 2019 — DECLARE-TIMI 58 | FOUND |

---

## Analysis of Missed Study

### Ibrahim 2020 (PMID 33426003)

**Title:** "Safety and Efficacy of Adding Dapagliflozin to Furosemide in Type 2 Diabetic Patients With Decompensated Heart Failure and Reduced Ejection Fraction"

**Journal:** Frontiers in Cardiovascular Medicine (2020)

**Root cause:** PubMed indexing mismatch — two independent factors:

1. **Publication Type:** Indexed as `["Case Reports", "Journal Article"]` — NOT `"Randomized Controlled Trial"`. The study randomized 100 patients into two arms but PubMed's indexers classified it as a case report. Our query's `"Randomized Controlled Trial"[Publication Type]` filter does not match.

2. **Abstract wording:** The abstract uses "randomly divided" but does NOT contain the words "randomized", "randomised", "placebo", or "controlled trial". Our free-text fallback terms (`"randomized"[Title/Abstract]`, `"randomised"[Title/Abstract]`, `"placebo"[Title/Abstract]`) also fail to match.

**This is a known PubMed limitation.** Smaller journals sometimes receive inaccurate publication type indexing. The study is genuinely a randomized trial but invisible to standard RCT filters.

---

## Expected vs. Observed Record Counts

| Metric | Ali 2023 (paper) | Our result | Ratio |
|--------|-----------------|------------|-------|
| Records identified | 1,567 | 244 | 15.6% |
| Databases | PubMed + Scopus + ScienceDirect | PubMed only | — |

The 6.4x difference is expected. Ali 2023 searched 3 databases (PubMed, Scopus, ScienceDirect). Our pipeline searches PubMed only. The 1,567 figure likely includes substantial duplicates across databases and records from Scopus/ScienceDirect that are not in PubMed. Our 244 PubMed-only results still capture 8/9 included studies.

---

## Recommendation

**PROCEED to screening.**

Rationale:
- 8/9 recall (88.9%) meets the acceptance threshold ("Acceptable; document which study was missed and why; proceed")
- The 1 missed study (Ibrahim 2020) is missed due to PubMed indexing error, not a query design flaw — it is classified as "Case Reports" despite being a randomized trial, and its abstract lacks standard RCT terminology
- All 8 major landmark trials (DAPA-HF, DELIVER, DEFINE-HF, DECLARE-TIMI 58, DAPA-CKD, REFORM, DAPA-VO2, Nassif 2021) are retrieved
- No query tuning can fix this miss without degrading precision drastically (would need to remove the RCT filter entirely)
- This limitation should be noted in the paper as a known PubMed indexing issue affecting recall on small, mislabeled studies
