#!/usr/bin/env python3
"""Multi-repo scanner wrapper for ProbablyFine deterministic pipeline."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from probablyfine.collectors import CollectorError, collect_dependabot_findings, collect_ecr_findings
from probablyfine.contracts import repo_root_from_module, validate_probablyfine_contract
from probablyfine.config_loader import (
    ProbablyFineConfig,
    ResolvedECRImageRef,
    load_probablyfine_config,
    resolve_ecr_image_reference,
)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def update_run_index(report_dir: Path, date_str: str) -> Path:
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(report_dir.glob("run-manifest-*.json")):
        payload = _read_json(manifest_path)
        if payload is None:
            continue
        outputs = payload.get("outputs", {}) if isinstance(payload.get("outputs"), dict) else {}
        rows.append(
            {
                "run_id": payload.get("run_id"),
                "repo_path": payload.get("repo_path"),
                "status": payload.get("status"),
                "started_at": payload.get("started_at"),
                "ended_at": payload.get("ended_at"),
                "report_md": outputs.get("report_md"),
                "report_json": outputs.get("report_json"),
                "manifest": str(manifest_path),
            }
        )

    rows.sort(key=lambda row: ((row.get("report_json") or ""), (row.get("run_id") or "")))
    index_path = report_dir / "index.json"
    write_manifest(
        index_path,
        {
            "date": date_str,
            "generated_at": utc_now().isoformat(),
            "total_runs": len(rows),
            "ok": sum(1 for row in rows if row.get("status") == "ok"),
            "failed": sum(1 for row in rows if row.get("status") != "ok"),
            "reports": rows,
        },
    )
    return index_path


def run_pipeline_for_repo(
    repo: Path,
    offline: bool,
    project_root: Path,
    mode: str,
    ecr_ref: ResolvedECRImageRef,
    collector_inputs: dict[str, str],
    collector_meta: dict[str, Any],
) -> tuple[bool, str, Path | None]:
    pf_dir = repo / ".probablyfine"
    started_at = utc_now()
    date_str = started_at.strftime("%Y-%m-%d")
    ts = started_at.strftime("%Y-%m-%dT%H%M%SZ")
    run_id = started_at.strftime("%Y%m%dT%H%M%S%fZ")

    cache_dir = pf_dir / "cache" / date_str
    report_dir = pf_dir / "reports" / date_str
    cache_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = report_dir / f"run-manifest-{run_id}.json"
    cache_audit_path = cache_dir / f"cache-audit-{run_id}.json"

    inputs = {
        "dependabot": collector_inputs["dependabot"],
        "ecr": collector_inputs["ecr"],
        "context": str(pf_dir / "context.json"),
        "config": str(pf_dir / "config.json"),
    }
    outputs = {
        "normalized": str(cache_dir / "normalized_findings.json"),
        "threat_intel": str(cache_dir / "threat_intel.json"),
        "env_overrides": str(cache_dir / "env_overrides.json"),
        "report_md": str(report_dir / f"report-{ts}.md"),
        "report_json": str(report_dir / f"report-{ts}.json"),
    }
    cmd = [
        sys.executable,
        "-m",
        "probablyfine.triage.triage_pipeline",
        "--dependabot",
        inputs["dependabot"],
        "--ecr",
        inputs["ecr"],
        "--context",
        inputs["context"],
        "--normalized",
        outputs["normalized"],
        "--threat-intel",
        outputs["threat_intel"],
        "--env-overrides",
        outputs["env_overrides"],
        "--output-md",
        outputs["report_md"],
        "--output-json",
        outputs["report_json"],
    ]
    if offline:
        cmd.append("--offline")

    env = os.environ.copy()
    src_dir = project_root / "src"
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) if not current else f"{src_dir}:{current}"

    status = "ok"
    exit_code = 0
    error: str | None = None
    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as exc:
        status = "error"
        exit_code = exc.returncode
        error = f"pipeline failed with exit code {exc.returncode}"

    ended_at = utc_now()
    write_manifest(
        manifest_path,
        {
            "run_id": run_id,
            "repo_path": str(repo),
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_seconds": round((ended_at - started_at).total_seconds(), 3),
            "mode": mode,
            "offline": offline,
            "status": status,
            "exit_code": exit_code,
            "error": error,
            "inputs": inputs,
            "outputs": outputs,
            "resolved_ecr_image_ref": {
                "normalized_ref": ecr_ref.normalized_ref,
                "image_type": ecr_ref.image_type,
                "image_value": ecr_ref.image_value,
                "image_id": ecr_ref.image_id,
            },
            "collector_meta": collector_meta,
            "command": cmd,
        },
    )
    write_manifest(
        cache_audit_path,
        {
            "run_id": run_id,
            "repo_path": str(repo),
            "date": date_str,
            "generated_at": ended_at.isoformat(),
            "status": status,
            "collector_inputs": collector_inputs,
            "collector_meta": collector_meta,
            "derived_artifacts": {
                "normalized_findings": outputs["normalized"],
                "threat_intel": outputs["threat_intel"],
                "env_overrides": outputs["env_overrides"],
            },
            "report_artifacts": {
                "markdown": outputs["report_md"],
                "json": outputs["report_json"],
                "manifest": str(manifest_path),
            },
        },
    )
    update_run_index(report_dir, date_str)
    if status != "ok":
        return False, error or "pipeline failed", manifest_path

    return True, "ok", manifest_path


def process_repo(
    repo: Path,
    offline: bool,
    project_root: Path,
    mode: str,
) -> tuple[Path, bool, str]:
    repo_path = repo.resolve()
    errors = validate_probablyfine_contract(repo_path, project_root)
    if errors:
        return repo_path, False, "; ".join(errors)

    config_path = repo_path / ".probablyfine" / "config.json"
    try:
        config: ProbablyFineConfig = load_probablyfine_config(config_path, project_root)
    except Exception as exc:
        return repo_path, False, f"{config_path}: typed config load failed: {exc}"

    if not config.processing.deterministic_mode:
        return repo_path, False, f"{config_path}: deterministic_mode must be true"

    try:
        ecr_ref = resolve_ecr_image_reference(config)
    except Exception as exc:
        return repo_path, False, f"{config_path}: ecr image reference resolution failed: {exc}"

    started_at = utc_now()
    date_str = started_at.strftime("%Y-%m-%d")
    ts = started_at.strftime("%Y-%m-%dT%H%M%SZ")
    cache_dir = repo_path / ".probablyfine" / "cache" / date_str
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        dep_path, dep_meta = collect_dependabot_findings(
            config=config,
            repo_path=repo_path,
            cache_dir=cache_dir,
            timestamp_token=ts,
        )
    except CollectorError as exc:
        return repo_path, False, f"dependabot collector failed: {exc}"

    try:
        ecr_path, ecr_meta = collect_ecr_findings(
            config=config,
            ecr_ref=ecr_ref,
            repo_path=repo_path,
            cache_dir=cache_dir,
            timestamp_token=ts,
        )
    except CollectorError as exc:
        return repo_path, False, f"ecr collector failed: {exc}"

    collector_inputs = {
        "dependabot": str(dep_path),
        "ecr": str(ecr_path),
    }
    collector_meta: dict[str, Any] = {
        "dependabot": dep_meta,
        "ecr": ecr_meta,
    }

    ok, detail, manifest = run_pipeline_for_repo(
        repo_path,
        offline=offline,
        project_root=project_root,
        mode=mode,
        ecr_ref=ecr_ref,
        collector_inputs=collector_inputs,
        collector_meta=collector_meta,
    )
    if manifest:
        detail = f"{detail}; manifest={manifest}"
    return repo_path, ok, detail


def load_repos(repo_args: list[Path], repo_list: Path | None) -> list[Path]:
    repos: list[Path] = list(repo_args)
    if repo_list is None:
        return repos

    with repo_list.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            repos.append(Path(line))
    return repos


def batched_repos(repos: list[Path], batch_size: int) -> list[list[Path]]:
    if batch_size <= 0:
        return [repos]
    return [repos[i : i + batch_size] for i in range(0, len(repos), batch_size)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repos", nargs="*", type=Path, help="One or more repository roots to scan")
    parser.add_argument(
        "--repo-list",
        type=Path,
        default=None,
        help="Optional newline-delimited file of repo paths (supports # comments).",
    )
    parser.add_argument("--offline", action="store_true", help="Skip internet EPSS/KEV fetch stage")
    parser.add_argument("--mode", choices=["sequential", "parallel"], default="sequential")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker count when --mode parallel")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Max repos per processing batch. 0 means no batching.",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional path to write deterministic run summary JSON.",
    )
    args = parser.parse_args()

    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    if args.batch_size < 0:
        raise SystemExit("--batch-size must be >= 0")

    repos = load_repos(args.repos, args.repo_list)
    if not repos:
        raise SystemExit("No repository paths supplied. Use positional repos and/or --repo-list.")

    project_root = repo_root_from_module(__file__)
    results: list[tuple[Path, bool, str]] = []
    batches = batched_repos(repos, args.batch_size)

    for batch_index, batch in enumerate(batches, start=1):
        print(f"batch {batch_index}/{len(batches)} size={len(batch)}")

        if args.mode == "sequential":
            for repo in batch:
                results.append(process_repo(repo, offline=args.offline, project_root=project_root, mode=args.mode))
        else:
            indexed_results: dict[int, tuple[Path, bool, str]] = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {
                    pool.submit(process_repo, repo, args.offline, project_root, args.mode): idx
                    for idx, repo in enumerate(batch)
                }
                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    indexed_results[idx] = future.result()
            for idx in range(len(batch)):
                results.append(indexed_results[idx])

    failures = [r for r in results if not r[1]]
    summary_payload = {
        "generated_at": utc_now().isoformat(),
        "mode": args.mode,
        "workers": args.workers,
        "batch_size": args.batch_size,
        "total_batches": len(batches),
        "offline": args.offline,
        "total": len(results),
        "ok": len(results) - len(failures),
        "failed": len(failures),
        "results": [
            {"repo": str(repo), "status": "ok" if ok else "error", "detail": detail}
            for repo, ok, detail in results
        ],
    }
    for repo, ok, detail in results:
        state = "OK" if ok else "ERROR"
        print(f"[{state}] {repo} :: {detail}")

    print(f"summary: total={len(results)} ok={len(results) - len(failures)} failed={len(failures)}")
    if args.summary_json is not None:
        write_manifest(args.summary_json, summary_payload)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
