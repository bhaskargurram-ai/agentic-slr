# r03 (Chang 2020 / ICI in melanoma) — extraction run report

**Date:** 2026-04-29
**Scope:** Run all 4 locked models against the 23 r03 final-included papers under the v3-locked extraction prompt. No evaluation in this round.
**Result:** ✅ **CLEAN.** 23 papers × 4 models = 92 extractions, **0 errors**, all 11 schema fields populated for every record. Total cost **$0.359**. Recommend **PROCEED to evaluation**.

---

## 1. Pre-flight checks

| # | Check | Result | Detail |
|--:|---|:-:|---|
| 1 | `dedup_decisions.final_included_pmids` length is 23 | PASS | n=23 |
| 2 | `ground_truth.extraction_ground_truth` has 10 entries | PASS | n=10 (9 trials + 1 marker) |
| 3 | `fulltext_pool` covers all 23 final PMIDs | PASS | all 23 present (pool has 118 total) |
| 4 | `extraction_schema.py` shows v3 LOCKED comment | PASS | "PROMPT VERSION: v3 (LOCKED 2026-04-28)" present |
| 5 | Together AI key works | PASS | 1-token chat probe returned content |
| 6 | OpenAI API key works | PASS | 1-token chat probe returned content |

All 6 pass. Proceeded.

## 2. Run summary per model

| Model | n_studies | input tokens | output tokens | wall time (s) | latency min / med / max (s) | errors | cost (USD) |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `gpt-4o-mini` | 23 | 121 443 | 5 975 | 120.1 | 3.34 / 4.11 / 13.14 | **0** | $0.0218 |
| `llama-3.3-70b` | 23 | 136 319 | 11 164 | 270.9 | 3.44 / 10.80 / 22.74 | **0** | $0.1298 |
| `qwen-3-235b` | 23 | 141 794 | 6 606 | 204.2 | 5.61 / 7.65 / 25.29 | **0** | $0.0323 |
| `deepseek-v3` | 23 | 133 555 | 6 807 | 213.0 | 5.47 / 7.82 / 15.80 | **0** | $0.1755 |
| **r03 total** | **92** | **533 111** | **30 552** | — | — | **0** | **$0.3594** |

Schema-completeness check (all 11 evaluation fields non-null/non-empty per record): **23/23 for every model**.

The integer-coercion parser fix held — even though Llama produced 11 164 output tokens (~2× the other models, and historically the model most likely to emit fractional `duration_weeks`), zero validation errors occurred. The fix from the previous task is now silently doing its job.

## 3. Sample comparison — CheckMate 067 / Larkin 2015 (PMID 26027431)

This is the **substituted** GT entry (replaces Chang 2020's PMID 28889792). It's the most informative single-trial comparison because (a) the trial has three arms, (b) we picked a two-arm comparison out of three for the GT, and (c) the prompt rule instructs models to sum all active arms — so prompt and GT diverge here by design.

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `first_author` | `Larkin` | `not_reported` ❌ | `Larkin` ✅ | `Larkin` ✅ | `Larkin` ✅ |
| `year` | `2015` | `2015` ✅ | `2015` ✅ | `2015` ✅ | `2015` ✅ |
| `phase` | `III` | `III` ✅ | `III` ✅ | `III` ✅ | `III` ✅ |
| `n_total` | `945` | `945` ✅ | `945` ✅ | `945` ✅ | `945` ✅ |
| `n_active` | `314` | `630` ⚠ | `630` ⚠ | `630` ⚠ | `630` ⚠ |
| `intervention` | `Nivolumab + Ipilimumab` | `Nivolumab` ❌ | `Nivolumab, Ipilimumab` ≈ | `Nivolumab` ❌ | `Nivolumab, Ipilimumab` ≈ |
| `primary_efficacy_outcome` | `Progression-free survival and overall survival (co-primary)` | `Progression-free survival` ≈ | `Progression-free survival` ≈ | `Progression-free survival and overall survival (co-primary end points)` ✅ | `Progression-free survival and overall survival` ✅ |

**The `n_active=630` finding is significant.** All four models computed 630 = 314 (nivo+ipi combination) + 316 (nivo monotherapy), correctly applying the prompt's rule 3: *"For 'n_active', sum the sample sizes of ALL active treatment arms if the trial has multiple doses or multiple active drugs."* Our GT carries 314 because the task instruction picked the combination-vs-ipilimumab two-arm comparison.

This is the same pattern as Lattanzi/Lagae-dose (paper says 0.7 mg/kg/day, review normalised to 0.8): models follow primary-publication conventions (or in this case the locked prompt rule) while GT follows the systematic-review's framing. Per your earlier note, this is publishable signal — *not* something to fix by re-tuning either the prompt or the GT.

Other sample-comparison takeaways:
- GPT-4o-mini's `first_author = "not_reported"` reproduces the same systematic weakness we saw on r02 (it doesn't pick up author bylines from cleaned fulltext); the v2 PubMed-author-injection step will repair this at evaluation time.
- Two models split intervention into a comma list (`"Nivolumab, Ipilimumab"`) rather than the GT's `"Nivolumab + Ipilimumab"`. The `string_contains_any` comparator should still match (token-overlap fallback catches both drug names), but worth tracking.
- DeepSeek and Qwen 3 give the more complete primary-outcome string, matching the co-primary GT phrasing. GPT and Llama truncate to the leading PFS endpoint.

