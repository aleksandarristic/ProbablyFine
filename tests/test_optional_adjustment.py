from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import optional_adjustment


class OptionalAdjustmentTests(unittest.TestCase):
    def test_stage_emits_annotations_without_mutating_base_score_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report_json = tmp_path / "report.json"
            output_json = tmp_path / "llm-adjustment.json"
            report_json.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "cve": "CVE-2024-1111",
                                "package": "requests",
                                "severity": "critical",
                                "e": "A",
                                "runtime": "runtime",
                                "source_bucket": "Both",
                                "fix_version": "2.32.5",
                                "risk": 90,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch(
                "sys.argv",
                [
                    "optional_adjustment.py",
                    "--report-json",
                    str(report_json),
                    "--output",
                    str(output_json),
                ],
            ):
                self.assertEqual(optional_adjustment.main(), 0)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertFalse(payload["adjustment_enabled"])
            self.assertEqual(payload["annotations"][0]["base_risk"], 90)
            self.assertEqual(payload["annotations"][0]["adjusted_risk"], 90)

    def test_stage_applies_adjusted_risk_only_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report_json = tmp_path / "report.json"
            output_json = tmp_path / "llm-adjustment.json"
            report_json.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "cve": "CVE-2024-1111",
                                "package": "requests",
                                "severity": "critical",
                                "e": "A",
                                "runtime": "runtime",
                                "source_bucket": "Both",
                                "fix_version": "2.32.5",
                                "risk": 90,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch(
                "sys.argv",
                [
                    "optional_adjustment.py",
                    "--report-json",
                    str(report_json),
                    "--output",
                    str(output_json),
                    "--enable-adjustment",
                ],
            ):
                self.assertEqual(optional_adjustment.main(), 0)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["adjustment_enabled"])
            self.assertGreater(payload["annotations"][0]["adjusted_risk"], payload["annotations"][0]["base_risk"])


if __name__ == "__main__":
    unittest.main()

