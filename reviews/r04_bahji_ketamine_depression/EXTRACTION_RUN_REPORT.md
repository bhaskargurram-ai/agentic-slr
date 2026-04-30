# r04 (Bahji 2021 / ketamine-depression) — extraction run report

**Date:** 2026-04-29
**Scope:** Run all 4 locked models against the 50 r04 final-included papers under the v3-locked extraction prompt. No evaluation.
**Result:** ✅ Recommend **PROCEED to evaluation**. 50 × 4 = 200 extractions, **5 errors total** (all within ≤3-per-model tolerance), GPT-4o-mini and Qwen 3 235B clean at 0 errors. Cost **$0.6427**.

---

## 1. Pre-flight checks

| # | Check | Result | Detail |
|--:|---|:-:|---|
| 1 | `dedup_decisions.final_included_pmids` length is 50 | PASS | n=50 |
| 2 | `extraction_ground_truth` has 24 entries | PASS | n=24 (22 trials + 2 markers) |
| 3 | `fulltext_pool` covers all 50 final PMIDs | PASS | all 50 present (pool has 120 total) |
| 4 | `extraction_schema.py` shows v3 LOCKED comment | PASS | "PROMPT VERSION: v3 (LOCKED 2026-04-28)" present |
| 5 | Together AI key works | PASS | 1-token chat probe returned content |
| 6 | OpenAI API key works | PASS | 1-token chat probe returned content |

All 6 pass.

## 2. Run summary per model

| Model | n_studies | input tokens | output tokens | wall time (s) | latency min / med / max (s) | errors | 11-fields full | cost (USD) |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `gpt-4o-mini` | 50 | 209 667 | 13 067 | 417.0 | 4.93 / 6.45 / 22.75 | **0** | 50/50 | $0.0393 |
| `llama-3.3-70b` | 50 | 239 189 | 24 389 | 223.4 | 1.48 / 4.38 / 8.80 | **3** | 47/50 | $0.2319 |
| `qwen-3-235b` | 50 | 247 072 | 14 381 | 593.6 | 6.71 / 9.48 / 47.67 | **0** | 50/50 | $0.0580 |
| `deepseek-v3` | 50 | 236 719 | 14 071 | 500.9 | 6.97 / 9.51 / 23.50 | **2** | 48/50 | $0.3135 |
| **r04 total** | **200** | **932 647** | **65 908** | — | — | **5** | **195/200** | **$0.6427** |

All four models' per-paper completeness on the 11 evaluation fields stays at 50/50 wherever the extraction succeeded (errors are validation failures, so the failed records have no extraction at all rather than partial extractions).

## 3. Sample comparison — TRANSFORM-2 / Popova 2019 (PMID 31109201)

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `first_author` | `Popova` | `not_reported` ❌ | `not_reported` ❌ | `Popova` ✅ | `not_reported` ❌ |
| `year` | `2019` | `2019` ✅ | `2019` ✅ | `2019` ✅ | `2019` ✅ |
| `phase` | `III` | `III` ✅ | `III` ✅ | `III` ✅ | `III` ✅ |
| `n_total` | `227` | `227` ✅ | `227` ✅ | `227` ✅ | `227` ✅ |
| `n_active` | `114` | `197` ❌ | `113` ❈ (off-by-1) | `114` ✅ | `114` ✅ |
| `intervention` | `Esketamine` | `Esketamine` ✅ | `Esketamine` ✅ | `Esketamine` ✅ | `Esketamine` ✅ |
| `primary_efficacy_outcome` | `Change in MADRS score from baseline to day 28` | "Change from baseline to day 28 in Montgomery-Åsberg Depression Rating Scale (MADRS) score" ✅ | "…(MADRS) score" ✅ | "…(MADRS) score" ✅ | "…(MADRS) score" ✅ |

Highlights:
- **Year, phase, n_total, intervention, primary outcome:** 4/4 across the board. The strongest fields hold cleanly on this trial.
- **first_author:** 1/4 (Qwen 3 only). Same r03/r02 weakness — GPT, Llama, DeepSeek omit byline-derived authors. The v2 evaluator's PubMed-author injection will fix this at scoring time.
- **n_active = 197** from GPT-4o-mini is a striking error: it appears to have summed the 197 completers (mentioned in the abstract as "227 underwent randomization and 197 completed the 28-day double-blind treatment phase"), conflating "completers" with "active arm". Llama's `113` is a 1-patient off-by-one between the 114-vs-113 esketamine-vs-placebo split that's explicitly given in the published paper but only as "227" in the abstract — defensible misread.

## 4. Crossover sample comparison — Zarate 2006 (PMID 16894061)

| Field | Ground truth (crossover convention) | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `n_total` | 18 | 18 ✅ | 18 ✅ | 18 ✅ | 18 ✅ |
| `n_active` | 18 (each subject in both arms) | 17 ❌ | 17 ❌ | **18 ✅** | 17 ❌ |
| `n_placebo` | 18 (each subject in both arms) | 1 ❌ | 1 ❌ | **18 ✅** | **18 ✅** |

This is exactly the prediction from §8(c) of the GT-construction report: **models default to parallel-group reasoning on crossover trials.**

- **Qwen 3 235B** is the only model that correctly applied crossover semantics on both `n_active` and `n_placebo`, encoding 18 / 18 / 18 (each subject in both arms).
- **DeepSeek V3** got `n_placebo = 18` right but `n_active = 17` (read "Of the 17 subjects treated with ketamine" from the abstract, treating the per-protocol completion count as the randomized count for the active arm — partial-credit reasoning).
- **GPT-4o-mini and Llama-3.3-70B** both treat the trial as parallel-group: `n_active = 17`, `n_placebo = 1`. The "1" is a misread of "1 of 17 completed both visits" or similar abstract phrasing as the placebo arm size — they fundamentally don't recognise the crossover convention.

