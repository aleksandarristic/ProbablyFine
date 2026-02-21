from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from probablyfine.triage import context_creator


class ContextCreatorCodexTests(unittest.TestCase):
    def test_codex_guided_mode_applies_answers_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "context.json"
            answers = tmp_path / "answers.json"
            answers.write_text(
                json.dumps(
                    {
                        "component.name": "payments-api",
                        "component.exposure": "public",
                        "data.confidentiality_requirement": "medium",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch(
                "sys.argv",
                [
                    "context_creator.py",
                    "--codex-guided",
                    "--answers-json",
                    str(answers),
                    "--output",
                    str(output),
                ],
            ):
                self.assertEqual(context_creator.main(), 0)

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["component"]["name"], "payments-api")
            self.assertEqual(payload["component"]["exposure"], "public")
            self.assertEqual(payload["data"]["confidentiality_requirement"], "medium")


if __name__ == "__main__":
    unittest.main()

