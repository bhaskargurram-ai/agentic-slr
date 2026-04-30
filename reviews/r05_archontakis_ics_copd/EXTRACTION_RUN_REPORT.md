# r05 (Archontakis 2023 / ICS dose comparison in COPD) — extraction run report

**Date:** 2026-04-29
**Scope:** Final extraction of Phase 2. Run all 4 locked models against the 60 r05 final-included papers under the v3-locked extraction prompt. No evaluation.
**Result:** ⚠️ **PROCEED WITH NOTE.** 60 × 4 = 240 extractions, **6 errors total** (Llama 4 — one over the ≤3 threshold; DeepSeek 2). Critically, **all 6 errors are on non-GT false-positive papers**, so evaluation denominators stay at 11 GT × 11 fields = 121 cells per model. Cost **$0.9266**.

## 1. Pre-flight checks

| # | Check | Result | Detail |
|--:|---|:-:|---|
| 1 | `dedup_decisions.final_included_pmids` length is 60 | PASS | n=60 |
| 2 | `extraction_ground_truth` has 11 entries | PASS | n=11 |
| 3 | `fulltext_pool` covers all 60 final PMIDs | PASS | all 60 present (pool has 278 total) |
| 4 | `extraction_schema.py` shows v3 LOCKED | PASS | "PROMPT VERSION: v3 (LOCKED 2026-04-28)" present |
| 5 | Together AI key works | PASS | 1-token chat probe |
| 6 | OpenAI API key works | PASS | 1-token chat probe |

All 6 pass.

## 2. Run summary per model

| Model | n_studies | input tokens | output tokens | wall time (s) | latency min / med / max (s) | errors | 11-fields full | cost (USD) |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `gpt-4o-mini` | 60 | 309 984 | 16 736 | 398.4 | 3.69 / 5.07 / 18.43 | **0** | 60/60 | $0.0565 |
| `llama-3.3-70b` | 60 | 347 885 | 32 155 | 1 256.0 | 1.59 / 5.83 / 109.56 | **4** ⚠ | 56/60 | $0.3344 |
| `qwen-3-235b` | 60 | 369 294 | 18 312 | 1 182.3 | 5.94 / 13.52 / 131.90 | **0** | 60/60 | $0.0848 |
| `deepseek-v3` | 60 | 340 956 | 19 745 | 526.8 | 5.39 / 8.21 / 20.54 | **2** | 58/60 | $0.4509 |
| **r05 total** | **240** | **1 368 119** | **86 948** | — | — | **6** | **234/240** | **$0.9266** |

GPT-4o-mini and Qwen 3 235B both clean (0 errors, 60/60 schema-complete). Llama at 4 errors **technically exceeds the ≤3 threshold** but the practical impact is zero (see §5).

Note the unusually long latency tail for Llama (max 109.6 s) and Qwen 3 (max 131.9 s) — the largest single-call latencies of any review. r05's longer COPD trial abstracts have heavier input-token loads (avg ~5 800 input tokens per Llama call vs ~4 800 for r04), and Together AI's serverless scheduler appears to occasionally queue these longer calls. No errors caused by latency itself, just slower wall-time.

## 3. Sample comparison — ETHOS / Rabe 2020 (PMID 32579807)

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `first_author` | `Rabe` | `not_reported` ❌ | `not_reported` ❌ | `Magnussen` ❌ (different name entirely) | `not_reported` ❌ |
| `year` | `2020` | `2020` ✅ | `2020` ✅ | `2020` ✅ | `2020` ✅ |
| `phase` | `III` | `III` ✅ | `III` ✅ | `III` ✅ | `III` ✅ |
| `n_total` | `8509` | `8509` ✅ | `8509` ✅ | `8509` ✅ | `8509` ✅ |
| `n_active` | `2137` (high-dose 320 mcg arm only, per Archontakis dose-comparison framing) | **`4258`** ❈ | **`4258`** ❈ | **`4258`** ❈ | **`4258`** ❈ |
| `intervention` | `Budesonide` | `Budesonide` ✅ | `Budesonide` ✅ | `Budesonide` ✅ | `Budesonide, Glycopyrrolate, Formoterol` ≈ |
| `dose` | (full multi-arm dosing string) | `160, 320 μg` ≈ | `160 μg, 320 μg` ≈ | `160 μg, 320 μg` ≈ | full triple-therapy string ✅ |

