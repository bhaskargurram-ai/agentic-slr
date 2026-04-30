"""
Shared config loading utility for multi-review pipeline.
All agents use this to load review-specific config via --config argument.
"""
import argparse
import json
from pathlib import Path


DEFAULT_CONFIG = "reviews/r01_lattanzi_dravet/config.json"


def add_config_arg(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """Add --config argument to an argparse parser."""
    if parser is None:
        parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG,
        help=f"Path to review config.json (default: {DEFAULT_CONFIG})",
    )
    return parser


def load_config(config_path: str = None) -> dict:
    """Load and return a review config dict."""
    path = Path(config_path or DEFAULT_CONFIG)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path) as f:
        return json.load(f)


def get_paths(config: dict) -> dict:
    """Return resolved Path objects from config paths."""
    p = config["paths"]
    return {
        "base_dir": Path(p["base_dir"]),
        "ground_truth": Path(p["ground_truth"]),
        "retrieved_dir": Path(p["retrieved_dir"]),
        "results_dir": Path(p["results_dir"]),
        "extractions_dir": Path(p["extractions_dir"]),
    }
