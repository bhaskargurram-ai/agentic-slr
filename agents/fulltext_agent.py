"""
Full-Text Assessment Agent (Second-stage LLM agent)
Takes papers that passed abstract screening and applies strict eligibility
criteria using full text + MeSH terms + extended metadata.
Goal: eliminate false positives while keeping all true positives.

Usage:
  python agents/fulltext_agent.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import sys
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths

def _load_fulltext_prompt(config: dict) -> str:
    """Load fulltext system prompt from the file specified in config."""
    prompt_path = config.get("prompts", {}).get("fulltext_system")
    if not prompt_path:
        raise FileNotFoundError("Config missing 'prompts.fulltext_system' path. Each review must specify its fulltext prompt file.")
    p = Path(prompt_path)
    if not p.exists():
        raise FileNotFoundError(f"Fulltext prompt file not found: {p}")
    return p.read_text().strip()

USER_PROMPT_TEMPLATE = """Assess this paper for final inclusion in the systematic review:

PMID: {pmid}
TITLE: {title}
JOURNAL: {journal} ({year})
PUBLICATION TYPES: {pub_types}

MESH TERMS:
{mesh_terms}

KEYWORDS:
{keywords}

FULL ABSTRACT:
{abstract}

FULL TEXT EXCERPT (first ~20k chars):
{fulltext}

