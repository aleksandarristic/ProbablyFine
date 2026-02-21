#!/usr/bin/env python3
"""Determinism verification harness for repeated pipeline runs."""

from __future__ import annotations

import argparse
import filecmp
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run_pipeline(
    output_root: Path,
    dependabot: Path,
    ecr: Path,
    context: Path,
    fixed_time: str,
) -> None:
    cmd = [
        sys.executable,
        "-m",
        "probablyfine.triage.triage_pipeline",
        "--dependabot",
        str(dependabot),
        "--ecr",
        str(ecr),
        "--context",
        str(context),
        "--normalized",
        str(output_root / "normalized_findings.json"),
        "--threat-intel",
        str(output_root / "threat_intel.json"),
        "--env-overrides",
        str(output_root / "env_overrides.json"),
        "--output-md",
        str(output_root / "contextual-threat-risk-triage.md"),
        "--output-json",
        str(output_root / "contextual-threat-risk-triage.json"),
        "--offline",
    ]
    env = os.environ.copy()
    env["PROBABLYFINE_FIXED_UTC_NOW"] = fixed_time
    src_dir = Path(__file__).resolve().parents[2]
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) if not current else f"{src_dir}:{current}"
    subprocess.run(cmd, env=env, check=True)


def _assert_equal_bytes(a: Path, b: Path) -> None:
    if not filecmp.cmp(a, b, shallow=False):
        raise RuntimeError(f"non-deterministic output detected: {a.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependabot", type=Path, required=True)
    parser.add_argument("--ecr", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument(
        "--fixed-time",
        default="2026-01-01T00:00:00+00:00",
        help="Fixed timestamp value injected into outputs for byte-stable comparison",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run_a = root / "run-a"
        run_b = root / "run-b"
        run_a.mkdir(parents=True, exist_ok=True)
        run_b.mkdir(parents=True, exist_ok=True)

        _run_pipeline(run_a, args.dependabot, args.ecr, args.context, args.fixed_time)
        _run_pipeline(run_b, args.dependabot, args.ecr, args.context, args.fixed_time)

        files = [
            "normalized_findings.json",
            "threat_intel.json",
            "env_overrides.json",
            "contextual-threat-risk-triage.md",
            "contextual-threat-risk-triage.json",
        ]
        for rel in files:
            _assert_equal_bytes(run_a / rel, run_b / rel)

    print("determinism-check: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

