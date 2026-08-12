from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_required_guides_exist(self):
        expected = [
            "architecture.md",
            "routing-guide.md",
            "platform-setup.md",
            "portable-agent-guide.md",
            "evaluation-report.md",
        ]
        for name in expected:
            self.assertTrue((ROOT / "docs" / name).is_file(), name)

    def test_readme_explains_v3_and_both_modes(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        required = ["StartupPlanner Pro v3", "团队模式", "独立模式", "Codex", "Cursor", "TRAE", "渐进加载", "route_eval.py", "token_budget.py"]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_root_agents_file_is_a_short_bootstrap(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 2200)
        self.assertIn("core/BOOTSTRAP.md", text)
        self.assertIn("单 Agent 串行角色模拟", text)

    def test_platform_guide_covers_three_tools(self):
        text = (ROOT / "docs" / "platform-setup.md").read_text(encoding="utf-8")
        for phrase in ["Codex", "Cursor", "TRAE", "AGENTS.md", ".cursor/rules", ".agents/skills"]:
            self.assertIn(phrase, text)

    def test_evaluation_report_is_reproducible_and_honest(self):
        text = (ROOT / "docs" / "evaluation-report.md").read_text(encoding="utf-8")
        for phrase in ["117", "100.00%", "0.00%", "52", "离线规则", "不等于三平台实机", "python"]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
