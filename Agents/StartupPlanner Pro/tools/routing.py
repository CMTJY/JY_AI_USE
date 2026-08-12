from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES_PATH = ROOT / "registry" / "routes.yaml"

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


def normalize(text):
    return re.sub(r"\s+", "", text).casefold()


def signal_matches(text, signals):
    normalized = normalize(text)
    return [str(signal) for signal in signals if normalize(str(signal)) in normalized]


def extract_intent(text, routes_config=None):
    config = routes_config or load_routes()
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
        specificity = max((len(normalize(item)) for item in positive), default=0)
        confidence = min(0.99, 0.72 + 0.05 * (len(positive) - 1) + 0.01 * min(specificity, 12))
        matches.append(
            {
                "route": route,
                "positive_signals": positive,
                "confidence": round(confidence, 2),
            }
        )
    return {
        "text": text,
        "matches": matches,
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
            }
            if current is None or candidate["confidence"] > current["confidence"]:
                by_agent[agent_id] = candidate
    tasks = sorted(by_agent.values(), key=lambda item: (_phase(item["route"]), item["route"]["id"]))
    return tasks


def rank_agents(intent, catalog=None):
    ranked = []
    for match in intent.get("matches", []):
        route = match["route"]
        for agent_id in route.get("preferred_agents", []):
            ranked.append(
                {
                    "agent_id": agent_id,
                    "score": match["confidence"],
                    "route_id": route["id"],
                    "matched_signals": match["positive_signals"],
                }
            )
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def route_request(text, routes_path=ROUTES_PATH):
    config = load_routes(routes_path)
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
