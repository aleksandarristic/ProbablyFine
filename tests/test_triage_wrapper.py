from __future__ import annotations

import sys
import unittest
from unittest import mock

from probablyfine.triage import triage


class TriageWrapperTests(unittest.TestCase):
    def test_wrapper_invokes_pipeline_main_directly(self) -> None:
        wrapper_argv = [
            "triage.py",
            "--dependabot",
            "dep.json",
            "--ecr",
            "ecr.json",
            "--context",
            "ctx.json",
            "--threat-intel",
            "intel.json",
            "--output",
            "report.md",
            "--offline",
        ]
        with mock.patch("sys.argv", wrapper_argv):
            with mock.patch.object(triage.triage_pipeline, "main", return_value=0) as pipeline_main:
                self.assertEqual(triage.main(), 0)
                self.assertEqual(sys.argv, wrapper_argv)

        pipeline_main.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
