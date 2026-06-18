from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine import scanner
from probablyfine.collectors import CollectorError, collect_dependabot_findings
from probablyfine.config_loader import load_probablyfine_config


class FailureModeTests(unittest.TestCase):
    def test_missing_config_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "repo-missing-config"
            pf_dir = repo / ".probablyfine"
            (pf_dir / "cache").mkdir(parents=True, exist_ok=True)
            (pf_dir / "reports").mkdir(parents=True, exist_ok=True)

            project_root = Path(__file__).resolve().parents[1]
            context_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "context.json"
            (pf_dir / "context.json").write_text(context_template.read_text(encoding="utf-8"), encoding="utf-8")

            with mock.patch.object(sys, "argv", ["scanner.py", str(repo), "--offline"]):
                rc = scanner.main()
            self.assertEqual(rc, 1)

    def test_dependabot_auth_failure_without_token_or_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "repo-auth-fail"
            pf_dir = repo / ".probablyfine"
            (pf_dir / "cache").mkdir(parents=True, exist_ok=True)
            (pf_dir / "reports").mkdir(parents=True, exist_ok=True)

            project_root = Path(__file__).resolve().parents[1]
            context_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "context.json"
            config_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "config.json"
            (pf_dir / "context.json").write_text(context_template.read_text(encoding="utf-8"), encoding="utf-8")
            (pf_dir / "config.json").write_text(config_template.read_text(encoding="utf-8"), encoding="utf-8")

            with mock.patch.dict(
                os.environ,
                {
                    "GITHUB_TOKEN": "",
                    "PROBABLYFINE_DEPENDABOT_FILE": "",
                    "PROBABLYFINE_ECR_FILE": str(tmp_path / "ecr_findings.json"),
                    "PYTHONPATH": str(project_root / "src"),
                },
                clear=False,
            ):
                (tmp_path / "ecr_findings.json").write_text('{"findings":[]}', encoding="utf-8")
                with mock.patch.object(sys, "argv", ["scanner.py", str(repo), "--offline"]):
                    rc = scanner.main()
            self.assertEqual(rc, 1)

    def test_dependabot_timeout_retries_are_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "repo-timeout"
            repo.mkdir(parents=True, exist_ok=True)
            cache_dir = tmp_path / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)

            project_root = Path(__file__).resolve().parents[1]
            config_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "config.json"
            config_path = tmp_path / "config.json"
            config_path.write_text(config_template.read_text(encoding="utf-8"), encoding="utf-8")
            config = load_probablyfine_config(config_path, project_root)

            with mock.patch.dict(
                os.environ,
                {
                    "GITHUB_TOKEN": "dummy-token",
                    "PROBABLYFINE_HTTP_MAX_ATTEMPTS": "1",
                    "PROBABLYFINE_HTTP_RETRY_SLEEP_SECONDS": "0",
                },
                clear=False,
            ):
                with mock.patch("probablyfine.collectors._http_get_json", side_effect=TimeoutError("simulated timeout")):
                    with self.assertRaises(CollectorError):
                        collect_dependabot_findings(
                            config=config,
                            repo_path=repo,
                            cache_dir=cache_dir,
                            timestamp_token="2026-02-21T000000Z",
                        )


if __name__ == "__main__":
    unittest.main()
