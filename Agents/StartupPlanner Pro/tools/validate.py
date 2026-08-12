from pathlib import Path
import argparse
import json

from common import load_yaml, parse_frontmatter, role_files


ROOT = Path(__file__).resolve().parents[1]


def validate_routes(routes, catalog):
    errors = []
    agents = {agent["id"]: agent for agent in catalog["agents"]}
    routed = set()
    for route in routes["routes"]:
        for agent_id in route.get("preferred_agents", []):
            if agent_id not in agents:
                errors.append(f"route {route['id']} references missing-agent {agent_id}")
            else:
                routed.add(agent_id)
                if agents[agent_id]["status"] != "active":
                    errors.append(f"route {route['id']} references inactive agent {agent_id}")
    for agent_id, agent in agents.items():
        if agent["status"] == "active" and agent["visibility"] == "specialist" and agent_id not in routed:
            errors.append(f"unreachable active specialist: {agent_id}")
    return errors


def validate_workflows(workflows):
    errors = []
    for name, document in workflows.items():
        tasks = {task["id"]: task for task in document["workflow"]["tasks"]}
        produced = [task["produces"]["id"] for task in tasks.values()]
        duplicates = sorted({artifact for artifact in produced if produced.count(artifact) > 1})
        if duplicates:
            errors.append(f"workflow {name} has duplicate producers: {duplicates}")
        visiting, visited = set(), set()

        def visit(task_id):
            if task_id in visiting:
                errors.append(f"workflow {name} has cycle at {task_id}")
                return
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in tasks[task_id].get("depends_on", []):
                if dependency not in tasks:
                    errors.append(f"workflow {name} task {task_id} missing dependency {dependency}")
                else:
                    visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in tasks:
            visit(task_id)
    return errors


def validate_contracts(root, catalog):
    errors = []
    required = {"schema_version", "id", "agent_id", "status", "visibility", "portable", "domains", "task_types", "when_to_use", "do_not_use_when", "handoff_targets"}
    contracts = {}
    for path in role_files(root):
        try:
            data, _ = parse_frontmatter(path)
        except Exception as exc:
            errors.append(str(exc))
            continue
        missing = required - set(data)
        if missing:
            errors.append(f"contract {path} missing {sorted(missing)}")
        if data.get("id") != data.get("agent_id"):
            errors.append(f"contract id mismatch: {path}")
        if data.get("id") in contracts:
            errors.append(f"duplicate contract id: {data.get('id')}")
        contracts[data.get("id")] = data
    ids = set(contracts)
    for agent_id, data in contracts.items():
        for target in data.get("handoff_targets", []):
            if target not in ids:
                errors.append(f"invalid handoff {agent_id} -> {target}")
    generated = {agent["id"] for agent in catalog["agents"]}
    if generated != ids:
        errors.append("generated catalog differs from role contracts")
    return errors


def validate_project(root=ROOT):
    root = Path(root)
    errors, warnings = [], []
    try:
        routes = load_yaml(root / "registry" / "routes.yaml")
        catalog = load_yaml(root / "registry" / "generated-agents.yaml")
        errors.extend(validate_routes(routes, catalog))
        errors.extend(validate_contracts(root, catalog))
        workflows = {path.stem: load_yaml(path) for path in (root / "workflows").glob("*.yaml")}
        errors.extend(validate_workflows(workflows))
        index = load_yaml(root / "registry" / "workflows.yaml")
        indexed = {item["id"] for item in index["workflows"]}
        if indexed != set(workflows):
            errors.append("workflow index differs from workflow files")
    except Exception as exc:
        errors.append(f"configuration load failed: {exc}")
    return {"status": "passed" if not errors else "failed", "errors": errors, "warnings": warnings, "checks": {"error_count": len(errors), "warning_count": len(warnings)}}


def main():
    parser = argparse.ArgumentParser(description="Validate StartupPlanner Pro v3")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_project()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status={report['status']} errors={len(report['errors'])} warnings={len(report['warnings'])}")
        for error in report["errors"]:
            print(f"ERROR {error}")
        for warning in report["warnings"]:
            print(f"WARNING {warning}")
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()

