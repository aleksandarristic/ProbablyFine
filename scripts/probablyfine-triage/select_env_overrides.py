#!/usr/bin/env python3
"""Stage 3: map context facts into bounded CVSSv4 Environmental overrides."""

from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_common import env_overrides_payload, read_json, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path, default=Path("context.json"))
    parser.add_argument("--output", type=Path, default=Path("env_overrides.json"))
    args = parser.parse_args()

    context = read_json(args.context)
    payload = env_overrides_payload(context)
    payload["context_json"] = "present" if context is not None else "missing"
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
