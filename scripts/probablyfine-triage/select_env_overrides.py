#!/usr/bin/env python3
"""Compatibility wrapper for packaged probablyfine triage stage."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from probablyfine.triage.select_env_overrides import main


if __name__ == "__main__":
    raise SystemExit(main())
