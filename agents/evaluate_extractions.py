"""
Compares extractions from all 4 models (OpenAI, Llama, Qwen, Mistral) against
ground truth. Scores each model per-field and overall.
Outputs tables for the paper.

Usage:
  python agents/evaluate_extractions.py --config reviews/r01_lattanzi_dravet/config.json
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths

# Field -> comparator type
FIELD_TYPES = {
    "first_author": "string_match",
    "year": "exact_int",
    "phase": "string_contains_any",
    "n_total": "exact_int",
    "n_active": "exact_int_tolerant",
    "n_placebo": "exact_int",
    "age_range_years": "range_match",
    "intervention": "string_contains_any",
    "dose": "string_contains_any",
    "primary_efficacy_outcome": "string_fuzzy",
    "maintenance_weeks_ge_12": "exact_bool",
}


def norm(s):
    return str(s or "").lower().strip()


def compare(field, gt_value, pred_value):
    """Returns (match: bool, note: str). Handles several comparator types."""
    if pred_value is None:
        return False, "pred is None"
    ftype = FIELD_TYPES.get(field, "string_fuzzy")

    if ftype == "exact_int":
        try:
            return int(gt_value) == int(pred_value), None
        except (ValueError, TypeError):
            return False, "type error"

    if ftype == "exact_int_tolerant":
        # Allow ±10% tolerance because models sometimes count differently
        try:
            gt, pr = int(gt_value), int(pred_value)
            diff = abs(gt - pr)
            tol = max(2, int(0.10 * gt))
            return diff <= tol, (f"diff={diff} tol={tol}" if diff > 0 else None)
        except (ValueError, TypeError):
            return False, "type error"

    if ftype == "exact_bool":
        return bool(gt_value) == bool(pred_value), None

    if ftype == "string_match":
        return norm(gt_value) == norm(pred_value), None

    if ftype == "string_contains_any":
        # Match if GT tokens appear in prediction or vice versa
        gt_n, pr_n = norm(gt_value), norm(pred_value)
        if not gt_n or not pr_n:
            return False, "empty"
        if gt_n in pr_n or pr_n in gt_n:
            return True, None
        # Try token overlap
        gt_tokens = set(gt_n.replace(",", " ").split())
        pr_tokens = set(pr_n.replace(",", " ").split())
        overlap = gt_tokens & pr_tokens
        if len(overlap) >= max(1, len(gt_tokens) // 2):
            return True, f"partial token match ({len(overlap)}/{len(gt_tokens)})"
        return False, None

    if ftype == "range_match":
        # Age ranges like "2-18" — extract numbers and compare
        import re
        gt_nums = sorted(int(x) for x in re.findall(r"\d+", str(gt_value)))
        pr_nums = sorted(int(x) for x in re.findall(r"\d+", str(pred_value)))
        return gt_nums == pr_nums, None

    if ftype == "string_fuzzy":
        gt_n, pr_n = norm(gt_value), norm(pred_value)
        if not gt_n or not pr_n:
            return False, "empty"
        # Substring or high word overlap
        gt_tokens = set(gt_n.split())
        pr_tokens = set(pr_n.split())
        if not gt_tokens:
            return False, "empty gt"
        overlap = len(gt_tokens & pr_tokens) / len(gt_tokens)
        return overlap >= 0.4, f"overlap={overlap:.2f}"

    return False, "unknown ftype"


def extract_value(extraction, field):
    """Get field value from extraction dict, handling model variations."""
    if not extraction:
        return None
    if field in extraction:
        return extraction[field]
    # Some models nest under different keys — try case-insensitive
    for k, v in extraction.items():
        if norm(k) == norm(field):
            return v
    return None


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    RESULTS_DIR = paths["results_dir"]
    # Load ground truth: support both new merged format and old separate format
    gt_path = paths["ground_truth"]
    with open(gt_path) as f:
        gt_raw = json.load(f)
    if "extraction_ground_truth" in gt_raw and gt_raw["extraction_ground_truth"]:
        gt_data = {
            "studies": gt_raw["extraction_ground_truth"],
            "extraction_fields_for_evaluation": gt_raw["extraction_fields_for_evaluation"],
        }
    else:
        # Fall back to old separate file
        old_gt = Path("data/ground_truth/extraction_ground_truth.json")
        with open(old_gt) as f:
            gt_data = json.load(f)

    MODEL_FILES = {
        "gpt-4o-mini":     RESULTS_DIR / "extractions_openai.json",
        "llama-3.3-70b":   RESULTS_DIR / "extractions_llama.json",
        "qwen-3-235b":     RESULTS_DIR / "extractions_qwen.json",
        "deepseek-v3":     RESULTS_DIR / "extractions_deepseek.json",
    }

    print(f"Review: {config['short_name']} ({config['review_id']})")

    gt_by_pmid = {s["pmid"]: s for s in gt_data["studies"]}
    fields_to_eval = gt_data["extraction_fields_for_evaluation"]

    all_results = {}  # model -> field -> list of (pmid, match, note)

    for model_name, filepath in MODEL_FILES.items():
        if not filepath.exists():
            print(f"⚠ {filepath} not found; skipping {model_name}")
            continue
        with open(filepath) as f:
            data = json.load(f)
        extractions = data.get("extractions", [])
        ex_by_pmid = {e["pmid"]: e.get("extraction") for e in extractions}

        field_results = defaultdict(list)
        for pmid, gt in gt_by_pmid.items():
            pred = ex_by_pmid.get(pmid)
            if pred is None:
                # GT paper not extracted (lost upstream in retrieval/screening/dedup);
                # don't penalise extraction accuracy for upstream pipeline filtering.
                continue
            for field in fields_to_eval:
                gt_value = gt.get(field)
                pred_value = extract_value(pred, field)
                match, note = compare(field, gt_value, pred_value)
                field_results[field].append({
                    "pmid": pmid,
                    "study": gt.get("short_name", ""),
                    "gt": gt_value,
                    "pred": pred_value,
                    "match": match,
                    "note": note,
                })
        all_results[model_name] = field_results

    # --- Print comparison table ---
    print("\n" + "=" * 100)
    print("FIELD-LEVEL ACCURACY BY MODEL")
    print("=" * 100)
    header = f"{'Field':<30}" + "".join(f"{m:>20}" for m in all_results.keys())
    print(header)
    print("-" * len(header))

    field_scores = {field: {} for field in fields_to_eval}
    for field in fields_to_eval:
        row = f"{field:<30}"
        for model_name in all_results:
            results = all_results[model_name][field]
            n_match = sum(1 for r in results if r["match"])
            n_total = len(results)
            acc = n_match / n_total if n_total else 0
            field_scores[field][model_name] = acc
            row += f"{n_match}/{n_total} ({acc:.0%})".rjust(20)
        print(row)

    # --- Overall accuracy per model ---
    print("\n" + "=" * 100)
    print("OVERALL ACCURACY BY MODEL (micro-avg across all fields)")
    print("=" * 100)
    overall = {}
    for model_name, field_results in all_results.items():
        total_match = sum(1 for field in field_results for r in field_results[field] if r["match"])
        total_n = sum(len(field_results[field]) for field in field_results)
        overall[model_name] = total_match / total_n if total_n else 0
        print(f"  {model_name:<25}  {total_match}/{total_n}  ({overall[model_name]:.1%})")

    # --- Save full detail ---
    out = {
        "field_scores": field_scores,
        "overall_accuracy": overall,
        "details_per_model": {
            m: {f: r for f, r in results.items()}
            for m, results in all_results.items()
        },
    }
    out_path = paths["results_dir"] / "extraction_evaluation.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFull detail saved to {out_path}")

    # --- Highlight disagreements (for paper's error analysis) ---
    print("\n" + "=" * 100)
    print("DISAGREEMENTS (fields where some models were right and others wrong)")
    print("=" * 100)
    for field in fields_to_eval:
        for pmid, gt in gt_by_pmid.items():
            try:
                matches = {m: next(r for r in all_results[m][field] if r["pmid"] == pmid)["match"]
                           for m in all_results}
            except StopIteration:
                # GT paper not extracted by some/all models — skip from disagreement table.
                continue
            if len(set(matches.values())) > 1:  # disagreement
                preds = {m: next(r for r in all_results[m][field] if r["pmid"] == pmid)["pred"]
                         for m in all_results}
                print(f"\n{field} | study={gt.get('short_name')} | GT={gt.get(field)!r}")
                for m in all_results:
                    mark = "✓" if matches[m] else "✗"
                    print(f"  {mark} {m:<22} -> {preds[m]!r}")


if __name__ == "__main__":
    main()
