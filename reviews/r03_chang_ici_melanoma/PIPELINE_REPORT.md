# r03 (Chang 2020 / ICI in advanced melanoma) — pipeline retrieval → dedup

**Date:** 2026-04-28
**Scope:** Apply the parser int-coercion fix, refresh r02, then run r03 retrieval through dedup. Stop before extraction so the user can build the r03 extraction ground truth.
**Result:** ✅ Parser fix verified; r02 now 0 errors across all 4 models. r03 reaches dedup with **8/9 sensitivity (88.9%)**, the one missed paper is a defensible secondary-publication choice rather than a content loss. Recommend **PROCEED to building r03 extraction ground truth**.

---

## 1. Parser fix verification

### Diff (`agents/extraction_together.py`)

```diff
+def _int_field_names() -> set[str]:
+    """Field names in StudyExtraction whose annotation includes int."""
+    names = set()
+    for name, info in StudyExtraction.model_fields.items():
+        ann = info.annotation
+        # Covers both `int` and `int | None` / `Optional[int]`.
+        if ann is int or (hasattr(ann, "__args__") and int in getattr(ann, "__args__", ())):
+            names.add(name)
+    return names
+
+_INT_FIELDS = _int_field_names()
+
+def _coerce_int_fields(obj: dict) -> dict:
+    """Round float values to int for int-typed schema fields (e.g. 79.1 → 79)."""
+    if not isinstance(obj, dict):
+        return obj
+    for f in _INT_FIELDS:
+        v = obj.get(f)
+        if isinstance(v, float):
+            obj[f] = int(round(v))
+    return obj
+
 def _validate_against_schema(obj: dict) -> tuple[dict | None, str | None]:
     """Coerce to StudyExtraction. Return (validated_dict, error_str)."""
     try:
+        obj = _coerce_int_fields(obj)
         validated = StudyExtraction.model_validate(obj)
         return validated.model_dump(), None
     except Exception as e:
         return None, f"schema validation failed: {e}"
```

Surgical 18 LOC, exclusively for int-typed fields (`{duration_weeks, n_active, n_placebo, n_total, year}`). No coercion for any other type.

### Unit test

```
Int fields detected: ['duration_weeks', 'n_active', 'n_placebo', 'n_total', 'year']
After coercion: {'duration_weeks': 79, 'n_total': 4744, 'year': 2019, 'intervention': 'Dapagliflozin'}
OK
```

### End-to-end test on the original failure pattern

Synthetic StudyExtraction-shaped dict with `duration_weeks=79.1` (the exact value Llama emitted on DAPA-HF) → `_validate_against_schema()` → returns `error=None`, `duration_weeks=79`, `type=int`. Reproduces the failure scenario and confirms the fix.

### Single-paper live test (DAPA-HF / PMID 31535829 on Llama)

`extract_one(client, llama_cfg, dapa)` → `error=None`, `parse_error=None`. (On this run Llama returned `duration_weeks=None` rather than computing from "median follow-up" — Together AI's serverless responses aren't bit-deterministic at temp=0; either way the coercion path is in place for any future float emission.)

## 2. r02 refresh — final numbers post-fix

Re-ran `extract_modal` on r02 with the fix in place, then re-evaluated. Drift between the previous v3 run and this run on the unchanged Qwen and DeepSeek models: 13 % of cells (Qwen) and 15 % (DeepSeek), concentrated in free-text fields (`primary_efficacy_outcome`, `country_region`, `design`); zero drift on numeric fields (`year`, `n_total`, `intervention`, `dose`). Expected for serverless temp=0 inference.

