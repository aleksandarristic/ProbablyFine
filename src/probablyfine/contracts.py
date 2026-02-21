#!/usr/bin/env python3
"""Deterministic helpers for `.probablyfine` contract and schema validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    """Raised when a schema or contract validation check fails."""


def repo_root_from_module(module_file: str) -> Path:
    return Path(module_file).resolve().parents[2]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _expect_type(value: Any, expected: str, path: str) -> None:
    checks = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
    }
    if not checks.get(expected, True):
        raise ValidationError(f"{path}: expected type '{expected}'")


def validate_json_schema(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    """Validate a JSON value against a bounded subset of JSON schema keywords."""
    if "type" in schema:
        _expect_type(value, schema["type"], path)

    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const value {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: value {value!r} not in enum {schema['enum']!r}")

    if "minLength" in schema and isinstance(value, str) and len(value) < int(schema["minLength"]):
        raise ValidationError(f"{path}: string shorter than minLength={schema['minLength']}")

    if schema.get("type") == "object" and isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required key '{key}'")

        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, val in value.items():
            if key in props:
                validate_json_schema(props[key], val, f"{path}.{key}")
            elif additional is False:
                raise ValidationError(f"{path}: unexpected key '{key}'")

    if schema.get("type") == "array" and isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(value):
                validate_json_schema(item_schema, item, f"{path}[{i}]")


def validate_probablyfine_contract(repo_path: Path, project_root: Path) -> list[str]:
    errors: list[str] = []
    repo = repo_path.resolve()
    pf = repo / ".probablyfine"
    schemas = project_root / "contracts" / "schemas"

    if not repo.exists() or not repo.is_dir():
        return [f"{repo}: repository path does not exist or is not a directory"]

    required_paths = [pf, pf / "context.json", pf / "config.json", pf / "cache", pf / "reports"]
    for p in required_paths:
        if not p.exists():
            errors.append(f"{repo}: missing required path: {p}")
    if errors:
        return errors

    try:
        context_schema = read_json(schemas / "context.schema.json")
        config_schema = read_json(schemas / "config.schema.json")
        context = read_json(pf / "context.json")
        config = read_json(pf / "config.json")
        validate_json_schema(context_schema, context)
        validate_json_schema(config_schema, config)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        errors.append(f"{repo}: contract/schema validation failed: {exc}")

    return errors
