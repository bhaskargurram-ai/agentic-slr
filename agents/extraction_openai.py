"""
OpenAI extraction baseline (gpt-4o-mini).

Usage:
  python agents/extraction_openai.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import json
import time
import sys
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from extraction_schema import StudyExtraction, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from config_utils import add_config_arg, load_config, get_paths

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


def extract_one(record: dict) -> dict:
    prompt = USER_PROMPT_TEMPLATE.format(
        title=record["title"],
        journal=record.get("journal", ""),
        year=record.get("year", ""),
        pmid=record["pmid"],
        fulltext=record.get("clean_text", record.get("abstract", ""))[:50000],
    )
    t0 = time.time()
    try:
        resp = client.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format=StudyExtraction,
            temperature=0.0,
        )
        latency = time.time() - t0
        parsed = resp.choices[0].message.parsed
        usage = resp.usage
        return {
            "pmid": record["pmid"],
            "model": MODEL,
            "latency_seconds": round(latency, 2),
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "extraction": parsed.model_dump(),
            "error": None,
        }
    except Exception as e:
        return {
            "pmid": record["pmid"],
            "model": MODEL,
            "latency_seconds": time.time() - t0,
            "extraction": None,
            "error": str(e),
        }


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    config = load_config(args.config)
    paths = get_paths(config)

    POOL_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    DEDUP_FILE = paths["results_dir"] / "dedup_decisions.json"
    OUTPUT_FILE = paths["results_dir"] / "extractions_openai.json"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Review: {config['short_name']} ({config['review_id']})")

    with open(POOL_FILE) as f:
        pool = json.load(f)
    with open(DEDUP_FILE) as f:
        dedup = json.load(f)

    final_pmids = set(dedup["final_included_pmids"])
    records = [r for r in pool["records"] if r["pmid"] in final_pmids]
    print(f"Extracting from {len(records)} included studies with {MODEL}...\n")

    results = []
    for rec in tqdm(records, desc="Extracting"):
        results.append(extract_one(rec))
        time.sleep(0.1)

    total_input = sum(r["input_tokens"] for r in results if r.get("input_tokens"))
    total_output = sum(r["output_tokens"] for r in results if r.get("output_tokens"))
    total_latency = sum(r["latency_seconds"] for r in results)
    # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output
    cost = (total_input * 0.15 + total_output * 0.60) / 1_000_000

    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "model": MODEL,
            "n_studies": len(results),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_latency_seconds": round(total_latency, 2),
            "estimated_cost_usd": round(cost, 4),
            "extractions": results,
        }, f, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}")
    print(f"Total input tokens:  {total_input:,}")
    print(f"Total output tokens: {total_output:,}")
    print(f"Total latency:       {total_latency:.1f}s")
    print(f"Estimated cost:      ${cost:.4f}")
    print(f"Errors:              {sum(1 for r in results if r['error'])}")


if __name__ == "__main__":
    main()
