#!/usr/bin/env python3
"""Schema version constants and deterministic migration policy."""

from __future__ import annotations

from typing import Any

from probablyfine.contracts import ValidationError

CURRENT_CONTEXT_SCHEMA_VERSION = "0.1.0"
CURRENT_CONFIG_SCHEMA_VERSION = "0.1.0"


def _require_version(payload: dict[str, Any], label: str) -> str:
    value = payload.get("schema_version")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label}: missing required non-empty schema_version")
    return value.strip()


def migrate_config_payload(payload: dict[str, Any]) -> dict[str, Any]:
    version = _require_version(payload, "$")
    if version == CURRENT_CONFIG_SCHEMA_VERSION:
        return payload
    raise ValidationError(
        "Unsupported config schema_version "
        f"'{version}'. Current supported version is '{CURRENT_CONFIG_SCHEMA_VERSION}'. "
        "No automatic migration is available for this version."
    )

