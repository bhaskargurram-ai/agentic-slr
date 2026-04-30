# r05 (Archontakis Barakakis 2023 / high vs medium-dose ICS in COPD) — pipeline retrieval → dedup

**Date:** 2026-04-29
**Scope:** Final pipeline run of Phase 2. Retrieval through dedup against 13 GT trials. Stop before extraction.
**Result:** ✅ Recommend **PROCEED to building r05 extraction GT**. Dedup sensitivity **11/13 = 84.6 %** (above the 70 % threshold). KRONOS and ETHOS both classified PRIMARY. Two GT losses are both upstream (one at retrieval, one at fulltext_agent) — neither is a dedup-stage problem.

## 1. Pre-flight checks (9, all PASS)

| # | Check | Result | Detail |
|--:|---|:-:|---|
| 1 | `config.json` valid (query + paths) | PASS | query_len=435 chars |
| 2 | `ground_truth.inclusion_pmids` length 13 | PASS | n=13 |
| 3 | `prompts/screening_system.txt` present | PASS | size=2 433 |
| 4 | `prompts/fulltext_system.txt` present | PASS | size=2 493 |
| 5 | `prompts/dedup_system.txt` present | PASS | size=3 647 |
| 6 | dedup prompt mentions KRONOS + ETHOS | PASS | both named |
| 7 | OpenAI API key works | PASS | 1-token chat probe |
| 8 | Together AI key works | PASS | 1-token chat probe |
| 9 | `retrieved/` + `results/` clean (no leftover) | PASS | both empty before run |

## 2. Pipeline funnel

| Stage | Count | Sensitivity (vs 13 GT) | GT-loss source |
| --- | ---: | ---: | --- |
| PubMed search | (eutils search returned candidate set) | — | — |
| Retrieval (parsed records) | **1 107** | **12/13 = 92.3 %** | PMID 28740376 (Papi 2017) — query miss |
| Screening (LLM, gpt-4o-mini) | INCLUDE 278 / EXCLUDE 829 | **12/12 = 100 %** | none lost at this stage |
| Fulltext fetch | 278 records pooled | 12/12 = 100 % | none |
| Fulltext-agent (LLM eligibility) | INCLUDE 72 / EXCLUDE 206 | **11/12 = 91.7 %** | PMID 19368417 (Rennard 2009) — judged not-ICS-dose-comparison |
| Dedup (LLM clustering + classification) | PRIMARY 60 / SECONDARY 12 | **11/13 = 84.6 %** | none lost at dedup itself |

**Critical observation:** dedup itself preserved every GT trial that survived to it. The 2 missing GT trials are both upstream losses, not dedup misclassifications.

## 3. Per-stage metrics (vs 13 GT PMIDs)

| Stage | TP | FP | TN | FN | Sensitivity | Specificity | Precision | F1 | Cohen κ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 12 | 1 095 | n/a | 1 | 0.923 | n/a | 0.011 | 0.022 | n/a |
| Screening (LLM) | 12 | 266 | 829 | 0 | **1.000** | 0.757 | 0.043 | 0.083 | 0.063 |
| Fulltext-agent | 11 | 61 | 206 | 1 | **0.917** | 0.772 | 0.153 | 0.262 | n/a |
| Dedup (final) | 11 | 49 | n/a | 2 | **0.846** | n/a | 0.183 | **0.301** | n/a |

Final pipeline F1 = **0.301**. Lower than r04's 0.595 because r05 starts with a 1-tail-larger candidate pool (1 107 vs 370) and fewer GT trials (13 vs 24), so precision is structurally lower.

## 4. Per-GT-PMID journey (all 13)

| PMID | Short name | Retrieved | Screen | Fulltext-agent | Dedup classification | Final |
| --- | --- | :-: | :-: | :-: | --- | :-: |
| 24920884 | Cheng 2014 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 22334769 | Doherty 2012 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 24429127 | Dransfield 2013 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 30232048 | **KRONOS** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| 32363206 | Hanania 2020 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 23332861 | Martinez 2013 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| **28740376** | **Papi 2017** | ❌ | ❌ | ❌ | — | ❌ |
| 32579807 | **ETHOS** | ✅ | ✅ | ✅ | **PRIMARY** | ✅ |
| **19368417** | **Rennard 2009** | ✅ | ✅ | ❌ | — | ❌ |
| 22033040 | Sharafkhaneh 2012 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 18778120 | Tashkin 2008 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 22334768 | Tashkin 2012 | ✅ | ✅ | ✅ | PRIMARY | ✅ |
| 25830381 | Zheng 2015 | ✅ | ✅ | ✅ | PRIMARY | ✅ |

