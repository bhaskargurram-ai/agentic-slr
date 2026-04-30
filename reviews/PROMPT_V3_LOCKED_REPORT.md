# Extraction prompt v3 — locked, with mixed results across r01/r02

**Date:** 2026-04-28
**Scope:** Apply two targeted clarifications to `extraction_schema.SYSTEM_PROMPT` (age range, maintenance duration), lock the prompt, and re-evaluate r01 + r02.
**Result:** ⚠️ **MIXED.** v3 succeeds on its target review (r02) but causes side-effect regressions on r01. Overall v2 accuracy: r02 improves for all 4 models (+0.0 / +4.8 / +2.6 / +5.2 pp); r01 is flat-to-down for 3 of 4 models, including a **−5.2 pp drop on DeepSeek V3** driven by non-target fields (`phase`, `age_range_years`). One extraction error introduced (Llama on DAPA-HF). Per task instruction "REPORT BLOCKER if regression detected", flagging for your decision before r03.

---

## 1. Prompt diff (verbatim)

The two modified rules sit in `agents/extraction_schema.py:39` (`SYSTEM_PROMPT`). All other rules (1–4, 7) are byte-for-byte unchanged.

### Rule 5 — `age_range_years`

```diff
-5. For 'age_range_years', use the inclusion criterion range (e.g., '2-18' for ages 2 to 18 years).
+5. For age_range_years:
+   - If the paper reports an explicit range (e.g., "ages 2 to 18 years"), output as "2-18" or "2 to 18".
+   - If the paper reports only a lower bound (e.g., "adults aged 18 years or older", "patients ≥18 years", "men and women aged 40 or above"), output as ">=18" or ">=40" — preserve the lower-bound number with ">=" prefix.
+   - If the paper reports only an upper bound (e.g., "children up to 12 years"), output as "<=12".
+   - If the paper reports both lower and upper bounds, output as "X-Y".
+   - If no age eligibility criterion is stated, output "not_reported".
```

### Rule 6 — `maintenance_weeks_ge_12`

```diff
-6. For 'maintenance_weeks_ge_12', return true ONLY if the paper explicitly states a maintenance phase of at least 12 weeks. Titration periods do not count.
+6. For maintenance_weeks_ge_12 (boolean):
+   - This field asks whether the trial's TREATMENT DURATION (or active follow-up duration) is at least 12 weeks total.
+   - The paper does not need to use the word "maintenance" for this to be True. Look for any of: total trial duration, treatment duration, follow-up period, study duration, observation period, or median follow-up.
+   - True = treatment or follow-up duration is at least 12 weeks (i.e., ≥84 days, ≥3 months).
+   - False = treatment or follow-up duration is less than 12 weeks (e.g., 4-week studies, single-dose studies, hospitalization-only studies of <3 months).
+   - If no duration information is stated, output False with a note in your reasoning.
```

### Lock statement

A new comment block was inserted **immediately above** `SYSTEM_PROMPT = """..."""`:

```python
# PROMPT VERSION: v3 (LOCKED 2026-04-28)
# This prompt was developed during r01 (Lattanzi/Dravet) and revised once
# after r02 (Ali/SGLT2-HF) to clarify two fields (age_range_years,
# maintenance_weeks_ge_12). It is FROZEN for r03/r04/r05, which serve
# as held-out validation.
# DO NOT MODIFY THIS PROMPT. If a new failure mode is identified on r03/r04/r05,
# document it as a finding in the paper rather than patching the prompt.
```

The schema (`StudyExtraction`, `RiskOfBias`), `USER_PROMPT_TEMPLATE`, evaluators, and ground truth are untouched.

## 2. Archive paths (pre-v3 snapshots preserved)

| Pre-v3 snapshot | Files |
| --- | --- |
| `reviews/_archive_pre_prompt_v3/r01_lattanzi_dravet/extractions/` | `extractions_{openai,llama,qwen,deepseek,all_openmodels_summary}.json` |
| `reviews/_archive_pre_prompt_v3/r01_lattanzi_dravet/results/` | `extraction_evaluation.json`, `extraction_evaluation_v2.json` |
| `reviews/_archive_pre_prompt_v3/r02_ali_sglt2_hf/extractions/` | same 5 |
| `reviews/_archive_pre_prompt_v3/r02_ali_sglt2_hf/results/` | same 2 |