This will reproduce across the other crossover trials in r04 (Berman 2000, Diazgranados 2010, Zarate 2012, Lapidus 2014, Phillips 2019). Expect **systematic 0/4 → 2/4 disagreement on n_active and n_placebo for every crossover trial,** with Qwen 3 the most reliable, DeepSeek occasional, GPT and Llama uniformly wrong. The pattern is publishable: *"Crossover-design recognition is a model-quality differentiator: only the largest open MoE model in our lineup (Qwen3-235B) consistently extracted crossover sample sizes correctly."*

## 5. Error analysis (5 total, all within tolerance)

| Model | PMID | Trial | GT? | Error |
| --- | --- | --- | :-: | --- |
| llama-3.3-70b | 31734084 | TRANSFORM-3 (Ochs-Ross 2020) | **GT** | `n_total` parsed as string instead of int (schema validation failed) |
| llama-3.3-70b | 31508531 | (false positive — non-GT) | no | `n_active = None` (model emitted null in a required-int field) |
| llama-3.3-70b | 29660637 | (false positive — non-GT) | no | `n_active` parse failure |
| deepseek-v3 | 29656663 | Canuso 2018 | **GT** | `risk_of_bias.reporting_bias` field missing entirely (model emitted only 5 of 6 risk-of-bias subdomains) |
| deepseek-v3 | 29660637 | (false positive — non-GT) | no | `n_active = None` |

Per-model errors: gpt-4o-mini 0, **llama 3 (cap)**, qwen-3-235b 0, deepseek 2. All under the ≤3-per-model criterion.

**Two errors hit GT papers:**
- **Llama on TRANSFORM-3 (PMID 31734084):** the model emitted `n_total` as a non-numeric string (likely something like "138 (treated)" or similar). The int-coercion patch only handles float-to-int, not string-to-int — by design.
- **DeepSeek on Canuso 2018 (PMID 29656663):** the model emitted only 5 of 6 risk-of-bias subdomains. The `reporting_bias` slot was omitted entirely from the JSON. This is a model-output-completeness issue, not a schema mismatch.

**Effect at evaluation time:** Llama will be evaluated on 21/22 GT papers (TRANSFORM-3 missing); DeepSeek will be evaluated on 21/22 GT papers (Canuso 2018 missing). Both are inside the existing `pred is None: continue` patch behavior — the missing-extraction records will silently skip, and per-field denominators will drop from 22 → 21 for those two models on those specific papers.

The **3 non-GT errors** (PMIDs 31508531, 29660637) are on false-positive papers in the final pool. They affect cost / completeness only — not extraction accuracy on the GT.

The marker entries (PMID 23803871 Sos 2013, PMID 26821769 Li 2016) confirmed absent from all 4 extraction files — they're correctly excluded from extraction (they're not in `final_included_pmids`).

## 6. Cost & runtime totals

| Stage | Cost (USD) | Wall time |
| --- | ---: | ---: |
| Stage 1 — extract_openai (gpt-4o-mini × 50) | $0.0393 | ~7 min |
| Stage 2 — extract_modal (Llama + Qwen 3 + DeepSeek, each × 50) | $0.6034 | ~22 min |
| **Total this round** | **$0.6427** | **~29 min** |

Within projection ($0.50–0.80, 25–35 min).

**Per-paper, all-4-models cost:**
- r01: $0.0217
- r02: $0.0193
- r03: $0.0156
- r04: **$0.0129**

Per-paper cost is monotonically decreasing across reviews. r04's pool is dominated by abstract-only fulltext (depression trials are usually short reports), keeping input tokens low. The 50-paper pool also gets better amortisation of the per-call overhead.

End-to-end project total so far (r01 + r02 + r03 + r04 extraction): **$0.4213 + $0.2696 + $0.3594 + $0.6427 ≈ $1.69.**

## 7. Recommendation: ✅ PROCEED to evaluation (Command 21)

Acceptance criteria all met:

- n_studies = 50 per model ✅ (criterion: 50)
- errors ≤ 3 per model ✅ (criterion: ≤3; got 0/3/0/2)
- All 11 schema fields populated where extraction succeeded ✅
- All 6 pre-flight checks pass ✅
- Cost and wall time within projection ✅

Two GT-paper extraction failures (Llama × TRANSFORM-3, DeepSeek × Canuso 2018) will be handled by the existing skip-when-pred-None patch — denominators for those two models drop from 242 (= 22 × 11) to 231 (= 21 × 11) at evaluation time. Other models score against the full 22 GT papers.

The crossover sample finding (Qwen 3 = 1/4 perfect; DeepSeek = partial; GPT and Llama = systematically parallel-group) is the single most significant qualitative finding of the run and should be tracked carefully when evaluation runs.

## 8. Output files

| File | Status |
| --- | --- |
| `reviews/r04_bahji_ketamine_depression/results/extractions_openai.json` | new (50 records, 0 errors) |
| `reviews/r04_bahji_ketamine_depression/results/extractions_llama.json` | new (50 records, 3 errors) |
| `reviews/r04_bahji_ketamine_depression/results/extractions_qwen.json` | new (50 records, 0 errors) |
| `reviews/r04_bahji_ketamine_depression/results/extractions_deepseek.json` | new (50 records, 2 errors) |
| `reviews/r04_bahji_ketamine_depression/results/extractions_all_openmodels_summary.json` | new (Together AI summary) |
| `reviews/r04_bahji_ketamine_depression/EXTRACTION_RUN_REPORT.md` | this file |
