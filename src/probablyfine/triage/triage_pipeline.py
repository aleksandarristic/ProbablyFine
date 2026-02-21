#!/usr/bin/env python3
"""Pipeline orchestrator for probablyfine-triage staged components."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_CONTEXT = Path("context.json")
DEFAULT_NORMALIZED = Path("normalized_findings.json")
DEFAULT_THREAT_INTEL = Path("threat_intel.json")
DEFAULT_ENV_OVERRIDES = Path("env_overrides.json")
DEFAULT_REPORT_MD = Path("contextual-threat-risk-triage.md")
DEFAULT_REPORT_JSON = Path("contextual-threat-risk-triage.json")


def run_stage(module: str, args: list[str]) -> None:
    src_dir = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) if not current else f"{src_dir}:{current}"
    cmd = [sys.executable, "-m", module] + args
    subprocess.run(cmd, check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, default=Path("dependabot.json"))
    parser.add_argument("--ecr", type=Path, default=Path("ecr_findings.json"))
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)

    parser.add_argument("--normalized", type=Path, default=DEFAULT_NORMALIZED)
    parser.add_argument("--threat-intel", type=Path, default=DEFAULT_THREAT_INTEL)
    parser.add_argument("--env-overrides", type=Path, default=DEFAULT_ENV_OVERRIDES)

    parser.add_argument("--output-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--llm-adjustment-output", type=Path, default=None)
    parser.add_argument("--enable-llm-adjustment", action="store_true")
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repo root containing .probablyfine/; default stage outputs are written to dated cache/reports paths",
    )

    parser.add_argument("--offline", action="store_true", help="Skip internet threat intel fetch")
    args = parser.parse_args()

    if args.repo_root:
        now = dt.datetime.now(dt.timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        ts = now.strftime("%Y-%m-%dT%H%M%SZ")
        pf_dir = args.repo_root / ".probablyfine"
        cache_dir = pf_dir / "cache" / date_str
        report_dir = pf_dir / "reports" / date_str
        cache_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)

        if args.context == DEFAULT_CONTEXT:
            args.context = pf_dir / "context.json"
        if args.normalized == DEFAULT_NORMALIZED:
            args.normalized = cache_dir / "normalized_findings.json"
        if args.threat_intel == DEFAULT_THREAT_INTEL:
            args.threat_intel = cache_dir / "threat_intel.json"
        if args.env_overrides == DEFAULT_ENV_OVERRIDES:
            args.env_overrides = cache_dir / "env_overrides.json"
        if args.output_md == DEFAULT_REPORT_MD:
            args.output_md = report_dir / f"report-{ts}.md"
        if args.output_json == DEFAULT_REPORT_JSON:
            args.output_json = report_dir / f"report-{ts}.json"

    run_stage(
        "probablyfine.triage.normalize_findings",
        ["--dependabot", str(args.dependabot), "--ecr", str(args.ecr), "--output", str(args.normalized)],
    )

    fetch_args = ["--normalized", str(args.normalized), "--output", str(args.threat_intel)]
    if args.offline:
        fetch_args.append("--offline")
    run_stage("probablyfine.triage.fetch_threat_intel", fetch_args)

    run_stage(
        "probablyfine.triage.select_env_overrides",
        ["--context", str(args.context), "--output", str(args.env_overrides)],
    )

    run_stage(
        "probablyfine.triage.score_and_rank",
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

    if args.llm_adjustment_output is not None:
        llm_args = [
            "--report-json",
            str(args.output_json),
            "--output",
            str(args.llm_adjustment_output),
        ]
        if args.enable_llm_adjustment:
            llm_args.append("--enable-adjustment")
        run_stage("probablyfine.triage.optional_adjustment", llm_args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
