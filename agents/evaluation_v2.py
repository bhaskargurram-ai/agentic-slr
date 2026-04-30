"""
Enhanced evaluation with post-processing normalizations and metadata injection.
Compares extractions from all 4 models against corrected ground truth.
Reports before/after accuracy deltas for each fix applied.

Usage:
  python agents/evaluation_v2.py --config reviews/r01_lattanzi_dravet/config.json
"""
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from config_utils import add_config_arg, load_config, get_paths

FIELD_TYPES = {
    "first_author": "string_match",
    "year": "exact_int",
    "phase": "phase_match",
    "n_total": "exact_int",
    "n_active": "exact_int_tolerant",
    "n_placebo": "exact_int",
    "age_range_years": "range_match",
    "intervention": "string_contains_any",
    "dose": "dose_match",
    "primary_efficacy_outcome": "string_fuzzy",
    "maintenance_weeks_ge_12": "exact_bool",
}


def norm(s):
    return str(s or "").lower().strip()


def normalize_phase(val):
    """Normalize phase values: arabic -> roman, strip prefixes."""
    s = norm(val)
    s = s.replace("phase ", "").replace("not_reported", "N/A").strip()
    mapping = {"1": "i", "2": "ii", "3": "iii", "4": "iv"}
    if s in mapping:
        s = mapping[s]
    return s


def normalize_dose(val):
    """Normalize dose strings for comparison."""
    s = norm(val)
    # Normalize units
    s = s.replace("mg/kg/d", "mg/kg/day")
    s = s.replace("mg/d", "mg/day")
    s = s.replace("bid", "twice daily")
    s = re.sub(r"[≤<=]+\s*", "up to ", s)
    # Remove parenthetical extras for containment matching
    return s


def extract_first_author_from_metadata(authors_list):
    """Parse first author last name from PubMed authors list (e.g., 'Devinsky O' -> 'Devinsky')."""
    if not authors_list:
        return None
    first = authors_list[0]
    # PubMed format: "LastName Initials" e.g. "Devinsky O"
    parts = first.strip().split()
    if len(parts) >= 2:
        return parts[0]
    return first


