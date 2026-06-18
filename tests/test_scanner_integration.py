from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine import scanner


class ScannerIntegrationTests(unittest.TestCase):
    def test_full_repo_processing_emits_cache_and_report_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "repo-a"
            pf_dir = repo / ".probablyfine"
            cache_root = pf_dir / "cache"
            report_root = pf_dir / "reports"
            cache_root.mkdir(parents=True, exist_ok=True)
            report_root.mkdir(parents=True, exist_ok=True)

            project_root = Path(__file__).resolve().parents[1]
            context_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "context.json"
            config_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "config.json"
            (pf_dir / "context.json").write_text(context_template.read_text(encoding="utf-8"), encoding="utf-8")
            (pf_dir / "config.json").write_text(config_template.read_text(encoding="utf-8"), encoding="utf-8")

            dep_file = tmp_path / "dependabot.json"
            ecr_file = tmp_path / "ecr_findings.json"
            dep_file.write_text(
                json.dumps(
                    [
                        {
                            "number": 101,
                            "security_advisory": {
                                "severity": "high",
                                "identifiers": [{"type": "CVE", "value": "CVE-2024-5555"}],
                                "cvss": {
                                    "vector_string": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H"
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
            ecr_file.write_text(
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

            env_updates = {
                "PROBABLYFINE_DEPENDABOT_FILE": str(dep_file),
                "PROBABLYFINE_ECR_FILE": str(ecr_file),
                "PYTHONPATH": str(project_root / "src"),
            }
            with mock.patch.dict(os.environ, env_updates, clear=False):
                with mock.patch.object(sys, "argv", ["scanner.py", str(repo), "--offline"]):
                    rc = scanner.main()
            self.assertEqual(rc, 0)

            dated_cache_dirs = [p for p in cache_root.iterdir() if p.is_dir()]
            dated_report_dirs = [p for p in report_root.iterdir() if p.is_dir()]
            self.assertEqual(len(dated_cache_dirs), 1)
            self.assertEqual(len(dated_report_dirs), 1)

            cache_dir = dated_cache_dirs[0]
            report_dir = dated_report_dirs[0]
            self.assertTrue((cache_dir / "normalized_findings.json").exists())
            self.assertTrue((cache_dir / "threat_intel.json").exists())
            self.assertTrue((cache_dir / "env_overrides.json").exists())
            self.assertTrue(any(cache_dir.glob("dependabot-raw-*.json")))
            self.assertTrue(any(cache_dir.glob("ecr-raw-*.json")))
            self.assertTrue(any(cache_dir.glob("cache-audit-*.json")))
            self.assertTrue(any(report_dir.glob("report-*.md")))
            self.assertTrue(any(report_dir.glob("report-*.json")))
            self.assertTrue(any(report_dir.glob("run-manifest-*.json")))
            self.assertTrue((report_dir / "index.json").exists())

            index_payload = json.loads((report_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index_payload["total_runs"], 1)
            self.assertEqual(index_payload["ok"], 1)
            self.assertEqual(index_payload["failed"], 0)
            self.assertEqual(len(index_payload["reports"]), 1)
            self.assertTrue(str(index_payload["reports"][0]["report_json"]).endswith(".json"))


if __name__ == "__main__":
    unittest.main()
