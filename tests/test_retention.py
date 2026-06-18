from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine import retention


class RetentionTests(unittest.TestCase):
    def test_retention_dry_run_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            cache = repo / ".probablyfine" / "cache"
            reports = repo / ".probablyfine" / "reports"
            for root in (cache, reports):
                (root / "2020-01-01").mkdir(parents=True, exist_ok=True)
                (root / "2024-01-01").mkdir(parents=True, exist_ok=True)
                (root / "2026-02-21").mkdir(parents=True, exist_ok=True)

            # Dry-run
            with mock.patch(
                "sys.argv",
                [
                    "retention.py",
                    "--repo",
                    str(repo),
                    "--keep-days",
                    "30",
                    "--keep-latest",
                    "1",
                ],
            ):
                self.assertEqual(retention.main(), 0)
            self.assertTrue((cache / "2020-01-01").exists())

            # Apply
            with mock.patch(
                "sys.argv",
                [
                    "retention.py",
                    "--repo",
                    str(repo),
                    "--keep-days",
                    "30",
                    "--keep-latest",
                    "1",
                    "--apply",
                ],
            ):
                self.assertEqual(retention.main(), 0)
            self.assertFalse((cache / "2020-01-01").exists())
            self.assertFalse((reports / "2020-01-01").exists())
            self.assertTrue((cache / "2026-02-21").exists())
            self.assertTrue((reports / "2026-02-21").exists())


if __name__ == "__main__":
    unittest.main()
