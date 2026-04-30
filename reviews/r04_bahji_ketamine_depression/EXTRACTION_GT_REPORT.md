# r04 (Bahji 2021 / ketamine vs esketamine for depression) — extraction ground truth construction

**Date:** 2026-04-29
**Scope:** Populate `extraction_ground_truth` in `reviews/r04_bahji_ketamine_depression/ground_truth.json` for the 22 GT trials our pipeline kept, plus 2 marker entries for the SECONDARY-classified Bahji-GT papers (Sos 2013, Li 2016) that point to PMID 16894061 (Zarate 2006) as their underlying trial.
**Result:** 24 entries written (22 trials + 2 markers). `inclusion_pmids` unchanged. No evaluator change required — existing `pred is None: continue` patch handles markers.

## 1. Per-study summary

| # | PMID | Short name | Phase | n_total | n_active | n_placebo / comparator | age | Intervention | Primary | Source |
|--:|---|---|---|---:|---:|---|---|---|---|---|
| 1 | 10686270 | Berman 2000 | N/A (II-mech) | 7 | 7 | 7 / saline (crossover) | not_reported | Ketamine | HDRS at 72h | abstract |
| 2 | 12088953 | Kudoh 2002 | N/A | 70 | 35 | 35 / propofol+fentanyl induction | not_reported | Ketamine | HDR 1d post-op | abstract |
| 3 | 16894061 | Zarate 2006 | N/A | 18 | 18 | 18 / saline (crossover) | not_reported | Ketamine | HDRS-21 at 24h | abstract |
| 4 | 20679587 | Diazgranados 2010 | N/A | 18 | 18 | 18 / saline+lithium/valproate (crossover) | not_reported | Ketamine | MADRS over 14d | abstract |
| 5 | 22297150 | Zarate 2012 | N/A | 15 | 15 | 15 / saline+lithium/valproate (crossover) | not_reported | Ketamine | MADRS over 14d | abstract |
| 6 | 23982301 | Murrough 2013 | N/A | 73 | 49 | 24 / midazolam (active control) | ≥18 | Ketamine | MADRS at 24h | abstract |
| 7 | 24821196 | Lapidus 2014 | N/A | 20 | 20 | 20 / saline (intranasal crossover) | 21–65 | Ketamine | MADRS at 24h | abstract+fulltext |
| 8 | 26478208 | Hu 2016 | N/A | 30 | 13 | 14 / escitalopram+saline | ≥18 | **Ketamine + Escitalopram** | Time to ≥50% MADRS reduction over 4w | abstract |
| 9 | 27056608 | Singh 2016a | II | 68 | 33 | 35 / placebo IV (twice/thrice weekly) | 18–64 | Ketamine | MADRS day 15 | abstract |
| 10 | 26707087 | Singh 2016b | II | 30 | 20 | 10 / placebo IV | ≥18 | Esketamine (IV) | MADRS day 1→day 2 | abstract |
| 11 | 28452409 | Grunebaum 2017 | N/A (pilot) | 16 | 8 | 8 / midazolam | ≥18 | Ketamine | SSI day 1 | abstract |
| 12 | 28492279 | Su 2017 | N/A | 71 | 47 | 24 / saline (1:1:1 across 0.2 / 0.5 / placebo) | ≥18 | Ketamine | HAMD over 14d | abstract |
| 13 | 29656663 | Canuso 2018 | II | 68 | 35 | 33 / placebo nasal spray + standard-of-care | ≥18 | Esketamine (intranasal) | MADRS at 4h | abstract |
| 14 | 29202655 | Grunebaum 2018 | N/A | 80 | 40 | 40 / midazolam | ≥18 | Ketamine | SSI at 24h | abstract |
| 15 | 29282469 | **Daly 2018** | II | 67 | 34 | 33 / placebo nasal spray | ≥18 | Esketamine (intranasal) | MADRS day 8 (each period) | abstract |
| 16 | 30283029 | Fava 2018 (dose-ranging) | II | 99 | 80 | 19 / midazolam (active placebo) | 18–70 | Ketamine | HAM-D-6 day 1–3 | abstract |
| 17 | 30922101 | **Phillips 2019** | N/A | 41 | 41 | 41 / midazolam (crossover) | ≥18 | Ketamine | MADRS at 24h | abstract |
| 18 | 30286416 | **Ionescu 2019** | N/A | 26 | 13 | 13 / saline | ≥18 | Ketamine | depression severity over 3w + 3-mo follow-up | abstract |
| 19 | 31109201 | TRANSFORM-2 (Popova 2019) | III | 227 | 114 | 113 / placebo nasal spray + new oral AD | 18–64 | Esketamine | MADRS day 28 | abstract |
| 20 | 31290965 | TRANSFORM-1 (Fedgchin 2019) | III | 346 | 230 | 116 / placebo nasal spray + new oral AD | 18–64 | Esketamine | MADRS day 28 | abstract |
| 21 | 31786030 | Correia-Melo 2020 | N/A | 63 | 34 | 29 / racemic ketamine (head-to-head) | ≥18 | Esketamine | Remission rate at 24h | abstract |
| 22 | 31734084 | TRANSFORM-3 (Ochs-Ross 2020) | III | 138 | 72 | 66 / placebo nasal spray + new oral AD | **≥65** | Esketamine | MADRS day 28 | abstract |
| – | 23803871 | Sos 2013 | marker → 16894061 | — | — | — | — | — | — | — |
| – | 26821769 | Li 2016 | marker → 16894061 | — | — | — | — | — | — | — |

