#!/usr/bin/env bash
# compile.sh — Build paper_anonymized.pdf and paper_with_authors.pdf
#
# Preferred engine: tectonic (single-binary self-contained TeX engine).
#   Install: brew install tectonic
# Fallback: pdflatex + bibtex (TeX Live / MacTeX).
#
# Usage:  ./compile.sh           # builds both versions
#         ./compile.sh anon      # anonymised only
#         ./compile.sh authors   # author version only
#         ./compile.sh clean     # remove intermediate / output files
set -euo pipefail
cd "$(dirname "$0")"

build_with_tectonic() {
    local stem="$1"
    echo "==> [tectonic] Building ${stem}.pdf"
    tectonic -X compile "${stem}.tex" >/dev/null 2>&1 || \
        tectonic -X compile "${stem}.tex"
    echo "    -> ${stem}.pdf"
}

build_with_pdflatex() {
    local stem="$1"
    echo "==> [pdflatex] Building ${stem}.pdf"
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    bibtex "${stem}" || true
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}.tex" >/dev/null
    echo "    -> ${stem}.pdf"
}

build_one() {
    if command -v tectonic >/dev/null 2>&1; then
        build_with_tectonic "$1"
    elif command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
        build_with_pdflatex "$1"
    else
        echo "ERROR: neither tectonic nor pdflatex+bibtex is installed." >&2
        echo "Install one with:  brew install tectonic" >&2
        exit 1
    fi
}

clean() {
    echo "==> Cleaning intermediate and output files"
    rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.spl *.pdf
}

case "${1:-both}" in
    anon)    build_one paper_anonymized ;;
    authors) build_one paper_with_authors ;;
    both)    build_one paper_anonymized; build_one paper_with_authors ;;
    clean)   clean ;;
    *)       echo "Usage: $0 [anon|authors|both|clean]"; exit 1 ;;
esac

echo "Done."
