"""
Screening Agent (OpenAI)
Reads title + abstract, applies eligibility criteria from config,
returns structured include/exclude decision with reasoning.

Usage:
  python agents/screening_agent.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import argparse
import sys
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"  # cheap, fast, strong enough for classification

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths

def _load_screening_prompt(config: dict) -> str:
    """Load screening system prompt from the file specified in config."""
    prompt_path = config.get("prompts", {}).get("screening_system")
    if not prompt_path:
        raise FileNotFoundError("Config missing 'prompts.screening_system' path. Each review must specify its screening prompt file.")
    p = Path(prompt_path)
    if not p.exists():
        raise FileNotFoundError(f"Screening prompt file not found: {p}")
    return p.read_text().strip()

USER_PROMPT_TEMPLATE = """Please screen the following paper:

PMID: {pmid}
TITLE: {title}
JOURNAL: {journal} ({year})
PUBLICATION TYPES: {pub_types}

ABSTRACT:
{abstract}

Decide INCLUDE or EXCLUDE and provide brief reasoning."""


class ScreeningDecision(BaseModel):
    decision: str = Field(description="Either 'INCLUDE' or 'EXCLUDE'")
    confidence: float = Field(description="0.0 to 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="1-2 sentence justification")
    matched_criteria: list[str] = Field(description="Which inclusion criteria the paper satisfies", default_factory=list)
    violated_criteria: list[str] = Field(description="Which exclusion criteria were triggered, if any", default_factory=list)


def screen_paper(record: dict, system_prompt: str = "") -> dict:
    """Screen a single paper via OpenAI structured output."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        pmid=record["pmid"],
        title=record["title"],
        journal=record.get("journal", ""),
        year=record.get("year", ""),
        pub_types=", ".join(record.get("publication_types", [])),
        abstract=record.get("abstract", "[No abstract available]"),
    )

    try:
        response = client.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ScreeningDecision,
            temperature=0.0,
        )
        parsed = response.choices[0].message.parsed
        return {
            "pmid": record["pmid"],
            "title": record["title"],
            "decision": parsed.decision,
            "confidence": parsed.confidence,
            "reasoning": parsed.reasoning,
            "matched_criteria": parsed.matched_criteria,
            "violated_criteria": parsed.violated_criteria,
            "error": None,
        }
    except Exception as e:
        return {
            "pmid": record["pmid"],
            "title": record["title"],
            "decision": "ERROR",
            "confidence": 0.0,
            "reasoning": f"API error: {e}",
            "matched_criteria": [],
            "violated_criteria": [],
            "error": str(e),
        }


def evaluate(decisions: list[dict], ground_truth_path: Path) -> dict:
    """Compute sensitivity, specificity, precision, F1, Cohen's kappa."""
    from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report

    with open(ground_truth_path) as f:
        gt = json.load(f)
    if "inclusion_pmids" in gt:
        positive_pmids = set(gt["inclusion_pmids"])
    else:
        positive_pmids = set(gt["evaluation_notes"]["primary_ground_truth_pmids"])

    y_true = []
    y_pred = []
    for d in decisions:
        if d["decision"] == "ERROR":
            continue
        truth = 1 if d["pmid"] in positive_pmids else 0
        pred = 1 if d["decision"] == "INCLUDE" else 0
        y_true.append(truth)
        y_pred.append(pred)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * sensitivity / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
    kappa = cohen_kappa_score(y_true, y_pred)

    return {
        "total_screened": len(y_true),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "sensitivity_recall": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "cohen_kappa": round(kappa, 4),
        "classification_report": classification_report(y_true, y_pred, target_names=["EXCLUDE", "INCLUDE"], zero_division=0),
    }


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    INPUT_FILE = paths["retrieved_dir"] / "pubmed_results.json"
    OUTPUT_FILE = paths["results_dir"] / "screening_decisions.json"
    GROUND_TRUTH_FILE = paths["ground_truth"]
    EVAL_FILE = paths["results_dir"] / "screening_evaluation.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    system_prompt = _load_screening_prompt(config)
    print(f"Review: {config['short_name']} ({config['review_id']})")
    print(f"Screening prompt loaded from: {config['prompts']['screening_system']}")

    with open(INPUT_FILE) as f:
        data = json.load(f)
    records = data["records"]
    print(f"Screening {len(records)} papers with {MODEL}...\n")

    decisions = []
    for rec in tqdm(records, desc="Screening"):
        decisions.append(screen_paper(rec, system_prompt=system_prompt))
        time.sleep(0.05)  # Gentle rate limiting

    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "model": MODEL,
            "total": len(decisions),
            "decisions": decisions,
        }, f, indent=2)
    print(f"\nDecisions saved to {OUTPUT_FILE}")

    # Evaluation
    print("\n" + "=" * 60)
    print("EVALUATION: Screening vs ground truth")
    print("=" * 60)
    metrics = evaluate(decisions, GROUND_TRUTH_FILE)
    for k, v in metrics.items():
        if k != "classification_report":
            print(f"  {k}: {v}")
    print("\nClassification report:")
    print(metrics["classification_report"])

    # List false negatives (missed relevant papers) and false positives
    with open(GROUND_TRUTH_FILE) as f:
        gt = json.load(f)
    if "inclusion_pmids" in gt:
        positive_pmids = set(gt["inclusion_pmids"])
    else:
        positive_pmids = set(gt["evaluation_notes"]["primary_ground_truth_pmids"])

    fn_papers = [d for d in decisions if d["pmid"] in positive_pmids and d["decision"] == "EXCLUDE"]
    if fn_papers:
        print(f"\nFALSE NEGATIVES ({len(fn_papers)} relevant papers incorrectly excluded):")
        for d in fn_papers:
            print(f"  - PMID {d['pmid']}: {d['title'][:80]}")
            print(f"    Reason given: {d['reasoning']}")

    fp_papers = [d for d in decisions if d["pmid"] not in positive_pmids and d["decision"] == "INCLUDE"]
    print(f"\nFalse positives (over-inclusion): {len(fp_papers)}")
    print(f"  (Acceptable - these would be filtered at full-text stage in real SLR)")

    with open(EVAL_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    if metrics["sensitivity_recall"] >= 0.95 and metrics["cohen_kappa"] >= 0.6:
        print("SUCCESS: Screening performance meets targets.")
    elif metrics["sensitivity_recall"] >= 0.95:
        print("PARTIAL: Sensitivity OK, but kappa low - too many false positives.")
        print("This is actually acceptable for SLR screening (prefer over-inclusion).")
    else:
        print("FAIL: Sensitivity below 95% - we are missing relevant papers. Must tune prompt.")
    print("=" * 60)


if __name__ == "__main__":
    main()
