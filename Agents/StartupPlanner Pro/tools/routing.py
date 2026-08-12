from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES_PATH = ROOT / "registry" / "routes.yaml"
ROUTE_INDEX_PATH = ROOT / "registry" / "route-index.yaml"
CATALOG_PATH = ROOT / "registry" / "generated-agents.yaml"
TAXONOMY_PATH = ROOT / "registry" / "taxonomy.yaml"

PHASE_ORDER = {
    "direction-discovery": 0,
    "general-research": 10,
    "market-research": 10,
    "user-validation": 10,
    "competitor-analysis": 10,
    "business-strategy": 20,
    "startup-validation": 25,
    "product-management": 30,
    "mvp-design": 35,
    "product-governance": 40,
    "architecture": 40,
    "quality-assurance": 65,
    "backend-development": 50,
    "frontend-development": 50,
    "mobile-development": 50,
    "code-review": 60,
    "deployment": 70,
    "business-plan-writing": 90,
}


def load_routes(path=ROUTES_PATH):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def select_runtime_domains(text, index):
    ranked = []
    for domain_id, cues in index["domains"]:
        matched = signal_matches(text, cues)
        if matched:
            ranked.append((max(len(normalize(cue)) for cue in matched), len(matched), domain_id))
    ranked.sort(reverse=True)
    return [{"id": domain_id, "file": f"route-domains/{domain_id}.yaml"} for _, _, domain_id in ranked[: index.get("max_shards", 2)]]


def load_runtime_routes(text, root=ROOT):
    root = Path(root)
    index = yaml.safe_load((root / "registry" / "route-index.yaml").read_text(encoding="utf-8"))
    routes = []
    for domain in select_runtime_domains(text, index):
        shard = yaml.safe_load((root / "registry" / domain["file"]).read_text(encoding="utf-8"))
        for compact in shard["routes"]:
            route = {
                "id": compact["id"],
                "domains": [domain["id"]],
                "task_types": compact.get("tasks", []),
                "positive_signals": compact.get("signals", []),
                "preferred_agents": compact.get("agents", []),
            }
            mapping = {
                "exclude": "negative_signals",
                "requires": "requires_any_context",
                "preconditions": "preconditions",
                "blocks_until": "blocks_until",
                "channels": "channels",
            }
            for source, target in mapping.items():
                if source in compact:
                    route[target] = compact[source]
            routes.append(route)
    return {"schema_version": "3.0", "routes": routes}


def normalize(text):
    return re.sub(r"\s+", "", text).casefold()


def signal_matches(text, signals):
    normalized = normalize(text)
    return [str(signal) for signal in signals if normalize(str(signal)) in normalized]


def _request_slots(text):
    taxonomy = load_routes(TAXONOMY_PATH)
    return {
        "channels": signal_matches(text, taxonomy.get("channels", [])),
        "lifecycle_stages": [
            stage for stage, aliases in taxonomy.get("lifecycle_aliases", {}).items() if signal_matches(text, aliases)
        ],
        "produces": signal_matches(text, taxonomy.get("artifact_types", [])),
    }


def _agent_catalog():
    catalog = load_routes(CATALOG_PATH)
    return {agent["id"]: agent for agent in catalog["agents"]}


def _candidate_score(text, route, agent, slots):
    route_channels = set(route.get("channels", [])) | set(agent.get("channels", []))
    agent_lifecycle = set(agent.get("lifecycle_stages", []))
    agent_produces = set(agent.get("produces", []))
    if slots["channels"] and route_channels and not set(slots["channels"]) & route_channels:
        return None, {"channels": "hard-filter"}
    if slots["lifecycle_stages"] and agent_lifecycle and not set(slots["lifecycle_stages"]) & agent_lifecycle:
        return None, {"lifecycle_stages": "hard-filter"}
    route_tasks, agent_tasks = set(route.get("task_types", [])), set(agent.get("task_types", []))
    route_domains, agent_domains = set(route.get("domains", [])), set(agent.get("domains", []))
    capability_hits = signal_matches(text, agent.get("capabilities", []))
    dimensions = {
        "task_types": 1.0 if route_tasks & agent_tasks else 0.0,
        "capabilities": 1.0 if capability_hits else 0.5,
        "domains": 1.0 if route_domains & agent_domains else 0.0,
        "produces": 1.0 if slots["produces"] and set(slots["produces"]) & agent_produces else 0.5,
        "channels": 1.0 if slots["channels"] and set(slots["channels"]) & route_channels else 0.5,
        "lifecycle_stages": 1.0 if slots["lifecycle_stages"] and set(slots["lifecycle_stages"]) & agent_lifecycle else 0.5,
    }
    weights = {"task_types": 0.30, "capabilities": 0.25, "domains": 0.15, "produces": 0.15, "channels": 0.10, "lifecycle_stages": 0.05}
    return round(sum(dimensions[key] * weight for key, weight in weights.items()), 2), dimensions