Apply the strict eligibility criteria and make the final INCLUDE/EXCLUDE decision."""


class FulltextDecision(BaseModel):
    decision: str = Field(description="'INCLUDE' or 'EXCLUDE'")
    confidence: float = Field(ge=0.0, le=1.0)
    study_design: str = Field(description="e.g., 'Phase III parallel-group RCT', 'Narrative review', 'Open-label extension'")
    population_match: bool = Field(description="Does the population include Dravet syndrome patients per inclusion criteria?")
    intervention_is_asm: bool = Field(description="Is the intervention an antiseizure medication?")
    has_randomized_phase: bool = Field(description="Does the paper report a randomized controlled phase?")
    primary_reasoning: str = Field(description="2-3 sentence justification citing specific evidence from the text")
    flag_for_human_review: bool = Field(default=False, description="True if the decision is borderline")


def assess_paper(record: dict, system_prompt: str = "") -> dict:
    user_prompt = USER_PROMPT_TEMPLATE.format(
        pmid=record["pmid"],
        title=record["title"],
        journal=record.get("journal", ""),
        year=record.get("year", ""),
        pub_types=", ".join(record.get("publication_types", [])),
        mesh_terms="\n".join(f"- {m}" for m in record.get("mesh_terms", [])) or "[None]",
        keywords=", ".join(record.get("keywords", [])) or "[None]",
        abstract=record.get("abstract", "")[:5000],
        fulltext=(record.get("fulltext_excerpt") or "[Full text not available]")[:15000],
    )

    try:
        response = client.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=FulltextDecision,
            temperature=0.0,
        )
        p = response.choices[0].message.parsed
        return {
            "pmid": record["pmid"],
            "title": record["title"],
            "decision": p.decision,
            "confidence": p.confidence,
            "study_design": p.study_design,
            "population_match": p.population_match,
            "intervention_is_asm": p.intervention_is_asm,
            "has_randomized_phase": p.has_randomized_phase,
            "reasoning": p.primary_reasoning,
            "flag_for_human_review": p.flag_for_human_review,
            "error": None,
        }
    except Exception as e:
        return {
            "pmid": record["pmid"],
            "title": record["title"],
            "decision": "ERROR",
            "reasoning": f"API error: {e}",
            "error": str(e),
        }


def evaluate(decisions: list[dict], ground_truth_path: Path) -> dict:
    from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report

    with open(ground_truth_path) as f:
        gt = json.load(f)
    if "inclusion_pmids" in gt:
        positive_pmids = set(gt["inclusion_pmids"])
    else:
        positive_pmids = set(gt["evaluation_notes"]["primary_ground_truth_pmids"])

    y_true, y_pred = [], []
    for d in decisions:
        if d["decision"] == "ERROR":
            continue
        y_true.append(1 if d["pmid"] in positive_pmids else 0)
        y_pred.append(1 if d["decision"] == "INCLUDE" else 0)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) else 0
    spec = tn / (tn + fp) if (tn + fp) else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0

    return {
        "total_assessed": len(y_true),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "sensitivity": round(sens, 4),
        "specificity": round(spec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "cohen_kappa": round(cohen_kappa_score(y_true, y_pred), 4),
        "report": classification_report(y_true, y_pred, target_names=["EXCLUDE", "INCLUDE"], zero_division=0),
    }


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    INPUT_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    OUTPUT_FILE = paths["results_dir"] / "fulltext_decisions.json"
    GROUND_TRUTH_FILE = paths["ground_truth"]
    EVAL_FILE = paths["results_dir"] / "fulltext_evaluation.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    system_prompt = _load_fulltext_prompt(config)
    print(f"Review: {config['short_name']} ({config['review_id']})")
    print(f"Fulltext prompt loaded from: {config['prompts']['fulltext_system']}")

    with open(INPUT_FILE) as f:
        data = json.load(f)
    records = data["records"]
    print(f"Full-text assessment of {len(records)} papers with {MODEL}...\n")

    decisions = []
    for rec in tqdm(records, desc="Assessing"):
        decisions.append(assess_paper(rec, system_prompt=system_prompt))
        time.sleep(0.05)

    with open(OUTPUT_FILE, "w") as f:
        json.dump({"model": MODEL, "total": len(decisions), "decisions": decisions}, f, indent=2)
    print(f"\nSaved to {OUTPUT_FILE}")

    metrics = evaluate(decisions, GROUND_TRUTH_FILE)
    print("\n" + "=" * 60)
    print("FULL-TEXT ASSESSMENT - EVALUATION")
    print("=" * 60)
    for k, v in metrics.items():
        if k != "report":
            print(f"  {k}: {v}")
    print("\n" + metrics["report"])

    with open(GROUND_TRUTH_FILE) as f:
        gt = json.load(f)
    if "inclusion_pmids" in gt:
        positive_pmids = set(gt["inclusion_pmids"])
    else:
        positive_pmids = set(gt["evaluation_notes"]["primary_ground_truth_pmids"])
    n_gt = len(positive_pmids)

    fn = [d for d in decisions if d["pmid"] in positive_pmids and d["decision"] == "EXCLUDE"]
    if fn:
        print(f"\nFALSE NEGATIVES ({len(fn)} - CRITICAL, must fix):")
        for d in fn:
            print(f"  - PMID {d['pmid']}: {d['title'][:80]}")
            print(f"    Design parsed as: {d.get('study_design')}")
            print(f"    Reason: {d['reasoning']}")

    fp = [d for d in decisions if d["pmid"] not in positive_pmids and d["decision"] == "INCLUDE"]
    if fp:
        print(f"\nFalse positives remaining ({len(fp)}):")
        for d in fp[:5]:
            print(f"  - PMID {d['pmid']}: {d['title'][:80]}")
            print(f"    Parsed as: {d.get('study_design')}")

    tp_list = [d for d in decisions if d["pmid"] in positive_pmids and d["decision"] == "INCLUDE"]
    print(f"\nTRUE POSITIVES correctly included: {len(tp_list)}/{n_gt}")
    for d in tp_list:
        print(f"  - PMID {d['pmid']}: {d['title'][:80]}")

    with open(EVAL_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    if metrics["sensitivity"] == 1.0 and metrics["specificity"] >= 0.85:
        print("SUCCESS: Full pipeline produces clean inclusion set.")
    elif metrics["sensitivity"] == 1.0:
        print(f"PARTIAL: All true positives kept, but {metrics['false_positives']} FPs remain.")
    else:
        print(f"FAIL: Lost {metrics['false_negatives']} true positive(s). Must tune criteria.")
    print("=" * 60)


if __name__ == "__main__":
    main()
