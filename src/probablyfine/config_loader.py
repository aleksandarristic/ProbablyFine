#!/usr/bin/env python3
"""Typed loader for `.probablyfine/config.json`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from probablyfine.contracts import ValidationError, read_json, repo_root_from_module, validate_json_schema
from probablyfine.schema_versioning import migrate_config_payload


@dataclass(frozen=True)
class DependabotSource:
    enabled: bool
    repository: str
    api_base: str


@dataclass(frozen=True)
class ECRImage:
    image_type: str
    value: str


@dataclass(frozen=True)
class ECRSource:
    enabled: bool
    region: str
    registry_id: str
    repository: str
    image: ECRImage
    image_uri: str


@dataclass(frozen=True)
class SourceConfig:
    dependabot: DependabotSource
    ecr: ECRSource


@dataclass(frozen=True)
class ProcessingConfig:
    deterministic_mode: bool
    allow_llm_adjustment: bool
    cache_root: str
    report_root: str


@dataclass(frozen=True)
class ProbablyFineConfig:
    schema_version: str
    component_name: str
    sources: SourceConfig
    processing: ProcessingConfig
    raw: dict[str, Any]


@dataclass(frozen=True)
class ResolvedECRImageRef:
    region: str
    registry_id: str
    repository: str
    image_type: str
    image_value: str
    image_uri: str
    normalized_ref: str
    image_id: dict[str, str]


def _require_dict(path: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: expected object")
    return value


def _require_bool(path: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"{path}: expected boolean")
    return value


def _require_str(path: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path}: expected non-empty string")
    return value


def project_root_for_module(module_file: str) -> Path:
    return repo_root_from_module(module_file)


def load_probablyfine_config(config_path: Path, project_root: Path) -> ProbablyFineConfig:
    payload = read_json(config_path)
    root = _require_dict("$", payload)
    root = migrate_config_payload(root)

    schema = read_json(project_root / "contracts" / "schemas" / "config.schema.json")
    validate_json_schema(schema, root)

    sources = _require_dict("$.sources", root.get("sources"))
    github = _require_dict("$.sources.github", sources.get("github"))
    aws = _require_dict("$.sources.aws", sources.get("aws"))
    dep_raw = _require_dict("$.sources.github.dependabot", github.get("dependabot"))
    ecr_raw = _require_dict("$.sources.aws.ecr", aws.get("ecr"))
    image_raw = _require_dict("$.sources.aws.ecr.image", ecr_raw.get("image"))
    proc_raw = _require_dict("$.processing", root.get("processing"))

    dependabot = DependabotSource(
        enabled=_require_bool("$.sources.github.dependabot.enabled", dep_raw.get("enabled")),
        repository=_require_str("$.sources.github.dependabot.repository", dep_raw.get("repository")),
        api_base=_require_str("$.sources.github.dependabot.api_base", dep_raw.get("api_base")),
    )
    ecr = ECRSource(
        enabled=_require_bool("$.sources.aws.ecr.enabled", ecr_raw.get("enabled")),
        region=_require_str("$.sources.aws.ecr.region", ecr_raw.get("region")),
        registry_id=_require_str("$.sources.aws.ecr.registry_id", ecr_raw.get("registry_id")),
        repository=_require_str("$.sources.aws.ecr.repository", ecr_raw.get("repository")),
        image=ECRImage(
            image_type=_require_str("$.sources.aws.ecr.image.type", image_raw.get("type")),
            value=_require_str("$.sources.aws.ecr.image.value", image_raw.get("value")),
        ),
        image_uri=_require_str("$.sources.aws.ecr.image_uri", ecr_raw.get("image_uri")),
    )
    processing = ProcessingConfig(
        deterministic_mode=_require_bool("$.processing.deterministic_mode", proc_raw.get("deterministic_mode")),
        allow_llm_adjustment=_require_bool("$.processing.allow_llm_adjustment", proc_raw.get("allow_llm_adjustment")),
        cache_root=_require_str("$.processing.cache_root", proc_raw.get("cache_root")),
        report_root=_require_str("$.processing.report_root", proc_raw.get("report_root")),
    )

    return ProbablyFineConfig(
        schema_version=_require_str("$.schema_version", root.get("schema_version")),
        component_name=_require_str("$.component_name", root.get("component_name")),
        sources=SourceConfig(dependabot=dependabot, ecr=ecr),
        processing=processing,
        raw=root,
    )


def resolve_ecr_image_reference(config: ProbablyFineConfig) -> ResolvedECRImageRef:
    ecr = config.sources.ecr
    image_type = ecr.image.image_type.strip().lower()
    value = ecr.image.value.strip()

    if image_type not in {"tag", "digest"}:
        raise ValidationError(f"$.sources.aws.ecr.image.type: unsupported type '{image_type}'")

    if image_type == "digest":
        if not value.startswith("sha256:"):
            raise ValidationError("$.sources.aws.ecr.image.value: digest must start with 'sha256:'")
        normalized_ref = f"{ecr.registry_id}.dkr.ecr.{ecr.region}.amazonaws.com/{ecr.repository}@{value}"
        image_id = {"imageDigest": value}
    else:
        normalized_ref = f"{ecr.registry_id}.dkr.ecr.{ecr.region}.amazonaws.com/{ecr.repository}:{value}"
        image_id = {"imageTag": value}

    return ResolvedECRImageRef(
        region=ecr.region,
        registry_id=ecr.registry_id,
        repository=ecr.repository,
        image_type=image_type,
        image_value=value,
        image_uri=ecr.image_uri,
        normalized_ref=normalized_ref,
        image_id=image_id,
    )