def compare(field, gt_value, pred_value):
    """Returns (match: bool, note: str)."""
    if pred_value is None:
        return False, "pred is None"
    ftype = FIELD_TYPES.get(field, "string_fuzzy")

    if ftype == "exact_int":
        try:
            return int(gt_value) == int(pred_value), None
        except (ValueError, TypeError):
            return False, "type error"

    if ftype == "exact_int_tolerant":
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

    if ftype == "phase_match":
        gt_p = normalize_phase(str(gt_value))
        pr_p = normalize_phase(str(pred_value))
        # Exact match after normalization (avoids "ii" matching "iii")
        if gt_p == pr_p:
            return True, None
        # Allow "n/a" variants
        na_variants = {"n/a", "n/a (investigator-initiated)", "not applicable", ""}
        if gt_p in na_variants and pr_p in na_variants:
            return True, None
        return False, f"gt_norm={gt_p} pr_norm={pr_p}"

    if ftype == "dose_match":
        gt_n = normalize_dose(str(gt_value))
        pr_n = normalize_dose(str(pred_value))
        if not gt_n or not pr_n or pr_n == "not_reported":
            return False, "empty or not_reported"
        # Direct containment
        if gt_n in pr_n or pr_n in gt_n:
            return True, None
        # Token overlap
        gt_tokens = set(gt_n.replace(",", " ").split())
        pr_tokens = set(pr_n.replace(",", " ").split())
        overlap = gt_tokens & pr_tokens
        if len(overlap) >= max(1, len(gt_tokens) // 2):
            return True, f"partial token match ({len(overlap)}/{len(gt_tokens)})"
        # Numeric comparison: extract all numbers and compare
        gt_nums = sorted(re.findall(r"[\d.]+", gt_n))
        pr_nums = sorted(re.findall(r"[\d.]+", pr_n))
        if gt_nums and gt_nums == pr_nums:
            return True, "numeric match"
        return False, None

    if ftype == "string_contains_any":
        gt_n, pr_n = norm(gt_value), norm(pred_value)
        if not gt_n or not pr_n:
            return False, "empty"
        if gt_n in pr_n or pr_n in gt_n:
            return True, None
        gt_tokens = set(gt_n.replace(",", " ").split())
        pr_tokens = set(pr_n.replace(",", " ").split())
        overlap = gt_tokens & pr_tokens
        if len(overlap) >= max(1, len(gt_tokens) // 2):
            return True, f"partial token match ({len(overlap)}/{len(gt_tokens)})"
        return False, None

    if ftype == "range_match":
        gt_nums = sorted(int(x) for x in re.findall(r"\d+", str(gt_value)))
        pr_nums = sorted(int(x) for x in re.findall(r"\d+", str(pred_value)))
        return gt_nums == pr_nums, None

    if ftype == "string_fuzzy":
        gt_n, pr_n = norm(gt_value), norm(pred_value)
        if not gt_n or not pr_n:
            return False, "empty"
        gt_tokens = set(gt_n.split())
        pr_tokens = set(pr_n.split())
        if not gt_tokens:
            return False, "empty gt"
        overlap = len(gt_tokens & pr_tokens) / len(gt_tokens)
        return overlap >= 0.4, f"overlap={overlap:.2f}"

    return False, "unknown ftype"


def extract_value(extraction, field):
    if not extraction:
        return None
    if field in extraction:
        return extraction[field]
    for k, v in extraction.items():
        if norm(k) == norm(field):
            return v
    return None


def run_evaluation(apply_fixes=True, label="", ground_truth_path=None, pool_path=None, results_dir=None):
    """Run evaluation with optional fixes. Returns (overall_dict, field_scores_dict, details)."""
    # Support both new merged format and old separate format
    with open(ground_truth_path) as f:
        gt_raw = json.load(f)
    if "extraction_ground_truth" in gt_raw and gt_raw["extraction_ground_truth"]:
        gt_data = {
            "studies": gt_raw["extraction_ground_truth"],
            "extraction_fields_for_evaluation": gt_raw["extraction_fields_for_evaluation"],
        }
    else:
        old_gt = Path("data/ground_truth/extraction_ground_truth.json")
        with open(old_gt) as f:
            gt_data = json.load(f)

    gt_by_pmid = {s["pmid"]: s for s in gt_data["studies"]}
    fields_to_eval = gt_data["extraction_fields_for_evaluation"]

    MODEL_FILES = {
        "gpt-4o-mini":     results_dir / "extractions_openai.json",
        "llama-3.3-70b":   results_dir / "extractions_llama.json",
        "qwen-3-235b":     results_dir / "extractions_qwen.json",
        "deepseek-v3":     results_dir / "extractions_deepseek.json",
    }

    # Load fulltext pool for metadata injection
    pool_by_pmid = {}
    if apply_fixes and pool_path and pool_path.exists():
        with open(pool_path) as f:
            pool = json.load(f)
        pool_by_pmid = {r["pmid"]: r for r in pool["records"]}

    all_results = {}

    for model_name, filepath in MODEL_FILES.items():
        if not filepath.exists():
            print(f"  [SKIP] {filepath} not found")
            continue
        with open(filepath) as f:
            data = json.load(f)
        extractions = data.get("extractions", [])
        ex_by_pmid = {e["pmid"]: e.get("extraction") for e in extractions}

        field_results = defaultdict(list)
        for pmid, gt in gt_by_pmid.items():
            pred = ex_by_pmid.get(pmid)
            if pred is None:
                continue
            # --- Apply post-processing fixes ---
            if apply_fixes and pred:
                # Fix 1: Inject first_author from PubMed metadata
                if pmid in pool_by_pmid:
                    meta_author = extract_first_author_from_metadata(
                        pool_by_pmid[pmid].get("authors", [])
                    )
                    if meta_author:
                        pred = dict(pred)  # copy to avoid mutating original
                        pred["first_author"] = meta_author

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
    print(f"\n{'=' * 100}")
    print(f"FIELD-LEVEL ACCURACY BY MODEL — {label}")
    print(f"{'=' * 100}")
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

    print(f"\n{'=' * 100}")
    print(f"OVERALL ACCURACY BY MODEL — {label}")
    print(f"{'=' * 100}")
    overall = {}
    for model_name, field_results in all_results.items():
        total_match = sum(1 for field in field_results for r in field_results[field] if r["match"])
        total_n = sum(len(field_results[field]) for field in field_results)
        overall[model_name] = total_match / total_n if total_n else 0
        print(f"  {model_name:<25}  {total_match}/{total_n}  ({overall[model_name]:.1%})")

    return overall, field_scores, all_results


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    GROUND_TRUTH_PATH = paths["ground_truth"]
    POOL_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    RESULTS_DIR = paths["results_dir"]

    print(f"Review: {config['short_name']} ({config['review_id']})")
    print("=" * 100)
    print("EVALUATION v2: Before/After Comparison with Post-Processing Fixes")
    print("=" * 100)

    eval_kwargs = dict(ground_truth_path=GROUND_TRUTH_PATH, pool_path=POOL_FILE, results_dir=RESULTS_DIR)

    # --- Baseline (no fixes) ---
    print("\n\n### BASELINE (original evaluation, corrected ground truth only)")
    baseline_overall, baseline_fields, _ = run_evaluation(
        apply_fixes=False, label="BASELINE (GT corrections only)", **eval_kwargs
    )

    # --- With all fixes ---
    print("\n\n### WITH ALL FIXES (metadata injection + normalization)")
    fixed_overall, fixed_fields, fixed_details = run_evaluation(
        apply_fixes=True, label="WITH FIXES", **eval_kwargs
    )

    # --- Delta report ---
    print(f"\n\n{'=' * 100}")
    print("ACCURACY DELTA: BASELINE -> WITH FIXES")
    print(f"{'=' * 100}")
    print(f"\n{'Model':<25} {'Baseline':>10} {'Fixed':>10} {'Delta':>10}")
    print("-" * 55)
    for model in baseline_overall:
        b = baseline_overall[model]
        f = fixed_overall[model]
        delta = f - b
        print(f"  {model:<23} {b:>9.1%} {f:>9.1%} {delta:>+9.1%}")

    # --- Per-field delta ---
    with open(GROUND_TRUTH_PATH) as gf:
        gt_raw = json.load(gf)
    if "extraction_fields_for_evaluation" in gt_raw and gt_raw["extraction_fields_for_evaluation"]:
        fields_to_eval = gt_raw["extraction_fields_for_evaluation"]
    else:
        old_gt = Path("data/ground_truth/extraction_ground_truth.json")
        with open(old_gt) as gf2:
            fields_to_eval = json.load(gf2)["extraction_fields_for_evaluation"]

    print(f"\n{'Field':<30} {'Baseline Avg':>15} {'Fixed Avg':>15} {'Delta':>10}")
    print("-" * 70)
    for field in fields_to_eval:
        if field in baseline_fields and baseline_fields[field]:
            b_avg = sum(baseline_fields[field].values()) / len(baseline_fields[field])
            f_avg = sum(fixed_fields[field].values()) / len(fixed_fields[field])
            delta = f_avg - b_avg
            marker = " ***" if abs(delta) > 0.05 else ""
            print(f"  {field:<28} {b_avg:>14.1%} {f_avg:>14.1%} {delta:>+9.1%}{marker}")

    # --- Save detailed results ---
    out = {
        "review_id": config["review_id"],
        "description": "evaluation_v2 with post-processing normalizations and PubMed author injection",
        "fixes_applied": [
            "Phase normalization: arabic numerals -> roman numerals (e.g., '2' -> 'II')",
            "Phase matching: strict equality (no substring matching)",
            "Dose normalization: mg/kg/d -> mg/kg/day, BID -> twice daily, <= -> up to",
            "Author metadata injection: first_author from PubMed authors[0] instead of LLM extraction",
            "Ground-truth corrections (if any) are defined per-review in the review's ground_truth.json",
        ],
        "baseline_accuracy": baseline_overall,
        "fixed_accuracy": fixed_overall,
        "baseline_field_scores": baseline_fields,
        "fixed_field_scores": fixed_fields,
    }
    out_path = RESULTS_DIR / "extraction_evaluation_v2.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    main()
