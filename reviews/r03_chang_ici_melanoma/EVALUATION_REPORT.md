# r03 (Chang 2020 / ICI in melanoma) — extraction evaluation

**Date:** 2026-04-29
**Scope:** Score the locked 4-model lineup against the 9-trial GT we built for r03 (8 native + 1 substituted CheckMate 067), then place r03 in cross-review context with r01 and r02.
**Result:** ✅ Recommend **PROCEED to r04**. Best model on r03 (DeepSeek V3, 80.8 %) sits 7.5 pp below its r02 score; no model collapsed (>15 pp drop), and the visible drops localise to four well-understood structural weaknesses (multi-arm n_active/n_placebo, ICI dose verbosity, "until-progression" maintenance phrasing, and age-not-reported in adult oncology abstracts).

## Headline

> **r03 v2 (post-processed) accuracy:** GPT-4o-mini **75.8 %**, Llama 3.3 70B **72.7 %**, Qwen 3 235B **78.8 %**, DeepSeek V3 **80.8 %**.
> **r03 raw accuracy:** GPT-4o-mini **66.7 %**, Llama 3.3 70B **64.6 %**, Qwen 3 235B **73.7 %**, DeepSeek V3 **77.8 %**.

n_studies_evaluated = **9** GT entries scored per model. The marker entry for PMID 28889792 (CheckMate 067 OS update) was auto-skipped — no model has an extraction for it because dedup substituted PMID 26027431 — so the denominator is **9 × 11 = 99 cells per model**, not 23 (which would have included the 14 false positives, unscored because they have no GT entry).

## 1. Pipeline / GT alignment

| | count |
| --- | ---: |
| GT trials in r03 GT (`extraction_ground_truth`) | 9 (+ 1 marker for PMID 28889792) |
| GT trials with extractions in all 4 models | **9/9** |
| Marker entries auto-skipped at evaluation | 1 (PMID 28889792 → 26027431) |
| Final-included PMIDs not in GT (false positives) | 14 (correctly unscored — no GT to compare against) |

No evaluator code change was required: the existing `pred is None: continue` patch from the prior task gracefully skipped the marker entry. Denominator confirmed at 99 = 9 × 11 by the raw evaluator's own console output.

## 2. r03 per-field accuracy (v2 post-processed)

| Field | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | ---: | ---: | ---: | ---: |
| `first_author` | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) |
| `year` | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) |
| `phase` | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) |
| `n_total` | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) |
| `n_active` | 5/9 (56 %) | 6/9 (67 %) | 7/9 (78 %) | 7/9 (78 %) |
| `n_placebo` | 3/9 (33 %) | 2/9 (22 %) | 3/9 (33 %) | 6/9 (67 %) |
| `age_range_years` | 4/9 (44 %) | 7/9 (78 %) | 4/9 (44 %) | 6/9 (67 %) |
| `intervention` | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) | 9/9 (100 %) |
| `dose` | 5/9 (56 %) | 2/9 (22 %) | 3/9 (33 %) | 4/9 (44 %) |
| `primary_efficacy_outcome` | 8/9 (89 %) | 8/9 (89 %) | 8/9 (89 %) | 8/9 (89 %) |
| `maintenance_weeks_ge_12` | 5/9 (56 %) | 2/9 (22 %) | 8/9 (89 %) | 4/9 (44 %) |
| **Overall** | **75/99 (75.8 %)** | **72/99 (72.7 %)** | **78/99 (78.8 %)** | **80/99 (80.8 %)** |

`year`, `phase`, `n_total`, `intervention`, and `first_author` (after PubMed-author injection) are all 9/9 across every model. The five fields where r03 takes its hits are:
- `n_active` (56–78 %): driven by multi-arm trials (CheckMate 067 has 3 arms, KEYNOTE-006 has 3 arms, KEYNOTE-002 has 3 arms, Ascierto 2017 is 2-arm dose comparison, CheckMate 238 is adjuvant active-vs-active).
- `n_placebo` (22–67 %): same root cause; "active-control" trials don't have a placebo at all and the schema field is being used as "comparator-arm count".
- `dose` (22–56 %): ICI doses include drug + dose + schedule + arm counts, often as combination strings; verbose.
- `maintenance_weeks_ge_12` (22–89 %): cancer trials use "treatment until progression" wording rather than a labelled maintenance phase or fixed duration; Qwen 3 reads it from total follow-up; Llama and DeepSeek read it more conservatively.
- `age_range_years` (44–78 %): six of nine r03 abstracts don't state the age inclusion criterion explicitly; v3 prompt rule says "if no age eligibility criterion is stated, output 'not_reported'", which is what GPT and Qwen 3 do — *but* GT carries `>=18` because it's the actual trial-protocol value. This is a GT-vs-prompt instruction tension on r03 abstracts specifically.

