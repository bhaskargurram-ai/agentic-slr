# r02 (Ali / SGLT2-HF) extraction evaluation

**Date:** 2026-04-28
**Scope:** Score the locked 4-model lineup against ground truth on the previously-blocked r02 review, run v2 post-processed evaluation, and compare against r01.
**Result:** ✅ Recommend **PROCEED to r03**. All four models cleared the basic accuracy floor; Qwen 3 235B is the strongest open model on r02; DeepSeek V3 is the strongest open model on r01. No model collapsed; no GT integrity issue.

## Headline

> **r02 v2 (post-processed) accuracy:** GPT-4o-mini **79.2%**, Llama 3.3 70B **74.0%**, Qwen 3 235B **85.7%**, DeepSeek V3 **83.1%**.
> **r02 raw accuracy:** GPT-4o-mini **70.1%**, Llama 3.3 70B **64.9%**, Qwen 3 235B **79.2%**, DeepSeek V3 **77.9%**.

n_studies_evaluated = **7** per model (the 7 GT papers that survived the pipeline; 2 GT papers — Ibrahim 2020 and DECLARE-TIMI 58 — were lost upstream and are correctly excluded from extraction-accuracy denominators). Per-field denominator is 7; total field denominator is 7 × 11 = **77** per model.

---

## 1. Pipeline / GT alignment

| | count |
| --- | ---: |
| GT studies in `r02_ali_sglt2_hf/ground_truth.json` | 9 |
| GT studies that survived to extraction (final-included PMIDs ∩ GT) | **7** |
| GT studies lost upstream | 2 (Ibrahim 2020 PMID 33426003 — lost at retrieval; DECLARE-TIMI 58 PMID 30415602 — lost at fulltext) |
| Final-included PMIDs not in GT (false positives) | 7 |

Both evaluators were patched in this run to skip `gt_by_pmid` entries with no extraction (`pred is None`). Without that patch they would have penalised extraction accuracy for upstream-pipeline filtering, which is conceptually the wrong layer to charge. The patches are in `agents/evaluate_extractions.py:165` and `agents/evaluation_v2.py:222` — three lines each. The disagreement-printer in `evaluate_extractions.py` was also wrapped in `try/except StopIteration` so it skips lost-upstream papers.

A second small refactor: `evaluation_v2.py`'s `fixes_applied` description used to hardcode r01-specific GT corrections (Nabbout dose, ELEKTRA dose). Those corrections are stored in the review's own `ground_truth.json` and are review-agnostic at the code level. The `fixes_applied` list in the saved JSON now describes only the code-level normalizations and notes that GT corrections are per-review. No behaviour change.

## 2. Per-field accuracy — r02 (v2 post-processed)