Earlier-layer archives (`reviews/_modal_archive/`, `reviews/_archive_pre_qwen3_migration/`, `reviews/_archive_pre_deepseek_migration/` if it had been created) are untouched.

## 3. Extraction re-run integrity

| Review | Model | n | Errors | All 11 fields populated |
| --- | --- | ---: | ---: | --- |
| r01 | gpt-4o-mini | 7 | 0 | yes |
| r01 | llama-3.3-70b | 7 | 0 | yes |
| r01 | qwen-3-235b | 7 | 0 | yes |
| r01 | deepseek-v3 | 7 | 0 | yes |
| r02 | gpt-4o-mini | 14 | 0 | yes |
| r02 | llama-3.3-70b | 14 | **1** | 13/14 |
| r02 | qwen-3-235b | 14 | 0 | yes |
| r02 | deepseek-v3 | 14 | 0 | yes |

**One new failure introduced by v3.** Llama on r02 / DAPA-HF (PMID 31535829) emitted `duration_weeks` as a fractional float (parsed `"median follow-up of 18.2 months" → 79.1 weeks`) which fails the strict-int Pydantic schema. The retry-once path produced the same float deterministically (`temperature=0`). Direct cause: the new "median follow-up" wording in rule 6. The paper-extraction-evaluation denominator for Llama on r02 therefore drops from 7×11=77 to 6×11=66 cells.

## 4. r01 — per-field accuracy (v2 post-processed)

Bold = target field. **NB regressions in this section are non-target side-effects.**

| Field | Model | r01 v2 (pre-v3) | r01 v2 (v3) | Δ |
| --- | --- | ---: | ---: | ---: |
| **`age_range_years`** | gpt-4o-mini | 57% | 57% | +0.0 |
| **`age_range_years`** | llama-3.3-70b | 71% | 71% | +0.0 |
| **`age_range_years`** | qwen-3-235b | 57% | 71% | **+14.3** |
| **`age_range_years`** | deepseek-v3 | 86% | 57% | **−28.6 ⚠** |
| **`maintenance_weeks_ge_12`** | gpt-4o-mini | 100% | 100% | +0.0 |
| **`maintenance_weeks_ge_12`** | llama-3.3-70b | 86% | 100% | **+14.3** |
| **`maintenance_weeks_ge_12`** | qwen-3-235b | 100% | 100% | +0.0 |
| **`maintenance_weeks_ge_12`** | deepseek-v3 | 86% | 86% | +0.0 |
| `phase` (non-target) | llama-3.3-70b | 43% | 29% | **−14.3 ⚠** |
| `phase` (non-target) | deepseek-v3 | 86% | 57% | **−28.6 ⚠** |
| `phase` (non-target) | qwen-3-235b | 57% | 71% | +14.3 |
| `n_placebo` (non-target) | qwen-3-235b | 71% | 86% | +14.3 |
| `primary_efficacy_outcome` (non-target) | llama-3.3-70b | 71% | 86% | +14.3 |

Other fields (`first_author`, `year`, `n_total`, `n_active`, `intervention`, `dose`) — exactly 0.0 pp delta on every model.

### r01 overall

| Model | r01 raw (pre-v3) | r01 raw (v3) | Δ raw | r01 v2 (pre-v3) | r01 v2 (v3) | Δ v2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-mini | 75.3% | 74.0% | −1.3 | 83.1% | 83.1% | +0.0 |
| llama-3.3-70b | 75.3% | 76.6% | +1.3 | 81.8% | 83.1% | +1.3 |
| qwen-3-235b | 79.2% | 84.4% | **+5.2** | 84.4% | 88.3% | **+3.9** |
| deepseek-v3 | 83.1% | 77.9% | **−5.2 ⚠** | 89.6% | 84.4% | **−5.2 ⚠** |

## 5. r02 — per-field accuracy (v2 post-processed)

