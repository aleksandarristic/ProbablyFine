#!/usr/bin/env python3
"""Deterministic structural validation for starter .probablyfine contract files."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
STARTER = ROOT / "templates" / "probablyfine-starter" / ".probablyfine"
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from probablyfine.contracts import validate_probablyfine_contract


def main() -> int:
    errors = validate_probablyfine_contract(STARTER.parent, ROOT)
    if errors:
        raise SystemExit("\n".join(errors))

    print("Contract/schema validation passed for starter .probablyfine files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
