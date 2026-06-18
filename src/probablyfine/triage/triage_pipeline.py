#!/usr/bin/env python3
"""Pipeline orchestrator for probablyfine-triage staged components."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .pipeline_common import (
    build_threat_cache,
    correlate,
    env_overrides_payload,
    extract_dependabot,
    extract_ecr,
    normalized_findings_payload,
    read_json,
    write_json,
)
from .fetch_threat_intel import empty_cache
from .score_and_rank import run_scoring

DEFAULT_CONTEXT = Path("context.json")
DEFAULT_NORMALIZED = Path("normalized_findings.json")
DEFAULT_THREAT_INTEL = Path("threat_intel.json")
DEFAULT_ENV_OVERRIDES = Path("env_overrides.json")
DEFAULT_REPORT_MD = Path("contextual-threat-risk-triage.md")
DEFAULT_REPORT_JSON = Path("contextual-threat-risk-triage.json")


def _find_latest_report(reports_root: Path) -> Optional[List[Dict[str, Any]]]:
    candidates = sorted(reports_root.glob("*/report-*.json"))
    if not candidates:
        return None
    data = read_json(candidates[-1])
    if isinstance(data, dict) and isinstance(data.get("findings"), list):
        return data["findings"]
    return None


def _existing_file(path: Path) -> Optional[Path]:
    return path if path.exists() else None


def _stage_normalize(dependabot_path: Optional[Path], ecr_path: Optional[Path]) -> Dict[str, Any]:
    dependabot_data = read_json(dependabot_path) if dependabot_path else None
    ecr_data = read_json(ecr_path) if ecr_path else None
    findings = extract_dependabot(dependabot_data) + extract_ecr(ecr_data)
    correlated = correlate(findings)
    return normalized_findings_payload(
        correlated,
        dependabot_present=dependabot_data is not None,
        ecr_present=ecr_data is not None,
    )


def _stage_threat_intel(
    normalized: Dict[str, Any],
    threat_intel_path: Path,
    offline: bool,
    reuse_cached: bool,
) -> Tuple[Dict[str, Any], str]:
    if reuse_cached and threat_intel_path.exists():
        return read_json(threat_intel_path), "no"
    cves = [
        item["cve"]
        for item in normalized.get("items", [])
        if isinstance(item.get("cve"), str)
    ]
    if offline:
        return empty_cache(cves), "no"
    return build_threat_cache(cves), "yes"


def _stage_env_overrides(context_path: Path) -> Dict[str, Any]:
    context = read_json(context_path)
    payload = env_overrides_payload(context)
    payload["context_json"] = "present" if context is not None else "missing"
    return payload


def _run(
    dependabot_path: Optional[Path],
    ecr_path: Optional[Path],
    context_path: Path,
    normalized_out: Path,
    threat_intel_out: Path,
    env_overrides_out: Path,
    output_md: Path,
    output_json: Path,
    offline: bool,
    reuse_threat_cache: bool,
    weights: Optional[Dict[str, float]] = None,
    previous_findings: Optional[List[Dict[str, Any]]] = None,
) -> None:
    normalized = _stage_normalize(dependabot_path, ecr_path)
    write_json(normalized_out, normalized)

    threat, intel_fetch_performed = _stage_threat_intel(
        normalized, threat_intel_out, offline, reuse_threat_cache
    )
    if not (reuse_threat_cache and threat_intel_out.exists()):
        write_json(threat_intel_out, threat)

    env_overrides = _stage_env_overrides(context_path)
    write_json(env_overrides_out, env_overrides)

    run_scoring(
        normalized=normalized,
        threat=threat,
        env_overrides=env_overrides,
        output_md=output_md,
        output_json=output_json,
        intel_fetch_performed=intel_fetch_performed,
        weights=weights,
        previous_findings=previous_findings,
    )


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
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repo root containing .probablyfine/; writes to dated cache and report dirs",
    )
    parser.add_argument("--offline", action="store_true", help="Skip EPSS/KEV fetch")
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

        config = read_json(pf_dir / "config.json") if (pf_dir / "config.json").exists() else {}
        weights: Optional[Dict[str, float]] = None
        if isinstance(config, dict):
            proc = config.get("processing", {})
            if isinstance(proc, dict) and isinstance(proc.get("scoring_weights"), dict):
                weights = proc["scoring_weights"]

        previous_findings = _find_latest_report(report_dir.parent) if report_dir.parent.exists() else None

        _run(
            dependabot_path=_existing_file(pf_dir / "dependabot.json"),
            ecr_path=_existing_file(pf_dir / "ecr_findings.json"),
            context_path=pf_dir / "context.json",
            normalized_out=cache_dir / "normalized_findings.json",
            threat_intel_out=cache_dir / "threat_intel.json",
            env_overrides_out=cache_dir / "env_overrides.json",
            output_md=report_dir / f"report-{ts}.md",
            output_json=report_dir / f"report-{ts}.json",
            offline=args.offline,
            reuse_threat_cache=True,
            weights=weights,
            previous_findings=previous_findings,
        )
    else:
        _run(
            dependabot_path=args.dependabot,
            ecr_path=args.ecr,
            context_path=args.context,
            normalized_out=args.normalized,
            threat_intel_out=args.threat_intel,
            env_overrides_out=args.env_overrides,
            output_md=args.output_md,
            output_json=args.output_json,
            offline=args.offline,
            reuse_threat_cache=False,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
