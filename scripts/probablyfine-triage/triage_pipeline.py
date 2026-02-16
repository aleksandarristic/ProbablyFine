#!/usr/bin/env python3
"""Pipeline orchestrator for probablyfine-triage staged components."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_stage(script: Path, args: list[str]) -> None:
    cmd = [sys.executable, str(script)] + args
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, default=Path("dependabot.json"))
    parser.add_argument("--ecr", type=Path, default=Path("ecr_findings.json"))
    parser.add_argument("--context", type=Path, default=Path("context.json"))

    parser.add_argument("--normalized", type=Path, default=Path("normalized_findings.json"))
    parser.add_argument("--threat-intel", type=Path, default=Path("threat_intel.json"))
    parser.add_argument("--env-overrides", type=Path, default=Path("env_overrides.json"))

    parser.add_argument("--output-md", type=Path, default=Path("contextual-threat-risk-triage.md"))
    parser.add_argument("--output-json", type=Path, default=Path("contextual-threat-risk-triage.json"))

    parser.add_argument("--offline", action="store_true", help="Skip internet threat intel fetch")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent

    run_stage(
        scripts_dir / "normalize_findings.py",
        ["--dependabot", str(args.dependabot), "--ecr", str(args.ecr), "--output", str(args.normalized)],
    )

    fetch_args = ["--normalized", str(args.normalized), "--output", str(args.threat_intel)]
    if args.offline:
        fetch_args.append("--offline")
    run_stage(scripts_dir / "fetch_threat_intel.py", fetch_args)

    run_stage(
        scripts_dir / "select_env_overrides.py",
        ["--context", str(args.context), "--output", str(args.env_overrides)],
    )

    run_stage(
        scripts_dir / "score_and_rank.py",
        [
            "--normalized",
            str(args.normalized),
            "--threat-intel",
            str(args.threat_intel),
            "--env-overrides",
            str(args.env_overrides),
            "--output-md",
            str(args.output_md),
            "--output-json",
            str(args.output_json),
            "--intel-fetch-performed",
            "no" if args.offline else "yes",
        ],
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
