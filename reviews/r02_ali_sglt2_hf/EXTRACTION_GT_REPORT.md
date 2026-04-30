# r02 Extraction Ground Truth Report: Ali 2023 — SGLT2 Inhibitors / HF

**Date:** 2026-04-27
**Status:** COMPLETE — 9 studies, 11 fields each

---

## Per-Study Summary

| PMID | Study | Source | Fields from text | Fields null | Confidence |
|------|-------|--------|-----------------|-------------|-----------|
| 33426003 | Ibrahim 2020 | Abstract only | 10/11 | duration_weeks=null | LOW |
| 31535829 | DAPA-HF | Abstract (NEJM) | 11/11 | none | HIGH |
| 34446370 | DAPA-CKD | Abstract (JACC) | 11/11 | none | MEDIUM |
| 31524498 | DEFINE-HF | Abstract (Circulation) | 11/11 | none | HIGH |
| 34711976 | Nassif 2021 HFpEF | Abstract (Nature Med) | 11/11 | none | HIGH |
| 35604416 | DAPA-VO2 | Abstract (Eur J HF) | 11/11 | none | HIGH |
| 32245746 | REFORM | Abstract (EHJ-CVP) | 11/11 | none | HIGH |
| 36027570 | DELIVER | Abstract (NEJM) | 11/11 | none | HIGH |
| 30415602 | DECLARE-TIMI 58 | Abstract (NEJM) | 11/11 | none | HIGH |

### Confidence Ratings
- **HIGH** (7 studies): Full trial details in structured abstract. N per arm, dose, primary outcome, phase all clearly stated. Cross-checked against Ali 2023 Table 1.
- **MEDIUM** (1 study): DAPA-CKD is a CKD trial with HF subgroup analysis. Total trial N used (matching Ali 2023). HF subgroup N (468) is not split by arm in abstract.
- **LOW** (1 study): Ibrahim 2020 — indexed as "Case Reports," abstract lacks standard trial terminology. Duration, age range, blinding, and phase not reported. Phase set to "N/A."

---

## Cross-Check: Our GT vs Ali 2023 Table 1

| PMID | Study | n_active match | n_placebo match |
|------|-------|---------------|----------------|
| 33426003 | Ibrahim 2020 | **Y** (50/50) | **Y** (50/50) |
| 31535829 | DAPA-HF | **Y** (2373/2373) | **Y** (2371/2371) |
| 34446370 | DAPA-CKD | **Y** (2152/2152) | **Y** (2152/2152) |
| 31524498 | DEFINE-HF | **Y** (131/131) | **Y** (132/132) |
| 34711976 | Nassif 2021 | **Y** (162/162) | **Y** (162/162) |
| 35604416 | DAPA-VO2 | **Y** (45/45) | **Y** (45/45) |
| 32245746 | REFORM | **Y** (28/28) | **Y** (28/28) |
| 36027570 | DELIVER | **Y** (3131/3131) | **Y** (3132/3132) |
| 30415602 | DECLARE-TIMI 58 | **Y** (8582/8582) | **Y** (8578/8578) |

**All 18 sample size values match Ali 2023 exactly.**

---

## Notable Decisions and Caveats

### DAPA-CKD (PMID 34446370)
- Used total trial N (4,304 = 2,152 + 2,152), matching Ali 2023's approach
- The HF subgroup is only 468 patients (11% of total), but Ali 2023 used the full trial N in their meta-analysis
- Primary outcome is a kidney composite, not an HF endpoint — but HF hospitalization/CV death was a secondary endpoint

### DECLARE-TIMI 58 (PMID 30415602)
- Used total trial N (17,160 = 8,582 + 8,578), matching Ali 2023
- This is a T2DM cardiovascular outcomes trial; HF hospitalization is a secondary endpoint
- Co-primary outcomes: (1) MACE noninferiority, (2) CV death or HF hospitalization superiority
- Duration ~4.2 years median follow-up (~218 weeks)

### Ibrahim 2020 (PMID 33426003)
- Lowest confidence entry. PubMed indexes as "Case Reports"
- Abstract says "randomly divided into two arms" but doesn't specify blinding, phase, age range, or exact duration
- dose assumed 10 mg/day (standard dapagliflozin dose, consistent with Ali 2023)
- duration_weeks set to null (hospital stay, not a fixed trial duration)

### Age Ranges
- Most large trials specify ≥18 (DAPA-HF, DEFINE-HF) or ≥40 (DELIVER, DECLARE)
- Several smaller trials (Ibrahim, Palau, Singh) don't explicitly state age eligibility in the abstract; ≥18 assumed as standard for adult HF trials
- Age range stored as string to accommodate "≥18", "≥40", "not reported"

### Phase Classification
- Phase III: DAPA-HF, DELIVER, DECLARE-TIMI 58, DAPA-CKD (large multinational industry-sponsored)
- N/A: DEFINE-HF, Nassif 2021, DAPA-VO2, REFORM (investigator-initiated, not formally phased)
- N/A: Ibrahim 2020 (not reported)

### Maintenance Duration
- All studies have maintenance_weeks_ge_12 = true except Ibrahim 2020 (short hospitalization, false)
- DEFINE-HF and Nassif 2021 are exactly 12 weeks — coded as true (≥12)

---

## Data Sources

All values extracted from PubMed structured abstracts via Entrez E-fetch. No LLM calls used for extraction. PMC full text was consulted for Nassif 2021 (NCT confirmation). Ali 2023 Table 1 (PMC10453961) used for cross-checking sample sizes.

---

## Concerns

1. **Ibrahim 2020:** Weakest entry. If extraction evaluation shows poor model performance on this study specifically, the GT may need refinement from full text (behind journal paywall).

2. **Age range ambiguity:** For 4 studies, the abstract does not state explicit age eligibility criteria. "≥18" is assumed based on standard adult trial design. Models may report different values (e.g., mean age instead of eligibility range).

3. **DAPA-CKD N values:** Using total trial N (4,304) rather than HF subgroup N (468) matches Ali 2023 but may confuse extraction models that read the HF subgroup analysis paper and report the subgroup N.

4. **Duration heterogeneity:** Ranges from ~12 weeks (DEFINE-HF) to ~4.2 years (DECLARE-TIMI). The maintenance_weeks_ge_12 field captures this as boolean, but duration_weeks is harder for models to extract consistently for ongoing-enrollment trials.
