"""
De-duplication / Primary-Publication Agent (v2: Embedding-Cluster Approach)
Identifies post-hoc analyses, sub-studies, or secondary publications of
already-included primary RCTs. This mirrors PRISMA's "multiple reports of the
same study" step.

Two-stage approach:
  Stage A: Embed title+abstract with text-embedding-3-small, cluster by cosine similarity.
  Stage B: Within each cluster, run LLM PRIMARY/SECONDARY classifier.
           Singleton clusters auto-classify as PRIMARY (no LLM call).

Usage:
  python agents/dedup_agent.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import math
import sys
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CLASSIFY_MODEL = "gpt-4o"  # Use gpt-4o for classification (more capable for nuanced dedup)
EMBEDDING_MODEL = "text-embedding-3-small"

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths


def _load_dedup_prompt(config: dict) -> str:
    """Load dedup system prompt from the file specified in config."""
    prompt_path = config.get("prompts", {}).get("dedup_system")
    if not prompt_path:
        raise FileNotFoundError("Config missing 'prompts.dedup_system' path.")
    p = Path(prompt_path)
    if not p.exists():
        raise FileNotFoundError(f"Dedup prompt file not found: {p}")
    return p.read_text().strip()


USER_PROMPT_TEMPLATE = """Here are all {n} candidate papers that passed full-text eligibility. Identify PRIMARY vs SECONDARY publications.

{papers}

