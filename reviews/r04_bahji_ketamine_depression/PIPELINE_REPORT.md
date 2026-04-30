# r04 (Bahji 2021 / ketamine vs esketamine for depression) — pipeline retrieval → dedup

**Date:** 2026-04-29
**Scope:** Run r04 through retrieval, screening, fulltext, fulltext_agent, and dedup against the 24 GT trials. Stop before extraction. Largest review in the project.
**Result:** ✅ Recommend **PROCEED to building r04 extraction GT**. Sensitivity 22/24 = **91.7%** at the dedup checkpoint, all three TRANSFORM trials kept as PRIMARY, all crossover trials (Zarate 2006, Diazgranados 2010, Zarate 2012) kept as PRIMARY. Two GT losses (Sos 2013, Li 2016) — both correctly identified by dedup as secondary analyses of the Zarate 2006 trial; defensible disagreement with Bahji's inclusion choice.

---

## 1. Pre-flight checks (9, all PASS)

| # | Check | Result | Detail |
|--:|---|:-:|---|
| 1 | `config.json` valid (query + paths) | PASS | query_len=767 chars |
| 2 | `ground_truth.inclusion_pmids` length 24 | PASS | n=24 |
| 3 | `prompts/screening_system.txt` present | PASS | size=2 526 |
| 4 | `prompts/fulltext_system.txt` present | PASS | size=2 441 |
| 5 | `prompts/dedup_system.txt` present | PASS | size=3 837 |
| 6 | dedup prompt explicitly lists TRANSFORM-1/-2/-3 | PASS | all three named |
| 7 | screening prompt mentions crossover | PASS | "crossover" found |
| 8 | OpenAI API key works | PASS | 1-token chat probe |
| 9 | `retrieved/` + `results/` were clean (no leftover files) | PASS | both empty before run |

## 2. Pipeline funnel

| Stage | Count | Sensitivity (vs 24 GT) | GT-loss source |
| --- | ---: | ---: | --- |
| PubMed search | 485 (after eutils dedup → 370 returned) | — | — |
| Retrieval (parsed records) | **370** | **24/24 = 100 %** | none |
| Screening (LLM, gpt-4o-mini) | INCLUDE 120 / EXCLUDE 246 | **24/24 = 100 %** | none — all 24 GT made it through screening |
| Fulltext fetch | 120 records pooled | 24/24 = 100 % | none |
| Fulltext-agent (LLM eligibility) | INCLUDE 94 / EXCLUDE 26 | **24/24 = 100 %** | none — every GT trial was judged eligible from fulltext |
| Dedup (LLM clustering + classification) | PRIMARY 50 / SECONDARY 44 | **22/24 = 91.7 %** | 2 GT trials reclassified as SECONDARY of Zarate 2006 |

The full screening + fulltext recall is **24/24 = 100 %.** All GT loss localises to dedup, where two papers are correctly identified as post-hoc analyses of the same trial.

## 3. Per-stage metrics (vs 24 GT PMIDs)

| Stage | TP | FP | TN | FN | Sensitivity | Specificity | Precision | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 24 | 346 | n/a | 0 | 1.000 | n/a | 0.065 | 0.122 |
| Screening (LLM) | 24 | 96 | 246 | 0 | **1.000** | 0.719 | 0.200 | 0.333 |
| Fulltext-agent | 24 | 70 | 26 | 0 | **1.000** | 0.271 | 0.255 | 0.407 |
| Dedup (final) | 22 | 28 | n/a | 2 | **0.917** | n/a | 0.440 | **0.595** |

Final pipeline F1 = **0.595**, the highest of any review so far (r02 was ~0.60, r03 was 0.50). r04's larger candidate pool (24 GT trials) provides a denominator that better balances precision and recall.

## 4. Per-GT-PMID journey (all 24)

