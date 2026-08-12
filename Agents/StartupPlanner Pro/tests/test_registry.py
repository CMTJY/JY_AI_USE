from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taxonomy = yaml.safe_load(
            (ROOT / "registry" / "taxonomy.yaml").read_text(encoding="utf-8")
        )
        cls.routes = yaml.safe_load(
            (ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8")
        )
        cls.workflows = yaml.safe_load(
            (ROOT / "registry" / "workflows.yaml").read_text(encoding="utf-8")
        )
        capabilities = yaml.safe_load(
            (ROOT / "agents" / "config" / "capabilities.yaml").read_text(encoding="utf-8")
        )
        cls.agent_ids = {agent["id"] for agent in capabilities["agents"]}

    def test_v3_registry_files_have_schema_version(self):
        self.assertEqual("3.0", str(self.taxonomy["schema_version"]))
        self.assertEqual("3.0", str(self.routes["schema_version"]))
        self.assertEqual("3.0", str(self.workflows["schema_version"]))

    def test_taxonomy_has_routing_dimensions(self):
        expected = {
            "domains",
            "task_types",
            "channels",
            "lifecycle_stages",
            "artifact_types",
        }
        self.assertTrue(expected.issubset(self.taxonomy))

    def test_route_targets_exist(self):
        for route in self.routes["routes"]:
            for agent_id in route.get("preferred_agents", []):
                self.assertIn(agent_id, self.agent_ids, route["id"])

    def test_previously_unreachable_specialists_have_routes(self):
        required = {
            "marketing-social-strategist",
            "marketing-douyin-strategist",
            "marketing-video-editing-coach",
            "marketing-xiaohongshu-operator",
            "marketing-xiaohongshu-specialist",
            "marketing-private-domain",
            "marketing-ecommerce",
            "marketing-cross-border-ecommerce",
            "marketing-livestream-coach",
            "product-director",
        }
        routed = {
            agent_id
            for route in self.routes["routes"]
            for agent_id in route.get("preferred_agents", [])
        }
        self.assertEqual(set(), required - routed)

    def test_zero_to_one_is_not_a_standalone_startup_trigger(self):
        discovery = next(
            route for route in self.routes["routes"] if route["id"] == "startup-direction-discovery"
        )
        self.assertNotIn("从0到1", discovery.get("positive_signals", []))
        self.assertIn("从0到1", self.taxonomy["lifecycle_aliases"]["launch"])

    def test_route_scoring_weights_sum_to_one(self):
        self.assertAlmostEqual(1.0, sum(self.routes["scoring"]["weights"].values()))
        self.assertLessEqual(self.routes["defaults"]["max_candidates"], 5)


if __name__ == "__main__":
    unittest.main()
