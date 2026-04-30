"""
Runs extraction on included papers through three open models hosted on
Together AI's serverless inference (Llama 3.3 70B Turbo, Qwen 2.5 72B Turbo,
Mistral Small 24B). Drop-in replacement for extraction_multimodel.py — same
output filenames, same JSON schema, so downstream evaluation is unchanged.

Usage:
  python agents/extraction_together.py --config reviews/r01_lattanzi_dravet/config.json
"""
import os
import re
import sys
import json
import time
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from together import Together

sys.path.insert(0, str(Path(__file__).parent))
from extraction_schema import StudyExtraction, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from config_utils import add_config_arg, load_config, get_paths

load_dotenv()

# Together AI pricing (USD per 1M tokens, as of April 2026 serverless tier)
PRICING = {
    "llama-3.3-70b": {"in": 0.88, "out": 0.88},
    "qwen-3-235b":   {"in": 0.20, "out": 0.60},
    "deepseek-v3":   {"in": 1.25, "out": 1.25},
}

MODEL_CONFIGS = [
    {
        "name": "llama-3.3-70b",
        "together_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "output_filename": "extractions_llama.json",
    },
    {
        "name": "qwen-3-235b",
        "together_model": "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
        "output_filename": "extractions_qwen.json",
    },
    {
        "name": "deepseek-v3",
        "together_model": "deepseek-ai/DeepSeek-V3",
        "output_filename": "extractions_deepseek.json",
    },
]