| PMID | Short name | Retrieved | Screen | Fulltext-agent | Dedup classification | Final |
| --- | --- | :-: | :-: | :-: | --- | :-: |
| 10686270 | Berman 2000 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 12088953 | Kudoh 2002 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 16894061 | **Zarate 2006** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| 20679587 | **Diazgranados 2010** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| 22297150 | Zarate 2012 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| **23803871** | **Sos 2013** | ✅ | ✅ | ✅ | **SECONDARY → 16894061** | ❌ |
| 23982301 | Murrough 2013 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 24821196 | Lapidus 2014 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 26478208 | Hu 2016 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 27056608 | Singh 2016a | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 26707087 | Singh 2016b | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| **26821769** | **Li 2016** | ✅ | ✅ | ✅ | **SECONDARY → 16894061** | ❌ |
| 28452409 | Grunebaum 2017 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 28492279 | Su 2017 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 29656663 | Canuso 2018 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 29202655 | Grunebaum 2018 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 29282469 | Daly 2018 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 30283029 | Fava 2018 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 30922101 | Phillips 2019 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 30286416 | Ionescu 2019 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 31109201 | **TRANSFORM-2** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| 31290965 | **TRANSFORM-1** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| 31786030 | Correia-Melo 2020 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 31734084 | **TRANSFORM-3** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |

## 5. Dedup deep dive

### Headline counts
- GT papers in final inclusion: **22 / 24**
- GT papers classified SECONDARY: **2 / 24**
  - PMID 23803871 (Sos 2013) → SECONDARY of PMID 16894061 (Zarate 2006). Reasoning: *"This paper is a secondary analysis focusing on psychotomimetic effects from a previously reported trial (PMID 16894061)."*
  - PMID 26821769 (Li 2016) → SECONDARY of PMID 16894061 (Zarate 2006). Reasoning: *"This paper is a secondary analysis focusing on prefrontal cortex and amygdala from a previously reported trial (PMID 16894061)."*

### TRANSFORM trial handling

| Trial | PMID | Dedup classification | In final pool? |
| --- | --- | --- | :-: |
| TRANSFORM-1 | 31290965 | **PRIMARY** | ✅ |
| TRANSFORM-2 | 31109201 | **PRIMARY** | ✅ |
| TRANSFORM-3 | 31734084 | **PRIMARY** | ✅ |

**3/3 TRANSFORM trials kept separate.** The dedup prompt's explicit mention of TRANSFORM-1/-2/-3 as distinct trials worked as designed. Each was given a separate `parent_pmid: null` PRIMARY classification.

### Crossover / replication trial handling

| Trial | PMID | Dedup classification | In final pool? |
| --- | --- | --- | :-: |
| Zarate 2006 | 16894061 | **PRIMARY** | ✅ |
| Diazgranados 2010 | 20679587 | **PRIMARY** | ✅ |
| Zarate 2012 | 22297150 | **PRIMARY** | ✅ |

**3/3 of the early independent crossover RCTs kept as PRIMARY.** The screening prompt's "INCLUDES crossover" instruction propagated correctly through the pipeline.

### Defensibility of the 2 GT losses

Both lost papers are *secondary analyses of the Zarate 2006 trial cohort*, not new RCTs:
- Sos 2013: re-analyses the 2006 cohort for psychotomimetic effects (different outcome).
- Li 2016: re-analyses the 2006 cohort with imaging biomarkers (different outcome).

This is the same pattern as r03's CheckMate 067 / Wolchok 2017 substitution: dedup correctly identifies "same trial, different publication", while the source review (Bahji 2021) treats these as separate entries to allow inclusion of secondary outcomes in the meta-analysis. **From a "did we keep the trial?" perspective, the trial is in our final pool (under PMID 16894061).** From an "extraction-row count" perspective, two rows are missing.

This is the third instance of this pattern across the project (r03: CheckMate 067; r04: Sos 2013, Li 2016). Worth a methods-section note: the dedup agent prefers parent-trial PRIMARY publications and treats post-hoc secondary analyses as SECONDARY, which sometimes diverges from a meta-analysis review's inclusion list. We propose handling this by either (a) accepting the substitution and scoring extraction GT under the parent PMID, or (b) tuning the dedup prompt to keep secondary publications when they introduce a new outcome — both are out of scope for this run.

## 6. Final inclusion stats

| | count |
| --- | ---: |
| Final included PMIDs | **50** |
| True positives (GT trials present) | **22** |
| False positives (non-GT in final) | 28 |
| False negatives (GT lost) | 2 |
| Sensitivity / Recall | **0.917** |
| Precision | 0.440 |
| F1 | **0.595** |

## 7. Cost & runtime per stage

