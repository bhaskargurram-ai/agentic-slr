"""
Retrieval Agent
Queries PubMed using the search strategy from a review's config.
Goal: Retrieve candidate studies for systematic review screening.
Success criterion: recall >= 100% against ground_truth PMIDs.

Usage:
  python agents/retrieval_agent.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import argparse
from pathlib import Path
from Bio import Entrez
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")

# --- Config loading ---
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths


def search_pubmed(query: str, max_results: int = 2000) -> list[str]:
    """Run ESearch on PubMed, return list of PMIDs."""
    print(f"Searching PubMed with query:\n{query}\n")
    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        sort="relevance",
    )
    result = Entrez.read(handle)
    handle.close()
    pmids = result["IdList"]
    print(f"Found {len(pmids)} PMIDs (total matching: {result['Count']})")
    return pmids


def fetch_metadata(pmids: list[str], batch_size: int = 100) -> list[dict]:
    """Fetch title, abstract, authors, journal for each PMID in batches."""
    records = []
    for i in tqdm(range(0, len(pmids), batch_size), desc="Fetching metadata"):
        batch = pmids[i : i + batch_size]
        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(batch),
            rettype="medline",
            retmode="xml",
        )
        data = Entrez.read(handle)
        handle.close()

        for article in data.get("PubmedArticle", []):
            try:
                medline = article["MedlineCitation"]
                pmid = str(medline["PMID"])
                art = medline["Article"]
                title = str(art.get("ArticleTitle", ""))

                abstract_parts = art.get("Abstract", {}).get("AbstractText", [])
                if abstract_parts:
                    abstract = " ".join(str(p) for p in abstract_parts)
                else:
                    abstract = ""

                journal = str(art.get("Journal", {}).get("Title", ""))
                year = ""
                pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                year = str(pub_date.get("Year", pub_date.get("MedlineDate", "")))[:4]

                authors = []
                for author in art.get("AuthorList", []):
                    last = author.get("LastName", "")
                    initials = author.get("Initials", "")
                    if last:
                        authors.append(f"{last} {initials}".strip())

                pub_types = [str(pt) for pt in art.get("PublicationTypeList", [])]

                records.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "authors": authors[:10],
                    "publication_types": pub_types,
                })
            except Exception as e:
                print(f"Error parsing record: {e}")
                continue
        time.sleep(0.15)  # Respect NCBI rate limit with API key (10 req/s)
    return records


def evaluate_recall(retrieved_pmids: list[str], ground_truth_path: str) -> dict:
    """Check how many ground-truth PMIDs are in retrieved set."""
    with open(ground_truth_path) as f:
        gt = json.load(f)
    # Support both old format (evaluation_notes.primary_ground_truth_pmids) and new (inclusion_pmids)
    if "inclusion_pmids" in gt:
        target_pmids = gt["inclusion_pmids"]
    else:
        target_pmids = gt["evaluation_notes"]["primary_ground_truth_pmids"]
    retrieved_set = set(retrieved_pmids)
    found = [p for p in target_pmids if p in retrieved_set]
    missed = [p for p in target_pmids if p not in retrieved_set]
    recall = len(found) / len(target_pmids) if target_pmids else 0
    return {
        "target_count": len(target_pmids),
        "found_count": len(found),
        "missed_count": len(missed),
        "recall": recall,
        "found_pmids": found,
        "missed_pmids": missed,
        "included_studies_details": gt.get("included_studies", []),
    }


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    SEARCH_QUERY = config["search"]["pubmed_query"]
    max_results = config["search"].get("max_results", 2000)
    OUTPUT_FILE = paths["retrieved_dir"] / "pubmed_results.json"
    GROUND_TRUTH_FILE = paths["ground_truth"]
    EVAL_FILE = paths["results_dir"] / "retrieval_evaluation.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Review: {config['short_name']} ({config['review_id']})")
    pmids = search_pubmed(SEARCH_QUERY, max_results=max_results)

    if not pmids:
        print("ERROR: No results from PubMed. Check query or API key.")
        return

    print(f"\nFetching metadata for {len(pmids)} records...")
    records = fetch_metadata(pmids)
    print(f"Successfully parsed {len(records)} records.\n")

    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "query": SEARCH_QUERY,
            "total_retrieved": len(records),
            "records": records,
        }, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")

    print("\n" + "=" * 60)
    print("EVALUATION: Recall vs ground truth")
    print("=" * 60)
    eval_result = evaluate_recall(
        [r["pmid"] for r in records],
        str(GROUND_TRUTH_FILE),
    )
    print(f"Target PMIDs: {eval_result['target_count']}")
    print(f"Found:        {eval_result['found_count']}")
    print(f"Missed:       {eval_result['missed_count']}")
    print(f"RECALL:       {eval_result['recall']:.2%}")

    if eval_result["missed_pmids"]:
        print("\nMissed PMIDs (NOT retrieved - we need to fix the query):")
        study_map = {s["pmid"]: s for s in eval_result["included_studies_details"] if s["pmid"]}
        for pmid in eval_result["missed_pmids"]:
            study = study_map.get(pmid, {})
            print(f"  - PMID {pmid}: {study.get('first_author', '?')} {study.get('year', '')} ({study.get('short_name', '')})")
            print(f"    {study.get('title', '')[:120]}")

    with open(EVAL_FILE, "w") as f:
        json.dump(eval_result, f, indent=2)
    print(f"\nEvaluation saved to {EVAL_FILE}")

    print("\n" + "=" * 60)
    if eval_result["recall"] >= 1.0:
        print("SUCCESS: 100% recall achieved. Ready for screening.")
    elif eval_result["recall"] >= 0.85:
        print("PARTIAL: >=85% recall. Acceptable but should investigate missed papers.")
    else:
        print("FAIL: Recall too low. Query needs expansion before proceeding.")
    print("=" * 60)


if __name__ == "__main__":
    main()
