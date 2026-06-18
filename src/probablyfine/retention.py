#!/usr/bin/env python3
"""Deterministic cache/report retention utility."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any


def _parse_date_dir(path: Path) -> dt.date | None:
    try:
        return dt.datetime.strptime(path.name, "%Y-%m-%d").date()
    except ValueError:
        return None


def _dated_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    items = [p for p in root.iterdir() if p.is_dir() and _parse_date_dir(p) is not None]
    return sorted(items, key=lambda p: p.name)


def _select_for_deletion(paths: list[Path], keep_days: int, keep_latest: int, today: dt.date) -> list[Path]:
    protected = set(paths[-keep_latest:]) if keep_latest > 0 else set()
    delete: list[Path] = []
    for path in paths:
        if path in protected:
            continue
        d = _parse_date_dir(path)
        if d is None:
            continue
        age_days = (today - d).days
        if age_days > keep_days:
            delete.append(path)
    return delete


def _remove_paths(paths: list[Path]) -> None:
    for path in paths:
        shutil.rmtree(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Target repository root containing .probablyfine/")
    parser.add_argument("--keep-days", type=int, default=30, help="Retain dated directories newer than this many days")
    parser.add_argument("--keep-latest", type=int, default=7, help="Always keep this many most recent dated directories")
    parser.add_argument("--apply", action="store_true", help="Apply cleanup. Default is dry-run.")
    parser.add_argument("--report-json", type=Path, default=None, help="Optional path to write retention report JSON")
    args = parser.parse_args()

    if args.keep_days < 0:
        raise SystemExit("--keep-days must be >= 0")
    if args.keep_latest < 0:
        raise SystemExit("--keep-latest must be >= 0")

    pf_dir = args.repo / ".probablyfine"
    cache_root = pf_dir / "cache"
    report_root = pf_dir / "reports"
    today = dt.datetime.now(dt.timezone.utc).date()

    cache_dirs = _dated_dirs(cache_root)
    report_dirs = _dated_dirs(report_root)
    delete_cache = _select_for_deletion(cache_dirs, args.keep_days, args.keep_latest, today)
    delete_reports = _select_for_deletion(report_dirs, args.keep_days, args.keep_latest, today)

    if args.apply:
        _remove_paths(delete_cache)
        _remove_paths(delete_reports)

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo": str(args.repo.resolve()),
        "mode": "apply" if args.apply else "dry-run",
        "keep_days": args.keep_days,
        "keep_latest": args.keep_latest,
        "cache": {
            "root": str(cache_root),
            "total_dated_dirs": len(cache_dirs),
            "delete_count": len(delete_cache),
            "delete_dirs": [str(p) for p in delete_cache],
        },
        "reports": {
            "root": str(report_root),
            "total_dated_dirs": len(report_dirs),
            "delete_count": len(delete_reports),
            "delete_dirs": [str(p) for p in delete_reports],
        },
    }

    if args.report_json:
        _write_json(args.report_json, payload)

    print(
        "retention "
        f"mode={payload['mode']} "
        f"cache_delete={len(delete_cache)} "
        f"reports_delete={len(delete_reports)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

