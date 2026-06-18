from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import triage_pipeline


class TriagePipelineTests(unittest.TestCase):
    def test_repo_root_reads_probablyfine_input_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "repo"
            pf_dir = repo / ".probablyfine"
            pf_dir.mkdir(parents=True)

            project_root = Path(__file__).resolve().parents[1]
            starter = project_root / "templates" / "probablyfine-starter" / ".probablyfine"
            (pf_dir / "context.json").write_text(
                (starter / "context.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (pf_dir / "config.json").write_text(
                (starter / "config.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (pf_dir / "dependabot.json").write_text(
                json.dumps(
                    [
                        {
                            "number": 101,
                            "security_advisory": {
                                "severity": "high",
                                "identifiers": [{"type": "CVE", "value": "CVE-2024-5555"}],
                                "cvss": {
                                    "vector_string": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H"
                                },
                            },
                            "dependency": {"package": {"name": "requests"}},
                            "security_vulnerability": {
                                "first_patched_version": {"identifier": "2.32.5"},
                                "severity": "high",
                            },
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (pf_dir / "ecr_findings.json").write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "severity": "MEDIUM",
                                "packageVulnerabilityDetails": {
                                    "vulnerabilityId": "CVE-2024-5555",
                                    "vulnerablePackages": [
                                        {"name": "requests", "fixedInVersion": "2.32.5"}
                                    ],
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                sys,
                "argv",
                ["triage_pipeline.py", "--repo-root", str(repo), "--offline"],
            ):
                self.assertEqual(triage_pipeline.main(), 0)

            report_json = next((pf_dir / "reports").glob("*/report-*.json"))
            payload = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["findings"]), 1)
            self.assertEqual(payload["findings"][0]["source_bucket"], "Both")

            normalized_json = next((pf_dir / "cache").glob("*/normalized_findings.json"))
            normalized = json.loads(normalized_json.read_text(encoding="utf-8"))
            self.assertEqual(normalized["inputs"]["dependabot.json"], "present")
            self.assertEqual(normalized["inputs"]["ecr_findings.json"], "present")


if __name__ == "__main__":
    unittest.main()