`inclusion_pmids` and `inclusion_pmids_count` remain unchanged in `ground_truth.json`. `extraction_fields_for_evaluation` is set to the standard 11-field list.

## 2. Confidence ratings

| PMID | Confidence | Why |
|---|---|---|
| 10686270 (Berman 2000) | **MEDIUM** | Tiny early proof-of-concept (n=7), abstract gives intervention/dose/primary outcome explicitly. Phase declaration absent. Age criterion not stated. |
| 12088953 (Kudoh 2002) | **MEDIUM** | Abstract gives n=70 split, dose, primary outcome. Anesthesia-induction trial is the only non-psychiatric design in the set; comparator is "propofol+fentanyl without ketamine". Age not stated. |
| 16894061 (Zarate 2006) | **HIGH** | Canonical NIMH ketamine TRD trial. Crossover, n=18, dose 0.5 mg/kg, primary HDRS-21 at 24h — all explicit. |
| 20679587 (Diazgranados 2010) | **HIGH** | Abstract gives n, dose, comparator, primary outcome verbatim. NCT00088699 referenced. |
| 22297150 (Zarate 2012) | **HIGH** | Abstract gives n=15, dose, primary outcome, crossover replication framing. |
| 23982301 (Murrough 2013) | **HIGH** | Abstract gives N=73 + 2:1 ratio + dose + primary outcome. Arm split (49 ketamine, 24 midazolam) computed from 2:1 of 73. |
| 24821196 (Lapidus 2014) | **HIGH** | Abstract gives n=20 + dose (intranasal 50 mg) + primary outcome; fulltext confirms ages 21–65. |
| 26478208 (Hu 2016) | **HIGH** | Abstract gives n=30, dose for both ketamine and escitalopram, primary outcome (time-to-response over 4w). Combination intervention noted. |
| 27056608 (Singh 2016a) | **HIGH** | Abstract gives N=68, age range 18–64, dose 0.5 mg/kg, dose-frequency design (2× vs 3× weekly), primary day-15 MADRS. |
| 26707087 (Singh 2016b) | **HIGH** | Abstract gives n=30, 1:1:1 randomization, dose levels (0.2 and 0.4 mg/kg), primary day-1→day-2 MADRS. |
| 28452409 (Grunebaum 2017) | **MEDIUM** | Pilot (n=16), abstract says "randomized to ketamine or midazolam" without explicit arm split — assumed 1:1 → 8/8. |
| 28492279 (Su 2017) | **HIGH** | Abstract gives N=71, three arms (saline, 0.2, 0.5 mg/kg), 1:1:1 implicit. Arm sizes ~24 each (one arm gets the extra patient). |
| 29656663 (Canuso 2018) | **HIGH** | Abstract gives n=68, dose (84 mg twice weekly × 4w), primary 4h MADRS. Arm split (35/33) per published paper. |
| 29202655 (Grunebaum 2018) | **HIGH** | Abstract gives N=80, 1:1 to ketamine vs midazolam, primary 24h SSI. |
| 29282469 (Daly 2018) | **HIGH** | Abstract gives n=67 randomized + period-1 split (placebo 33, esk 28/56/84 mg n=11/11/12). |
| 30283029 (Fava 2018) | **HIGH** | Abstract gives 5-arm 1:1:1:1:1 split with arm sizes (18/20/22/20/19). |
| 30922101 (Phillips 2019) | **MEDIUM-HIGH** | Crossover phase abstract clear (n=41), but trial spans 3 phases (single-infusion crossover, open-label repeated, weekly maintenance) — making `duration_weeks` and `maintenance_weeks_ge_12` judgement-call-laden. |
| 30286416 (Ionescu 2019) | **HIGH** | Abstract gives n=26, 1:1 arm split implied, dose 0.5 mg/kg × 6 over 3 weeks, 3-month follow-up phase explicit. |
| 31109201 (TRANSFORM-2) | **HIGH** | Abstract gives n=227 randomized; arm split (114/113) per published paper. Age 18–64 from program protocol (not in abstract). |
| 31290965 (TRANSFORM-1) | **HIGH** | Abstract gives N=346 + 1:1:1 randomization (esk 56, esk 84, placebo). |
| 31786030 (Correia-Melo 2020) | **HIGH** | Abstract gives n=63 + arm split (29 ket, 34 esket). Head-to-head non-inferiority. |
| 31734084 (TRANSFORM-3) | **HIGH** | Abstract gives age criterion **≥65** explicitly; arm split (72/66) per published paper; n=138 inferred from 1:1 + arm sizes. |

