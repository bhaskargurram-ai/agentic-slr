Final submission package — Expert Systems with Applications
============================================================

Manuscript:
  Multi-Agent Large Language Model Pipeline for Cross-Domain
  Systematic Literature Review Automation: A Five-Specialty
  Evaluation Across 62 Randomized Controlled Trials

Author:
  Yoshitha Challagulla
  ZASTI, India
  gurrambhaskar.ai@gmail.com

Date prepared: 30 April 2026


Files in this package
---------------------

  01_Cover_Letter.pdf            Cover letter to the Editor-in-Chief.
  02_Title_Page.pdf              Title page with author info; submit
                                 separately so reviewers see only the
                                 anonymised manuscript.
  03_Highlights.pdf              Five research highlights (max 85 chars
                                 each), per Elsevier guidelines.
  04_Manuscript_anonymized.pdf   Main manuscript file for peer review.
                                 Contains no author or affiliation
                                 information. (19 pages.)
  05_Manuscript_with_authors.pdf Camera-ready version with author info
                                 restored. Provided for the editor's
                                 reference; do not upload as the blinded
                                 manuscript.
  06_Declaration_of_Interest.pdf Conflict-of-interest statement (none
                                 declared).
  07_ORCID.pdf                   ORCID identifier document for the
                                 corresponding author
                                 (0009-0005-2947-102X). Upload when EM
                                 prompts for ORCID as a separate file.

  figures/                       The four figures as separate PDFs, in
                                 case the journal requires them
                                 individually:
    Figure_1.pdf  Combined PRISMA-style flow across 5 reviews
    Figure_2.pdf  Per-model v2 extraction accuracy (4 LLMs x 5 reviews)
    Figure_3.pdf  Per-field cross-domain accuracy heatmap
    Figure_4.pdf  Cost-quality frontier across the 4 LLMs

  source_files/                  LaTeX sources for the editor's records:
    paper_anonymized.tex         Main .tex file (peer-review version)
    paper_with_authors.tex       Camera-ready .tex
    references.bib               Bibliography (104 verified entries)
    cas-sc.cls, cas-common.sty,
    cas-model2-names.bst         Elsevier CAS template files
    thumbnails/                  Logo icons used by the template
    compile.sh                   Build script (uses tectonic with
                                 pdflatex+bibtex fallback)
    figures/                     Figure scripts (.py) and rendered
                                 outputs (.pdf, .png)


Editorial Manager upload order
------------------------------

When you click "Submit New Manuscript" in Editorial Manager and reach
the Files step, upload the items in this order. The Item Type column
shows the dropdown choice to select for each file in EM.

  Order  Item Type             File to upload
  -----  --------------------  ----------------------------------------
   1     Cover Letter          01_Cover_Letter.pdf
   2     Title Page            02_Title_Page.pdf
   3     Highlights            03_Highlights.pdf
   4     Manuscript            04_Manuscript_anonymized.pdf
   5     Conflict of Interest  06_Declaration_of_Interest.pdf
   6     ORCID                 07_ORCID.pdf
   7     Figure (x4)           figures/Figure_1.pdf .. Figure_4.pdf
   8     Optional source       source_files/  (zip on request)

The author manuscript (05_Manuscript_with_authors.pdf) is NOT
typically uploaded; it is included for your reference only.


Generative-AI declaration
-------------------------

The required Elsevier declaration appears in the manuscript file
immediately before the references section, per Editorial Manager
guidance.


Reproducibility
---------------

All code, prompts, ground-truth files and per-paper model outputs are
publicly available at:

  https://github.com/bhaskargurram-ai/agentic-slr
