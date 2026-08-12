from pathlib import Path
import argparse
import shutil
import re

import yaml

from common import load_yaml, parse_frontmatter
from token_budget import estimate_tokens


ROOT = Path(__file__).resolve().parents[1]


class PackageError(ValueError):
    pass


MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]+)?\)")


def _repair_local_links(package):
    for path in package.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        repaired = re.sub(r"\]\(\.\./\.\./[^/)]+\.md([#)]?)", r"](../../AGENT.md\1", text)
        repaired = repaired.replace("(skills/", "(../") if path.parent.name != package.name else repaired
        if repaired != text:
            path.write_text(repaired, encoding="utf-8", newline="\n")


def validate_package(package, forbidden_agent_ids=()):
    package = Path(package).resolve()
    errors = []
    for path in package.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for agent_id in forbidden_agent_ids:
            if agent_id in text:
                errors.append(f"team agent reference: {path.relative_to(package)} -> {agent_id}")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1)
            if "://" in target or target.startswith(("mailto:", "/")):
                continue
            resolved = (path.parent / target).resolve()
            if package not in resolved.parents and resolved != package:
                errors.append(f"link escapes package: {path.relative_to(package)} -> {target}")
            elif not resolved.exists():
                errors.append(f"broken link: {path.relative_to(package)} -> {target}")
    return errors


def package_agent(agent_id, output_root, root=ROOT):
    root = Path(root)
    output_root = Path(output_root).resolve()
    catalog = load_yaml(root / "registry" / "generated-agents.yaml")
    agent = next((item for item in catalog["agents"] if item["id"] == agent_id), None)
    if not agent:
        raise PackageError(f"Unknown agent: {agent_id}")
    if agent["status"] != "active" or agent["visibility"] != "specialist" or not agent["portable"]:
        raise PackageError(f"Agent is not portable: {agent_id}")
    package = output_root / agent_id
    if package.exists():
        raise PackageError(f"Output already exists: {package}")
    package.mkdir(parents=True)
    source = root / "agents" / agent["file"]
    bootstrap = (root / "adapters" / "portable" / "BOOTSTRAP.md").read_text(encoding="utf-8")
    contract, body = parse_frontmatter(source)
    contract["invocation"] = "manual"
    contract["handoff_targets"] = []
    contract["reviewer"] = "self-review-disclosed"
    contract["runtime_mode"] = "standalone"
    other_agent_ids = [item["id"] for item in catalog["agents"] if item["id"] != agent_id]
    standalone_body = body
    for other_id in other_agent_ids:
        standalone_body = standalone_body.replace(other_id, "standalone-self-review")
    role_text = f"---\n{yaml.safe_dump(contract, allow_unicode=True, sort_keys=False).rstrip()}\n---\n\n{standalone_body}"
    agent_text = f"{role_text.rstrip()}\n\n---\n\n{bootstrap.rstrip()}\n"
    (package / "AGENT.md").write_text(agent_text, encoding="utf-8", newline="\n")
    source_skills = source.parent / "skills"
    if source_skills.is_dir():
        shutil.copytree(source_skills, package / "skills")
    _repair_local_links(package)
    for path in package.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for other_id in other_agent_ids:
            text = text.replace(other_id, "standalone-self-review")
        path.write_text(text, encoding="utf-8", newline="\n")
    readme = f"""# {agent['name']} 独立包

来源：StartupPlanner Pro `{agent_id}` v{agent['version']}。

## 使用

- Codex：把 `AGENT.md` 放在项目根目录并重命名或合并为 `AGENTS.md`。
- Cursor：在对话中引用 `AGENT.md`，或创建一条 `.cursor/rules` 规则指向它。
- TRAE：把本目录放入项目并在规则或自定义 Agent 中引用 `AGENT.md`。

本包按独立模式工作，不依赖 StartupPlanner Pro 主控。若包含 `skills/`，只按任务需要读取 1–3 个技能。
"""
    (package / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    low, high = estimate_tokens(agent_text)
    manifest = {
        "schema_version": "3.0",
        "agent_id": agent_id,
        "agent_version": agent["version"],
        "source": f"agents/{agent['file']}",
        "files": sorted([path.relative_to(package).as_posix() for path in package.rglob("*") if path.is_file()] + ["manifest.yaml"]),
        "token_estimate": {"low": low, "high": high},
        "team_runtime_required": False,
    }
    (package / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
    )
    for _ in range(4):
        package_texts = []
        for path in package.rglob("*"):
            if path.is_file():
                try:
                    package_texts.append(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    pass
        package_low, package_high = estimate_tokens("".join(package_texts))
        current = (manifest["token_estimate"].get("package_low"), manifest["token_estimate"].get("package_high"))
        manifest["token_estimate"].update({"package_low": package_low, "package_high": package_high})
        (package / "manifest.yaml").write_text(
            yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
        )
        if current == (package_low, package_high):
            break
    errors = validate_package(package, other_agent_ids)
    if errors:
        shutil.rmtree(package)
        raise PackageError("Package validation failed: " + "; ".join(errors))
    return package


def main():
    parser = argparse.ArgumentParser(description="Export a portable StartupPlanner Pro specialist")
    parser.add_argument("agent_id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    package = package_agent(args.agent_id, Path(args.output))
    print(package)


if __name__ == "__main__":
    main()