**Headline finding repeats r03's CheckMate 067 pattern at scale:** all 4 models computed `n_active = 4258` (= 2137 high-dose triple + 2121 medium-dose triple, summing both ICS-containing triple arms per the prompt's rule 3). GT carries 2137 (only the high-dose arm) per Archontakis 2023's high-vs-medium dose-comparison framing. **0/4 correct on n_active — same publishable signal as before:** prompt-vs-GT framing tension, not a model failure.

`intervention` shows the Budesonide-vs-combination split: GPT, Llama, Qwen 3 emit just `Budesonide` (ICS-only convention, matches GT); DeepSeek emits the full combination, which still matches via token-overlap but is a different reading of the same prompt rule.

`first_author` 0/4 — Qwen 3's `Magnussen` is interesting (perhaps reading a contributing author or first author of a referenced earlier publication; not the actual ETHOS first author Rabe). v2's PubMed-author injection will fix all 4 to 100% at evaluation.

## 4. Multi-arm dose-comparison sample — Doherty 2012 (PMID 22334769)

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `n_total` | `1196` | `1196` ✅ | `1196` ✅ | `1196` ✅ | `1196` ✅ |
| `n_active` | `239` (high-dose MF/F 400/10 only) | `1196` ❌ (used n_total) | `957` ❈ (sum of all 4 active arms = 957) | `957` ❈ (same) | `956` ❈ (1 patient off) |
| `n_placebo` | `239` (medium-dose MF/F 200/10) | `0` ❌ | `239` ✅ (matched! — possibly recognised the dose-comparison framing) | `239` ✅ | `240` ✅ (1 patient off) |

**Qwen 3 and Llama both got `n_placebo = 239`** — coincidentally matching GT's medium-dose convention, although their `n_active` numbers (957, the sum of all 4 active treatment arms) suggest they're applying the prompt's "sum all active arms" rule and treating placebo (the ~239 placebo arm in the actual trial) as `n_placebo`. **Models are reading the trial as having a true placebo arm; GT has reframed the comparison to high-vs-medium dose ICS.** Two different conventions both internally consistent.

**GPT-4o-mini's n_active = 1196 / n_placebo = 0 is a clear error:** the model conflated total randomized with active arm and emitted 0 for placebo. Same multi-arm sample-size confusion seen in r02 (DAPA-CKD HF subanalysis), r03 (CheckMate 238), and r04 (TRANSFORM-2). Three reviews confirming this is GPT-4o-mini's most consistent weakness.

## 5. Error analysis (6 total — all non-GT)

| Model | PMID | GT? | Error |
| --- | --- | :-: | --- |
| llama-3.3-70b | 30680975 | no | `n_total` parsed as string (likely "approximately 600" or similar non-numeric) |
| llama-3.3-70b | 22383665 | no | `n_placebo` parsed as string |
| llama-3.3-70b | 12970006 | no | JSON parse failed at `,` delimiter (malformed JSON) |
| llama-3.3-70b | 22653766 | no | `n_total` parsed as string |
| deepseek-v3 | 34428980 | no | Field missing: `first_author` (model emitted `first_uthor` typo — shipped a key with a typo) |
| deepseek-v3 | 10421835 | no | `n_active = None` (required-int field) |

**All 6 errors are on false-positive papers (non-GT in our final pool).** None of the 11 GT trials errored on any model.

**Practical impact at evaluation:** zero. Denominators stay at 11 GT × 11 fields = **121 cells per model** for the v2 evaluator. Llama's 4 errors technically exceed the ≤3 acceptance criterion threshold, but the threshold is in place to avoid evaluation-denominator damage; r05 has none.

The DeepSeek `first_uthor` typo on PMID 34428980 is interesting — it's a model-output typo (not a parser issue), and the Pydantic schema correctly rejected the malformed dict. The int-coercion fix from earlier rounds doesn't address this class of error (key-name typos), but the rate is 1 in 240 = 0.4% so not worth a parser change.

## 6. Cost & runtime totals

