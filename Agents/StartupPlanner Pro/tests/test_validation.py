from pathlib import Path
import copy
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from token_budget import build_report, estimate_tokens  # noqa: E402
from validate import validate_project, validate_routes, validate_runtime_routes, validate_workflows  # noqa: E402


class ValidationTests(unittest.TestCase):
    def test_unknown_route_target_is_an_error(self):
        catalog = yaml.safe_load((ROOT / "registry" / "generated-agents.yaml").read_text(encoding="utf-8"))
        routes = yaml.safe_load((ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8"))
        broken = copy.deepcopy(routes)
        broken["routes"][0]["preferred_agents"] = ["missing-agent"]
        errors = validate_routes(broken, catalog)
        self.assertTrue(any("missing-agent" in error for error in errors))

    def test_unreachable_active_specialist_is_an_error(self):
        catalog = yaml.safe_load((ROOT / "registry" / "generated-agents.yaml").read_text(encoding="utf-8"))
        routes = yaml.safe_load((ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8"))
        broken = copy.deepcopy(routes)
        broken["routes"] = [route for route in broken["routes"] if "marketing-douyin-strategist" not in route.get("preferred_agents", [])]
        errors = validate_routes(broken, catalog)
        self.assertTrue(any("marketing-douyin-strategist" in error and "unreachable" in error for error in errors))

    def test_workflow_cycle_is_an_error(self):
        workflow = {
            "workflow": {
                "id": "broken",
                "tasks": [
                    {"id": "a", "depends_on": ["b"], "produces": {"id": "artifact-a"}},
                    {"id": "b", "depends_on": ["a"], "produces": {"id": "artifact-b"}},
                ],
            }
        }
        errors = validate_workflows({"broken": workflow})
        self.assertTrue(any("cycle" in error for error in errors))

    def test_current_project_has_no_validation_errors(self):
        report = validate_project(ROOT)
        self.assertEqual([], report["errors"])
        self.assertEqual("passed", report["status"])

    def test_token_estimate_is_conservative_range(self):
        low, high = estimate_tokens("中英文 mixed text" * 100)
        self.assertGreater(low, 0)
        self.assertGreaterEqual(high, low)

    def test_token_report_contains_progressive_layers(self):
        report = build_report(ROOT)
        names = {layer["name"] for layer in report["layers"]}
        self.assertTrue({"platform-entry", "routing-bootstrap", "specialist-roles", "skills"}.issubset(names))
        self.assertEqual(0, report["hard_errors"])
        self.assertEqual(0, report["warnings"])

    def test_runtime_route_shards_cover_source_routes_once(self):
        source = yaml.safe_load((ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8"))
        index = yaml.safe_load((ROOT / "registry" / "route-index.yaml").read_text(encoding="utf-8"))
        source_ids = [route["id"] for route in source["routes"]]
        runtime_ids = []
        for domain_id, _ in index["domains"]:
            file = f"route-domains/{domain_id}.yaml"
            shard = yaml.safe_load((ROOT / "registry" / file).read_text(encoding="utf-8"))
            runtime_ids.extend(route["id"] for route in shard["routes"])
        self.assertCountEqual(source_ids, runtime_ids)
        self.assertEqual(len(runtime_ids), len(set(runtime_ids)))

    def test_runtime_route_validator_rejects_duplicate_route(self):
        source = yaml.safe_load((ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8"))
        index = yaml.safe_load((ROOT / "registry" / "route-index.yaml").read_text(encoding="utf-8"))
        shards = {
            domain_id: yaml.safe_load((ROOT / "registry" / f"route-domains/{domain_id}.yaml").read_text(encoding="utf-8"))
            for domain_id, _ in index["domains"]
        }
        broken = copy.deepcopy(shards)
        broken["core"]["routes"].append(copy.deepcopy(broken["tech"]["routes"][0]))
        errors = validate_runtime_routes(source, index, broken)
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_runtime_route_validator_rejects_stale_content(self):
        source = yaml.safe_load((ROOT / "registry" / "routes.yaml").read_text(encoding="utf-8"))
        index = yaml.safe_load((ROOT / "registry" / "route-index.yaml").read_text(encoding="utf-8"))
        shards = {
            domain_id: yaml.safe_load((ROOT / "registry" / f"route-domains/{domain_id}.yaml").read_text(encoding="utf-8"))
            for domain_id, _ in index["domains"]
        }
        broken = copy.deepcopy(shards)
        broken["tech"]["routes"][0]["signals"] = ["stale-signal"]
        errors = validate_runtime_routes(source, index, broken)
        self.assertTrue(any("stale" in error for error in errors))

    def test_bootstrap_uses_progressive_route_loading(self):
        bootstrap = (ROOT / "core" / "BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("registry/route-index.yaml", bootstrap)
        self.assertNotIn("registry/routes.yaml", bootstrap)
        self.assertNotIn("registry/generated-agents.yaml", bootstrap)


if __name__ == "__main__":
    unittest.main()
