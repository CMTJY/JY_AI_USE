from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "workflows"
EXPECTED = {
    "business-plan",
    "product-development",
    "software-delivery",
    "marketing-campaign",
    "channel-operation",
    "research-project",
}


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {
            path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
            for path in WORKFLOWS.glob("*.yaml")
        }

    def test_all_v3_workflows_exist(self):
        self.assertEqual(EXPECTED, set(self.documents))
        for name, document in self.documents.items():
            self.assertEqual("3.0", str(document["schema_version"]), name)

    def test_dags_are_acyclic_and_dependencies_exist(self):
        for name, document in self.documents.items():
            tasks = {task["id"]: task for task in document["workflow"]["tasks"]}
            visiting, visited = set(), set()

            def visit(task_id):
                if task_id in visiting:
                    self.fail(f"cycle in {name}: {task_id}")
                if task_id in visited:
                    return
                visiting.add(task_id)
                for dependency in tasks[task_id].get("depends_on", []):
                    self.assertIn(dependency, tasks, f"{name}:{task_id}")
                    visit(dependency)
                visiting.remove(task_id)
                visited.add(task_id)

            for task_id in tasks:
                visit(task_id)

    def test_artifact_producers_are_unique(self):
        for name, document in self.documents.items():
            produced = [task["produces"]["id"] for task in document["workflow"]["tasks"]]
            self.assertEqual(len(produced), len(set(produced)), name)

    def test_professional_tasks_use_capability_slots(self):
        allowed_fixed = {"core-orchestrator", "core-quality-reviewer", "core-aggregator", "tech-code-reviewer"}
        for name, document in self.documents.items():
            for task in document["workflow"]["tasks"]:
                fixed = task.get("agent")
                if fixed:
                    self.assertIn(fixed, allowed_fixed, f"{name}:{task['id']}")
                    continue
                assignment = task.get("assignment")
                self.assertIsNotNone(assignment, f"{name}:{task['id']}")
                self.assertTrue(assignment["required"].get("task_types"), f"{name}:{task['id']}")
                self.assertEqual("most-specific", assignment["selection"])

    def test_reviewers_are_not_fixed_executors(self):
        for name, document in self.documents.items():
            for task in document["workflow"]["tasks"]:
                if task.get("agent"):
                    self.assertNotEqual(task["agent"], task.get("reviewer"), f"{name}:{task['id']}")

    def test_channel_workflow_has_all_specialist_branches(self):
        tasks = self.documents["channel-operation"]["workflow"]["tasks"]
        channels = {channel for task in tasks for channel in task.get("assignment", {}).get("conditional", {}).get("channels", [])}
        expected = {"xiaohongshu", "douyin", "private-domain", "amazon", "shopify", "taobao", "livestream", "linkedin"}
        self.assertTrue(expected.issubset(channels))


if __name__ == "__main__":
    unittest.main()