For each paper, decide PRIMARY or SECONDARY. If SECONDARY, name the PMID of the primary trial it derives from (choose from this list)."""


class PaperClassification(BaseModel):
    pmid: str
    classification: str = Field(description="'PRIMARY' or 'SECONDARY'")
    confidence: float = Field(ge=0.0, le=1.0)
    parent_pmid: str | None = Field(default=None, description="If SECONDARY, the PMID of the primary trial paper")
    reasoning: str = Field(description="1-2 sentences")


class DedupResult(BaseModel):
    classifications: list[PaperClassification]


# ---------------------------------------------------------------------------
# Stage A: Embedding
# ---------------------------------------------------------------------------

def compute_embeddings(records: list[dict]) -> tuple[dict, dict]:
    """Compute embeddings for each paper's title+abstract.

    Returns:
        embeddings: dict mapping pmid -> list[float] (1536-dim)
        stats: dict with token/cost info
    """
    texts = {}
    for r in records:
        title = r.get("title", "")
        abstract = r.get("abstract", "")[:2000]
        texts[r["pmid"]] = f"{title}\n\n{abstract}"

    # Batch embed (API supports up to 2048 inputs)
    pmid_list = list(texts.keys())
    text_list = [texts[p] for p in pmid_list]

    total_tokens = 0
    all_vectors = []

    BATCH = 100
    for start in range(0, len(text_list), BATCH):
        batch_texts = text_list[start:start + BATCH]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch_texts,
        )
        for item in response.data:
            all_vectors.append(item.embedding)
        total_tokens += response.usage.total_tokens
        if start + BATCH < len(text_list):
            time.sleep(0.1)

    embeddings = {pmid_list[i]: all_vectors[i] for i in range(len(pmid_list))}
    cost = total_tokens * 0.02 / 1_000_000  # $0.02 per 1M tokens
    stats = {
        "model": EMBEDDING_MODEL,
        "n_papers": len(embeddings),
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(cost, 6),
    }
    return embeddings, stats


# ---------------------------------------------------------------------------
# Stage A: Clustering
# ---------------------------------------------------------------------------

def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def cluster_papers(
    embeddings: dict[str, list[float]],
    threshold: float = 0.55,
) -> tuple[list[list[str]], dict]:
    """Cluster papers by cosine similarity using Union-Find.

    Returns:
        clusters: list of lists of PMIDs (connected components)
        sim_stats: similarity distribution info
    """
    pmids = list(embeddings.keys())
    n = len(pmids)

    # Union-Find
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Compute pairwise similarities and build edges
    sim_pairs = []  # for stats
    edges_above = 0
    for i in range(n):
        for j in range(i + 1, n):
            sim = _cosine_sim(embeddings[pmids[i]], embeddings[pmids[j]])
            sim_pairs.append(sim)
            if sim > threshold:
                union(i, j)
                edges_above += 1

    # Extract connected components
    from collections import defaultdict
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(pmids[i])
    clusters = list(groups.values())

    # Similarity distribution stats
    sim_stats = {
        "total_pairs": len(sim_pairs),
        "edges_above_threshold": edges_above,
        "threshold": threshold,
    }
    if sim_pairs:
        sim_pairs_sorted = sorted(sim_pairs, reverse=True)
        sim_stats["pairs_above_0.70"] = sum(1 for s in sim_pairs if s > 0.70)
        sim_stats["pairs_above_0.60"] = sum(1 for s in sim_pairs if s > 0.60)
        sim_stats["pairs_above_0.55"] = sum(1 for s in sim_pairs if s > 0.55)
        sim_stats["pairs_above_0.50"] = sum(1 for s in sim_pairs if s > 0.50)
        sim_stats["max_similarity"] = round(sim_pairs_sorted[0], 4)
        sim_stats["median_similarity"] = round(sim_pairs_sorted[len(sim_pairs_sorted) // 2], 4)
        sim_stats["min_similarity"] = round(sim_pairs_sorted[-1], 4)

    return clusters, sim_stats


# ---------------------------------------------------------------------------
# Stage B: Per-cluster LLM classification
# ---------------------------------------------------------------------------

def _extract_trial_names(text: str) -> str:
    """Extract trial names / NCT numbers from text for dedup hint."""
    import re
    names = set()
    # Look for common trial name patterns
    for pattern in [
        r'(?:NCT\d{6,})',  # NCT registration numbers
        r'(?:GWPCARE\d[A-Za-z]*)',
        r'(?:DAPA-[A-Z0-9]+)',
        r'(?:DELIVER|DEFINE-HF|DECLARE|REFORM|EMPEROR)',
        r'(?:CheckMate[ -]\d+)',
        r'(?:KEYNOTE[ -]\d+)',
        r'(?:TRANSFORM[ -]\d+)',
        r'(?:ETHOS|KRONOS|STICLO)',
        r'(?:FAiRE-DS-\d)',
    ]:
        names.update(re.findall(pattern, text, re.IGNORECASE))
    return ", ".join(sorted(names)) if names else "none found"


def _extract_sample_size(text: str) -> str:
    """Try to extract sample size from text."""
    import re
    # Look for "N = XXX" or "XXX patients were randomized"
    patterns = [
        r'(\d+)\s+patients?\s+(?:were|was)\s+random',
        r'[Nn]\s*=\s*(\d+)\s+(?:patients?|participants?|subjects?)',
        r'enrolled\s+(\d+)\s+(?:patients?|participants?)',
        r'(?:random\w+)\s+(\d+)\s+(?:patients?|participants?)',
    ]
    for pat in patterns:
        m = re.search(pat, text[:10000])
        if m:
            return m.group(1) + " patients"
    return "not extracted"


def _classify_cluster(records: list[dict], system_prompt: str) -> list[dict]:
    """Run LLM classification on a single cluster of papers."""
    papers_text = ""
    for i, r in enumerate(records, 1):
        import re as _re
        full_text = r.get("clean_text", "") or r.get("abstract", "") or ""
        # Extract NCT numbers from full text
        ncts = sorted(set(_re.findall(r'NCT\d{6,}', full_text)))
        nct_str = ", ".join(ncts) if ncts else "not found"

        papers_text += f"\n--- Paper {i} ---\n"
        papers_text += f"PMID: {r['pmid']}\n"
        papers_text += f"TITLE: {r['title']}\n"
        papers_text += f"JOURNAL: {r.get('journal', '')} ({r.get('year', '')})\n"
        papers_text += f"NCT REGISTRATION: {nct_str}\n"
        papers_text += f"ABSTRACT: {r.get('abstract', '')[:1500]}\n"

    user_prompt = USER_PROMPT_TEMPLATE.format(n=len(records), papers=papers_text)

    response = client.chat.completions.parse(
        model=CLASSIFY_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=DedupResult,
        temperature=0.0,
    )
    return [c.model_dump() for c in response.choices[0].message.parsed.classifications]


def classify_all(records: list[dict], system_prompt: str = "", results_dir: Path = None) -> tuple[list[dict], dict]:
    """Classify papers using embedding-cluster approach.

    Returns:
        classifications: list of dicts with pmid, classification, parent_pmid, etc.
        clustering_info: dict with embedding stats, cluster info, similarity stats
    """
    record_by_pmid = {r["pmid"]: r for r in records}

    # Stage A: Embeddings
    print("  Stage A: Computing embeddings...")
    embeddings, embed_stats = compute_embeddings(records)
    print(f"    {embed_stats['n_papers']} papers embedded, {embed_stats['total_tokens']} tokens, ~${embed_stats['estimated_cost_usd']}")

    # Stage A: Clustering
    print("  Stage A: Clustering by cosine similarity...")
    clusters, sim_stats = cluster_papers(embeddings, threshold=0.55)

    cluster_sizes = sorted([len(c) for c in clusters], reverse=True)
    singletons = sum(1 for s in cluster_sizes if s == 1)
    multi = [s for s in cluster_sizes if s > 1]
    print(f"    {len(clusters)} clusters: {singletons} singletons, {len(multi)} multi-paper ({multi})")
    print(f"    Sim stats: {sim_stats['pairs_above_0.55']} pairs above 0.55, max={sim_stats.get('max_similarity', 'N/A')}")

    # Check for oversized clusters
    for c in clusters:
        if len(c) > 10:
            print(f"    WARNING: Cluster of size {len(c)} detected. Listing PMIDs:")
            for pmid in c[:15]:
                print(f"      - {pmid}: {record_by_pmid[pmid]['title'][:80]}")
            if len(c) > 15:
                print(f"      ... and {len(c) - 15} more")

    # Preserve original record order for deterministic LLM output
    original_order = {r["pmid"]: i for i, r in enumerate(records)}

    # Stage B: Per-cluster classification
    print("\n  Stage B: Per-cluster LLM classification...")
    all_classifications = []
    llm_calls = 0
    llm_tokens_in = 0
    llm_tokens_out = 0

    for idx, cluster_pmids in enumerate(clusters):
        # Sort cluster PMIDs by their original input order for determinism
        cluster_pmids = sorted(cluster_pmids, key=lambda p: original_order.get(p, 0))
        cluster_records = [record_by_pmid[p] for p in cluster_pmids]

        if len(cluster_pmids) == 1:
            # Singleton: auto-PRIMARY
            all_classifications.append({
                "pmid": cluster_pmids[0],
                "classification": "PRIMARY",
                "confidence": 1.0,
                "parent_pmid": None,
                "reasoning": "Singleton cluster — no similar papers in candidate pool.",
            })
        else:
            # Multi-paper cluster: LLM classification
            print(f"    Cluster {idx + 1}: {len(cluster_pmids)} papers -> LLM call")
            for r in cluster_records:
                print(f"      - {r['pmid']}: {r['title'][:70]}")
            results = _classify_cluster(cluster_records, system_prompt)
            all_classifications.extend(results)
            llm_calls += 1

    # Stage C: Post-classification validation
    # Override SECONDARY→PRIMARY if concrete evidence shows papers are different trials.
    # Uses only strong signals to avoid false overrides:
    #   1. Different NCT registration numbers (most reliable)
    #   2. Child paper's TITLE or early text contains a trial name absent from parent's TITLE
    #      (avoids false positives from discussion-section references to other trials)
    #   3. Very different sample sizes (>3x ratio)
    print("\n  Stage C: Post-classification validation...")
    import re as _re

    TRIAL_PATTERN = (
        r'(?:GWPCARE\d[A-Za-z]*|DAPA-[A-Z0-9]+|DELIVER|DEFINE-HF|DECLARE|REFORM|EMPEROR|'
        r'CheckMate[ -]\d+|KEYNOTE[ -]\d+|TRANSFORM[ -]\d+|ETHOS|KRONOS|STICLO|FAiRE-DS-\d)'
    )

    overrides = 0
    for c in all_classifications:
        if c["classification"] != "SECONDARY" or not c.get("parent_pmid"):
            continue
        child_pmid = c["pmid"]
        parent_pmid = c["parent_pmid"]
        child_rec = record_by_pmid.get(child_pmid, {})
        parent_rec = record_by_pmid.get(parent_pmid, {})

        child_full = child_rec.get("clean_text", "") or child_rec.get("abstract", "")
        parent_full = parent_rec.get("clean_text", "") or parent_rec.get("abstract", "")

        override_reasons = []

        # Check 1: Different NCT numbers → different trials (strong signal)
        child_ncts = set(_re.findall(r'NCT\d{6,}', child_full))
        parent_ncts = set(_re.findall(r'NCT\d{6,}', parent_full))
        if child_ncts and parent_ncts and not (child_ncts & parent_ncts):
            override_reasons.append(f"different NCTs: child={child_ncts}, parent={parent_ncts}")

        # Check 2: Trial name in child's TITLE or methods section that parent's TITLE/methods lacks
        # Uses first 5000 chars (covers abstract + intro + methods in typical PMC articles)
        # but NOT the full text (to avoid discussion-section references)
        child_title = child_rec.get("title", "")
        parent_title = parent_rec.get("title", "")
        child_early = child_title + " " + child_full[:5000]
        parent_early = parent_title + " " + parent_full[:5000]
        child_trial_names = set(_re.findall(TRIAL_PATTERN, child_early, _re.IGNORECASE))
        parent_trial_names = set(_re.findall(TRIAL_PATTERN, parent_early, _re.IGNORECASE))
        child_unique_early = child_trial_names - parent_trial_names
        if child_unique_early:
            override_reasons.append(f"child title/methods has trial name(s) absent from parent: {child_unique_early}")

        # Check 3: Very different sample sizes (>3x) → different trials
        child_n = _extract_sample_size(child_full)
        parent_n = _extract_sample_size(parent_full)
        if child_n != "not extracted" and parent_n != "not extracted":
            try:
                cn = int(child_n.split()[0])
                pn = int(parent_n.split()[0])
                if cn > 0 and pn > 0:
                    ratio = max(cn, pn) / min(cn, pn)
                    if ratio > 3.0:
                        override_reasons.append(f"sample sizes differ {ratio:.1f}x: child={cn}, parent={pn}")
            except ValueError:
                pass

        if override_reasons:
            c["classification"] = "PRIMARY"
            c["confidence"] = 0.8
            c["reasoning"] = f"OVERRIDE SECONDARY→PRIMARY: {'; '.join(override_reasons)}. Original: {c['reasoning']}"
            c["parent_pmid"] = None
            overrides += 1
            print(f"    OVERRIDE: {child_pmid} SECONDARY→PRIMARY ({'; '.join(override_reasons)})")

    if overrides:
        print(f"    {overrides} override(s) applied")
    else:
        print(f"    No overrides needed")

    # Save clustering details
    clustering_info = {
        "embedding_stats": embed_stats,
        "similarity_stats": sim_stats,
        "n_clusters": len(clusters),
        "cluster_sizes": cluster_sizes,
        "singletons": singletons,
        "multi_paper_clusters": len(multi),
        "llm_calls": llm_calls,
        "clusters_detail": [
            {"cluster_id": i, "pmids": c, "size": len(c)}
            for i, c in enumerate(clusters)
        ],
    }

    if results_dir:
        clustering_file = results_dir / "dedup_clustering.json"
        with open(clustering_file, "w") as f:
            json.dump(clustering_info, f, indent=2)
        print(f"\n  Clustering details saved to {clustering_file}")

    return all_classifications, clustering_info


def evaluate(final_included_pmids: list[str], ground_truth_path: Path) -> dict:
    with open(ground_truth_path) as f:
        gt = json.load(f)
    if "inclusion_pmids" in gt:
        positive = set(gt["inclusion_pmids"])
    else:
        positive = set(gt["evaluation_notes"]["primary_ground_truth_pmids"])
    final = set(final_included_pmids)

    tp = len(positive & final)
    fp = len(final - positive)
    fn = len(positive - final)
    sens = tp / (tp + fn) if (tp + fn) else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0

    return {
        "ground_truth_count": len(positive),
        "final_included_count": len(final),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "sensitivity": round(sens, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "missed_pmids": sorted(positive - final),
        "extra_pmids": sorted(final - positive),
    }


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    FULLTEXT_DECISIONS = paths["results_dir"] / "fulltext_decisions.json"
    FULLTEXT_POOL = paths["retrieved_dir"] / "fulltext_pool.json"
    OUTPUT_FILE = paths["results_dir"] / "dedup_decisions.json"
    GROUND_TRUTH_FILE = paths["ground_truth"]
    EVAL_FILE = paths["results_dir"] / "final_pipeline_evaluation.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    system_prompt = _load_dedup_prompt(config)
    print(f"Review: {config['short_name']} ({config['review_id']})")
    print(f"Dedup prompt loaded from: {config['prompts']['dedup_system']}")

    with open(FULLTEXT_DECISIONS) as f:
        ft = json.load(f)
    with open(FULLTEXT_POOL) as f:
        pool = json.load(f)
    pool_by_pmid = {r["pmid"]: r for r in pool["records"]}

    included = [d["pmid"] for d in ft["decisions"] if d["decision"] == "INCLUDE"]
    records = [pool_by_pmid[p] for p in included if p in pool_by_pmid]
    print(f"Classifying {len(records)} papers as PRIMARY or SECONDARY...\n")

    classifications, clustering_info = classify_all(
        records, system_prompt=system_prompt, results_dir=paths["results_dir"]
    )

    title_map = {r["pmid"]: r["title"] for r in records}
    final_included = []
    print("\nResults:")
    for c in classifications:
        mark = "PRIMARY  " if c["classification"] == "PRIMARY" else "SECONDARY"
        print(f"  {mark} PMID {c['pmid']}: {title_map.get(c['pmid'], '')[:70]}")
        if c["classification"] == "SECONDARY":
            parent_title = title_map.get(c["parent_pmid"], "?")
            print(f"               -> derived from PMID {c['parent_pmid']}: {parent_title[:60]}")
            print(f"               reason: {c['reasoning']}")
        else:
            final_included.append(c["pmid"])

    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "model": CLASSIFY_MODEL,
            "approach": "embedding-cluster-v2",
            "clustering_summary": {
                "n_clusters": clustering_info["n_clusters"],
                "singletons": clustering_info["singletons"],
                "multi_paper_clusters": clustering_info["multi_paper_clusters"],
                "cluster_sizes": clustering_info["cluster_sizes"],
                "llm_calls": clustering_info["llm_calls"],
                "embedding_cost_usd": clustering_info["embedding_stats"]["estimated_cost_usd"],
            },
            "classifications": classifications,
            "final_included_pmids": final_included,
        }, f, indent=2)

    print("\n" + "=" * 60)
    print("FINAL PIPELINE EVALUATION")
    print("=" * 60)
    metrics = evaluate(final_included, GROUND_TRUTH_FILE)
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    with open(EVAL_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    if metrics["sensitivity"] == 1.0 and metrics["precision"] >= 0.85:
        print("SUCCESS: Final inclusion set matches ground truth closely.")
    elif metrics["sensitivity"] == 1.0:
        print(f"ACCEPTABLE: All true positives retained, {metrics['false_positives']} FPs remain.")
    else:
        print(f"FAIL: Dedup agent lost {metrics['false_negatives']} true positive(s).")
    print("=" * 60)


if __name__ == "__main__":
    main()