| Field | Model | r02 v2 (pre-v3) | r02 v2 (v3) | Δ |
| --- | --- | ---: | ---: | ---: |
| **`age_range_years`** | gpt-4o-mini | 0% | 0% | +0.0 |
| **`age_range_years`** | llama-3.3-70b | 0% | **50%** | **+50.0 ✅** |
| **`age_range_years`** | qwen-3-235b | 0% | 14% | **+14.3 ✅** |
| **`age_range_years`** | deepseek-v3 | 0% | 14% | **+14.3 ✅** |
| **`maintenance_weeks_ge_12`** | gpt-4o-mini | 71% | 71% | +0.0 |
| **`maintenance_weeks_ge_12`** | llama-3.3-70b | 43% | 67% | **+23.8 ✅** |
| **`maintenance_weeks_ge_12`** | qwen-3-235b | 86% | **100%** | **+14.3 ✅** |
| **`maintenance_weeks_ge_12`** | deepseek-v3 | 43% | 86% | **+42.9 ✅** |
| `phase` (non-target) | llama-3.3-70b | 14% | 0% | **−14.3 ⚠** |
| `n_placebo` (non-target) | llama-3.3-70b | 86% | 83% | −2.4 |
| `dose` (non-target) | llama-3.3-70b | 86% | 83% | −2.4 |
| `primary_efficacy_outcome` (non-target) | llama-3.3-70b | 86% | 83% | −2.4 |

The −2.4 entries on Llama for `n_placebo`, `dose`, `primary_efficacy_outcome` come from the denominator change (6 instead of 7 papers due to the DAPA-HF extraction error), not a content change — every other paper Llama got right pre-v3 it still gets right under v3 in those fields.

### r02 overall

| Model | r02 raw (pre-v3) | r02 raw (v3) | Δ raw | r02 v2 (pre-v3) | r02 v2 (v3) | Δ v2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-mini | 70.1% | 70.1% | +0.0 | 79.2% | 79.2% | +0.0 |
| llama-3.3-70b | 64.9% | 69.7% | **+4.8** | 74.0% | 78.8% | **+4.8** |
| qwen-3-235b | 79.2% | 83.1% | **+3.9** | 85.7% | 88.3% | **+2.6** |
| deepseek-v3 | 77.9% | 83.1% | **+5.2** | 83.1% | 88.3% | **+5.2** |

## 6. Net impact summary

- **r01:** GPT flat, Llama +1.3 pp, Qwen3 **+3.9 pp**, DeepSeek **−5.2 pp**. The DeepSeek regression is driven by non-target fields (`phase` 86 % → 57 %; `age_range_years` 86 % → 57 %).
- **r02:** GPT flat, Llama **+4.8 pp**, Qwen3 **+2.6 pp**, DeepSeek **+5.2 pp**. All four models gained or held on their overall score; the two target fields gained materially in 6 of 8 model × field cells.

The v3 prompt does what it was designed to do *on r02*. It also noticeably perturbs DeepSeek's behaviour on r01 fields the edits weren't aimed at — DeepSeek seems to over-attend to the new bullet structure and starts emitting `N/A` and looser age strings on Dravet papers it previously got right.

## 7. Side-effect check (regressions > 5 pp on any model × non-target-field × review)

| Model × field × review | Δ (v2) | Why |
| --- | ---: | --- |
| **deepseek-v3 × `phase` × r01** | **−28.6 pp** | DeepSeek now writes `N/A` for some Phase III trials on r01; non-target field; clearly induced by the prompt edit. |
| **deepseek-v3 × `age_range_years` × r01** | **−28.6 pp** | Target field, but **regressed**, not improved. DeepSeek emits `>=2` style for Dravet trials whose GT is the explicit `2-18` range — the new lower-bound bullet bleeds into cases where an explicit upper bound exists. |
| **llama-3.3-70b × `phase` × r01** | −14.3 pp | Non-target. Llama writes `not_reported` more often on r01 phases under v3. |
| **llama-3.3-70b × `phase` × r02** | −14.3 pp | Non-target. Llama drops from 1/7 to 0/7 on r02 phase. (Was already the worst-performing model on r02 phase pre-v3; this completes the collapse.) |