| Model | n | Errors | Cost (USD) | r02 raw | r02 v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` (re-eval only, extractions unchanged) | 14 | 0 | — | 70.1 % | 79.2 % |
| `llama-3.3-70b` | 14 | **0** ↓ from 1 | $0.0911 | 70.1 % | 79.2 % |
| `qwen-3-235b` | 14 | 0 | $0.0252 | 80.5 % | 87.0 % |
| `deepseek-v3` | 14 | 0 | $0.1376 | 83.1 % | 88.3 % |

Total r02 errors across the four models: **0**. The Llama `duration_weeks` float failure is gone; Llama's denominator is back to the full 7×11=77 cells.

Headline movement vs. the previous v3 evaluation:

| Model | r02 v2 (v3, pre-fix) | r02 v2 (v3, post-fix) | Δ |
| --- | ---: | ---: | ---: |
| gpt-4o-mini | 79.2 % | 79.2 % | +0.0 |
| llama-3.3-70b | 78.8 % (n=66) | **79.2 % (n=77)** | +0.4 |
| qwen-3-235b | 88.3 % | 87.0 % | −1.3 (drift) |
| deepseek-v3 | 88.3 % | 88.3 % | +0.0 |

## 3. r03 pipeline funnel

| Stage | Count | Sensitivity (vs 9 GT) | Notes |
| --- | ---: | ---: | --- |
| PubMed search | 485 | — | 9 GT all matched |
| Retrieval (after metadata parse) | 483 | **9/9 = 100 %** | 2 records dropped during XML parse, none of them GT |
| Screening (LLM, gpt-4o-mini) | INCLUDE: 118 / EXCLUDE: 365 | **9/9 = 100 %** | 109 false positives passed through, no GT dropped |
| Fulltext fetch | 118 records pooled | 9/9 = 100 % | abstract or PMC fulltext per record |
| Fulltext-agent (LLM RCT eligibility) | INCLUDE: 49 / EXCLUDE: 69 | **9/9 = 100 %** | 40 FPs remain after fulltext review |
| Dedup (LLM clustering + classification) | PRIMARY: 23 / SECONDARY: 26 | **8/9 = 88.9 %** | 1 GT classified SECONDARY (see §6) |

**Final included pool: 23 PMIDs.** True positives: 8. False positives: 15. False negatives: 1. F1 = 0.50; precision = 0.348; sensitivity = 0.889.

## 4. r03 stage-by-stage metrics (against 9 GT PMIDs)

| Stage | TP | FP | TN | FN | Sensitivity | Specificity | Precision | F1 | Cohen κ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 9 | 474 | n/a | 0 | 1.000 | n/a | 0.019 | 0.037 | n/a |
| Screening (LLM) | 9 | 109 | 365 | 0 | **1.000** | 0.770 | 0.076 | 0.142 | 0.111 |
| Fulltext-agent | 9 | 40 | 69 | 0 | **1.000** | 0.633 | 0.184 | 0.310 | n/a |
| Dedup (final) | 8 | 15 | n/a | 1 | **0.889** | n/a | 0.348 | 0.500 | n/a |

Recall stays at 100 % through the LLM screening and LLM fulltext-agent stages. The single drop is at dedup, which is reasoning over publication relationships rather than re-judging eligibility.

## 5. r03 per-GT-PMID journey

| PMID | Short name (Chang 2020 GT) | Retrieved | Screen | Fulltext-agent | Dedup classification | Final |
| --- | --- | :-: | :-: | :-: | --- | :-: |
| 21639810 | Robert 2011 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 28961465 | Hamid 2017 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 25399552 | CheckMate 066 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 25795410 | CheckMate 037 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 28359784 | Ascierto 2017 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 27622997 | CheckMate 069 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 25891173 | KEYNOTE-006 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 28891423 | CheckMate 238 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| **28889792** | **CheckMate 067** (overall-survival update) | ✅ | ✅ | ✅ | **SECONDARY → 26027431** | ❌ |

## 6. Findings / concerns

**(a) Single dedup miss is a "primary-publication choice" disagreement, not a content loss.** PMID 28889792 (Wolchok et al., NEJM 2017, "Overall Survival with Combined Nivolumab and Ipilimumab in Advanced Melanoma") was classified as SECONDARY to PMID 26027431 (Larkin et al., NEJM 2015, the initial CheckMate 067 publication) with the dedup agent's stated reasoning:

> "This paper provides 3-year overall survival outcomes from the CheckMate 067 trial, which is already reported in PMID 26027431. It is an updated analysis of the same cohort." (confidence 0.95)

That reasoning is *correct* — both papers report on the same trial (NCT01844505). Chang 2020's GT prefers the longer-follow-up 2017 paper because it has the mature OS data; our agent prefers the original 2015 paper because that's where the trial was first registered and randomised. From a "did we keep the trial?" perspective, the trial is in our final pool (under PMID 26027431). For the paper's evaluation table this counts as a false negative; for an actual systematic review it'd be a stylistic substitution.

**Two ways to handle this in the next stage:**
1. Accept the dedup result as-is, build r03 extraction GT against our 23-paper final pool (replacing PMID 28889792 with PMID 26027431 if extraction-of-the-trial is the goal).
2. Patch dedup-agent prompting to prefer the publication with longest follow-up. Out of scope for this task — would require re-running r03 dedup. Worth discussing before r04/r05 if it's a recurring pattern.

**(b) Fulltext-agent precision on r03 is lower than r02.** r02 had 21 records reach extraction (14 + 7 FP); r03 has 49 reaching dedup (49 = 9 TP + 40 FP). The melanoma ICI search retrieves many adjacent-but-non-eligible RCTs (other PD-1 trials, ipilimumab dose-escalation studies) that survive eligibility checks because they are RCTs with the right intervention class but for the wrong indication or wrong line of therapy. Dedup further compresses to 23, but precision stays 0.35. Not a blocker — final pipeline F1 of 0.50 is comparable to r02's pipeline before the extraction-GT-built step.

**(c) Pipeline integrity green elsewhere.** No retrieval gaps, no screening drops, no fulltext-fetch failures (118/118 fetched). Sensitivity to fulltext-agent inclusive: 9/9 = 100 %.

## 7. Cost & runtime

| Stage | Wall time | Cost (USD) |
| --- | ---: | ---: |
| r02 extract_modal re-run (post-fix) | ~ 8 min | $0.2636 |
| r02 evaluate (raw + v2) | < 5 s | $0 |
| r03 retrieval (PubMed eutils) | < 30 s | $0 (no LLM) |
| r03 screening (gpt-4o-mini × 483) | ≈ 19 min | ~$0.05 (estimated from r02 token rate) |
| r03 fulltext fetch (PMC + abstracts × 118) | ≈ 4 min | $0 (no LLM) |
| r03 fulltext_agent (gpt-4o-mini × 118) | ≈ 6 min | ~$0.04 (estimated) |
| r03 dedup (gpt-4o-mini × 49 classifications + clustering) | ≈ 3 min | ~$0.03 (estimated) |
| **Total this round** | **≈ 40 min** | **≈ $0.39** |

(The screening and fulltext-agent stages stream nothing to disk during the run, hence the ~19 min for r03 screening; this is sequential gpt-4o-mini × 483 with a 50 ms inter-call sleep. Worth parallelising before r04/r05 — async batch of 8–16 would cut wall time to a few minutes — but not in scope.)

## 8. Output files

| File | Status |
| --- | --- |
| `agents/extraction_together.py` | edited (parser int-coercion fix only) |
| `reviews/r02_ali_sglt2_hf/results/extractions_{llama,qwen,deepseek}.json` | regenerated post-fix |
| `reviews/r02_ali_sglt2_hf/results/extraction_evaluation{,_v2}.json` | regenerated |
| `reviews/r03_chang_ici_melanoma/retrieved/{pubmed_results,fulltext_pool}.json` | new |
| `reviews/r03_chang_ici_melanoma/results/{retrieval,screening,fulltext}_evaluation.json` | new |
| `reviews/r03_chang_ici_melanoma/results/screening_decisions.json` | new (483 decisions) |
| `reviews/r03_chang_ici_melanoma/results/fulltext_decisions.json` | new (118 decisions) |
| `reviews/r03_chang_ici_melanoma/results/dedup_{decisions,clustering}.json` | new |
| `reviews/r03_chang_ici_melanoma/results/final_pipeline_evaluation.json` | new |
| `reviews/r03_chang_ici_melanoma/PIPELINE_REPORT.md` | this file |

## 9. Recommendation

**✅ PROCEED to building r03 extraction ground truth (next command).**

The 23-paper final pool is in good shape:
- All 9 trials Chang 2020 included are represented (8 by their GT-canonical PMID, 1 — CheckMate 067 — by its initial-publication PMID 26027431 instead of the 2017 OS update PMID 28889792).
- 15 false positives are mostly other ICI melanoma RCTs (CheckMate 064, KEYNOTE-001 components, dose-comparison studies) that a human reviewer would exclude for "wrong line of therapy", "wrong combination", or "secondary publication of an already-included trial".
- Extraction GT for r03 should be built for the 9 included trials (or 8 if we keep PMID 28889792 as canonical and accept that we'll evaluate extraction on PMID 26027431 — equivalent trial, alternate publication). Either choice is defensible; flagging for your call before the GT-construction step.

If you confirm the 26027431-as-CheckMate-067-substitute approach, extraction can run on the full 23-paper pool with ground truth on the 9 GT trials and the GT correction described above documented in the paper's methods section.

Stopping here as instructed.
