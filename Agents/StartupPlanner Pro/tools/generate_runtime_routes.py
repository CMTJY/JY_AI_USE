from pathlib import Path
from collections import defaultdict
import json

from common import load_yaml


ROOT = Path(__file__).resolve().parents[1]

DOMAIN_ORDER = ["core", "tech", "research", "strategy", "product", "marketing", "finance", "organization", "risk", "business-plan"]

FIELD_MAP = {
    "task_types": "tasks",
    "positive_signals": "signals",
    "preferred_agents": "agents",
    "negative_signals": "exclude",
    "requires_any_context": "requires",
    "preconditions": "preconditions",
    "blocks_until": "blocks_until",
    "channels": "channels",
}


def compact_route(route):
    compact = {"id": route["id"]}
    for source, target in FIELD_MAP.items():
        if source in route:
            compact[target] = route[source]
    return compact


def generate(root=ROOT):
    root = Path(root)
    source = load_yaml(root / "registry" / "routes.yaml")
    grouped = defaultdict(list)
    for route in source["routes"]:
        domains = route.get("domains") or ["core"]
        if len(domains) != 1:
            raise ValueError(f"runtime sharding requires one domain per route: {route['id']}")
        grouped[domains[0]].append(compact_route(route))

    shard_dir = root / "registry" / "route-domains"
    shard_dir.mkdir(parents=True, exist_ok=True)
    domain_items = []
    for domain in DOMAIN_ORDER:
        relative = f"route-domains/{domain}.yaml"
        shard = {"schema_version": "3.0", "domain": domain, "routes": grouped.get(domain, [])}
        (root / "registry" / relative).write_text(
            json.dumps(shard, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
        )
        cues = []
        for route in source["routes"]:
            if domain not in route.get("domains", []):
                continue
            cues.extend(route.get("positive_signals", []))
        domain_items.append([domain, list(dict.fromkeys(str(cue) for cue in cues))])

    index = {"schema_version": "3.0", "max_shards": 2, "domains": domain_items}
    (root / "registry" / "route-index.yaml").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    generate()
