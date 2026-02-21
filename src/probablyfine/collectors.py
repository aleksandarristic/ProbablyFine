#!/usr/bin/env python3
"""Deterministic collectors for external finding sources."""

from __future__ import annotations

import json
import os
import time
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


def _env_int(name: str, default: int, min_value: int = 0, max_value: int = 3600) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise CollectorError(f"{name} must be an integer") from exc
    if parsed < min_value or parsed > max_value:
        raise CollectorError(f"{name} must be between {min_value} and {max_value}")
    return parsed


def _retry_call(fn, attempts: int, sleep_seconds: int, label: str):
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt == attempts:
                break
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
    raise CollectorError(f"{label} failed after {attempts} attempts: {last_exc}")


def validate_collector_auth(config: ProbablyFineConfig, repo_path: Path) -> list[str]:
    errors: list[str] = []

    dep = config.sources.dependabot
    if dep.enabled:
        override = os.environ.get("PROBABLYFINE_DEPENDABOT_FILE", "").strip()
        if override and not Path(override).exists():
            errors.append(f"PROBABLYFINE_DEPENDABOT_FILE does not exist: {override}")
        elif not override:
            token = os.environ.get("GITHUB_TOKEN", "").strip()
            fallback = repo_path / "dependabot.json"
            if not token and not fallback.exists():
                errors.append(
                    "Dependabot auth unavailable: set GITHUB_TOKEN or provide "
                    "PROBABLYFINE_DEPENDABOT_FILE or repo-local dependabot.json"
                )

    ecr = config.sources.ecr
    if ecr.enabled:
        override = os.environ.get("PROBABLYFINE_ECR_FILE", "").strip()
        if override and not Path(override).exists():
            errors.append(f"PROBABLYFINE_ECR_FILE does not exist: {override}")
        elif not override:
            fallback = repo_path / "ecr_findings.json"
            if not fallback.exists():
                try:
                    import boto3  # type: ignore # noqa: F401
                except Exception:
                    errors.append(
                        "ECR auth unavailable: install boto3 with AWS credentials or provide "
                        "PROBABLYFINE_ECR_FILE or repo-local ecr_findings.json"
                    )

    return errors


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

    max_attempts = _env_int("PROBABLYFINE_HTTP_MAX_ATTEMPTS", 3, 1, 10)
    retry_sleep = _env_int("PROBABLYFINE_HTTP_RETRY_SLEEP_SECONDS", 1, 0, 60)
    page_sleep = _env_int("PROBABLYFINE_GITHUB_PAGE_SLEEP_SECONDS", 0, 0, 60)
    timeout = _env_int("PROBABLYFINE_HTTP_TIMEOUT_SECONDS", timeout_seconds, 1, 120)

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
        payload = _retry_call(
            lambda: _http_get_json(url, headers=headers, timeout=timeout),
            attempts=max_attempts,
            sleep_seconds=retry_sleep,
            label=f"Dependabot page {page} request",
        )
        if not isinstance(payload, list):
            raise CollectorError("Dependabot API payload is not a list")
        alerts.extend(payload)
        if len(payload) < 100:
            break
        if page_sleep > 0:
            time.sleep(page_sleep)
        page += 1

    _write_json(out_path, alerts)
    return out_path, {
        "source": "github-api",
        "items": len(alerts),
        "pages": page,
        "timeout_seconds": timeout,
        "max_attempts": max_attempts,
        "retry_sleep_seconds": retry_sleep,
        "page_sleep_seconds": page_sleep,
    }


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
    max_attempts = _env_int("PROBABLYFINE_AWS_MAX_ATTEMPTS", 3, 1, 10)
    retry_sleep = _env_int("PROBABLYFINE_AWS_RETRY_SLEEP_SECONDS", 1, 0, 60)
    timeout = _env_int("PROBABLYFINE_AWS_TIMEOUT_SECONDS", 20, 1, 120)

    try:
        import boto3  # type: ignore
        from botocore.config import Config as BotoConfig  # type: ignore
    except Exception:
        if fallback.exists():
            payload = _read_json(fallback)
            _write_json(out_path, payload)
            return out_path, {"source": f"file:{fallback}"}
        raise CollectorError("boto3 is not available and no local ecr_findings.json fallback exists")

    client = boto3.client(
        "ecr",
        region_name=ecr_ref.region,
        config=BotoConfig(connect_timeout=timeout, read_timeout=timeout, retries={"max_attempts": 1}),
    )
    try:
        payload = _retry_call(
            lambda: client.describe_image_scan_findings(
                registryId=ecr_ref.registry_id,
                repositoryName=ecr_ref.repository,
                imageId=ecr_ref.image_id,
            ),
            attempts=max_attempts,
            sleep_seconds=retry_sleep,
            label="ECR describe_image_scan_findings",
        )
    except Exception as exc:
        if fallback.exists():
            payload = _read_json(fallback)
            _write_json(out_path, payload)
            return out_path, {"source": f"file:{fallback}", "fallback_reason": str(exc)}
        raise CollectorError(f"ECR API request failed: {exc}")

    _write_json(out_path, payload)
    return out_path, {
        "source": "aws-ecr-api",
        "image_id": ecr_ref.image_id,
        "timeout_seconds": timeout,
        "max_attempts": max_attempts,
        "retry_sleep_seconds": retry_sleep,
    }