## 3. Cross-review comparison

### Overall (raw + v2, 3 reviews)

| Model | r01 raw | r01 v2 | r02 raw | r02 v2 | r03 raw | r03 v2 | mean v2 (3 rev) | sd v2 (3 rev) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 74.0 % | 83.1 % | 70.1 % | 79.2 % | 66.7 % | **75.8 %** | 79.4 % | 3.7 % |
| `llama-3.3-70b` | 76.6 % | 83.1 % | 70.1 % | 79.2 % | 64.6 % | **72.7 %** | 78.4 % | 5.2 % |
| `qwen-3-235b` | 84.4 % | 88.3 % | 80.5 % | 87.0 % | 73.7 % | **78.8 %** | 84.7 % | 5.2 % |
| `deepseek-v3` | 77.9 % | 84.4 % | 83.1 % | 88.3 % | 77.8 % | **80.8 %** | **84.5 %** | 3.8 % |

- **DeepSeek V3 leads on the lowest-variance score** (84.5 % mean v2, 3.8 pp sd) — most reliable across domains.
- **Qwen 3 235B leads on the highest mean** (84.7 %) but with double DeepSeek's variance.
- **r03 is uniformly the hardest review for all 4 models.** Every model scores its lowest of the three reviews on r03.
- **No model collapsed.** Largest single-review drop: Qwen 3 from 87.0 % (r02 v2) to 78.8 % (r03 v2) = **−8.2 pp**, well under the >15 pp blocker threshold. Llama drops 6.5 pp; GPT drops 3.4 pp; DeepSeek drops 7.5 pp.

### Per-field across reviews (mean of 4 models, v2)

| Field | r01 v2 mean | r02 v2 mean | r03 v2 mean |
| --- | ---: | ---: | ---: |
| `first_author` | 100 % | 100 % | 100 % |
| `year` | 100 % | 100 % | 100 % |
| `phase` | 53.6 % | 60.7 % | **100 %** |
| `n_total` | 82.1 % | 100 % | 100 % |
| `n_active` | 82.1 % | 92.9 % | **69.4 %** |
| `n_placebo` | 78.6 % | 85.7 % | **38.9 %** |
| `age_range_years` | 64.3 % | 17.9 % | 58.3 % |
| `intervention` | 100 % | 100 % | 100 % |
| `dose` | 85.7 % | 85.7 % | **38.9 %** |
| `primary_efficacy_outcome` | 89.3 % | 96.4 % | 88.9 % |
| `maintenance_weeks_ge_12` | 96.4 % | 78.6 % | **52.8 %** |

**Stable-easy fields (≥ 90 % across all 3 reviews):** `first_author` (after v2 PubMed injection), `year`, `intervention`, `primary_efficacy_outcome`. Universally easy.

**Stable-hard / domain-dependent fields:**
- `phase` was 53–60 % on r01/r02; **jumps to 100 % on r03**. Why: r03's GT phase values are unambiguous (`II` for two trials, `III` for the rest), models read them right; r01 and r02 both had `N/A` / `N/A (investigator-initiated)` / phase-IIIb-style edge cases that the strict-equality v2 comparator handled inconsistently.
- `n_active` and `n_placebo` move oppositely: r03 has the most multi-arm trials (3 of 9 are 3-arm; 1 is 2-arm-no-placebo; 1 is active-vs-active adjuvant), driving a **30 pp drop on n_active and 47 pp drop on n_placebo** vs r02. Both fields are working as designed (the schema explicitly says to sum active arms; the GT pulls a sub-set of arms for the review-level comparison; mismatch is structural).
- `dose` was stable at 85.7 % on r01 and r02; r03 drops to **38.9 %**. ICI doses are simply more verbose ("Ipilimumab 10 mg/kg + dacarbazine 850 mg/m² at weeks 1, 4, 7, 10; then dacarbazine alone every 3 weeks through week 22; ipilimumab/placebo every 12 weeks as maintenance") — models extract a shorter formulation that doesn't contain enough of the GT tokens to satisfy `string_contains_any` even with token-overlap fallback.
- `maintenance_weeks_ge_12` peaked at 96 % on epilepsy (r01, where "maintenance period" is in every paper), 79 % on HF (r02, where most trials have multi-month follow-up), and **53 %** on melanoma (r03, where treatment is "until progression" in many cases — Llama reads that as `False`, Qwen 3 infers `True`).
- `age_range_years` improved from 18 % (r02 disaster) to 58 % (r03) thanks to the v3 prompt revision, but **6 of 9 r03 abstracts genuinely don't state the age criterion explicitly**. GPT and Qwen 3 (both honest readers) write `not_reported` and miss; Llama and DeepSeek (more inferential) write `>=18` and match GT.

