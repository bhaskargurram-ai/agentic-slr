# Extraction lineup locked: GPT-4o-mini + Llama 3.3 70B + Qwen 3 235B + DeepSeek V3

**Date:** 2026-04-28
**Scope:** Pre-flight probe of the locked 4-model lineup; full re-run of r01; first successful run of r02; report.
**Result:** ✅ **CLEAN PASS.** All 4 models served all 21 papers (7 in r01 + 14 in r02). **0 errors across 84 model-paper extractions.** All 11 schema fields populated on every record. **PROCEED to r02 evaluation.**

---

## 1. Probe re-confirmation

Pre-flight probe issued one chat completion per model: `messages=[{"role":"user","content":"Reply with: ok"}], temperature=0.0, max_tokens=5`.

| Slot | Provider | Model ID | Status | Reply | Latency | Tokens (in / out) |
| --- | --- | --- | --- | --- | --- | --- |
| Closed baseline | OpenAI | `gpt-4o-mini` | ✅ OK | `ok` | 0.89 s | 11 / 1 |
| Dense 70B | Together AI | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | ✅ OK | `ok` | 0.34 s | 39 / 2 |
| MoE Alibaba | Together AI | `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | ✅ OK | `ok` | 1.02 s | 12 / 2 |
| MoE DeepSeek | Together AI | `deepseek-ai/DeepSeek-V3` | ✅ OK | `ok` | 0.55 s | 11 / 2 |

All four serverless. Catalog had not shifted between probe and bulk extraction.

---

## 2. Code changes

### `agents/extraction_together.py` (265 LOC, model mapping only)
- `PRICING` dict: removed `qwen-2.5-72b` and `mistral-small-24b`; added `qwen-3-235b` ($0.20 / $0.60 per 1M) and `deepseek-v3` ($1.25 / $1.25 per 1M).
- `MODEL_CONFIGS`: removed Mistral and old Qwen entries; added `qwen-3-235b` → `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` (filename kept as `extractions_qwen.json` for downstream consistency) and `deepseek-v3` → `deepseek-ai/DeepSeek-V3` → `extractions_deepseek.json`.
- Llama entry unchanged.
- All other logic (retry-once, robust JSON parse with fence-stripping + balanced-brace fallback, schema validation, per-paper output keys) untouched.

### `agents/evaluate_extractions.py` (240 LOC)
- `MODEL_FILES` dict: replaced `"qwen-2.5-72b" → extractions_qwen.json` with `"qwen-3-235b" → extractions_qwen.json`; replaced `"mistral-small-24b" → extractions_mistral.json` with `"deepseek-v3" → extractions_deepseek.json`. Print headers in the accuracy table now use `qwen-3-235b` and `deepseek-v3` automatically (the dict keys are the labels).

### `agents/evaluation_v2.py` (363 LOC)
- Same `MODEL_FILES` substitution as above.

### Untouched (per task constraints)
- `agents/extraction_schema.py` — schema locked.
- `agents/extraction_openai.py` — closed baseline unchanged.
- `agents/modal_*.py`, `agents/extraction_multimodel.py` — Modal historical artifacts, still on disk.
- `run_pipeline.py` — `extract_modal` stage still routes to `extraction_together.py` (set in the original migration).
- Ground truth JSON files.

### Archives created / preserved
- `reviews/_archive_pre_qwen3_migration/r01_lattanzi_dravet/extractions/` — copies of all five r01 result files immediately before this re-run (`extractions_openai.json`, `extractions_llama.json`, `extractions_qwen.json` [Modal-era Qwen 2.5 72B], `extractions_mistral.json` [Modal-era Mistral, now retired], `extractions_all_openmodels_summary.json`).
- `reviews/_modal_archive/r01/` — preserved (Modal-era originals from the very first migration attempt).
- `reviews/_modal_archive/r02/` — preserved (Modal-era partial r02 Llama snapshot, the run that originally surfaced the migration need).
- The retired `extractions_mistral.json` was removed from the live `reviews/r01_lattanzi_dravet/results/` directory after archiving so the evaluator does not see a stale file. The archive copy is preserved.

---

## 3. r01 extraction results

Live files: `reviews/r01_lattanzi_dravet/results/extractions_{openai,llama,qwen,deepseek}.json`. 7 included studies (final-inclusion PMIDs from `dedup_decisions.final_included_pmids`). All 11 critical schema fields (`first_author`, `year`, `phase`, `design`, `blinding`, `country_region`, `n_total`, `n_active`, `n_placebo`, `age_range_years`, `intervention`) populated for every record across every model.

| Model | n | Errors | Input tokens | Output tokens | Wall (s) | Latency min / med / max (s) | Cost (USD) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `gpt-4o-mini` | 7 | 0 | 53 945 | 1 801 | 54.65 | 4.89 / 5.48 / 14.48 | $0.0092 |
| `llama-3.3-70b` | 7 | 0 | 58 665 | 2 727 | 76.53 | 3.18 / 9.74 / 19.20 | $0.0540 |
| `qwen-3-235b` | 7 | 0 | 61 952 | 2 237 | 93.20 | 9.74 / 12.85 / 18.05 | $0.0137 |
| `deepseek-v3` | 7 | 0 | 57 715 | 2 094 | 84.13 | 10.16 / 11.91 / 14.08 | $0.0748 |
| **r01 total** | **28** | **0** | **232 277** | **8 859** | — | — | **$0.1517** |

### r01 sample comparison — Devinsky 2017 NEJM (GWPCARE1 Part B), PMID 28538134

Cannabidiol vs. placebo in Dravet syndrome, NEJM 2017;376:2011–2020.

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `first_author` | `Devinsky` | `not_reported` | `Devinsky` | `Devinsky` | `Devinsky` |
| `year` | `2017` | `2017` | `2017` | `2017` | `2017` |
| `n_total` | `120` | `120` | `120` | `120` | `120` |
| `n_active` | `61` | `120` | `60` | `60` | `61` |
| `intervention` | `Pharmaceutical-grade cannabidiol` | `Cannabidiol` | `Cannabidiol` | `Cannabidiol` | `Cannabidiol` |
| `dose` | `20 mg/kg/day` | `20 mg/kg/day` | `20 mg per kilogram of body weight per day` | `20 mg/kg/day` | `20 mg/kg/day` |
| `primary_efficacy_outcome` | `Percentage change in convulsive seizure frequency` | `change in convulsive-seizure frequency` | `Change in convulsive-seizure frequency over a 14-week treatment period` | `Change in convulsive-seizure frequency over a 14-week treatment period, as compared with a 4-week baseline period` | `change in convulsive-seizure frequency` |

All four models agree on `year`, `n_total`, `intervention` (generic-name normalisation), and `dose` (modulo verbosity). DeepSeek-V3 matches the ground truth exactly on `n_active` (61); Llama and Qwen3 round to 60. GPT-4o-mini misreads `n_active` (uses the total instead of the active arm) and writes `not_reported` for `first_author` despite "Devinsky" being on the title line — these are baseline known weaknesses of the closed model.

---

## 4. r02 extraction results

Live files: `reviews/r02_ali_sglt2_hf/results/extractions_{openai,llama,qwen,deepseek}.json`. 14 included studies. All 11 critical fields populated for every record across every model.

| Model | n | Errors | Input tokens | Output tokens | Wall (s) | Latency min / med / max (s) | Cost (USD) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `gpt-4o-mini` | 14 | 0 | 94 728 | 3 809 | 109.53 | 4.49 / 5.93 / 13.61 | $0.0165 |
| `llama-3.3-70b` | 14 | 0 | 103 494 | 6 124 | 84.48 | 2.03 / 4.86 / 12.69 | $0.0965 |
| `qwen-3-235b` | 14 | 0 | 110 030 | 3 983 | 176.87 | 5.06 / 13.15 / 31.58 | $0.0244 |
| `deepseek-v3` | 14 | 0 | 101 766 | 3 978 | 102.82 | 4.49 / 7.52 / 9.61 | $0.1322 |
| **r02 total** | **56** | **0** | **410 018** | **17 894** | — | — | **$0.2696** |

### r02 sample comparison — DAPA-HF, PMID 31535829

Dapagliflozin in patients with reduced-EF heart failure, McMurray et al., NEJM 2019;381:1995–2008.

| Field | Ground truth | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 |
| --- | --- | --- | --- | --- | --- |
| `first_author` | `McMurray` | `not_reported` | `not_reported` | `McMurray` | `McMurray` |
| `year` | `2019` | `2019` | `2019` | `2019` | `2019` |
| `n_total` | `4744` | `4744` | `4744` | `4744` | `4744` |
| `n_active` | `2373` | `2373` | `2373` | `2373` | `2373` |
| `intervention` | `Dapagliflozin` | `Dapagliflozin` | `Dapagliflozin` | `Dapagliflozin` | `Dapagliflozin` |
| `dose` | `10 mg once daily` | `10 mg once daily` | `10 mg once daily` | `10 mg once daily` | `10 mg once daily` |
| `primary_efficacy_outcome` | `Composite of worsening heart failure (hospitalization or urgent visit for IV therapy) or cardiovascular death` | `composite of worsening heart failure or cardiovascular death` | `A composite of worsening heart failure (hospitalization or an urgent visit resulting in intravenous therapy for heart failure) or cardiovascular death` | `A composite of worsening heart failure (hospitalization or an urgent visit resulting in intravenous therapy for heart failure) or cardiovascular death` | `Composite of worsening heart failure (hospitalization or urgent visit requiring intravenous therapy) or cardiovascular death` |

Numeric agreement is total: every model reproduces `n_total = 4744` and `n_active = 2373` exactly. Generic-drug normalisation is consistent across all four. Qwen3 and DeepSeek correctly identify the first author; Llama and GPT-4o-mini fall back to `not_reported`. Llama, Qwen3, and DeepSeek all return the full primary-outcome composite definition; GPT-4o-mini truncates to the short form.

---

## 5. Cost & runtime totals

| | gpt-4o-mini | llama-3.3-70b | qwen-3-235b | deepseek-v3 | **Per-review total** |
| --- | ---: | ---: | ---: | ---: | ---: |
| r01 (7 papers) | $0.0092 | $0.0540 | $0.0137 | $0.0748 | **$0.1517** |
| r02 (14 papers) | $0.0165 | $0.0965 | $0.0244 | $0.1322 | **$0.2696** |
| **r01 + r02 (21 papers)** | **$0.0257** | **$0.1505** | **$0.0381** | **$0.2070** | **$0.4213** |

Per-paper, all-4-models cost: ≈ **$0.020**. Llama and DeepSeek-V3 dominate the bill; Qwen3-235B is the cheapest open model in the lineup at this token mix (output tokens are short, and Qwen3's $0.20 / $0.60 split favours short-output extraction work).

### Projected cost for r03 + r04 + r05

- Using r02's per-paper cost of $0.0193 (heavier dose-finding HF / oncology trials drive r02's per-paper cost slightly higher than r01's $0.0217 — the r02 number is the conservative one because it reflects longer full-text inputs).
- Assuming r03–r05 each include ~12 studies (typical SLR scope; final counts to be confirmed when the dedup stage runs on each):
  - **~36 additional papers ⇒ ≈ $0.69 total across all 4 models for r03+r04+r05.**
  - If average inclusion is ~15 studies per review: ≈ $0.87.
- For full project (r01–r05, all 4 models, ~57 papers): **≈ $1.10 end-to-end.** Well below the $0.07–$0.30-per-run budget anticipated when the migration was scoped.

---

## 6. Recommendation: ✅ PROCEED to r02 evaluation

All acceptance criteria met:

- All 4 models, both reviews: **0 errors** across 84 extractions (the criterion was ≤ 1 per model).
- All 11 critical schema fields populated for every record (criterion was "all 11 schema fields present").
- Sample comparisons (Devinsky 2017 / DAPA-HF) show high inter-model agreement on numeric fields, expected verbosity differences on free-text outcomes, and known weaknesses (GPT-4o-mini's `first_author` reluctance) reproduced from earlier runs.
- The retired Mistral file is gone from the live results dir; the archive preserves it.

The lineup is locked: `gpt-4o-mini`, `llama-3.3-70b` (Llama-3.3-70B-Instruct-Turbo), `qwen-3-235b` (Qwen3-235B-A22B-Instruct-2507-tput), `deepseek-v3` (DeepSeek-V3). The codebase routes `extract_modal` → `extraction_together.py` for the three open models, and `evaluate_extractions.py` / `evaluation_v2.py` know about exactly these four labels.

Next step: run evaluation against ground truth on r02 (the previously blocked stage), then extract + evaluate r03–r05 at the projected ~$0.69 incremental cost.
