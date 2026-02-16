#!/usr/bin/env python3
"""Stage 1: deterministic normalization/dedup for Dependabot + ECR findings."""

from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_common import (
    correlate,
    extract_dependabot,
    extract_ecr,
    normalized_findings_payload,
    read_json,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, default=Path("dependabot.json"))
    parser.add_argument("--ecr", type=Path, default=Path("ecr_findings.json"))
    parser.add_argument("--output", type=Path, default=Path("normalized_findings.json"))
    args = parser.parse_args()

    dependabot_data = read_json(args.dependabot)
    ecr_data = read_json(args.ecr)

    findings = extract_dependabot(dependabot_data) + extract_ecr(ecr_data)
    correlated = correlate(findings)

    payload = normalized_findings_payload(
        correlated,
        dependabot_present=dependabot_data is not None,
        ecr_present=ecr_data is not None,
    )
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