## 4. r03 disagreement analysis (10 most informative cases)

| # | Field | Trial (PMID) | n right / 4 | GT | Right models | Wrong models |
| --: | --- | --- | :-: | --- | --- | --- |
| 1 | `n_active` | **CheckMate 067 (26027431)** | **0/4** | `314` | — | all four → `630` (314 combo + 316 nivo monotherapy, summed per prompt rule 3) |
| 2 | `age_range_years` | CheckMate 066 (25399552) | 2/4 | `>=18` | llama, deepseek | gpt → `not_reported`; qwen → `not_reported` |
| 3 | `age_range_years` | KEYNOTE-006 (25891173) | 2/4 | `>=18` | llama, deepseek | gpt → `not_reported`; qwen → `not_reported` |
| 4 | `dose` | CheckMate 066 (25399552) | 2/4 | full GT string with comparator detail | gpt, deepseek (`3 mg/kg every 2 weeks`) | llama, qwen (verbose `"3 mg per kilogram of body weight every 2 weeks"`) |
| 5 | `dose` | CheckMate 067 (26027431) | 2/4 | full multi-arm dosing string | gpt, qwen | llama, deepseek (slightly different multi-arm phrasings) |
| 6 | `first_author` | CheckMate 066 (25399552) | 2/4 | `Robert` | qwen, deepseek | gpt → `not_reported`; llama → `not_reported` |
| 7 | `first_author` | KEYNOTE-006 (25891173) | 2/4 | `Robert` | qwen, deepseek | gpt → `not_reported`; llama → `not_reported` |
| 8 | `first_author` | CheckMate 238 (28891423) | 2/4 | `Weber` | qwen, deepseek | gpt → `not_reported`; llama → `not_reported` |
| 9 | `maintenance_weeks_ge_12` | KEYNOTE-002 (28961465) | 2/4 | `True` | gpt, qwen | llama → `False`; deepseek → `False` |
| 10 | `maintenance_weeks_ge_12` | CheckMate 067 (26027431) | 2/4 | `True` | qwen, deepseek | gpt → `False`; llama → `False` |
| 11 | `n_active` | CheckMate 238 (28891423) | 2/4 | `453` | qwen, deepseek | gpt, llama → `906` (used n_total) |

All four task-specific cells the user asked us to verify:

| Cell | Result |
| --- | --- |
| **CheckMate 067 `n_active`** | All 4 models → `630` (314+316). GT = `314`. **0/4 correct, as predicted.** Models followed prompt rule 3 ("sum all active arms") on a 3-arm trial; GT carries the two-arm CheckMate-067 framing the task brief specified. |
| **CheckMate 238 `age_range_years`** | All 4 models → `>=15`. GT = `>=15`. **4/4 correct.** The unusually-low-bound age was preserved by every model. v3 prompt's lower-bound rule is doing real work here. |
| **KEYNOTE-002 `phase`** | All 4 models → `II`. GT = `II`. **4/4 correct.** |
| **CheckMate 069 `phase`** | All 4 models → `II`. GT = `II`. **4/4 correct.** |

Three of four cells the user flagged as risk areas turned out to be 4/4. The one that didn't (CheckMate 067 n_active) is exactly the prompt-vs-GT divergence the prior extraction-run report already documented — not new information; just confirmed.

## 5. Concerns / surface check