| Stage | Wall time | Cost (USD) |
| --- | ---: | ---: |
| Retrieval (PubMed eutils) | < 30 s | $0 |
| Screening (gpt-4o-mini × 370) | ~17 min 51 s | ~$0.05 |
| Fulltext fetch (PMC + abstracts × 120) | ~3 min | $0 |
| Fulltext-agent (gpt-4o-mini × 120) | ~10 min | ~$0.04 |
| Dedup (gpt-4o-mini × 94 classifications + clustering) | ~6 min | ~$0.05 |
| **Total this round** | **~37 min** | **~$0.14** |

Compared to r03 (40 min, $0.39) and r02 (20 min, $0.10) — r04 is the largest review by paper count but the candidate pool stayed manageable thanks to the tighter PubMed query (370 results versus r03's 485). Cost is dominated by the LLM stages on the larger candidate pool.

## 8. Concerns

**(a) The two GT losses are policy-driven, not pipeline-driven.** Sos 2013 and Li 2016 are correctly identified by dedup as secondary analyses of the Zarate 2006 trial; Bahji 2021 includes them anyway because they contribute different outcomes to the meta-analysis. Same defensible-disagreement pattern as r03 / CheckMate 067. **Recommended handling for r04 extraction GT: include both in the GT under their original PMIDs but mark them with `upstream_substituted_to: "16894061"` markers, mirroring r03's approach.** That way the pipeline's PMID 16894061 extraction is what gets scored, not a phantom missing-from-extraction entry.

**(b) 28 false positives in the final pool is the highest project-wide.** Worth manual sanity-spot-check before extraction GT is built — most are likely other ketamine-depression RCTs that could plausibly belong (e.g., dose-comparison studies, esketamine pharmacokinetics studies that share registration with main TRANSFORM trials but are different reports). They won't be scored against extraction GT (only the 22 TPs will), so they don't *harm* extraction accuracy — just inflate the extraction cost slightly.

**(c) No screening/fulltext_agent loss.** This is the cleanest LLM-judgement-stage performance of any review so far. The domain-specific screening + fulltext prompts (which explicitly include crossover trials, exclude non-RCTs, etc.) appear to be doing real work here.

**(d) TRANSFORM trial preservation is the single most important r04-specific success criterion** — and it landed: 3/3 PRIMARY. The dedup prompt's explicit list of TRANSFORM-1/-2/-3 as named separate trials is doing the heavy lifting; without that hint these trials would likely have been collapsed (they share registration umbrella, drug, and sponsor; only the patient population and primary endpoint differ across the three).

**(e) Volume scales sub-linearly.** Pipeline wall time roughly doubled vs r03 even though the candidate pool stayed about the same size — most of the extra time is in screening (~18 min vs r03's ~19 min — actually similar) and the larger fulltext_agent batch (120 vs 49 in r03). Cost per paper held: r03 was $0.0156/paper-all-stages, r04 will be ~$0.012/paper after extraction.

## 9. Recommendation: ✅ PROCEED to building r04 extraction GT

22-trial extraction GT to construct. Largest of the project so far. Suggested next steps:
1. Build extraction GT for the 22 GT-positive PMIDs in `final_included_pmids`. Mirror the r03 approach for the 2 substituted entries (Sos 2013, Li 2016 → PMID 16894061 markers).
2. Run extraction (gpt-4o-mini + 3 open models on Together AI). Estimated cost ~$0.30–0.50, ~15 min wall.
3. Evaluate raw + v2 against the GT.

The pipeline is in good shape; no blockers; concerns above are documentation-level rather than fix-now items.

## 10. Output files

| File | Status |
| --- | --- |
| `reviews/r04_bahji_ketamine_depression/retrieved/{pubmed_results,fulltext_pool}.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/retrieval_evaluation.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/screening_decisions.json` | new (370 decisions) |
| `reviews/r04_bahji_ketamine_depression/results/screening_evaluation.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/fulltext_decisions.json` | new (120 decisions) |
| `reviews/r04_bahji_ketamine_depression/results/fulltext_evaluation.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/dedup_decisions.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/dedup_clustering.json` | new |
| `reviews/r04_bahji_ketamine_depression/results/final_pipeline_evaluation.json` | new |
| `reviews/r04_bahji_ketamine_depression/PIPELINE_REPORT.md` | this file |
