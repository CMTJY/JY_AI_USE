from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_required_platform_adapters_exist(self):
        expected = [
            ROOT / "adapters" / "codex" / "AGENTS.snippet.md",
            ROOT / "adapters" / "cursor" / "startupplanner.mdc",
            ROOT / "adapters" / "cursor" / "startupplanner-command.md",
            ROOT / "adapters" / "trae" / "AGENTS.snippet.md",
            ROOT / "adapters" / "trae" / "startupplanner-bootstrap" / "SKILL.md",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), path)

    def test_adapters_reference_canonical_bootstrap_and_disclose_fallback(self):
        for path in (ROOT / "adapters").rglob("*"):
            if not path.is_file() or "portable" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIn("core/BOOTSTRAP.md", text, path)
            self.assertIn("单 Agent 串行角色模拟", text, path)

    def test_adapters_are_thin_and_do_not_copy_business_rules(self):
        forbidden = ["startup-direction-discovery", "marketing-xiaohongshu-operator", "Task Packet v3", "评分：任务类型"]
        for path in (ROOT / "adapters").rglob("*"):
            if not path.is_file() or "portable" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertLess(len(text), 2400, path)
            for phrase in forbidden:
                self.assertNotIn(phrase, text, path)


if __name__ == "__main__":
    unittest.main()
