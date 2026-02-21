from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import fetch_threat_intel


class FetchThreatIntelTests(unittest.TestCase):
    def test_offline_emits_deterministic_empty_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            normalized_path = tmp_path / "normalized_findings.json"
            output_path = tmp_path / "threat_intel.json"
            normalized_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {"cve": "CVE-2024-0002"},
                            {"cve": "CVE-2024-0001"},
                            {"cve": "CVE-2024-0002"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                sys,
                "argv",
                [
                    "fetch_threat_intel.py",
                    "--normalized",
                    str(normalized_path),
                    "--output",
                    str(output_path),
                    "--offline",
                ],
            ):
                rc = fetch_threat_intel.main()
            self.assertEqual(rc, 0)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["fetch_status"], "fallback-empty")
            self.assertEqual(
                [item["cve"] for item in payload["items"]],
                ["CVE-2024-0001", "CVE-2024-0002"],
            )

    def test_fetch_failure_falls_back_to_empty_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            normalized_path = tmp_path / "normalized_findings.json"
            output_path = tmp_path / "threat_intel.json"
            normalized_path.write_text(
                json.dumps({"items": [{"cve": "CVE-2024-1111"}]}),
                encoding="utf-8",
            )

            with mock.patch.object(fetch_threat_intel, "build_threat_cache", side_effect=RuntimeError("boom")):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "fetch_threat_intel.py",
                        "--normalized",
                        str(normalized_path),
                        "--output",
                        str(output_path),
                    ],
                ):
                    rc = fetch_threat_intel.main()
            self.assertEqual(rc, 0)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["fetch_status"], "fallback-empty")
            self.assertEqual(payload["items"][0]["cve"], "CVE-2024-1111")


if __name__ == "__main__":
    unittest.main()
