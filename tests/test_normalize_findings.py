from __future__ import annotations

import unittest

from probablyfine.triage.pipeline_common import (
    InputFinding,
    correlate,
    normalized_findings_payload,
)


class NormalizeFindingsTests(unittest.TestCase):
    def test_correlation_is_order_stable_for_base_vector(self) -> None:
        finding_a = InputFinding(
            source="Dependabot",
            cve="CVE-2024-0001",
            package="openssl",
            severity="high",
            fix_version="1.0.2z",
            base_vector="CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N",
            evidence="a",
        )
        finding_b = InputFinding(
            source="ECR",
            cve="CVE-2024-0001",
            package="openssl",
            severity="critical",
            fix_version="1.0.2y",
            base_vector="CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H",
            evidence="b",
        )

        first = correlate([finding_a, finding_b])
        second = correlate([finding_b, finding_a])

        self.assertEqual(first[0].cve, second[0].cve)
        self.assertEqual(first[0].package, second[0].package)
        self.assertEqual(first[0].severity, second[0].severity)
        self.assertEqual(first[0].fix_version, second[0].fix_version)
        self.assertEqual(first[0].base_vector, second[0].base_vector)

    def test_payload_is_sorted_and_deduped(self) -> None:
        findings = [
            InputFinding(
                source="ECR",
                cve="CVE-2025-9999",
                package="zlib",
                severity="medium",
                fix_version=None,
                base_vector=None,
                evidence="e2",
            ),
            InputFinding(
                source="Dependabot",
                cve="CVE-2024-1111",
                package="requests",
                severity="high",
                fix_version="2.32.5",
                base_vector=None,
                evidence="e1",
            ),
            InputFinding(
                source="ECR",
                cve="CVE-2024-1111",
                package="requests",
                severity="low",
                fix_version="2.32.4",
                base_vector=None,
                evidence="e3",
            ),
        ]

        payload = normalized_findings_payload(
            correlate(findings),
            dependabot_present=True,
            ecr_present=True,
        )
        items = payload["items"]

        self.assertEqual([item["cve"] for item in items], ["CVE-2024-1111", "CVE-2025-9999"])
        self.assertEqual(items[0]["source_bucket"], "Both")
        self.assertEqual(items[0]["severity"], "high")
        self.assertEqual(items[0]["fix_version"], "2.32.4")


if __name__ == "__main__":
    unittest.main()
