#!/usr/bin/env python3
"""Optional bounded adjustment annotations stage."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .pipeline_common import read_json, write_json


def _delta_for_row(row: dict[str, Any]) -> tuple[int, str]:
    severity = str(row.get("severity", "unknown")).lower()
    threat = str(row.get("e", "X")).upper()
    runtime = str(row.get("runtime", "unknown")).lower()
    source = str(row.get("source_bucket", "Dependabot-only"))

    delta = 0
    reasons: list[str] = []

    if severity == "critical" and threat == "A":
        delta += 5
        reasons.append("critical severity with active threat signal")
    if runtime == "runtime" and source in {"Both", "ECR-only"}:
        delta += 3
        reasons.append("runtime-relevant production surface")
    if str(row.get("fix_version", "unknown")) == "unknown":
        delta -= 2
        reasons.append("fix version unknown lowers confidence")

    if not reasons:
        reasons.append("no bounded adjustment rule matched")
    return delta, "; ".join(reasons)


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--enable-adjustment", action="store_true")
    args = parser.parse_args()

    payload = read_json(args.report_json) or {}
    findings = payload.get("findings", []) if isinstance(payload, dict) else []

    annotations: list[dict[str, Any]] = []
    for row in findings:
        if not isinstance(row, dict):
            continue
        base_risk = _as_int(row.get("risk"), 0)
        delta, rationale = _delta_for_row(row)
        adjusted = max(0, min(100, base_risk + delta)) if args.enable_adjustment else base_risk
        annotations.append(
            {
                "cve": row.get("cve"),
                "package": row.get("package"),
                "base_risk": base_risk,
                "suggested_delta": delta,
                "adjusted_risk": adjusted,
                "applied": bool(args.enable_adjustment),
                "rationale": rationale,
            }
        )

    write_json(
        args.output,
        {
            "feature_flag": "processing.allow_llm_adjustment",
            "adjustment_enabled": bool(args.enable_adjustment),
            "annotations": annotations,
            "source_report": str(args.report_json),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
