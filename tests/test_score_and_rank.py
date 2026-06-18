from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import score_and_rank


class ScoreAndRankTests(unittest.TestCase):
    def test_scoring_is_deterministic_and_sorted(self) -> None:
        normalized = {
            "inputs": {"dependabot.json": "present", "ecr_findings.json": "present"},
            "items": [
                {
                    "cve": "cve-2024-0001",
                    "package": "openssl",
                    "severity": "critical",
                    "fix_version": "3.0.13",
                    "cvss4_base_vector": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H",
                    "sources": ["ECR", "Dependabot"],
                    "source_bucket": "Both",
                    "evidence_ids": ["b", "a"],
                },
                {
                    "cve": "CVE-2024-0002",
                    "package": "zlib",
                    "severity": "medium",
                    "fix_version": None,
                    "cvss4_base_vector": None,
                    "sources": ["ECR"],
                    "source_bucket": "ECR-only",
                    "evidence_ids": ["z"],
                },
            ],
        }
        threat_intel = {
            "items": [
                {"cve": "CVE-2024-0001", "epss_probability": 0.95, "cisa_kev_listed": False},
                {"cve": "CVE-2024-0002", "epss_probability": 0.05, "cisa_kev_listed": False},
            ]
        }
        env_overrides = {
            "context_json": "present",
            "overrides": {
                "CR": "CR:H",
                "IR": "IR:M",
                "AR": "AR:M",
                "MAV": "MAV:N",
                "MAC": "MAC:H",
                "MPR": "MPR:L",
                "exposure": "internal",
            },
            "runtime_presence_default": "runtime",
            "runtime_presence_by_package": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            normalized_path = tmp_path / "normalized_findings.json"
            threat_path = tmp_path / "threat_intel.json"
            env_path = tmp_path / "env_overrides.json"
            md_a = tmp_path / "report-a.md"
            json_a = tmp_path / "report-a.json"
            md_b = tmp_path / "report-b.md"
            json_b = tmp_path / "report-b.json"

            normalized_path.write_text(json.dumps(normalized), encoding="utf-8")
            threat_path.write_text(json.dumps(threat_intel), encoding="utf-8")
            env_path.write_text(json.dumps(env_overrides), encoding="utf-8")

            for md_out, json_out in ((md_a, json_a), (md_b, json_b)):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "score_and_rank.py",
                        "--normalized",
                        str(normalized_path),
                        "--threat-intel",
                        str(threat_path),
                        "--env-overrides",
                        str(env_path),
                        "--output-md",
                        str(md_out),
                        "--output-json",
                        str(json_out),
                        "--intel-fetch-performed",
                        "yes",
                    ],
                ):
                    rc = score_and_rank.main()
                self.assertEqual(rc, 0)

            first_json = json.loads(json_a.read_text(encoding="utf-8"))
            second_json = json.loads(json_b.read_text(encoding="utf-8"))
            self.assertEqual(first_json, second_json)
            self.assertEqual(md_a.read_text(encoding="utf-8"), md_b.read_text(encoding="utf-8"))

            findings = first_json["findings"]
            self.assertEqual(findings[0]["cve"], "CVE-2024-0001")
            self.assertGreater(findings[0]["risk"], findings[1]["risk"])
            self.assertIn("/E:A", findings[0]["final_vector"])
            self.assertEqual(findings[1]["final_vector"], "unknown")


if __name__ == "__main__":
    unittest.main()