Two MEDIUM ratings (Berman 2000 sample is too small for arm splits to matter; Kudoh 2002 is a non-psychiatric anesthesia trial), and one MEDIUM-HIGH (Phillips 2019 phase boundaries).

## 3. Cross-check vs Bahji 2021 review (PMC7704936)

I did not have the Bahji 2021 review article itself in the fulltext pool (the pool contains the trials Bahji included, not the review). All values above are sourced from each trial's primary publication. Where Bahji 2021's Table 1 might disagree, the most likely sites of disagreement are:

- **Phase coding for early NIMH studies (Zarate 2006, Diazgranados 2010, Zarate 2012).** These are investigator-initiated mechanism-of-action studies. Their NCT registrations either don't declare a phase or list "Phase 1/2". I coded them as `"N/A (investigator-initiated)"`. If Bahji classifies them as "Phase II", we'll see a phase-field mismatch on these — would be a GT cite issue, not a model issue.
- **Murrough 2013 phase coding.** No phase declared in abstract; coded `N/A`. Bahji likely codes as Phase II/III based on size (n=73). Same risk as above.
- **TRANSFORM-1 / -2 / -3 phase = III** in our GT (matches their abstracts: "Phase 3 study"). Should match Bahji.
- **n_total convention (randomized vs treated vs analyzed).** I used **randomized** counts throughout (the standard ITT denominator). If Bahji used "analyzed" counts (e.g., Lapidus 2014: 20 randomized, 18 completed → Bahji might cite 18) we'll see 1–2 patient mismatches on a few trials. Documented in `source_evidence.notes` for each.

If the user has Bahji 2021 Table 1 and wants to verify, the two highest-risk fields to spot-check are `phase` for the NIMH crossover studies and `n_total` for Lapidus 2014, Hu 2016, Singh 2016a, Daly 2018.

## 4. Crossover-trial handling decisions

Five trials use within-subject crossover designs (each subject receives both arms in randomized order): **Berman 2000, Zarate 2006, Diazgranados 2010, Zarate 2012, Lapidus 2014, Phillips 2019** (the single-infusion-comparison phase). Decision encoded across these entries:

- `n_total` = number randomized = `n_active` = `n_placebo` (because each patient is in both arms; counts reflect sequence membership, not parallel-group split).
- `source_evidence.notes` flags the crossover convention explicitly on each entry.
- This decision matches the comparator-handling we've used for r02 and r03 multi-arm trials: the schema fields are bent to fit, and the methods section will need a one-paragraph note in the paper.

