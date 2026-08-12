from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]


def contracts():
    for path in (ROOT / "agents").rglob("*.md"):
        if "skills" in path.parts or "templates" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
        if not match:
            raise ValueError(f"Missing frontmatter: {path}")
        data = yaml.safe_load(match.group(1))
        data["file"] = path.relative_to(ROOT / "agents").as_posix()
        yield data


def main():
    fields = ["schema_version", "id", "name", "version", "status", "visibility", "invocation", "portable", "domains", "task_types", "channels", "lifecycle_stages", "capabilities", "produces", "when_to_use", "do_not_use_when", "required_inputs", "optional_inputs", "handoff_targets", "reviewer", "file"]
    agents = []
    seen = set()
    all_contracts = list(contracts())
    ids = {item["id"] for item in all_contracts}
    for data in sorted(all_contracts, key=lambda item: item["id"]):
        if data["id"] in seen:
            raise ValueError(f"Duplicate agent id: {data['id']}")
        seen.add(data["id"])
        missing = set(data.get("handoff_targets", [])) - ids
        if missing:
            raise ValueError(f"Unknown handoff from {data['id']}: {sorted(missing)}")
        agents.append({key: data.get(key) for key in fields})
    output = {"schema_version": "3.0", "generated_from": "agents/** role frontmatter", "agents": agents}
    (ROOT / "registry" / "generated-agents.yaml").write_text(
        yaml.safe_dump(output, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