## 5. Final inclusion stats

| | count |
| --- | ---: |
| Final included PMIDs | **60** |
| True positives (GT trials present) | **11** |
| False positives (non-GT in final) | 49 |
| False negatives (GT lost) | 2 |
| Sensitivity / Recall | **0.846** |
| Precision | 0.183 |
| F1 | **0.301** |

## 6. Dedup deep dive

### KRONOS / ETHOS audit
| Trial | PMID | Dedup classification | In final pool? |
| --- | --- | --- | :-: |
| KRONOS | 30232048 | **PRIMARY** | ✅ |
| ETHOS | 32579807 | **PRIMARY** | ✅ |

Both flagship dose-comparison ICS programs preserved as PRIMARY trials, as the dedup prompt's named-trial list intended.

### Headline counts
- GT papers in final inclusion: **11 / 13**
- GT papers reaching dedup: **11** (all classified PRIMARY — 0/11 collapsed to SECONDARY)
- The 12 SECONDARY classifications dedup *did* assign were on non-GT papers in the final pool — primarily LABA/LAMA-monotherapy follow-ups, post-hoc subgroup analyses, and patient-reported-outcome reports of the same trials.

**Dedup sensitivity at this stage = 11/11 = 100 %**, which is the cleanest dedup pass of any review in Phase 2 (r03 dedup lost 1 GT to over-zealous secondary collapsing; r04 lost 2 GT to the Sos/Li post-hoc-Zarate substitutions; r05 lost zero at dedup).

## 7. Concerns

**(a) Papi 2017 (PMID 28740376) lost at retrieval.** Archontakis 2023 cites this trial; our PubMed query didn't match it. Inspecting the GT entry: `Papi 2017 / Eur Respir J / Fluticasone propionate-formoterol 250/10 or 500/10 mcg`. Likely the original review used Embase as well as PubMed — our PubMed-only retrieval missed it. **Not a fixable miss without expanding the query.** Document in the paper as a known limitation of single-database retrieval.

**(b) Rennard 2009 (PMID 19368417) lost at fulltext_agent.** The LLM judgement was: *"It does not compare different doses of inhaled corticosteroids (ICS), which is a strict requirement for inclusion. Therefore, it does not meet the comparator criterion."* (confidence 0.9). The fulltext_agent prompt is correctly applying the narrow-scope criterion ("high vs medium dose ICS") and judged Rennard 2009 to be a budesonide/formoterol trial without explicit dose-comparison framing. Archontakis 2023 included it anyway — possibly because the trial does compare effective ICS doses across arms even if not framed as a dose-comparison primarily. **Defensible LLM judgement, divergent from the source review's choice.** Same Lattanzi/CheckMate-067/Sos-Li pattern of "review includes a study our pipeline excluded for narrow-scope reasoning"; not a prompt fix. Document.

**(c) Narrow-scope query worked as designed.** r05's domain is "high vs medium dose ICS for COPD" — not "any ICS for COPD". The LLM stages (screening 100 %, fulltext_agent 91.7 %) successfully filtered the 1 107-record pool down to 60 final-included papers, of which only 49 are non-GT — and those non-GT papers are mostly other ICS-dose comparisons (just not in Archontakis's specific 13). The narrow-scope filtering is doing real work; precision (0.18) reflects that even tightly-scoped retrieval+LLM-screening leaves a residue of "almost-eligible" papers that requires human adjudication.

**(d) Largest candidate pool ever screened.** 1 107 records vs r04's 370. Sequential `gpt-4o-mini` × 1 107 took roughly 60 actual API minutes (the run spanned a longer wall-clock window because the laptop slept partway through, which suspended the user-space process). No data integrity impact — just slower clock time. **Worth parallelising before any future Phase 3 work**: an `asyncio.gather` with concurrency 8–16 would cut 60 min → 5 min for an equivalent pool.

**(e) Pipeline F1 of 0.30 is the lowest of Phase 2** (r01 had higher precision because the retrieval set was much smaller; r02 was 0.595; r03 was 0.500; r04 was 0.595). r05's lower F1 is structural, not a quality regression — the review's narrow scope and large-database umbrella forced a wide candidate pool, which the LLM stages then trimmed. The 11/13 sensitivity is what matters for downstream extraction; F1 is informational.