## 4. Cost & runtime totals

| | Cost (USD) | Wall time |
| --- | ---: | ---: |
| Stage 1 — extract_openai (gpt-4o-mini × 23) | $0.0218 | 2 min 0 s |
| Stage 2 — extract_modal (Llama + Qwen 3 + DeepSeek, each × 23) | $0.3376 | 11 min 30 s |
| **Total this round** | **$0.3594** | **~13.5 min** |

In line with projection ($0.30–0.50, 10–15 min). Per-paper, all-4-models cost: **≈ $0.0156** for r03, slightly cheaper than r02's $0.020 (Qwen 3 spent fewer output tokens on these mostly-abstract-only papers — only 2 of 23 had PMC fulltext, so the input pool is tight).

End-to-end project so far: r01 + r02 + r03 = $0.4213 + $0.2696 + $0.3594 = **$1.05**.

## 5. Error analysis

**No errors to analyse — 0/92 extractions failed.** The closest things to error-class events are:

1. **Prompt-vs-GT divergence on CheckMate 067 `n_active`** (§3 above). Affects all 4 models on this single field × paper cell. Not a code error; not a model error; a methodological choice that will surface as 4× incorrect at evaluation time. Belongs in the paper, not in a fix.
2. **Verbose author commas vs " + " separators** for combination interventions. May or may not be marked wrong by the comparator. Will know after evaluation.

No paper-level extraction failures, no schema-validation rejects, no parser-stage parse_errors.

## 6. Recommendation

**✅ PROCEED to evaluation (Command 17).**

Acceptance criteria fully met:
- n_studies = 23 per model ✅ (criterion: 23)
- errors ≤ 2 per model ✅ (criterion: ≤2; got 0/0/0/0)
- All 11 schema fields populated per extraction ✅ (criterion: all 11; got 23/23 records fully populated for every model)
- All 6 pre-flight checks pass ✅
- Cost and wall time within projection ✅

The CheckMate 067 substitution is producing extractions on PMID 26027431 (the paper we kept) that the existing evaluator will score against the GT entry under the same PMID. The marker entry for PMID 28889792 will be auto-skipped by the `pred is None` patch from the prior round.

## 7. Output files

| File | Status |
| --- | --- |
| `reviews/r03_chang_ici_melanoma/results/extractions_openai.json` | new (23 records, 0 errors) |
| `reviews/r03_chang_ici_melanoma/results/extractions_llama.json` | new (23 records, 0 errors) |
| `reviews/r03_chang_ici_melanoma/results/extractions_qwen.json` | new (23 records, 0 errors) |
| `reviews/r03_chang_ici_melanoma/results/extractions_deepseek.json` | new (23 records, 0 errors) |
| `reviews/r03_chang_ici_melanoma/results/extractions_all_openmodels_summary.json` | new (combined Together AI summary) |
| `reviews/r03_chang_ici_melanoma/EXTRACTION_RUN_REPORT.md` | this file |

Stopping here as instructed.
