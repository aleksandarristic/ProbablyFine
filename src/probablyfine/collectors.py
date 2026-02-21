#!/usr/bin/env python3
"""Deterministic collectors for external finding sources."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from probablyfine.config_loader import ProbablyFineConfig, ResolvedECRImageRef


class CollectorError(Exception):
    """Raised when a collector cannot fetch required source data."""


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _http_get_json(url: str, headers: dict[str, str], timeout: int) -> Any:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def collect_dependabot_findings(
    config: ProbablyFineConfig,
    repo_path: Path,
    cache_dir: Path,
    timestamp_token: str,
    timeout_seconds: int = 20,
) -> tuple[Path, dict[str, Any]]:
    dep = config.sources.dependabot
    out_path = cache_dir / f"dependabot-raw-{timestamp_token}.json"

    if not dep.enabled:
        _write_json(out_path, [])
        return out_path, {"source": "disabled", "items": 0}

    override = os.environ.get("PROBABLYFINE_DEPENDABOT_FILE", "").strip()
    if override:
        payload = _read_json(Path(override))
        _write_json(out_path, payload)
        count = len(payload) if isinstance(payload, list) else 0
        return out_path, {"source": f"file:{override}", "items": count}

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        fallback = repo_path / "dependabot.json"
        if fallback.exists():
            payload = _read_json(fallback)
            _write_json(out_path, payload)
            count = len(payload) if isinstance(payload, list) else 0
            return out_path, {"source": f"file:{fallback}", "items": count}
        raise CollectorError("GITHUB_TOKEN is required when dependabot source is enabled")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "probablyfine-scanner",
    }
    alerts: list[Any] = []
    page = 1
    while True:
        q = urllib.parse.urlencode({"state": "open", "per_page": "100", "page": str(page)})
        url = f"{dep.api_base.rstrip('/')}/repos/{dep.repository}/dependabot/alerts?{q}"
        payload = _http_get_json(url, headers=headers, timeout=timeout_seconds)
        if not isinstance(payload, list):
            raise CollectorError("Dependabot API payload is not a list")
        alerts.extend(payload)
        if len(payload) < 100:
            break
        page += 1

    _write_json(out_path, alerts)
    return out_path, {"source": "github-api", "items": len(alerts), "pages": page}


def collect_ecr_findings(
    config: ProbablyFineConfig,
    ecr_ref: ResolvedECRImageRef,
    repo_path: Path,
    cache_dir: Path,
    timestamp_token: str,
) -> tuple[Path, dict[str, Any]]:
    out_path = cache_dir / f"ecr-raw-{timestamp_token}.json"

    if not config.sources.ecr.enabled:
        _write_json(out_path, {"findings": []})
        return out_path, {"source": "disabled"}

    override = os.environ.get("PROBABLYFINE_ECR_FILE", "").strip()
    if override:
        payload = _read_json(Path(override))
        _write_json(out_path, payload)
        return out_path, {"source": f"file:{override}"}

    fallback = repo_path / "ecr_findings.json"

    try:
        import boto3  # type: ignore
    except Exception:
        if fallback.exists():
            payload = _read_json(fallback)
            _write_json(out_path, payload)
            return out_path, {"source": f"file:{fallback}"}
        raise CollectorError("boto3 is not available and no local ecr_findings.json fallback exists")

    client = boto3.client("ecr", region_name=ecr_ref.region)
    try:
        payload = client.describe_image_scan_findings(
            registryId=ecr_ref.registry_id,
            repositoryName=ecr_ref.repository,
            imageId=ecr_ref.image_id,
        )
    except Exception as exc:
        if fallback.exists():
            payload = _read_json(fallback)
            _write_json(out_path, payload)
            return out_path, {"source": f"file:{fallback}", "fallback_reason": str(exc)}
        raise CollectorError(f"ECR API request failed: {exc}")

    _write_json(out_path, payload)
    return out_path, {"source": "aws-ecr-api", "image_id": ecr_ref.image_id}
