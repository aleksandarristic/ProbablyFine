#!/usr/bin/env python3
"""Check `.probablyfine/context.json` for schema drift, staleness, and completeness gaps."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from probablyfine.contracts import ValidationError, read_json, validate_json_schema


def _collect_unknown_paths(node: Any, path: str = "$") -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if isinstance(value, str) and value.strip().lower() == "unknown":
                out.append(child)
            else:
                out.extend(_collect_unknown_paths(value, child))
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            out.extend(_collect_unknown_paths(item, f"{path}[{idx}]"))
    return out


def evaluate_context(context_path: Path, schema_path: Path, max_age_days: int, max_unknown_fields: int) -> dict[str, Any]:
    warnings: list[str] = []
    schema_errors: list[str] = []
    exists = context_path.exists()
    payload = read_json(context_path) if exists else None

    if not exists:
        warnings.append("context file missing")
        return {
            "context_path": str(context_path),
            "exists": False,
            "schema_valid": False,
            "schema_errors": ["missing file"],
            "age_days": None,
            "unknown_fields": [],
            "warnings": warnings,
        }

    schema = read_json(schema_path)
    try:
        validate_json_schema(schema, payload)
        schema_valid = True
    except (ValidationError, json.JSONDecodeError) as exc:
        schema_valid = False
        schema_errors.append(str(exc))
        warnings.append("schema validation failed")

    mtime = dt.datetime.fromtimestamp(context_path.stat().st_mtime, tz=dt.timezone.utc)
    age_days = (dt.datetime.now(dt.timezone.utc) - mtime).days
    if age_days > max_age_days:
        warnings.append(f"context appears stale: age_days={age_days} > max_age_days={max_age_days}")

    unknown_fields = _collect_unknown_paths(payload if isinstance(payload, (dict, list)) else {})
    if len(unknown_fields) > max_unknown_fields:
        warnings.append(
            f"context has high unknown-field count: {len(unknown_fields)} > max_unknown_fields={max_unknown_fields}"
        )

    allowed_endpoints = (
        payload.get("network", {}).get("allowed_endpoints", [])
        if isinstance(payload, dict)
        else []
    )
    if isinstance(allowed_endpoints, list) and not allowed_endpoints:
        warnings.append("network.allowed_endpoints is empty")

    return {
        "context_path": str(context_path),
        "exists": True,
        "schema_valid": schema_valid,
        "schema_errors": schema_errors,
        "age_days": age_days,
        "unknown_fields": unknown_fields,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path, default=Path(".probablyfine/context.json"))
    parser.add_argument("--schema", type=Path, default=Path("contracts/schemas/context.schema.json"))
    parser.add_argument("--max-age-days", type=int, default=30)
    parser.add_argument("--max-unknown-fields", type=int, default=8)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    if args.max_age_days < 0:
        raise SystemExit("--max-age-days must be >= 0")
    if args.max_unknown_fields < 0:
        raise SystemExit("--max-unknown-fields must be >= 0")

    report = evaluate_context(args.context, args.schema, args.max_age_days, args.max_unknown_fields)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if report["warnings"]:
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        return 2

    print("context-drift-check: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

