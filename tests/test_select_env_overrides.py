from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import select_env_overrides


class SelectEnvOverridesTests(unittest.TestCase):
    def test_nested_context_schema_maps_to_expected_overrides(self) -> None:
        context_payload = {
            "schema_version": "0.1.0",
            "component": {"exposure": "internal"},
            "network": {
                "internet_ingress": {"public_entrypoint": True, "unrestricted": False, "mTLS": "unknown"},
                "service_reachability": {
                    "reachable_from_internet_directly": False,
                    "reachable_via_public_ingress": True,
                    "reachable_from_same_vpc": True,
                    "reachable_only_from_cluster": False,
                },
            },
            "auth_boundary": {
                "internet_to_ingress": "strong",
                "ingress_to_service": "weak",
                "privilege_required": "service",
            },
            "data": {
                "confidentiality_requirement": "high",
                "integrity_requirement": "medium",
                "availability_requirement": "low",
            },
            "controls": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            context_path = tmp_path / "context.json"
            output_path = tmp_path / "env_overrides.json"
            context_path.write_text(json.dumps(context_payload), encoding="utf-8")

            with mock.patch.object(
                sys,
                "argv",
                [
                    "select_env_overrides.py",
                    "--context",
                    str(context_path),
                    "--output",
                    str(output_path),
                ],
            ):
                rc = select_env_overrides.main()
            self.assertEqual(rc, 0)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["context_json"], "present")
            self.assertEqual(payload["overrides"]["CR"], "CR:H")
            self.assertEqual(payload["overrides"]["IR"], "IR:M")
            self.assertEqual(payload["overrides"]["AR"], "AR:L")
            self.assertEqual(payload["overrides"]["MAV"], "MAV:N")
            self.assertEqual(payload["overrides"]["MPR"], "MPR:L")
            self.assertEqual(payload["overrides"]["MAC"], "MAC:H")


if __name__ == "__main__":
    unittest.main()
