#!/usr/bin/env python3
"""Stage 2: deterministic EPSS/KEV threat intel fetch and cache generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline_common import KEV_REPO_URL, EPSS_URL, build_threat_cache, read_json, write_json


def empty_cache(cves: list[str]) -> dict:
    return {
        "generated_at": None,
        "sources": {"epss": EPSS_URL, "kev": KEV_REPO_URL},
        "items": [
            {
                "cve": cve,
                "epss_probability": None,
                "epss_percentile": None,
                "cisa_kev_listed": False,
                "kev_date_added": None,
                "kev_due_date": None,
            }
            for cve in sorted(set(cves))
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized", type=Path, default=Path("normalized_findings.json"))
    parser.add_argument("--output", type=Path, default=Path("threat_intel.json"))
    parser.add_argument("--offline", action="store_true", help="Skip internet fetch and emit null intel")
    args = parser.parse_args()

    normalized = read_json(args.normalized) or {}
    items = normalized.get("items", []) if isinstance(normalized, dict) else []
    cves = sorted(
        {
            item.get("cve")
            for item in items
            if isinstance(item, dict) and isinstance(item.get("cve"), str) and item.get("cve")
        }
    )

    if args.offline:
        write_json(args.output, empty_cache(cves))
        return 0

    cache = build_threat_cache(cves)
    write_json(args.output, cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
