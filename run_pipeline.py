"""
Top-level runner for the multi-review SLR pipeline.

Usage:
  python run_pipeline.py --review r01 --stage retrieval
  python run_pipeline.py --review r01 --stage screening
  python run_pipeline.py --review r01 --stage fulltext
  python run_pipeline.py --review r01 --stage fulltext_agent
  python run_pipeline.py --review r01 --stage dedup
  python run_pipeline.py --review r01 --stage extract_openai
  python run_pipeline.py --review r01 --stage extract_modal
  python run_pipeline.py --review r01 --stage evaluate
  python run_pipeline.py --review r01 --stage all
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Map short review IDs to config paths
REVIEW_CONFIGS = {
    "r01": "reviews/r01_lattanzi_dravet/config.json",
    "r02": "reviews/r02_ali_sglt2_hf/config.json",
    "r03": "reviews/r03_chang_ici_melanoma/config.json",
    "r04": "reviews/r04_bahji_ketamine_depression/config.json",
    "r05": "reviews/r05_archontakis_ics_copd/config.json",
}

# Map stage names to agent scripts
STAGE_AGENTS = {
    "retrieval":      "agents/retrieval_agent.py",
    "screening":      "agents/screening_agent.py",
    "fulltext":       "agents/fetch_fulltext.py",
    "fulltext_agent": "agents/fulltext_agent.py",
    "dedup":          "agents/dedup_agent.py",
    "extract_openai": "agents/extraction_openai.py",
    "extract_modal":  "agents/extraction_together.py",
    "evaluate":       "agents/evaluation_v2.py",
    "evaluate_v1":    "agents/evaluate_extractions.py",
}

# Order for running 'all' stages
ALL_STAGES = [
    "retrieval",
    "screening",
    "fulltext",
    "fulltext_agent",
    "dedup",
    "extract_openai",
    "extract_modal",
    "evaluate_v1",
    "evaluate",
]


def run_stage(review_id: str, stage: str):
    config_path = REVIEW_CONFIGS.get(review_id)
    if not config_path:
        print(f"ERROR: Unknown review '{review_id}'. Available: {list(REVIEW_CONFIGS.keys())}")
        sys.exit(1)

    if not Path(config_path).exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    agent_script = STAGE_AGENTS.get(stage)
    if not agent_script:
        print(f"ERROR: Unknown stage '{stage}'. Available: {list(STAGE_AGENTS.keys())}")
        sys.exit(1)

    if not Path(agent_script).exists():
        print(f"ERROR: Agent script not found: {agent_script}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"PIPELINE: {review_id} / {stage}")
    print(f"Config:   {config_path}")
    print(f"Agent:    {agent_script}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(
        [sys.executable, agent_script, "--config", config_path],
        cwd=str(Path(__file__).parent),
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Multi-review SLR pipeline runner")
    parser.add_argument(
        "--review",
        required=True,
        choices=list(REVIEW_CONFIGS.keys()),
        help="Review ID (r01-r05)",
    )
    parser.add_argument(
        "--stage",
        required=True,
        choices=list(STAGE_AGENTS.keys()) + ["all"],
        help="Pipeline stage to run",
    )
    args = parser.parse_args()

    if args.stage == "all":
        for stage in ALL_STAGES:
            rc = run_stage(args.review, stage)
            if rc != 0:
                print(f"\nERROR: Stage '{stage}' failed with return code {rc}. Stopping.")
                sys.exit(rc)
        print("\n\nAll stages complete.")
    else:
        rc = run_stage(args.review, args.stage)
        sys.exit(rc)


if __name__ == "__main__":
    main()