def _parse_json_from_text(text: str) -> tuple[dict | None, str | None]:
    """Robust JSON parse: strip markdown fences, find outermost {...}."""
    if text is None:
        return None, "empty response"
    s = text.strip()
    # strip ```json ... ``` or ``` ... ``` fences
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", s, re.DOTALL)
    if fence:
        s = fence.group(1).strip()
    # try direct
    try:
        return json.loads(s), None
    except Exception:
        pass
    # fallback: outermost balanced braces
    start = s.find("{")
    if start == -1:
        return None, "no JSON object found in response"
    depth = 0
    end = -1
    for i in range(start, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None, "unbalanced braces in response"
    snippet = s[start : end + 1]
    try:
        return json.loads(snippet), None
    except Exception as e:
        return None, f"json parse failed: {e}"


def _int_field_names() -> set[str]:
    """Field names in StudyExtraction whose annotation includes int."""
    names = set()
    for name, info in StudyExtraction.model_fields.items():
        ann = info.annotation
        # Covers both `int` and `int | None` / `Optional[int]`.
        if ann is int or (hasattr(ann, "__args__") and int in getattr(ann, "__args__", ())):
            names.add(name)
    return names


_INT_FIELDS = _int_field_names()


def _coerce_int_fields(obj: dict) -> dict:
    """Round float values to int for int-typed schema fields (e.g. 79.1 → 79)."""
    if not isinstance(obj, dict):
        return obj
    for f in _INT_FIELDS:
        v = obj.get(f)
        if isinstance(v, float):
            obj[f] = int(round(v))
    return obj


def _validate_against_schema(obj: dict) -> tuple[dict | None, str | None]:
    """Coerce to StudyExtraction. Return (validated_dict, error_str)."""
    try:
        obj = _coerce_int_fields(obj)
        validated = StudyExtraction.model_validate(obj)
        return validated.model_dump(), None
    except Exception as e:
        return None, f"schema validation failed: {e}"


def _call_with_retry(client: Together, model: str, system: str, user: str, max_tokens: int = 2048):
    """One-shot call; retry once after 3s on failure."""
    last_err = None
    for attempt in range(2):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            return resp, time.time() - t0, None
        except Exception as e:
            last_err = e
            if attempt == 0:
                time.sleep(3)
    return None, 0.0, f"API call failed after retry: {last_err}"


def extract_one(client: Together, model_cfg: dict, record: dict) -> dict:
    schema_hint = json.dumps(StudyExtraction.model_json_schema(), indent=2)
    full_system = SYSTEM_PROMPT + "\n\nThe JSON output must conform to this schema:\n" + schema_hint
    user_prompt = USER_PROMPT_TEMPLATE.format(
        title=record["title"],
        journal=record.get("journal", ""),
        year=record.get("year", ""),
        pmid=record["pmid"],
        fulltext=record.get("clean_text", record.get("abstract", ""))[:50000],
    )

    resp, latency, api_err = _call_with_retry(
        client, model_cfg["together_model"], full_system, user_prompt
    )
    if api_err:
        return {
            "extraction": None,
            "raw_output": None,
            "parse_error": None,
            "latency_seconds": round(latency, 2),
            "input_tokens": 0,
            "output_tokens": 0,
            "error": api_err,
            "pmid": record["pmid"],
            "model": model_cfg["name"],
        }

    text = resp.choices[0].message.content
    parsed, parse_err = _parse_json_from_text(text)
    extraction = None
    final_err = None
    if parsed is not None:
        validated, val_err = _validate_against_schema(parsed)
        if validated is not None:
            extraction = validated
        else:
            parse_err = val_err
            final_err = val_err
    else:
        final_err = parse_err

    usage = resp.usage
    return {
        "extraction": extraction,
        "raw_output": text if extraction is None else None,
        "parse_error": parse_err,
        "latency_seconds": round(latency, 2),
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "error": final_err,
        "pmid": record["pmid"],
        "model": model_cfg["name"],
    }


def run_model(client: Together, model_cfg: dict, records: list[dict], out_path: Path) -> dict:
    print(f"\n{'=' * 60}")
    print(f"Running {model_cfg['name']} ({model_cfg['together_model']}) on {len(records)} papers")
    print(f"{'=' * 60}")

    results = []
    t_wall = time.time()
    for rec in tqdm(records, desc=model_cfg["name"]):
        results.append(extract_one(client, model_cfg, rec))

    wall = time.time() - t_wall
    total_in = sum(r.get("input_tokens", 0) or 0 for r in results)
    total_out = sum(r.get("output_tokens", 0) or 0 for r in results)
    total_lat = sum(r.get("latency_seconds", 0) or 0 for r in results)
    errors = sum(1 for r in results if r.get("error"))

    price = PRICING[model_cfg["name"]]
    cost = (total_in * price["in"] + total_out * price["out"]) / 1_000_000

    summary = {
        "model": model_cfg["name"],
        "provider": "together_ai",
        "together_model": model_cfg["together_model"],
        "n_studies": len(results),
        "wall_time_seconds": round(wall, 2),
        "total_model_latency_seconds": round(total_lat, 2),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "estimated_cost_usd": round(cost, 4),
        "errors": errors,
        "extractions": results,
    }

    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Wall time: {wall:.1f}s")
    print(f"  Latency sum: {total_lat:.1f}s")
    print(f"  Tokens: in={total_in:,} out={total_out:,}")
    print(f"  Cost: ${cost:.4f}")
    print(f"  Errors: {errors}")
    print(f"  Saved to: {out_path}")
    return summary


def main():
    parser = add_config_arg()
    args = parser.parse_args()
    review_config = load_config(args.config)
    paths = get_paths(review_config)

    POOL_FILE = paths["retrieved_dir"] / "fulltext_pool.json"
    DEDUP_FILE = paths["results_dir"] / "dedup_decisions.json"
    RESULTS_DIR = paths["results_dir"]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("ERROR: TOGETHER_API_KEY not set in environment / .env")
        sys.exit(1)
    client = Together(api_key=api_key)

    print(f"Review: {review_config['short_name']} ({review_config['review_id']})")

    with open(POOL_FILE) as f:
        pool = json.load(f)
    with open(DEDUP_FILE) as f:
        dedup = json.load(f)

    final_pmids = set(dedup["final_included_pmids"])
    records = [r for r in pool["records"] if r["pmid"] in final_pmids]
    print(f"Will extract from {len(records)} included studies across {len(MODEL_CONFIGS)} open models on Together AI.")

    summaries = []
    for mc in MODEL_CONFIGS:
        out_path = RESULTS_DIR / mc["output_filename"]
        summaries.append(run_model(client, mc, records, out_path))

    combined = RESULTS_DIR / "extractions_all_openmodels_summary.json"
    with open(combined, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"\n\nAll models complete. Combined summary: {combined}")
    total_cost = sum(s["estimated_cost_usd"] for s in summaries)
    total_errors = sum(s["errors"] for s in summaries)
    print(f"Grand total cost: ${total_cost:.4f}    Total errors: {total_errors}")


if __name__ == "__main__":
    main()