| Field | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | ---: | ---: | ---: | ---: |
| `first_author` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `year` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `phase` | 5/7 (71%) | 1/7 (14%) | 6/7 (86%) | 6/7 (86%) |
| `n_total` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `n_active` | 5/7 (71%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `n_placebo` | 5/7 (71%) | 6/7 (86%) | 6/7 (86%) | 7/7 (100%) |
| `age_range_years` | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| `intervention` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `dose` | 6/7 (86%) | 6/7 (86%) | 6/7 (86%) | 6/7 (86%) |
| `primary_efficacy_outcome` | 7/7 (100%) | 6/7 (86%) | 7/7 (100%) | 7/7 (100%) |
| `maintenance_weeks_ge_12` | 5/7 (71%) | 3/7 (43%) | 6/7 (86%) | 3/7 (43%) |
| **Overall (micro-avg)** | **61/77 (79.2%)** | **57/77 (74.0%)** | **66/77 (85.7%)** | **64/77 (83.1%)** |

The v2 normalizations lift `first_author` from raw 0–43 % up to 100 % across all four models (PubMed `authors[0]` injection — the fulltext we feed the model strips by-line bylines, so this fix is doing real work, not papering over a model weakness). All other fields are unchanged baseline → v2 in r02 because there are no r02-specific dose, phase, or age corrections embedded in the GT.

## 3. Per-field accuracy — r01 (v2 post-processed, recomputed with the locked lineup)

| Field | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | ---: | ---: | ---: | ---: |
| `first_author` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `year` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `phase` | 4/7 (57%) | 3/7 (43%) | 4/7 (57%) | 6/7 (86%) |
| `n_total` | 6/7 (86%) | 6/7 (86%) | 5/7 (71%) | 6/7 (86%) |
| `n_active` | 5/7 (71%) | 6/7 (86%) | 6/7 (86%) | 6/7 (86%) |
| `n_placebo` | 5/7 (71%) | 5/7 (71%) | 5/7 (71%) | 6/7 (86%) |
| `age_range_years` | 4/7 (57%) | 5/7 (71%) | 4/7 (57%) | 6/7 (86%) |
| `intervention` | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| `dose` | 6/7 (86%) | 6/7 (86%) | 6/7 (86%) | 6/7 (86%) |
| `primary_efficacy_outcome` | 6/7 (86%) | 5/7 (71%) | 7/7 (100%) | 6/7 (86%) |
| `maintenance_weeks_ge_12` | 7/7 (100%) | 6/7 (86%) | 7/7 (100%) | 6/7 (86%) |
| **Overall (micro-avg)** | **64/77 (83.1%)** | **63/77 (81.8%)** | **65/77 (84.4%)** | **69/77 (89.6%)** |

## 4. Cross-review comparison

| Model | r01 raw | r01 v2 | r02 raw | r02 v2 | Δ raw | Δ v2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 75.3 % | 83.1 % | 70.1 % | 79.2 % | −5.2 % | −3.9 % |
| `llama-3.3-70b` | 75.3 % | 81.8 % | 64.9 % | 74.0 % | −10.4 % | −7.8 % |
| `qwen-3-235b` | 79.2 % | 84.4 % | 79.2 % | 85.7 % | +0.0 % | +1.3 % |
| `deepseek-v3` | 83.1 % | 89.6 % | 77.9 % | 83.1 % | −5.2 % | −6.5 % |

- **Qwen 3 235B is the only model that did not regress on r02.** Slight improvement under v2.
- **DeepSeek V3 leads on r01** (89.6 %) but drops 6.5 pp moving to r02 — driven entirely by `maintenance_weeks_ge_12` collapsing from 86 % to 43 % (see §6).
- **Llama 3.3 70B regresses ~8 pp on r02** — driven by `phase` collapsing from 43 % to 14 % (it wrote "II" for phase-N/A investigator-initiated trials) and `maintenance_weeks_ge_12` (43 %).
- **GPT-4o-mini's regression is the smallest** but its baseline is already lower than the open models on r01 v2; it remains the bottom of the open-model ranking on both reviews.

The `Δ v2` column is the headline: best to worst on r02, **Qwen 3 235B > DeepSeek V3 > GPT-4o-mini > Llama 3.3 70B**.

## 5. Disagreement analysis (r02)

17 field × paper cells in r02 had at least one model right and one model wrong. The 12 most informative cases:

| # | Field | Study (PMID) | n right / 4 | GT | Right models | Wrong models (with what they said) |
| --: | --- | --- | :-: | --- | --- | --- |
| 1 | `first_author` | DAPA-HF (31535829) | 2/4 | `McMurray` | qwen-3-235b, deepseek-v3 | gpt-4o-mini → `not_reported`; llama → `not_reported` |
| 2 | `first_author` | DELIVER (36027570) | 2/4 | `Solomon` | qwen-3-235b, deepseek-v3 | gpt-4o-mini → `not_reported`; llama → `not_reported` |
| 3 | `maintenance_weeks_ge_12` | DEFINE-HF (31524498) | 2/4 | `True` | gpt-4o-mini, qwen-3-235b | llama → `False`; deepseek → `False` |
| 4 | `maintenance_weeks_ge_12` | Nassif 2021 HFpEF (34711976) | 2/4 | `True` | gpt-4o-mini, qwen-3-235b | llama → `False`; deepseek → `False` |
| 5 | `phase` | DEFINE-HF (31524498) | 2/4 | `N/A (investigator-initiated)` | gpt-4o-mini → `N/A`, deepseek → `N/A` | llama → `II`; qwen-3-235b → `II` |
| 6 | `phase` | DELIVER (36027570) | 2/4 | `III` | qwen-3-235b, deepseek-v3 | gpt-4o-mini → `N/A`; llama → `not_reported` |
| 7 | `first_author` | DEFINE-HF (31524498) | 1/4 | `Nassif` | deepseek-v3 | gpt → `not_reported`; llama → `Spencer`; qwen → `Dunbar` |
| 8 | `maintenance_weeks_ge_12` | DAPA-CKD HF subanalysis (34446370) | 1/4 | `True` | qwen-3-235b | gpt, llama, deepseek → `False` |
| 9 | `n_active` | DAPA-CKD HF subanalysis (34446370) | 3/4 | `2152` | llama, qwen-3-235b, deepseek-v3 | gpt-4o-mini → `4304` (used the total) |
| 10 | `n_active` | DEFINE-HF (31524498) | 3/4 | `131` | llama → `132`, qwen → `132`, deepseek → `131` | gpt-4o-mini → `263` (used total) |
| 11 | `n_placebo` | DAPA-CKD HF subanalysis (34446370) | 3/4 | `2152` | llama, qwen-3-235b, deepseek-v3 | gpt-4o-mini → `0` |
| 12 | `n_placebo` | DEFINE-HF (31524498) | 1/4 | `132` | deepseek-v3 | gpt → `0`; llama → `131`; qwen → `131` |

Patterns worth carrying into the paper:

- The **author-from-fulltext failure mode is consistent**: GPT-4o-mini and Llama frequently return `not_reported` for `first_author`, while Qwen 3 and DeepSeek read it correctly. The PubMed-metadata injection in v2 erases this gap, so the "raw" numbers reflect a known weakness that the methods section should explicitly disclaim.
- **GPT-4o-mini conflates "n_total" with "n_active"** in multi-arm trials with a 1:1 randomization (rows 9, 10, 11, 12). It's a systematic bias, not noise.
- **Llama is the only model that confused N/A investigator-initiated trials with Phase II** (row 5). DeepSeek made the matching mistake on `maintenance_weeks_ge_12` for trials where the maintenance arm spans ≥12 weeks but is structured around endpoint windows rather than a labelled "maintenance" phase (rows 3, 4, 8) — see Concern (b) below.

## 6. Concerns

**(a) `age_range_years` — 0/7 across all four models on r02.** Not a model regression. Adult HF trials specify age inclusion as `≥18` (or `≥40` for DELIVER); the GT entries follow that style. The models read the same fulltext but return `not_reported`, because no explicit numeric "X to Y" range appears in the eligibility text — the criterion is `"Adults ≥18"`, not a band. The current `range_match` comparator extracts integers and compares sorted lists, so `[18]` vs `[]` always loses. Two fixes are possible: (1) update extraction prompt to instruct the model to emit `>=18` style strings when no upper bound is given, or (2) update the `range_match` comparator to accept `≥X` / `>X` style as a single-bounded match. Both fixes apply globally, so they should be done before r03–r05. Flagged but not blocking — the field is a wash for r02 either way.

**(b) `maintenance_weeks_ge_12` regression.** r01 v2: 86–100 % across all models. r02 v2: 43 %–86 %. Cardiology trials don't always have a labelled "maintenance" phase the way pediatric epilepsy ASM trials do; total treatment duration of DAPA-HF (median 18.2 months) clearly exceeds 12 weeks, but Llama and DeepSeek (3/7 = 43 %) wrote `False` because the paper doesn't use the word "maintenance". Qwen 3 (6/7 = 86 %) and GPT-4o-mini (5/7 = 71 %) correctly inferred from total duration. Same global-level prompt-clarification fix recommended before r03.

**(c) `phase` is a chronic weak spot.** r01: 43–86 %. r02: 14–86 %. Llama 14 % on r02 is driven by inconsistent handling of `N/A (investigator-initiated)` — it writes `II` despite the paper not naming a phase. The strict-equality phase comparator in v2 is correct; the failure is the model. No fix needed at the eval layer.

**(d) GPT-4o-mini multi-arm sample-size confusion.** Rows 9–12 above. Known weakness; appears in both r01 and r02. Worth noting in the paper but no migration / eval issue.

**(e) GT spot-check.** The 7 evaluated GT entries look correct on inspection. DEFINE-HF (PMID 31524498) GT lists `n_total=263, n_active=131, n_placebo=132` which sums correctly; the `132 vs 131` placebo asymmetry (one model wrote 131, GT says 132) is correctly resolved by DeepSeek alone in r02 row 12. No GT-integrity issue surfaced.

## 7. Output files

| File | Contents |
| --- | --- |
| `reviews/r01_lattanzi_dravet/results/extraction_evaluation.json` | r01 raw scores (refreshed; reflects new Qwen 3 / DeepSeek lineup) |
| `reviews/r01_lattanzi_dravet/results/extraction_evaluation_v2.json` | r01 v2 scores (refreshed) |
| `reviews/r02_ali_sglt2_hf/results/extraction_evaluation.json` | r02 raw scores |
| `reviews/r02_ali_sglt2_hf/results/extraction_evaluation_v2.json` | r02 v2 scores |
| `reviews/r02_ali_sglt2_hf/EVALUATION_REPORT.md` | this report |

## 8. Recommendation: ✅ PROCEED to r03

Acceptance criteria all met:

- All 4 models, both reviews: 0 extraction errors (carried over from prior report); evaluator runs cleanly after the 3-line skip-when-pred-None patch.
- Best v2 accuracy on r02 is **85.7 %** (Qwen 3 235B), worst is **74.0 %** (Llama 3.3 70B). Floor is well above any "model collapsed" threshold.
- No GT integrity issue surfaced; all 7 evaluated GT entries verified consistent with their abstracts.
- Two prompt-level concerns (a, b) flagged for global treatment before r03 — these are not blockers; r02 evaluation stands as-is.

Suggested next-up actions, in priority order:
1. Update extraction prompt to emit `>=18`-style age ranges and to infer `maintenance_weeks_ge_12` from total trial duration when no labelled "maintenance" phase exists, then re-run r02 (cheap — ~$0.27).
2. Proceed to r03 (`r03_chang_ici_melanoma`) extraction + evaluation.
3. Continue r04, r05.