def extract_intent(text, routes_config=None):
    config = routes_config or load_routes()
    agents = _agent_catalog()
    slots = _request_slots(text)
    matches = []
    for route in config["routes"]:
        positive = signal_matches(text, route.get("positive_signals", []))
        negative = signal_matches(text, route.get("negative_signals", []))
        if not positive or negative:
            continue
        context_required = route.get("requires_any_context", [])
        context = signal_matches(text, context_required)
        if context_required and not context:
            continue
        agent_id = route.get("preferred_agents", [None])[0]
        agent = agents.get(agent_id)
        if not agent or agent.get("status") != "active" or agent.get("schema_version") != "3.0":
            continue
        if agent.get("visibility") not in {"specialist", "internal"} or agent.get("invocation") == "manual":
            continue
        if not (ROOT / "agents" / agent.get("file", "missing")).is_file():
            continue
        if agent.get("reviewer") == agent_id:
            continue
        if signal_matches(text, agent.get("do_not_use_when", [])):
            continue
        confidence, dimensions = _candidate_score(text, route, agent, slots)
        if confidence is None or confidence < config.get("defaults", {}).get("min_confidence", 0.70):
            continue
        matches.append(
            {
                "route": route,
                "positive_signals": positive,
                "confidence": confidence,
                "dimensions": dimensions,
            }
        )
    return {
        "text": text,
        "matches": matches,
        "slots": slots,
        "compound": len(matches) > 1,
    }


def _task_type(route):
    return route.get("task_types", [route["id"]])[0]


def _phase(route):
    return PHASE_ORDER.get(_task_type(route), 50)


def decompose_request(text, routes_config=None):
    intent = extract_intent(text, routes_config)
    by_agent = {}
    for match in intent["matches"]:
        route = match["route"]
        for agent_id in route.get("preferred_agents", [])[:1]:
            current = by_agent.get(agent_id)
            candidate = {
                "route": route,
                "selected": agent_id,
                "confidence": match["confidence"],
                "positive_signals": match["positive_signals"],
                "dimensions": match["dimensions"],
            }
            if current is None or candidate["confidence"] > current["confidence"]:
                by_agent[agent_id] = candidate
    tasks = sorted(by_agent.values(), key=lambda item: (_phase(item["route"]), item["route"]["id"]))
    return tasks


def rank_agents(intent, catalog=None):
    allowed = None
    if catalog:
        allowed = {agent["id"] for agent in catalog.get("agents", []) if agent.get("status") == "active"}
    ranked = []
    for match in intent.get("matches", []):
        route = match["route"]
        for agent_id in route.get("preferred_agents", []):
            if allowed is not None and agent_id not in allowed:
                continue
            ranked.append(
                {
                    "agent_id": agent_id,
                    "score": match["confidence"],
                    "route_id": route["id"],
                    "matched_signals": match["positive_signals"],
                }
            )
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def route_request(text, routes_path=None):
    config = load_routes(routes_path) if routes_path else load_runtime_routes(text)
    decomposed = decompose_request(text, config)
    if not decomposed:
        return {
            "schema_version": "3.0",
            "input": text,
            "compound": False,
            "direction_gate_required": False,
            "clarification_required": True,
            "clarification_question": "你希望最终得到什么具体交付物？",
            "tasks": [],
        }

    direction_gate = any(item["selected"] == "core-orchestrator" for item in decomposed)
    tasks = []
    prior_by_phase = []
    for index, item in enumerate(decomposed, start=1):
        route = item["route"]
        phase = _phase(route)
        depends_on = [task["task_id"] for task in prior_by_phase if task["phase"] < phase]
        task = {
            "task_id": f"route-{index}-{route['id']}",
            "objective": f"执行 {route['id']} 对应的原子任务",
            "selected": item["selected"],
            "confidence": item["confidence"],
            "matched": {
                "route_id": route["id"],
                "signals": item["positive_signals"],
                "domains": route.get("domains", []),
                "task_types": route.get("task_types", []),
                "channels": route.get("channels", []),
                "score_dimensions": item["dimensions"],
            },
            "depends_on": depends_on,
            "fallbacks": route.get("fallback_agents", []),
            "rejected": [],
            "clarification_required": False,
            "clarification_question": None,
        }
        tasks.append(task)
        prior_by_phase.append({"task_id": task["task_id"], "phase": phase})

    return {
        "schema_version": "3.0",
        "input": text,
        "compound": len(tasks) > 1,
        "direction_gate_required": direction_gate,
        "clarification_required": False,
        "clarification_question": None,
        "tasks": tasks,
    }
