# Agentic SLR — Multi-Agent LLM Pipeline for Cross-Domain Systematic Literature Review Automation

This repository accompanies the manuscript:

> **Multi-Agent Large Language Model Pipeline for Cross-Domain Systematic
> Literature Review Automation: A Five-Specialty Evaluation Across 62
> Randomized Controlled Trials**
> *Submitted to Expert Systems with Applications, 2026.*

It contains all code, prompts, ground-truth files, model outputs and
evaluation reports needed to reproduce every figure and table in the
manuscript.

---

## Repository contents

```
.
├── paper/                          Manuscript, references, figures, cover letter
│   ├── paper_anonymized.tex        Peer-review version (no author info)
│   ├── paper_with_authors.tex      Camera-ready version
│   ├── references.bib              103 verified references
│   ├── highlights.md               5 research highlights
│   ├── cover_letter.md             Cover letter for the editor
│   ├── compile.sh                  pdflatex + bibtex build script
│   ├── PAPER_GENERATION_REPORT.md  Audit log (anon, numerics, refs)
│   ├── cas-sc.cls                  Elsevier single-column class
│   ├── cas-common.sty              Elsevier shared style
│   ├── cas-model2-names.bst        APA-style bibliography
│   └── figures/                    Figure scripts + PDF/PNG outputs
├── agents/                         Pipeline source code
│   ├── retrieval_agent.py          PubMed E-utilities retrieval
│   ├── screening_agent.py          Abstract-screening agent
│   ├── fetch_fulltext.py           Full-text retrieval (PMC/EuropePMC)
│   ├── fulltext_agent.py           Full-text eligibility agent
│   ├── dedup_agent.py              Cluster + classify primary/secondary
│   ├── extraction_schema.py        Pydantic schema + LOCKED v3 prompt
│   ├── extraction_openai.py        GPT-4o-mini extraction
│   ├── extraction_together.py      Together-AI extraction (Llama/Qwen/DeepSeek)
│   ├── extraction_multimodel.py    Driver across all 4 models
│   ├── evaluate_extractions.py     Raw evaluation
│   └── evaluation_v2.py            v2 post-processed evaluation
├── reviews/                        Per-review configs, ground truths, results
│   ├── PHASE2_FINAL_REPORT.md      Cross-review aggregate report
│   ├── PROMPT_V3_LOCKED_REPORT.md  Prompt-locking decision log
│   ├── EXTRACTION_LINEUP_LOCKED_REPORT.md  Model-lineup lock log
│   ├── target_reviews.md           Selection criteria for the 5 SLRs
│   ├── r01_lattanzi_dravet/        Pediatric epilepsy (Dravet)
│   ├── r02_ali_sglt2_hf/           Cardiology (SGLT2 in HF)
│   ├── r03_chang_ici_melanoma/     Oncology (ICI in melanoma)
│   ├── r04_bahji_ketamine_depression/  Psychiatry (ketamine)
│   └── r05_archontakis_ics_copd/   Respiratory (ICS in COPD)
├── run_pipeline.py                 Orchestrator (one stage at a time)
├── requirements.txt                Python dependencies
├── LICENSE                         MIT
└── .gitignore
```

Each `reviews/r0*/` directory holds:
- `config.json` — the review's PubMed query and inclusion/exclusion criteria
- `ground_truth.json` — the source SLR's included PMIDs and 11-field
  extraction values
- `prompts/` — the per-review screening, full-text and dedup prompts
- `results/` — pipeline-stage outputs and the four LLMs' extraction JSON
- `EVALUATION_REPORT.md`, `PIPELINE_REPORT.md`, `EXTRACTION_*_REPORT.md`
  — narrative reports for that review

## Quick reproduction

1. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set API keys in a `.env` file (NOT included; see `.env.example`):
   ```
   OPENAI_API_KEY=sk-...
   TOGETHER_API_KEY=...
   ```
3. Run a stage of the pipeline for any review:
   ```bash
   python run_pipeline.py --review r01_lattanzi_dravet --stage retrieval
   python run_pipeline.py --review r01_lattanzi_dravet --stage screening
   python run_pipeline.py --review r01_lattanzi_dravet --stage fulltext
   python run_pipeline.py --review r01_lattanzi_dravet --stage dedup
   python run_pipeline.py --review r01_lattanzi_dravet --stage extraction
   python run_pipeline.py --review r01_lattanzi_dravet --stage evaluate
   ```
4. Build the manuscript PDF:
   ```bash
   cd paper && ./compile.sh both
   ```

The locked v3 extraction prompt (Appendix A of the manuscript) lives in
`agents/extraction_schema.py`. **It must not be modified to reproduce the
reported numbers.**

## Headline results

| Model | Mean v2 accuracy | SD | Phase-2 cost |
|-------|:-:|:-:|:-:|
| **Qwen 3 235B-A22B** | **80.9%** | 6.2 pp | $0.21 |
| DeepSeek V3        | 80.8% | 6.6 pp | $1.15 |
| GPT-4o-mini        | 75.9% | 6.2 pp | $0.14 |
| Llama 3.3 70B      | 75.1% | 7.0 pp | $0.85 |

Mean retrieval recall across the five reviews: 96.2%.
Total end-to-end cost for the entire benchmark: **USD 3.21**.

See `paper/PAPER_GENERATION_REPORT.md` for a full numerical audit.

## Citing this work

If you use the pipeline, ground truths or evaluation scripts, please
cite the paper (citation will be updated on acceptance).

## License

Code is released under the MIT License (see `LICENSE`). The manuscript,
figures and reports are released under the CC-BY-4.0 license, consistent
with Elsevier's author-rights policy for accepted manuscripts.

## Contact

Yoshitha Challagulla — `bhaskar@zasti.ai`
