#!/usr/bin/env python3
"""Compatibility wrapper that re-exports packaged pipeline helpers."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from probablyfine.triage.pipeline_common import *  # noqa: F403
