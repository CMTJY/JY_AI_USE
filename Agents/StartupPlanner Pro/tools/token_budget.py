from pathlib import Path
import argparse
import json
import math


ROOT = Path(__file__).resolve().parents[1]


def estimate_tokens(text):
    return math.ceil(len(text) / 3.0), math.ceil(len(text) / 1.5)


def layer(name, paths, budget=None, hard=False, aggregation="sum"):
    files = [Path(path) for path in paths if Path(path).is_file()]
    texts = [path.read_text(encoding="utf-8") for path in files]
    if aggregation == "max":
        text = max(texts, key=len, default="")
    else:
        text = "".join(texts)
    low, high = estimate_tokens(text)
    status = "passed"
    if budget is not None and high > budget:
        status = "error" if hard else "warning"
    return {"name": name, "files": len(files), "aggregation": aggregation, "chars": len(text), "estimated_tokens_low": low, "estimated_tokens_high": high, "budget": budget, "status": status}


def build_report(root=ROOT):
    root = Path(root)
    role_paths = [path for path in (root / "agents").rglob("*.md") if "skills" not in path.parts and "templates" not in path.parts and "core" not in path.parts]
    skill_paths = list((root / "agents").rglob("SKILL.md"))
    entry_paths = [root / "AGENTS.md"] + list((root / "adapters").rglob("*.md")) + list((root / "adapters").rglob("*.mdc"))
    routing_base = [root / "core" / "BOOTSTRAP.md", root / "registry" / "route-index.yaml"]
    route_shards = sorted((root / "registry" / "route-domains").glob("*.yaml"), key=lambda path: path.stat().st_size, reverse=True)
    routing_paths = routing_base + route_shards[:2]
    layers = [
        layer("platform-entry", entry_paths, budget=1500, hard=False, aggregation="max"),
        layer("routing-bootstrap", routing_paths, budget=4000, hard=False),
        layer("specialist-max", role_paths, budget=8000, hard=False, aggregation="max"),
        layer("specialist-roles", role_paths),
        layer("skills", skill_paths),
    ]
    return {"schema_version": "3.0", "layers": layers, "hard_errors": sum(item["status"] == "error" for item in layers), "warnings": sum(item["status"] == "warning" for item in layers)}


def main():
    parser = argparse.ArgumentParser(description="Report StartupPlanner Pro token budgets")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report["layers"]:
            print(f"{item['name']}: files={item['files']} chars={item['chars']} tokens={item['estimated_tokens_low']}-{item['estimated_tokens_high']} budget={item['budget']} status={item['status']}")
        print(f"hard_errors={report['hard_errors']} warnings={report['warnings']}")
    raise SystemExit(1 if report["hard_errors"] else 0)


if __name__ == "__main__":
    main()