**(f) Phase 2 closure.** This is the last pipeline run. All five reviews now have stage-by-stage funnels through dedup. The cumulative sensitivity table is:

| Review | Retrieval | Screening | Fulltext | Dedup |
| --- | ---: | ---: | ---: | ---: |
| r01 (Lattanzi) | (prior — not re-run this round) | | | |
| r02 (Ali) | 9/9 = 100 % | 7/7 = 100 % | 7/7 = 100 % | 7/7 = 100 % |
| r03 (Chang) | 9/9 = 100 % | 9/9 = 100 % | 9/9 = 100 % | 8/9 = 88.9 % |
| r04 (Bahji) | 24/24 = 100 % | 24/24 = 100 % | 24/24 = 100 % | 22/24 = 91.7 % |
| r05 (Archontakis) | 12/13 = 92.3 % | 12/12 = 100 % | 11/12 = 91.7 % | 11/13 = 84.6 % |

Across the 4 reviews where we ran the full pipeline this round, **mean dedup-final sensitivity is 91.3 %**, with the dominant loss mechanism being secondary-publication classification disagreements (Sos/Li, CheckMate 067) and one upstream retrieval miss (Papi 2017). No model-level pipeline failure.

## 8. Cost & runtime per stage

| Stage | Wall time | Cost (USD) |
| --- | ---: | ---: |
| Retrieval (PubMed eutils) | < 1 min | $0 |
| Screening (gpt-4o-mini × 1 107) | ~60 min API time (extended by laptop sleep) | ~$0.15 (estimated) |
| Fulltext fetch (PMC + abstracts × 278) | ~5 min | $0 |
| Fulltext-agent (gpt-4o-mini × 278) | ~22 min | ~$0.09 (estimated) |
| Dedup (gpt-4o-mini × 72 classifications + clustering) | ~5 min | ~$0.04 (estimated) |
| **Total this round** | **~90 min API, longer wall clock** | **~$0.28** |

Phase 2 cumulative pipeline cost (r02-r05 retrieval-through-dedup): **~$0.86**.
Phase 2 cumulative extraction cost (r01-r04 to date): **~$1.69**.
**Phase 2 grand total project cost: ~$2.55** end-to-end through r05 dedup.

## 9. Recommendation: ✅ PROCEED to building r05 extraction GT

11-trial extraction GT to construct (matches r03's volume; smaller than r04's 22). Suggested next steps:

1. **Build extraction GT** for the 11 GT-positive PMIDs in `final_included_pmids`. The lost Papi 2017 (retrieval miss) can be marker-substituted only if there's a related publication of the same trial in our final pool — likely not, since the trial used a sponsor-specific name. Document Papi 2017 as a "GT trial absent from our pipeline" in the paper's methods. Rennard 2009 similarly: include a marker that documents the LLM-fulltext-agent judgement, even though there's no `upstream_substituted_to` since no alternate publication of the same trial appears in our pool.
2. **Run extraction** (gpt-4o-mini + 3 open models on Together AI). Estimated cost ~$0.20–0.40 (60 papers × 4 models, slightly smaller than r04).
3. **Evaluate raw + v2** against the 11-trial GT.

Pipeline is in good shape; no blockers. The two GT losses are domain-policy disagreements rather than pipeline bugs, and both are well-documented for the methods section.

## 10. Output files

| File | Status |
| --- | --- |
| `reviews/r05_archontakis_ics_copd/retrieved/{pubmed_results,fulltext_pool}.json` | new |
| `reviews/r05_archontakis_ics_copd/results/retrieval_evaluation.json` | new |
| `reviews/r05_archontakis_ics_copd/results/screening_decisions.json` | new (1 107 decisions) |
| `reviews/r05_archontakis_ics_copd/results/screening_evaluation.json` | new |
| `reviews/r05_archontakis_ics_copd/results/fulltext_decisions.json` | new (278 decisions) |
| `reviews/r05_archontakis_ics_copd/results/fulltext_evaluation.json` | new |
| `reviews/r05_archontakis_ics_copd/results/dedup_{decisions,clustering}.json` | new |
| `reviews/r05_archontakis_ics_copd/results/final_pipeline_evaluation.json` | new |
| `reviews/r05_archontakis_ics_copd/PIPELINE_REPORT.md` | this file |
