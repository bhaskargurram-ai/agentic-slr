# Cover letter for Expert Systems with Applications submission

**To:** The Editor-in-Chief, Expert Systems with Applications
**Re:** Manuscript submission --- "Multi-Agent Large Language Model
Pipeline for Cross-Domain Systematic Literature Review Automation:
A Five-Specialty Evaluation Across 62 Randomized Controlled Trials"

Dear Editor,

We are pleased to submit our research article for consideration as a
full research paper in *Expert Systems with Applications*.

## Why ESWA

The manuscript presents a multi-agent expert system that automates the
end-to-end systematic-literature-review (SLR) workflow --- retrieval,
screening, full-text assessment, deduplication and structured data
extraction --- and benchmarks it against five published medical SLRs
covering 62 randomized controlled trials in five clinical specialties.
The work fits the journal's scope on three counts:

1. **Expert-system architecture.** The pipeline composes six
domain-aware agents whose individual outputs are auditable and whose
combined behaviour is reproducible. The architecture is transparent
to a degree that monolithic LLM applications are not.
2. **Practical application.** All five source reviews and all four
evaluated LLMs are publicly available; the total end-to-end cost
across the entire benchmark was under USD 4. Practitioners can adopt
the architecture immediately.
3. **Empirical breadth.** To our knowledge this is the first paper to
benchmark four frontier LLMs (closed dense, open dense, two open
mixture-of-experts) on SLR extraction across five distinct medical
specialties using a single locked schema and prompt.

## Key findings

- Two open mixture-of-experts models (Qwen 3 235B-A22B and DeepSeek V3)
match or exceed the closed baseline (GPT-4o-mini) on structured medical
extraction across five specialties. Mean v2-post-processed accuracy:
Qwen 3 235B 80.9%, DeepSeek V3 80.8%, GPT-4o-mini 75.9%, Llama 3.3 70B
75.1%.
- Mean retrieval recall against the source SLRs was 96.2%, with
end-to-end pipeline F1 ranging from 0.30 (COPD) to 1.00 (epilepsy).
- Four cumulative cross-review patterns are documented that no
single-domain study could surface, including a previously unreported
ground-truth-versus-source-paper framing-decision confound that
systematically reduces apparent extraction accuracy by 3-8 percentage
points.

## Originality and authorship

The manuscript has not been published elsewhere and is not under
consideration at another journal. All contributions and any competing
interests are disclosed in the manuscript. The work uses only public
data sources (PubMed, Europe PMC, the published source SLRs) and
publicly accessible LLM APIs; no human-subjects approval is required.

## Suggested reviewers

We respectfully suggest the following potential reviewers, drawn from
authors of closely related work (none with a conflict of interest):

- Iain J. Marshall, King's College London (RobotReviewer; Marshall &
Wallace 2019, Systematic Reviews)
- Rens van de Schoot, Utrecht University (ASReview; Nature Machine
Intelligence 2021)
- Gerald Gartlehner, Danube University Krems (LLM data-extraction
proof-of-concept; Research Synthesis Methods 2024)
- Sophia Ananiadou, University of Manchester (text-mining for systematic
review)
- Julian H. Elliott, Cochrane Australia (living systematic reviews)

We can suggest additional reviewers on request.

## Statement of significance

This work directly informs review-team practice in three ways. It
identifies a default LLM choice (Qwen 3 235B-A22B) that delivers the
best mean accuracy at low cost. It documents two operationalisable
weaknesses (multi-arm sample-size confusion and crossover trial
recognition) that can be patched with one-sentence prompt revisions.
And it establishes a baseline cost figure (USD 0.015 per paper across
four models) below which multi-model SLR extraction becomes economically
indistinguishable from single-model extraction.

We submit the manuscript and accompanying supplementary materials for
your consideration and look forward to your editorial decision.

With kind regards,

[Corresponding author]

---

## Submission package contents

- `paper_anonymized.tex` --- main manuscript, anonymised for peer review
- `references.bib` --- bibliography (103 entries)
- `highlights.md` --- 5 research highlights
- `figures/` --- figures 1-4 as PDF and PNG with generation scripts
- `cas-sc.cls`, `cas-common.sty`, `cas-model2-names.bst` --- Elsevier
CAS template files (single-column variant)

The full source code, ground-truth files and model outputs supporting
the manuscript are available in a public repository (URL redacted in
this anonymised submission; will be provided on acceptance).