Three of the four flagged regressions are on a *non-target* field (`phase`) and one is on a *target* field that should have improved. Per task spec: "If any field regressed by >5pp, FLAG IT — that may mean the prompt edit was too aggressive." → flagged.

## 8. New extraction error introduced

| Review | Model | PMID | Field that broke | Cause |
| --- | --- | --- | --- | --- |
| r02 | llama-3.3-70b | 31535829 (DAPA-HF) | `duration_weeks` | Llama emitted a float (`79.1`) computed from "median follow-up of 18.2 months". Strict-int schema rejected. Retry produced the same value. The new rule-6 phrase "median follow-up" plausibly directs the model to convert this number — it's not a model regression, it's an instruction-following success that ran into the schema's int constraint. |

This is exactly 1 error, at the upper bound of the previous "≤ 1 errors per model" tolerance but above this task's "verify 0 errors" wording.

## 9. Cost & runtime for the v3 re-runs

| Stage | Cost (USD) | Wall time |
| --- | ---: | ---: |
| r01 extract_openai | $0.0095 | 60.7 s |
| r01 extract_modal (Llama + Qwen3 + DeepSeek) | $0.1474 | 217.6 s |
| r02 extract_openai | $0.0171 | 89.4 s |
| r02 extract_modal (Llama + Qwen3 + DeepSeek) | $0.2624 | 444.7 s (Llama 99 + Qwen3 222 + DeepSeek 128) |
| Evaluations (×4 raw + ×4 v2 calls, two reviews) | $0 | < 60 s |
| **Total this round** | **$0.4364** | < 15 min |

## 10. Recommendation

**REPORT BLOCKER (per task spec).** Two non-trivial issues:

1. **DeepSeek V3 regressed −5.2 pp overall on r01** under v3, almost entirely on two fields the edit wasn't aimed at (`phase`, `age_range_years`). The lock comment now declares the prompt frozen — but freezing it in this state means we ship the paper with a known, prompt-induced 5 pp accuracy drop on the strongest open model on the seed review. Worth a discussion before committing.
2. **One extraction error introduced** (Llama on DAPA-HF). It's a strict-int / instruction-following collision, not a model failure. Fixable in two minutes by coercing whole-number floats to int in `extraction_together._validate_against_schema` (no schema change, no prompt change), but per task constraints I have not made that fix.

Three options for your call:

- **Option A — Accept v3 as-is, lock as instructed.** r02 wins ($+2.6$ to $+5.2$ pp, the target review) outweigh r01 losses for three of four models; DeepSeek r01 takes a hit but remains near 84 %. Treat the DeepSeek r01 regression as a paper-level finding ("prompt-induced trade-off across reviews"). One extraction error survives.
- **Option B — Coerce-int parser fix only.** Land a 3-line change in `extraction_together.py` to round `duration_weeks` to int before validation. That clears the Llama DAPA-HF error (back to 0/14 errors, 14×11=154 evaluable cells) without touching the prompt. The DeepSeek r01 regression is unaffected.
- **Option C — Revert the v3 prompt.** Restore the previous wording, accept the 0 % `age_range_years` and 43 %/43 % `maintenance_weeks_ge_12` deficits on r02 as known limitations to discuss in the paper, and proceed to r03 with the original prompt.

If you tell me which option, I'll execute it and roll forward to r03 in one shot. Otherwise stopping here as instructed.

## 11. Output files

| File | Status |
| --- | --- |
| `agents/extraction_schema.py` | edited (rule 5, rule 6, lock comment) |
| `reviews/r01_lattanzi_dravet/results/extractions_{openai,llama,qwen,deepseek}.json` | regenerated under v3 |
| `reviews/r01_lattanzi_dravet/results/extraction_evaluation{,_v2}.json` | regenerated under v3 |
| `reviews/r02_ali_sglt2_hf/results/extractions_{openai,llama,qwen,deepseek}.json` | regenerated under v3 |
| `reviews/r02_ali_sglt2_hf/results/extraction_evaluation{,_v2}.json` | regenerated under v3 |
| `reviews/_archive_pre_prompt_v3/...` | created |
| `reviews/PROMPT_V3_LOCKED_REPORT.md` | this file |