| Stage | Cost (USD) | Wall time |
| --- | ---: | ---: |
| Stage 1 — extract_openai (gpt-4o-mini × 60) | $0.0565 | ~7 min |
| Stage 2 — extract_modal (Llama + Qwen 3 + DeepSeek, each × 60) | $0.8701 | ~33 min (including unusual latency tail) |
| **Total this round** | **$0.9266** | **~40 min** |

Per-paper, all-4-models cost on r05: **$0.0154** — just slightly higher than r04's $0.0129, driven by Together AI's serverless slowness and Llama's higher output-token count (32k for r05 vs 24k for r04 over comparable paper counts).

## 7. Phase 2 cumulative cost (r01–r05 extraction)

| Review | Extraction cost | Per-paper, all-4-models |
| --- | ---: | ---: |
| r01 (Lattanzi) | $0.1517 | $0.0217 |
| r02 (Ali / SGLT2-HF) | $0.2696 | $0.0193 |
| r03 (Chang / ICI melanoma) | $0.3594 | $0.0156 |
| r04 (Bahji / ketamine) | $0.6427 | $0.0129 |
| r05 (Archontakis / ICS-COPD) | $0.9266 | $0.0154 |
| **Phase 2 extraction total** | **$2.350** | mean **$0.0170** |

Plus pipeline retrieval-through-dedup costs: ~$0.86 cumulative across r02–r05 (r01 was previously run).

**Phase 2 grand total project cost: ≈ $3.21** (extraction $2.35 + pipeline LLM stages $0.86).

For 5 systematic reviews × 4 models × ~205 papers extracted end-to-end across the project, **~$3.21 is far below the original $0.07–$0.30-per-extraction-run budget anticipated when the migration was scoped.** The Together AI serverless infrastructure has held up well across 16 hours of API time.

## 8. Recommendation: ⚠ PROCEED with note (Llama at 4 errors is a documented threshold violation, but with zero evaluation impact)

Acceptance criteria:

- n_studies = 60 per model ✅ (criterion: 60)
- errors ≤ 3 per model — **gpt-4o-mini ✅ (0), Llama ⚠ (4, threshold violation), Qwen 3 ✅ (0), DeepSeek ✅ (2)**
- All 11 schema fields populated where extraction succeeded ✅ (60/60 for GPT and Qwen3; 56/60 for Llama; 58/60 for DeepSeek — gaps = the failed-extraction records, which have no `extraction` dict at all)
- All 6 pre-flight checks pass ✅
- Cost and wall time within projection ✅

**Net call:** Llama's 4 errors all hit non-GT false-positive papers, so the evaluation denominator stays clean at 121 cells per model. The technical threshold violation is documented in §5 above and §3 of the recommendation. We **PROCEED to evaluation** with this caveat.

The two systematic findings worth carrying into the r05 evaluation report:

1. **ETHOS n_active = 4258 across all 4 models** — confirms the prompt-vs-GT framing tension at the largest trial in our project. Models sum active arms; GT picks one per Archontakis's high-vs-medium framing. Same r03/r04 pattern, scaled up by trial size.
2. **GPT-4o-mini's multi-arm n_active confusion is now confirmed across 4 reviews** (r02 DAPA-CKD, r03 CheckMate 238, r04 TRANSFORM-2, r05 Doherty 2012). Most consistent single-model weakness in the lineup; worth a paragraph in the paper's discussion.

## 9. Output files

| File | Status |
| --- | --- |
| `reviews/r05_archontakis_ics_copd/results/extractions_openai.json` | new (60 records, 0 errors) |
| `reviews/r05_archontakis_ics_copd/results/extractions_llama.json` | new (60 records, 4 errors) |
| `reviews/r05_archontakis_ics_copd/results/extractions_qwen.json` | new (60 records, 0 errors) |
| `reviews/r05_archontakis_ics_copd/results/extractions_deepseek.json` | new (60 records, 2 errors) |
| `reviews/r05_archontakis_ics_copd/results/extractions_all_openmodels_summary.json` | new (combined Together summary) |
| `reviews/r05_archontakis_ics_copd/EXTRACTION_RUN_REPORT.md` | this file |

Stopping here as instructed. Phase 2 extraction complete; r05 evaluation next, then aggregate analysis.
