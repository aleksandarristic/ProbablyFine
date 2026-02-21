from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from probablyfine.config_loader import load_probablyfine_config
from probablyfine.contracts import ValidationError


class ConfigVersioningTests(unittest.TestCase):
    def test_unsupported_schema_version_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = Path(__file__).resolve().parents[1]
            config_template = project_root / "templates" / "probablyfine-starter" / ".probablyfine" / "config.json"
            payload = json.loads(config_template.read_text(encoding="utf-8"))
            payload["schema_version"] = "0.0.1"
            config_path = tmp_path / "config.json"
            config_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ValidationError):
                load_probablyfine_config(config_path, project_root)


if __name__ == "__main__":
    unittest.main()
