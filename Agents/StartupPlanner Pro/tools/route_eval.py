from pathlib import Path
import argparse
import json

import yaml

from routing import route_request


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "routing-cases.yaml"
CATALOG_PATH = ROOT / "registry" / "generated-agents.yaml"


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def build_cases(cases_path=CASES_PATH, catalog_path=CATALOG_PATH):
    config = load_yaml(cases_path)
    cases = []
    for case in config.get("cases", []):
        item = dict(case)
        item["source"] = "curated"
        cases.append(item)
    if config.get("expand_active_specialist_examples"):
        catalog = load_yaml(catalog_path)
        for agent in catalog["agents"]:
            if agent["status"] != "active" or agent["visibility"] != "specialist":
                continue
            for index, example in enumerate(agent["when_to_use"][:3], start=1):
                expected_agents = [agent["id"]]
                if agent["id"] == "director-bp":
                    expected_agents.insert(0, "core-orchestrator")
                cases.append(
                    {
                        "id": f"contract-{agent['id']}-{index}",
                        "input": str(example),
                        "expected_agents": expected_agents,
                        "forbidden_agents": [],
                        "direction_gate_required": agent["id"] == "director-bp",
                        "source": "agent-contract",
                    }
                )
    return cases


def evaluate(cases_path=CASES_PATH, catalog_path=CATALOG_PATH):
    cases = build_cases(cases_path, catalog_path)
    results = []
    atomic_total = 0
    atomic_pass = 0
    expected_total = 0
    expected_missing = 0
    direction_negative_total = 0
    direction_false_positives = 0
    bp_gate_misses = 0
    selected_total = 0
    unnecessary_calls = 0
    for case in cases:
        actual = route_request(case["input"])
        selected = [task["selected"] for task in actual["tasks"]]
        expected = case.get("expected_agents", [])
        forbidden = case.get("forbidden_agents", [])
        missing = [agent for agent in expected if agent not in selected]
        forbidden_selected = [agent for agent in forbidden if agent in selected]
        unexpected = [agent for agent in selected if agent not in expected]
        clarification_ok = actual["clarification_required"] == case.get("clarification_required", False)
        direction_expected = case.get("direction_gate_required", False)
        direction_ok = actual["direction_gate_required"] == direction_expected
        exact_match = not unexpected if len(expected) <= 1 else True
        passed = not missing and not forbidden_selected and exact_match and clarification_ok and direction_ok
        expected_total += len(expected)
        expected_missing += len(missing)
        selected_total += len(selected)
        unnecessary_calls += len(unexpected)
        if len(expected) <= 1:
            atomic_total += 1
            atomic_pass += int(passed)
        if not direction_expected:
            direction_negative_total += 1
            direction_false_positives += int(actual["direction_gate_required"])
        if "director-bp" in expected and not actual["direction_gate_required"]:
            bp_gate_misses += 1
        results.append(
            {
                "id": case["id"],
                "source": case["source"],
                "passed": passed,
                "expected": expected,
                "selected": selected,
                "missing": missing,
                "forbidden_selected": forbidden_selected,
                "unexpected": unexpected,
            }
        )
    passed_count = sum(item["passed"] for item in results)
    return {
        "schema_version": "3.0",
        "cases": len(cases),
        "passed": passed_count,
        "failed": len(cases) - passed_count,
        "pass_rate": round(passed_count / len(cases), 4) if cases else 0,
        "atomic_accuracy": round(atomic_pass / atomic_total, 4) if atomic_total else 0,
        "specialist_miss_rate": round(expected_missing / expected_total, 4) if expected_total else 0,
        "unnecessary_call_rate": round(unnecessary_calls / selected_total, 4) if selected_total else 0,
        "direction_false_positive_rate": round(direction_false_positives / direction_negative_total, 4) if direction_negative_total else 0,
        "bp_direction_gate_misses": bp_gate_misses,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate StartupPlanner Pro v3 routing rules")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()
    report = evaluate()
    if args.write_baseline:
        baseline = {key: value for key, value in report.items() if key != "results"}
        (ROOT / "evals" / "regression-baseline.yaml").write_text(
            yaml.safe_dump(baseline, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
        )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"cases={report['cases']} passed={report['passed']} failed={report['failed']} pass_rate={report['pass_rate']:.2%}")
        print(f"atomic_accuracy={report['atomic_accuracy']:.2%} specialist_miss_rate={report['specialist_miss_rate']:.2%}")
        print(f"unnecessary_call_rate={report['unnecessary_call_rate']:.2%}")
        print(f"direction_false_positive_rate={report['direction_false_positive_rate']:.2%} bp_gate_misses={report['bp_direction_gate_misses']}")
        for item in report["results"]:
            if not item["passed"]:
                print(f"FAIL {item['id']}: expected={item['expected']} selected={item['selected']} missing={item['missing']} forbidden={item['forbidden_selected']}")
    raise SystemExit(0 if report["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
