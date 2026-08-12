from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = ROOT / "agents"


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def role_files():
    for path in AGENTS_ROOT.rglob("*.md"):
        if "skills" not in path.parts and "templates" not in path.parts:
            yield path


def split_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not match:
        raise ValueError(f"Missing frontmatter: {path}")
    return yaml.safe_load(match.group(1)), text[match.end():]


def route_metadata(routes):
    result = {}
    for route in routes["routes"]:
        for agent_id in route.get("preferred_agents", []):
            item = result.setdefault(agent_id, {"domains": set(), "task_types": set(), "signals": [], "negative": [], "channels": set()})
            item["domains"].update(route.get("domains", []))
            item["task_types"].update(route.get("task_types", []))
            item["channels"].update(route.get("channels", []))
            item["signals"].extend(route.get("positive_signals", []))
            item["negative"].extend(route.get("negative_signals", []))
    return result


def three_examples(agent, signals):
    examples = [str(x) for x in signals[:3]]
    while len(examples) < 3:
        examples.append(f"需要{agent['name']}产出{(agent.get('produces') or ['专业交付物'])[0]}")
    return examples


def two_exclusions(agent, negatives):
    examples = [str(x) for x in negatives[:2]]
    defaults = ["任务属于其他明确专业领域", "只需要主控协调而不需要本角色专业产物"]
    for item in defaults:
        if len(examples) >= 2:
            break
        examples.append(item)
    return examples


def build_contract(old, registry_agent, routing, override):
    agent_id = old["agent_id"]
    status = registry_agent.get("status", "active")
    is_core = agent_id.startswith("core-")
    is_deprecated = status == "deprecated"
    visibility = "internal" if is_core or is_deprecated else "specialist"
    domains = sorted(routing.get("domains") or {registry_agent.get("department", "core")})
    task_types = sorted(routing.get("task_types") or set(old.get("capabilities", [])[:1]) or {"orchestration"})
    contract = {
        "schema_version": "3.0",
        "id": agent_id,
        "agent_id": agent_id,
        "name": old.get("name", registry_agent.get("name", agent_id)),
        "description": old.get("description", ""),
        "version": "3.0.0",
        "status": status,
        "visibility": visibility,
        "invocation": "system-only" if visibility == "internal" else "router-or-manual",
        "portable": visibility == "specialist" and status == "active",
        "domains": domains,
        "task_types": task_types,
        "channels": sorted(routing.get("channels", [])),
        "lifecycle_stages": ["discovery", "validation", "launch", "growth", "optimization", "scale", "release"],
        "capabilities": old.get("capabilities", registry_agent.get("capabilities", [])),
        "produces": registry_agent.get("produces", []),
        "when_to_use": three_examples(registry_agent, routing.get("signals", [])),
        "do_not_use_when": two_exclusions(registry_agent, routing.get("negative", [])),
        "required_inputs": ["objective"],
        "optional_inputs": ["constraints", "context", "available_evidence"],
        "handoff_targets": [],
        "reviewer": None if agent_id == "core-quality-reviewer" or is_deprecated else "core-quality-reviewer",
    }
    for key in ("emoji", "color"):
        if key in old:
            contract[key] = old[key]
    contract.update(override or {})
    return contract


def main():
    capabilities = load_yaml(ROOT / "agents" / "config" / "capabilities.yaml")
    registry = {agent["id"]: agent for agent in capabilities["agents"]}
    routing = route_metadata(load_yaml(ROOT / "registry" / "routes.yaml"))
    overrides = load_yaml(ROOT / "registry" / "agent-overrides.yaml").get("agents", {})
    for path in role_files():
        old, body = split_frontmatter(path)
        agent_id = old["agent_id"]
        contract = build_contract(old, registry[agent_id], routing.get(agent_id, {}), overrides.get(agent_id))
        rendered = yaml.safe_dump(contract, allow_unicode=True, sort_keys=False, width=120).rstrip()
        path.write_text(f"---\n{rendered}\n---\n\n{body.lstrip()}", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