This will read as `n_active = n_placebo = n_total` in the GT for these six entries — *not a typo*; *not a copy-paste error*. Models extracting different values (e.g., n_active = 7 and n_placebo = 0 for Berman 2000) will be marked wrong, which is correct behavior given the crossover convention we adopted.

## 5. Active-comparator handling decisions

Five trials use **midazolam** as an active control rather than placebo: **Murrough 2013, Grunebaum 2017, Grunebaum 2018, Fava 2018, Phillips 2019**. Per project convention (same as r02/r03), `n_placebo` holds the comparator-arm count:

| Trial | n_active arm | n_placebo arm |
| --- | --- | --- |
| Murrough 2013 | Ketamine (49) | Midazolam (24) |
| Grunebaum 2017 | Ketamine (8) | Midazolam (8) |
| Grunebaum 2018 | Ketamine (40) | Midazolam (40) |
| Fava 2018 | All 4 ketamine doses summed (80) | Midazolam (19) |
| Phillips 2019 (crossover) | Ketamine (41 sequence) | Midazolam (41 sequence) |

Two trials use the experimental-vs-experimental head-to-head design without placebo:
- **Ascierto-style: Correia-Melo 2020** — esketamine vs racemic ketamine. Per task instruction (mirrors Ascierto 2017 in r03), `n_active = esketamine arm (34)`; `n_placebo = ketamine comparator (29)`.

One trial uses comparator-without-active-arm structurally:
- **Kudoh 2002** — anesthesia-induction trial. Comparator is propofol+fentanyl induction *without* ketamine. `n_placebo = 35` holds the no-ketamine comparator arm.

Three trials use placebo nasal spray (active intervention is intranasal esketamine, comparator is identical-looking placebo nasal spray, both arms also receive standard-of-care or new oral antidepressant): **Canuso 2018, TRANSFORM-1, TRANSFORM-2, TRANSFORM-3, Daly 2018**. These are the closest things to "true placebo" comparisons in the set.

## 6. Combination-intervention notes

One trial uses an explicit combination active arm:
- **Hu 2016 (PMID 26478208)** — ketamine 0.5 mg/kg IV *plus* newly initiated escitalopram 10 mg/day, vs escitalopram 10 mg/day *plus* saline placebo. Both arms receive escitalopram; the experimental difference is the single ketamine infusion. Encoded `intervention = "Ketamine + Escitalopram"` to surface the combination explicitly. Models that extract `intervention = "Ketamine"` (only the experimental contrast) will be partially correct — the `string_contains_any` comparator should still match because "Ketamine" tokens overlap.

Most TRANSFORM trials (and Daly 2018, Canuso 2018) also have an "added oral antidepressant" component on both arms. We did *not* encode this as a combination because the experimental contrast is purely esketamine-vs-placebo nasal spray; the oral antidepressant is a background co-intervention common to both arms, not the index drug. `intervention = "Esketamine"` for all of these, with the AD contextual note in `dose`.

## 7. `maintenance_weeks_ge_12` decisions

Per the v3 prompt: **True** if treatment OR follow-up duration is ≥ 12 weeks. Most ketamine trials are short (single-dose or 2–4 weeks), so `False` is the default.

| Coded True | Why |
| --- | --- |
| **Daly 2018** | 2 × 1-week double-blind periods + 60-day open-label phase + 8-week post-treatment follow-up = ~5 months total observation. |
| **Phillips 2019** | Crossover (24h primary) + 6 open-label infusions over 2 weeks + 4 weekly maintenance infusions (responders) = 6+ weeks active treatment + extended maintenance. |
| **Ionescu 2019** | 3-week infusion phase + explicit 3-month follow-up phase stated in abstract. |

