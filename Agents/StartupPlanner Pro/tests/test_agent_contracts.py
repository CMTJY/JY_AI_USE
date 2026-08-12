from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = ROOT / "agents"
REQUIRED_FIELDS = {
    "schema_version",
    "id",
    "name",
    "version",
    "status",
    "visibility",
    "portable",
    "domains",
    "task_types",
    "lifecycle_stages",
    "capabilities",
    "produces",
    "when_to_use",
    "do_not_use_when",
    "required_inputs",
    "optional_inputs",
    "handoff_targets",
}


def role_files():
    for path in AGENTS_ROOT.rglob("*.md"):
        if "skills" in path.parts or "templates" in path.parts:
            continue
        yield path


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        raise AssertionError(f"missing frontmatter: {path}")
    return yaml.safe_load(match.group(1))


class AgentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = {data["id"]: (path, data) for path in role_files() if (data := frontmatter(path))}

    def test_every_role_uses_v3_contract(self):
        for agent_id, (path, data) in self.contracts.items():
            self.assertEqual("3.0", str(data.get("schema_version")), path)
            self.assertEqual(agent_id, data.get("agent_id"), path)
            self.assertEqual(set(), REQUIRED_FIELDS - set(data), path)

    def test_active_specialists_are_portable_with_examples(self):
        for agent_id, (path, data) in self.contracts.items():
            if data["status"] != "active" or data["visibility"] != "specialist":
                continue
            self.assertTrue(data["portable"], path)
            self.assertGreaterEqual(len(data["when_to_use"]), 3, path)
            self.assertGreaterEqual(len(data["do_not_use_when"]), 2, path)
            self.assertTrue(data["domains"], path)
            self.assertTrue(data["task_types"], path)

    def test_core_controls_are_system_only_and_not_portable(self):
        for agent_id, (path, data) in self.contracts.items():
            if not agent_id.startswith("core-"):
                continue
            self.assertEqual("internal", data["visibility"], path)
            self.assertEqual("system-only", data["invocation"], path)
            self.assertFalse(data["portable"], path)

    def test_deprecated_director_is_not_routable(self):
        data = self.contracts["director-startup"][1]
        self.assertEqual("deprecated", data["status"])
        self.assertEqual("internal", data["visibility"])

    def test_handoff_targets_and_reviewers_exist(self):
        ids = set(self.contracts)
        for agent_id, (path, data) in self.contracts.items():
            self.assertTrue(set(data["handoff_targets"]).issubset(ids), path)
            reviewer = data.get("reviewer")
            if reviewer:
                self.assertIn(reviewer, ids, path)
                self.assertNotEqual(agent_id, reviewer, path)

    def test_generated_catalog_matches_role_contracts(self):
        catalog = yaml.safe_load(
            (ROOT / "registry" / "generated-agents.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("3.0", str(catalog["schema_version"]))
        generated_ids = {agent["id"] for agent in catalog["agents"]}
        self.assertEqual(set(self.contracts), generated_ids)


if __name__ == "__main__":
    unittest.main()
