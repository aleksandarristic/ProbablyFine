#!/usr/bin/env python3
"""Backward-compatible wrapper for staged probablyfine-triage pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from triage_pipeline import _run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, default=Path("dependabot.json"))
    parser.add_argument("--ecr", type=Path, default=Path("ecr_findings.json"))
    parser.add_argument("--context", type=Path, default=Path("context.json"))
    parser.add_argument("--threat-intel", type=Path, default=Path("threat_intel.json"))
    parser.add_argument("--output", type=Path, default=Path("contextual-threat-risk-triage.md"))
    parser.add_argument("--offline", action="store_true", help="Do not fetch EPSS/KEV")
    args = parser.parse_args()

    _run(
        dependabot_path=args.dependabot,
        ecr_path=args.ecr,
        context_path=args.context,
        normalized_out=Path("normalized_findings.json"),
        threat_intel_out=args.threat_intel,
        env_overrides_out=Path("env_overrides.json"),
        output_md=args.output,
        output_json=args.output.with_suffix(".json"),
        offline=args.offline,
        reuse_threat_cache=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