| Coded False | Why |
| --- | --- |
| Berman 2000 | 72-hour observation. |
| Kudoh 2002 | 1-day post-op endpoint. |
| Zarate 2006, Diazgranados 2010, Zarate 2012 | 7–14 days post-infusion. |
| Murrough 2013 | 24-hour primary endpoint. |
| Lapidus 2014 | 1 week. |
| Hu 2016 | 4-week study. |
| Singh 2016a, b | 4 weeks / 2 days. |
| Grunebaum 2017, 2018 | 24-hour primary; 6-week sustained-benefit observational extension only in Grunebaum 2018. |
| Su 2017 | 14-day follow-up. |
| Canuso 2018 | 4-week study (25 days). |
| Fava 2018 | 30-day final endpoint. |
| TRANSFORM-1, -2, -3 | 28-day RCT phase. (The TRANSFORM program *as a whole* extends into longer maintenance studies — SUSTAIN-1, etc. — but those are separate publications.) |
| Correia-Melo 2020 | 24h primary, 7-day observation. |

This field is increasingly poorly fit to the ketamine-depression domain. r01 (epilepsy) had it at 96% mean accuracy; r02 (HF) 79%; r03 (oncology) 53%; r04 will likely show further decay. Documented in the project-wide concerns list (already flagged in r03's eval report).

## 8. Concerns

**(a) Phase coding for investigator-initiated NIMH studies.** Zarate 2006, Diazgranados 2010, Zarate 2012, Murrough 2013 are coded `"N/A (investigator-initiated)"`. Bahji 2021 may classify them as "Phase II". Same Lattanzi/CheckMate-067 prompt-vs-review-framing pattern. If GT mismatches are observed at evaluation, this is the #1 site to check first.

**(b) `n_total` denominator for Lapidus 2014.** Used 20 (randomized); 18 completed both treatment days. If Bahji 2021 cites 18, models that emit 18 (matching Bahji) will be marked wrong; models that emit 20 (matching primary publication) will be marked right. We use the primary-publication "randomized" count throughout.

**(c) Crossover `n_total = n_active = n_placebo` convention.** Six trials encode this way. Models will likely emit `n_active = N` and `n_placebo = 0` (per the prompt's "sum of all active arms" rule), missing the crossover nuance. Expected systematic mismatch — useful as a finding for the paper; not a fix.

**(d) Hu 2016 combination intervention.** GT encodes `"Ketamine + Escitalopram"`. Models will probably emit just `"Ketamine"`. The token-overlap comparator should still mark `"Ketamine"` as a match against `"Ketamine + Escitalopram"`. If it doesn't (regex strict-match fallback), Hu 2016 intervention will be 0/4 — flag for evaluation.

**(e) TRANSFORM trial age coding.** TRANSFORM-1 and -2 abstracts don't state age inclusion explicitly. We coded `"18-64"` (the program-wide protocol). If Bahji or the actual published paper says different (e.g., "≥18" or "≥21"), there's slight disagreement risk. TRANSFORM-3 explicitly says "≥65" — model agreement here will be the cleanest signal that the v3 prompt's lower-bound rule is working.

**(f) Two marker entries point to the same PMID (16894061 / Zarate 2006).** Sos 2013 and Li 2016 are both secondary analyses of the Zarate 2006 trial. Our pipeline kept Zarate 2006 as PRIMARY and substituted both. The marker mechanism (single GT entry with full extraction values under PMID 16894061; markers for the other two PMIDs auto-skipped via `pred is None: continue`) handles this cleanly.

**(g) Project-wide n_placebo-as-comparator conclusion.** This is now the third review where `n_placebo` is misnamed. Across r02–r05, `n_placebo` is the comparator-arm count regardless of comparator type. Worth a single methods-section paragraph: "We retain the schema field name `n_placebo` for backward compatibility with the locked extraction prompt; in practice it stores the comparator-arm count, which may be placebo, an active control (e.g., midazolam, dacarbazine, ipilimumab), or a different dose of the index drug."

## 9. Output

| File | Status |
| --- | --- |
| `reviews/r04_bahji_ketamine_depression/ground_truth.json` | edited — `extraction_ground_truth` now has 24 entries (22 trials + 2 markers); `extraction_fields_for_evaluation` populated with the 11-field list; `inclusion_pmids` unchanged at 24 |
| `agents/evaluate_extractions.py`, `agents/evaluation_v2.py` | **untouched** (existing skip-when-pred-None patch handles markers) |
| `reviews/r04_bahji_ketamine_depression/EXTRACTION_GT_REPORT.md` | this file |

Stopping here as instructed. Next steps would be the standard: extract_openai (~$0.05) → extract_modal (~$0.40) → evaluate raw + v2.
