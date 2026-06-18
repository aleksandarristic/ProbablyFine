from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import verify_determinism


class VerifyDeterminismTests(unittest.TestCase):
    def test_harness_passes_for_static_fixture_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dep = tmp_path / "dependabot.json"
            ecr = tmp_path / "ecr.json"
            context = tmp_path / "context.json"

            dep.write_text(
                json.dumps(
                    [
                        {
                            "number": 1,
                            "security_advisory": {
                                "severity": "high",
                                "identifiers": [{"type": "CVE", "value": "CVE-2024-1111"}],
                            },
                            "dependency": {"package": {"name": "requests"}},
                            "security_vulnerability": {"first_patched_version": {"identifier": "2.32.5"}},
                        }
                    ]
                ),
                encoding="utf-8",
            )
            ecr.write_text(json.dumps({"findings": []}), encoding="utf-8")

            project_root = Path(__file__).resolve().parents[1]
            starter_context = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "context.json"
            context.write_text(starter_context.read_text(encoding="utf-8"), encoding="utf-8")

            with mock.patch(
                "sys.argv",
                [
                    "verify_determinism.py",
                    "--dependabot",
                    str(dep),
                    "--ecr",
                    str(ecr),
                    "--context",
                    str(context),
                    "--fixed-time",
                    "2026-01-01T00:00:00+00:00",
                ],
            ):
                self.assertEqual(verify_determinism.main(), 0)


if __name__ == "__main__":
    unittest.main()

