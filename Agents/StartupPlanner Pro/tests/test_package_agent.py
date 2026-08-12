from pathlib import Path
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from package_agent import PackageError, package_agent  # noqa: E402


class PackageAgentTests(unittest.TestCase):
    def test_specialist_can_be_exported_as_standalone_package(self):
        with tempfile.TemporaryDirectory() as directory:
            package = package_agent("marketing-xiaohongshu-operator", Path(directory))
            self.assertTrue((package / "AGENT.md").is_file())
            self.assertTrue((package / "README.md").is_file())
            self.assertTrue((package / "manifest.yaml").is_file())
            manifest = yaml.safe_load((package / "manifest.yaml").read_text(encoding="utf-8"))
            self.assertEqual("marketing-xiaohongshu-operator", manifest["agent_id"])
            self.assertEqual("3.0.0", manifest["agent_version"])
            self.assertGreater(manifest["token_estimate"]["high"], 0)
            text = (package / "AGENT.md").read_text(encoding="utf-8")
            self.assertIn("独立模式", text)
            self.assertNotIn("agents/core/orchestrator", text)

    def test_core_role_cannot_be_exported(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PackageError):
                package_agent("core-orchestrator", Path(directory))

    def test_package_contains_no_unrelated_agent_files(self):
        with tempfile.TemporaryDirectory() as directory:
            package = package_agent("marketing-xiaohongshu-operator", Path(directory))
            markdown = list(package.rglob("*.md"))
            names = {path.name for path in markdown}
            self.assertTrue(names.issubset({"AGENT.md", "README.md", "SKILL.md", "SKILL_INDEX.md"}))


if __name__ == "__main__":
    unittest.main()
