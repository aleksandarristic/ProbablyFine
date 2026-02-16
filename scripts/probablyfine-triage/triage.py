#!/usr/bin/env python3
"""Backward-compatible wrapper for staged probablyfine-triage pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, default=Path("dependabot.json"))
    parser.add_argument("--ecr", type=Path, default=Path("ecr_findings.json"))
    parser.add_argument("--context", type=Path, default=Path("context.json"))
    parser.add_argument("--threat-intel", type=Path, default=Path("threat_intel.json"))
    parser.add_argument("--output", type=Path, default=Path("contextual-threat-risk-triage.md"))
    parser.add_argument("--offline", action="store_true", help="Do not fetch EPSS/KEV")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    cmd = [
        sys.executable,
        str(scripts_dir / "triage_pipeline.py"),
        "--dependabot",
        str(args.dependabot),
        "--ecr",
        str(args.ecr),
        "--context",
        str(args.context),
        "--threat-intel",
        str(args.threat_intel),
        "--output-md",
        str(args.output),
    ]
    if args.offline:
        cmd.append("--offline")

    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
