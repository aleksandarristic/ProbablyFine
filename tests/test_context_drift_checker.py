from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import context_drift_checker


class ContextDriftCheckerTests(unittest.TestCase):
    def test_warns_on_stale_and_unknown_heavy_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            context = tmp_path / "context.json"
            schema = Path(__file__).resolve().parents[1] / "contracts" / "schemas" / "context.schema.json"
            payload = {
                "schema_version": "0.1.0",
                "component": {
                    "name": "svc",
                    "type": "service",
                    "runtime": "unknown",
                    "orchestrator": "unknown",
                    "cloud": "unknown",
                    "platform": "unknown",
                    "namespace": "unknown",
                    "exposure": "unknown",
                },
                "network": {
                    "internet_ingress": {
                        "public_entrypoint": False,
                        "unrestricted": False,
                        "fronted_by": [],
                        "authn": "unknown",
                        "authz": "unknown",
                        "rate_limited": False,
                        "waf": "unknown",
                        "mTLS": "unknown",
                    },
                    "service_reachability": {
                        "reachable_from_internet_directly": False,
                        "reachable_via_public_ingress": False,
                        "reachable_from_same_vpc": False,
                        "reachable_only_from_cluster": False,
                    },
                    "allowed_endpoints": [],
                    "default_deny": True,
                },
                "auth_boundary": {
                    "internet_to_ingress": "unknown",
                    "ingress_to_service": "unknown",
                    "service_requires_auth": False,
                    "auth_type": [],
                    "privilege_required": "unknown",
                },
                "data": {
                    "confidentiality_requirement": "unknown",
                    "integrity_requirement": "unknown",
                    "availability_requirement": "unknown",
                },
                "controls": {
                    "reverse_proxy_hardened": False,
                    "input_validation_at_edge": "unknown",
                    "egress_restricted": "unknown",
                    "pod_security": "unknown",
                    "network_policy_enforced": "unknown",
                },
            }
            context.write_text(json.dumps(payload), encoding="utf-8")
            old_time = 946684800  # 2000-01-01
            os.utime(context, (old_time, old_time))

            with mock.patch(
                "sys.argv",
                [
                    "context_drift_checker.py",
                    "--context",
                    str(context),
                    "--schema",
                    str(schema),
                    "--max-age-days",
                    "1",
                    "--max-unknown-fields",
                    "1",
                ],
            ):
                self.assertEqual(context_drift_checker.main(), 2)


if __name__ == "__main__":
    unittest.main()

