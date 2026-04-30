"""
v4: Trusts the NCBI ID Converter for PMCID verification, parses PMC XML when
available, falls back to rich structured abstracts + MeSH for closed-access papers.

Usage:
  python agents/fetch_fulltext.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import re
import sys
import requests
from pathlib import Path
from xml.etree import ElementTree as ET
from Bio import Entrez
from tqdm import tqdm

env_path = ".env"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths

ID_CONVERTER = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"

EXCLUDE_SECTIONS = {
    "references", "acknowledgments", "acknowledgements", "author contributions",
    "conflicts of interest", "conflict of interest", "funding", "declarations",
    "competing interests", "ethics approval", "consent", "data availability",
    "supplementary material", "supplementary information", "supporting information",
    "appendix", "abbreviations",
}


def clean_text(t):
    return re.sub(r"\s+", " ", t or "").strip()


def extract_all_text(el):
    parts = []
    if el.text: parts.append(el.text)
    for c in el:
        parts.append(extract_all_text(c))
        if c.tail: parts.append(c.tail)
    return "".join(parts)


def get_verified_pmcid(pmid):
    """Returns PMCID only if NCBI ID Converter reports a real mapping (no error)."""
    try:
        r = requests.get(ID_CONVERTER, params={
            "ids": pmid, "format": "json", "tool": "slr-agent", "email": os.getenv("NCBI_EMAIL"),
        }, timeout=15)
        rec = (r.json().get("records") or [{}])[0]
        if rec.get("status") == "error":
            return None
        return rec.get("pmcid")
    except Exception:
        return None


def fetch_pmc_xml(pmcid):
    try:
        handle = Entrez.efetch(db="pmc", id=pmcid.replace("PMC", ""), rettype="full", retmode="xml")
        text = handle.read()
        handle.close()
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")
        return text
    except Exception:
        return None


def parse_pmc(xml_text):
    result = {"title": "", "abstract": "", "sections": [], "clean_text": ""}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return result

    title_el = root.find(".//article-title")
    if title_el is not None:
        result["title"] = clean_text(extract_all_text(title_el))

    abstract_el = root.find(".//abstract")
    if abstract_el is not None:
        parts = []
        for sec in abstract_el.findall(".//sec"):
            title_sub = sec.find("title")
            t = clean_text(extract_all_text(title_sub)) if title_sub is not None else ""
            txt = clean_text(extract_all_text(sec))
            if t and txt.lower().startswith(t.lower()):
                txt = txt[len(t):].strip()
            parts.append(f"{t}: {txt}" if t else txt)
        if not parts:
            parts.append(clean_text(extract_all_text(abstract_el)))
        result["abstract"] = "\n".join(parts)

    body = root.find(".//body")
    if body is not None:
        for sec in body.findall(".//sec"):
            title_el = sec.find("title")
            if title_el is None: continue
            t = clean_text(extract_all_text(title_el))
            tl = t.lower()
            if any(ex in tl for ex in EXCLUDE_SECTIONS): continue
            txt = clean_text(extract_all_text(sec))
            if txt.lower().startswith(tl):
                txt = txt[len(t):].strip()
            result["sections"].append({"title": t, "text": txt})

    parts = []
    if result["abstract"]:
        parts.append("ABSTRACT\n" + result["abstract"])
    for s in result["sections"]:
        parts.append(f"\n{s['title'].upper()}\n{s['text']}")
    result["clean_text"] = "\n\n".join(parts)
    return result


def fetch_pubmed_rich(pmid):
    try:
        h = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="xml")
        data = Entrez.read(h); h.close()
        if not data.get("PubmedArticle"):
            return {}
        article = data["PubmedArticle"][0]
        med = article["MedlineCitation"]
        art = med["Article"]
        title = str(art.get("ArticleTitle", ""))
        journal = str(art.get("Journal", {}).get("Title", ""))
        pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        year = str(pub_date.get("Year", pub_date.get("MedlineDate", "")))[:4]
        authors = []
        for author in art.get("AuthorList", []):
            last = author.get("LastName", "")
            init = author.get("Initials", "")
            if last:
                authors.append(f"{last} {init}".strip())
        abstract_parts = art.get("Abstract", {}).get("AbstractText", [])
        structured_abs = ""
        for p in abstract_parts:
            label = getattr(p, "attributes", {}).get("Label", "")
            structured_abs += (f"{label}: " if label else "") + str(p) + "\n"
        mesh = []
        for mh in med.get("MeshHeadingList", []):
            desc = str(mh.get("DescriptorName", ""))
            quals = [str(q) for q in mh.get("QualifierName", [])]
            mesh.append(desc + (f" / {', '.join(quals)}" if quals else ""))
        pub_types = [str(pt) for pt in art.get("PublicationTypeList", [])]
        return {
            "title": title, "journal": journal, "year": year,
            "authors": authors, "abstract": structured_abs.strip(),
            "mesh_terms": mesh, "publication_types": pub_types,
        }
    except Exception:
        return {}


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    DEDUP_FILE = paths["results_dir"] / "dedup_decisions.json"
    SCREENING_FILE = paths["results_dir"] / "screening_decisions.json"
    OUTPUT_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    PUBMED_RESULTS = paths["retrieved_dir"] / "pubmed_results.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Review: {config['short_name']} ({config['review_id']})")

    # Determine which PMIDs to fetch full text for.
    # Prefer dedup (post-pipeline), fall back to screening (mid-pipeline).
    if DEDUP_FILE.exists():
        with open(DEDUP_FILE) as f:
            final_pmids = json.load(f)["final_included_pmids"]
        print(f"Source: dedup_decisions.json ({len(final_pmids)} PMIDs)")
    elif SCREENING_FILE.exists():
        with open(SCREENING_FILE) as f:
            decisions = json.load(f)["decisions"]
        final_pmids = [d["pmid"] for d in decisions if d["decision"] == "INCLUDE"]
        print(f"Source: screening_decisions.json ({len(final_pmids)} INCLUDE PMIDs)")
    else:
        raise FileNotFoundError(
            f"Neither {DEDUP_FILE} nor {SCREENING_FILE} found. "
            "Run screening or dedup first."
        )
    # Load existing retrieved records as fallback metadata
    pool = {}
    if PUBMED_RESULTS.exists():
        with open(PUBMED_RESULTS) as f:
            pool = {r["pmid"]: r for r in json.load(f).get("records", [])}

    print(f"Fetching v4 (verified) full text for {len(final_pmids)} studies...\n")

    enriched = []
    for pmid in tqdm(final_pmids, desc="Processing"):
        verified_pmcid = get_verified_pmcid(pmid)
        rich_pm = fetch_pubmed_rich(pmid)
        base = pool.get(pmid, {})

        source = "abstract_only"
        clean = {"title": "", "abstract": "", "sections": [], "clean_text": ""}

        if verified_pmcid:
            xml_text = fetch_pmc_xml(verified_pmcid)
            if xml_text:
                clean = parse_pmc(xml_text)
                if clean["clean_text"] and len(clean["clean_text"]) > 5000:
                    source = "pmc_fulltext_verified"

        if source == "abstract_only":
            parts = []
            if rich_pm.get("title") or base.get("title"):
                parts.append("TITLE\n" + (rich_pm.get("title") or base.get("title", "")))
            if rich_pm.get("abstract"):
                parts.append("STRUCTURED ABSTRACT\n" + rich_pm["abstract"])
            elif base.get("abstract"):
                parts.append("ABSTRACT\n" + base["abstract"])
            if rich_pm.get("mesh_terms"):
                parts.append("MESH TERMS\n" + "\n".join(f"- {m}" for m in rich_pm["mesh_terms"]))
            if rich_pm.get("publication_types"):
                parts.append("PUBLICATION TYPES\n" + ", ".join(rich_pm["publication_types"]))
            clean["clean_text"] = "\n\n".join(parts)
            clean["abstract"] = rich_pm.get("abstract", base.get("abstract", ""))

        enriched.append({
            "pmid": pmid,
            "pmcid": verified_pmcid,
            "source": source,
            "title": rich_pm.get("title") or base.get("title", ""),
            "authors": rich_pm.get("authors") or base.get("authors", []),
            "journal": rich_pm.get("journal") or base.get("journal", ""),
            "year": rich_pm.get("year") or base.get("year", ""),
            "mesh_terms": rich_pm.get("mesh_terms", []),
            "publication_types": rich_pm.get("publication_types", []),
            "abstract": clean.get("abstract", ""),
            "section_count": len(clean.get("sections", [])),
            "section_titles": [s["title"] for s in clean.get("sections", [])],
            "clean_text": clean.get("clean_text", ""),
        })
        time.sleep(0.2)

    with open(OUTPUT_FILE, "w") as f:
        json.dump({"total": len(enriched), "records": enriched}, f, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}\n")
    print(f"{'PMID':<12} {'source':<30} {'chars':>8} {'sects':>6}  key-terms")
    for r in enriched:
        ct = r["clean_text"].lower()
        has = {k: (k in ct) for k in ["placebo", "mg/kg", "randomiz", "seizure"]}
        print(f"{r['pmid']:<12} {r['source']:<30} {len(r['clean_text']):>8} {r['section_count']:>6}  {has}")


if __name__ == "__main__":
    main()
