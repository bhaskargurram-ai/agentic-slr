"""
Runs extraction on included papers through all three open models on Modal
(Llama 3.3 70B, Qwen 2.5 72B, Mistral Small 24B), then combines results with the
existing OpenAI baseline for a 4-model comparison.

Usage:
  python agents/extraction_multimodel.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import sys
import json
import time
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from extraction_schema import StudyExtraction, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from config_utils import add_config_arg, load_config, get_paths

import modal

load_dotenv()


def run_model(config: dict, records: list[dict], schema: dict) -> dict:
    """Run extraction on all papers through one Modal model."""
    print(f"\n{'=' * 60}")
    print(f"Running {config['name']} on {len(records)} papers")
    print(f"{'=' * 60}")

    Extractor = modal.Cls.from_name(config["app"], config["class"])
    extractor = Extractor()

    results = []
    t_wall_start = time.time()
    for rec in tqdm(records, desc=config["name"]):
        user_prompt = USER_PROMPT_TEMPLATE.format(
            title=rec["title"],
            journal=rec.get("journal", ""),
            year=rec.get("year", ""),
            pmid=rec["pmid"],
            fulltext=rec.get("clean_text", rec.get("abstract", ""))[:50000],
        )
        try:
            result = extractor.extract.remote(SYSTEM_PROMPT, user_prompt, schema)
            result["pmid"] = rec["pmid"]
            result["model"] = config["name"]
            results.append(result)
        except Exception as e:
            results.append({
                "pmid": rec["pmid"],
                "model": config["name"],
                "error": f"Remote call failed: {e}",
                "extraction": None,
            })

    wall_time = time.time() - t_wall_start
    total_in = sum(r.get("input_tokens", 0) or 0 for r in results)
    total_out = sum(r.get("output_tokens", 0) or 0 for r in results)
    total_latency = sum(r.get("latency_seconds", 0) or 0 for r in results)
    errors = sum(1 for r in results if r.get("error"))

    summary = {
        "model": config["name"],
        "n_studies": len(results),
        "wall_time_seconds": round(wall_time, 2),
        "total_model_latency_seconds": round(total_latency, 2),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "errors": errors,
        "extractions": results,
    }

    with open(config["output_file"], "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Wall time: {wall_time:.1f}s")
    print(f"  Model latency (sum): {total_latency:.1f}s")
    print(f"  Input tokens:  {total_in:,}")
    print(f"  Output tokens: {total_out:,}")
    print(f"  Errors: {errors}")
    print(f"  Saved to: {config['output_file']}")
    return summary


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    review_config = load_config(args.config)
    paths = get_paths(review_config)

    POOL_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    DEDUP_FILE = paths["results_dir"] / "dedup_decisions.json"
    RESULTS_DIR = paths["results_dir"]

    MODEL_CONFIGS = [
        {
            "name": "llama-3.3-70b",
            "app": "slr-llama-extractor",
            "class": "LlamaExtractor",
            "output_file": RESULTS_DIR / "extractions_llama.json",
        },
        {
            "name": "qwen-2.5-72b",
            "app": "slr-qwen-extractor",
            "class": "QwenExtractor",
            "output_file": RESULTS_DIR / "extractions_qwen.json",
        },
        {
            "name": "mistral-small-24b",
            "app": "slr-mistral-extractor",
            "class": "MistralExtractor",
            "output_file": RESULTS_DIR / "extractions_mistral.json",
        },
    ]

    print(f"Review: {review_config['short_name']} ({review_config['review_id']})")

    with open(POOL_FILE) as f:
        pool = json.load(f)
    with open(DEDUP_FILE) as f:
        dedup = json.load(f)

    final_pmids = set(dedup["final_included_pmids"])
    records = [r for r in pool["records"] if r["pmid"] in final_pmids]
    print(f"Will extract from {len(records)} included studies across {len(MODEL_CONFIGS)} open models.")

    schema = StudyExtraction.model_json_schema()

    summaries = []
    for mc in MODEL_CONFIGS:
        summary = run_model(mc, records, schema)
        summaries.append(summary)

    combined = RESULTS_DIR / "extractions_all_openmodels_summary.json"
    with open(combined, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"\n\nAll models complete. Combined summary: {combined}")


if __name__ == "__main__":
    main()