**(a) `maintenance_weeks_ge_12` continues to weaken across domains.** 96 % → 79 % → 53 %. The schema field is increasingly mismatched to the domain language. Llama and DeepSeek default to `False` for "treatment until progression" wording. Not a fix-now item — the prompt is locked, and this is the expected behaviour the v3 lock-comment was anticipating ("a new failure mode … document it as a finding in the paper rather than patching the prompt"). Will continue to track on r04 and r05.

**(b) `dose` field collapse on r03 (38.9 %) is a comparator artifact, not a model failure.** Inspection of the r03 dose disagreements (rows 4–5 above) shows models produce semantically-correct dose strings; they just don't share enough surface tokens with the GT's verbose multi-arm dose string to clear the `string_contains_any` threshold. If you want to recover this without touching the prompt, the right move is to *split* the dose comparator: extract the index drug's dose ("3 mg/kg every 2 weeks") from each side and require token overlap on that subset only. Out of scope for this report; flagging for the post-r05 evaluator-tuning stage.

**(c) `n_active` / `n_placebo` floor on r03 is a known structural mismatch.** r03 has the most multi-arm trials (5 of 9 are not 1:1 with placebo). Models follow the prompt; GT follows the systematic-review framing. Same Lattanzi-Lagae-dose pattern, three reviews running. Belongs in the paper's results section as a finding.

**(d) `age_range_years` partial recovery.** The v3 prompt revision lifted r02 from 18 % to 58 % on r03. The remaining gap is *honest* — six of nine r03 abstracts don't state the age criterion, and GPT/Qwen 3 correctly emit `not_reported` per the prompt. Llama and DeepSeek emit `>=18` (matching GT) — the *less faithful* readers are getting credit on this field, which is worth noting in the paper but isn't fixable from the prompt side without telling the model to assume `>=18` (which would harm CheckMate 238 where the answer is `>=15`).

**(e) GPT-4o-mini multi-arm sample-size confusion persists on r03.** Row 11 above (CheckMate 238: GPT writes `906` when GT = `453`) reproduces the same r02 weakness (DAPA-CKD subanalysis). Three reviews now showing this pattern.

**(f) GT integrity check.** Spot inspection of all 9 r03 GT entries against the matched extractions: the 11-field values are internally consistent. The two highest-impact disagreements (n_active on CheckMate 067 and dose on CheckMate 067) are *not* GT errors — they're the documented prompt-vs-GT-framing tensions described in §6 of the GT-construction report.

## 6. Cost & runtime

| Stage | Cost | Wall time |
| --- | ---: | ---: |
| r03 evaluate_v1 (raw) | $0 | < 5 s |
| r03 evaluate (v2) | $0 | < 5 s |
| **Total** | **$0** | **< 10 s** |

Pure-Python evaluation; no LLM calls.

## 7. Recommendation: ✅ PROCEED to r04 (Bahji ketamine/depression)

Acceptance criteria all met:

- All 4 models scored. Best v2 = **80.8 %** (DeepSeek), worst = **72.7 %** (Llama). Floor is 50+ pp above any "model collapsed" threshold.
- Largest single-model r02 → r03 v2 drop is **−8.2 pp** (Qwen 3, 87.0 → 78.8). Well under the > 15 pp blocker condition.
- All 9 GT entries scored, marker auto-skipped, denominator clean at 99.
- Five new findings cleanly attributable to the r03 oncology domain rather than to migration / pipeline / model-quality regressions.

Suggested before r04, in priority order:
1. **Build r04 extraction GT once retrieval/screening/dedup completes.** r04 is the largest review (24 trials per the protocol notes); GT construction will be more work than r03's.
2. **Optional eval-layer follow-ups (post-r05):** split-dose comparator, `n_active`-as-comparator-aware comparator, `maintenance_weeks_ge_12` sentinel for "until progression" trials. None of these are blockers; all of them belong to the paper's "limitations of the evaluation comparator" section.

## 8. Output files

| File | Contents |
| --- | --- |
| `reviews/r03_chang_ici_melanoma/results/extraction_evaluation.json` | r03 raw scores |
| `reviews/r03_chang_ici_melanoma/results/extraction_evaluation_v2.json` | r03 v2 scores |
| `reviews/r03_chang_ici_melanoma/EVALUATION_REPORT.md` | this report |
