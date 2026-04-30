# r02 Extraction Run Report — Ali 2023 (SGLT2/HF)

**Date:** 2026-04-28
**Status:** PARTIAL — OpenAI complete; Modal stopped at user request after Llama cold-start failure

---

## Pre-Flight Checks

| Check | Result |
|------|--------|
| `results/dedup_decisions.json` exists; `final_included_pmids` length 14 | PASS (14) |
| `ground_truth.json` has `extraction_ground_truth` populated with 9 studies | PASS (9) |
| `retrieved/fulltext_pool.json` exists; contains the 14 final-included papers | PASS (110 records, 14 final-included filtered at runtime) |
| Modal apps deployed (`slr-llama-extractor`, `slr-qwen-extractor`, `slr-mistral-extractor`) | PASS (all 3 `deployed`) |
| `OPENAI_API_KEY` set in `.env` | PASS |

All pre-flight checks passed before launch.

---

## Run Summary Per Model

| Model | n_studies | tokens_in | tokens_out | latency | errors | cost |
|-------|----------:|----------:|-----------:|--------:|-------:|-----:|
| gpt-4o-mini | 14 | 94,728 | 3,840 | 110.9 s | 0 | $0.0165 |
| llama-3.3-70b | — (not run) | — | — | — | cold-start failure | ~$0 (no extractions completed) |
| qwen-2.5-72b | not run | — | — | — | — | — |
| mistral-small-24b | not run | — | — | — | — | — |

Output files:
- `reviews/r02_ali_sglt2_hf/results/extractions_openai.json` (present)
- `extractions_llama.json`, `extractions_qwen.json`, `extractions_mistral.json` — **not created**

---

## Modal Failure Detail (Llama)

`modal app logs slr-llama-extractor` showed vLLM engine init failure during cold-start:

```
ValueError: The model's max seq len (16384) is larger than the maximum number
of tokens that can be stored in KV cache (6976). Try increasing
`gpu_memory_utilization` or decreasing `max_model_len` when initializing the engine.
```

The container auto-restarted and began reloading the 30 safetensor shards a second time. The same `max_model_len=16384` config would hit the same wall, so the user halted the run before more GPU time was burned. Qwen and Mistral never started — the script runs models sequentially.

**Fix needed in `agents/modal_llama.py`** (or wherever the Llama vLLM engine is configured): either lower `max_model_len` (e.g. to 8192) or raise `gpu_memory_utilization` so the KV cache fits the requested context window. After redeploy, re-run `extract_modal`.

---

## Sample Outputs Comparison — DAPA-HF (PMID 31535829)

Only OpenAI ran. Other columns left blank.

| Field | gpt-4o-mini | llama-3.3-70b | qwen-2.5-72b | mistral-small-24b |
|-------|-------------|---------------|--------------|-------------------|
| first_author | `not_reported` | — | — | — |
| year | 2019 | — | — | — |
| n_total | 4744 | — | — | — |
| intervention | Dapagliflozin | — | — | — |
| primary_efficacy_outcome | composite of worsening heart failure or cardiovascular death | — | — | — |

GT for DAPA-HF: first_author=McMurray, year=2019, n_total=4744, intervention=Dapagliflozin 10 mg, primary outcome composite of worsening HF event or CV death. OpenAI matches on year/n_total/intervention; first_author was missed (`not_reported`) — likely because the abstract record didn't contain the author byline in the text passed to the model.

---

## Cost & Runtime Totals

- Total cost so far: **$0.0165** (OpenAI only). Modal GPU spend negligible (failed cold-start; no successful inference).
- Total wall time spent: **~14 min** (OpenAI ~2 min + Modal cold-start attempts ~12 min before stop).

---

## Recommendation

**REPORT BLOCKER.** Do **not** proceed to evaluation (Command 7c) yet — only 1 of 4 models has output. Required before re-running:

1. Fix the vLLM config in the Llama Modal app (`max_model_len` vs. KV cache mismatch). Verify Qwen and Mistral apps don't have the same config issue before redeploying.
2. Redeploy the 3 Modal apps.
3. Re-run `python run_pipeline.py --review r02 --stage extract_modal`.

Once all 4 models have `extractions_*.json` files with `n_studies = 14` and `errors = 0`, proceed to evaluation.
