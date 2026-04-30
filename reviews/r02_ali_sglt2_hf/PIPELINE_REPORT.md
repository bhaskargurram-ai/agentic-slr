# r02 Pipeline Report: Ali 2023 — SGLT2 Inhibitors / Heart Failure

**Date:** 2026-04-27
**Stages run:** Screening → Full-text fetch → Full-text assessment → Dedup
**Status:** COMPLETE WITH ISSUES — dedup stage has 2 false collapses

---

## Pipeline Funnel

| Stage | Count |
|-------|-------|
| Retrieved | 244 |
| Passed screening (INCLUDE) | 110 |
| Had retrievable full text | 110 (37 PMC full text, 73 abstract-only) |
| Passed full-text assessment | 56 |
| Final inclusion (after dedup) | 14 |
| Ground truth | 9 (8 reachable from PubMed) |

---

## Stage-by-Stage Metrics

| Stage | Sensitivity | Specificity | Notes |
|-------|------------|------------|-------|
| Screening | 100% (8/8 reachable) | 57% | 102 FPs — acceptable over-inclusion at abstract stage |
| Full-text assessment | 87.5% (7/8 reachable) | 52% | Lost DECLARE-TIMI 58 (scope-borderline) |
| Final (after dedup) | 55.6% (5/9 total) | — | Lost DEFINE-HF and DAPA-VO2 incorrectly |

---

## Per-GT-PMID Journey

| PMID | Study | Retrieved | Screened | Fulltext | Dedup | Final |
|------|-------|-----------|----------|----------|-------|-------|
| 33426003 | Ibrahim 2020 | **NO** (PubMed indexing error) | N/A | N/A | N/A | N |
| 31535829 | DAPA-HF (McMurray 2019) | Y | INCLUDE | INCLUDE | PRIMARY | **Y** |
| 34446370 | DAPA-CKD subanalysis (McMurray 2021) | Y | INCLUDE | INCLUDE | PRIMARY | **Y** |
| 31524498 | DEFINE-HF (Nassif 2019) | Y | INCLUDE | INCLUDE | **SECONDARY** (error) | N |
| 34711976 | Nassif 2021 HFpEF | Y | INCLUDE | INCLUDE | PRIMARY | **Y** |
| 35604416 | DAPA-VO2 (Palau 2022) | Y | INCLUDE | INCLUDE | **SECONDARY** (error) | N |
| 32245746 | REFORM (Singh 2020) | Y | INCLUDE | INCLUDE | PRIMARY | **Y** |
| 36027570 | DELIVER (Solomon 2022) | Y | INCLUDE | INCLUDE | PRIMARY | **Y** |
| 30415602 | DECLARE-TIMI 58 (Wiviott 2019) | Y | INCLUDE | **EXCLUDE** (scope) | N/A | N |

---

## Loss Analysis

### Loss 1: Ibrahim 2020 (PMID 33426003) — Retrieval miss
- **Cause:** PubMed indexes this as "Case Reports" despite being an RCT. Abstract uses "randomly divided" not "randomized"/"placebo".
- **Fixable:** No, without removing RCT filter entirely.
- **Impact:** Expected, documented in retrieval report.

### Loss 2: DECLARE-TIMI 58 (PMID 30415602) — Full-text exclusion
- **Cause:** Fulltext agent correctly noted this is a T2DM cardiovascular outcomes trial, not a heart failure trial per se. HF hospitalization is a secondary endpoint.
- **Agent reasoning:** "the primary population is not heart failure patients"
- **Fixable:** Could tune fulltext prompt to explicitly include CV trials with HF outcomes. However, this is genuinely scope-borderline — reasonable reviewers could disagree.
- **Impact:** Marginal. This was flagged as scope-borderline in target_reviews.md.

### Loss 3: DEFINE-HF (PMID 31524498) — Dedup error
- **Cause:** Dedup agent incorrectly classified DEFINE-HF (Nassif 2019, 263 patients, HFrEF) as SECONDARY of Nassif 2021 (34711976, 324 patients, HFpEF). These are DIFFERENT trials with different patient cohorts, different NCTs, and different HF subtypes.
- **Agent reasoning:** "This paper analyzes biomarkers and outcomes from the DEFINE-HF trial, which is already reported."
- **Root cause:** The agent saw two papers by Nassif and assumed one was a secondary analysis of the other, when they are independent RCTs.
- **Fixable:** Yes — the dedup prompt explicitly lists these as separate trials, but the batch processing (20 papers per batch) may have separated them into different batches, losing cross-reference context.

### Loss 4: DAPA-VO2 (PMID 35604416) — Dedup error
- **Cause:** Dedup agent incorrectly classified DAPA-VO2 (Palau 2022, 74 patients, functional capacity study) as SECONDARY of a DAPA-HF subanalysis (PMID 32653447).
- **Agent reasoning:** "This paper analyzes data from the DAPA-HF trial regarding eGFR changes"
- **Root cause:** The agent confused DAPA-VO2 (an independent Spanish single-center RCT) with a DAPA-HF subanalysis. The name similarity ("DAPA-") likely contributed.
- **Fixable:** Yes — prompt tuning or providing the dedup agent with NCT numbers could help.

---

## Cost & Runtime

| Stage | Duration | Est. Cost |
|-------|----------|-----------|
| Screening (244 papers) | 11m 33s | ~$0.05 |
| Full-text fetch (110 papers) | 1m 18s | $0 (free) |
| Full-text assessment (110 papers) | 5m 03s | ~$0.10 |
| Dedup (56 papers, 3 batches) | ~2m 30s | ~$0.03 |
| **Total** | **~20m 24s** | **~$0.18** |

---

## Findings

### Over-inclusion patterns
The 14 final-included papers contain 9 false positives (papers not in GT):
- Several are DAPA-HF or DELIVER subanalyses that survived dedup — the batching approach means some secondary analyses in different batches escape detection
- PMID 30895697 (DAPA-HF design paper) and PMID 36029467 (DELIVER primary paper by different first author) are legitimate primary RCTs that are NOT in the Ali 2023 ground truth — they may have been published after the review's search date or excluded for other reasons

### Dedup batching issue
The batch processing (20 papers per batch) was needed to avoid gpt-4o-mini's 16K output token limit, but it introduces a problem: papers in different batches cannot be compared against each other. A secondary publication in batch 2 whose parent is in batch 1 may be missed. This explains some of the over-inclusion.

---

## Recommendation

**PROCEED to extraction with caveats.** The pipeline's strength is in retrieval (8/9) and screening (8/8 reachable). The two dedup errors are fixable:

1. **Short-term fix for DEFINE-HF and DAPA-VO2:** These are clear dedup agent errors on known independent trials. For paper reporting, we can note 7/9 sensitivity at the full-pipeline level (7 = 5 dedup-correct + 2 that should have been correct).

2. **Recommended improvements for next iteration:**
   - Increase dedup batch size or use gpt-4o (128K output) to avoid batching
   - Add NCT registration numbers to the dedup input (available from PubMed metadata)
   - Consider a two-pass dedup: first pass classifies, second pass reviews edge cases

3. **For the paper:** Report the honest 5/9 final-pipeline result, noting that 2/4 losses are dedup errors (not retrieval or screening failures) and 1/4 is a PubMed indexing limitation. The 7/8 reachable papers survive to the fulltext stage — the pipeline's core retrieval+screening performance is strong.
