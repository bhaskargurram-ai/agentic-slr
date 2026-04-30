#!/usr/bin/env bash
# compile.sh — Build paper_anonymized.pdf and paper_with_authors.pdf
# Requires: pdflatex, bibtex (TeX Live or MacTeX).
#
# Usage:  ./compile.sh           # builds both versions
#         ./compile.sh anon      # builds anonymised only
#         ./compile.sh authors   # builds author version only
#         ./compile.sh clean     # removes intermediate files
set -euo pipefail
cd "$(dirname "$0")"

build_one() {
    local stem="$1"
    echo "==> Building ${stem}.pdf"
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    bibtex "${stem}" || true
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    echo "    -> ${stem}.pdf"
}

clean() {
    echo "==> Cleaning intermediate files"
    rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.spl
}

case "${1:-both}" in
    anon)    build_one paper_anonymized ;;
    authors) build_one paper_with_authors ;;
    both)    build_one paper_anonymized; build_one paper_with_authors ;;
    clean)   clean ;;
    *)       echo "Usage: $0 [anon|authors|both|clean]"; exit 1 ;;
esac

echo "Done."
