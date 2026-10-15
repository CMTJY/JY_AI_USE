#!/usr/bin/env python3
"""Install bundled memory rules without replacing existing project instructions.

Only call for a selected manager/team initialization, never for a check.
Uses the Python standard library and performs no remote operations.
"""

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys


PROTOCOL_START = b"<!-- teampnew:wiki-memory-agent:start -->"
PROTOCOL_END = b"<!-- teampnew:wiki-memory-agent:end -->"
ROUTE_START = b"<!-- teampnew:route-first:start -->"
ROUTE_END = b"<!-- teampnew:route-first:end -->"
ROUTING_SUPPLEMENT = """
## teamPNew 项目补充

以下是本项目对上述通用记忆协议的具体化规则：
- 每轮先定点检查并读取 `memory/INDEX.md` 和 `memory/workflows/route-first.md`；再匹配目录、位置和文件名称，只读取本任务命中的路由与文件。不执行上述通用协议的全量 memory 路径列举，不递归扫描本地项目、memory 或飞书知识库。无匹配时只在已明确父目录做一层名称定位，或询问精确入口。
- `memory/workflows/route-first.md` 是每轮必读的固定规则，不能因任务关键词未命中而跳过。每次新增、删除、移动、重命名文件或飞书节点后，在同轮结束前同步相应目录路由、索引和链接，失败写为待核验。
- 用户选择一致性检查时，不自动创建 AGENTS、memory 或索引；空项目、缺少可用飞书记忆或不能识别总管理/团队类型时停止并提示初始化。有效项目只核对已登记范围的位置和名称，不比较飞书正文，不自动修复差异。
- 总管理项目的明确范围包含用户登记的全部知识库入口；团队项目仅保留本项目的指南、目的地、路由和总管理入口。
""".strip().encode("utf-8")


def normalized(data):
    return data.replace(b"\r\n", b"\n").strip()


def verify_bundle(skill_root):
    assets = skill_root / "assets"
    bundle = assets / "wiki-memory-agent"
    manifest = json.loads((assets / "wiki-memory-agent.manifest.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    actual = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
    if set(expected) != actual:
        raise ValueError("Bundled wiki-memory-agent file inventory differs from manifest")
    for rel, digest in expected.items():
        path = bundle / rel
        if path.is_symlink() or not path.resolve().is_relative_to(bundle.resolve()):
            raise ValueError(f"Unsafe bundled path: {rel}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Bundled file checksum mismatch: {rel}")
    return bundle


def checked_target(project, relative):
    path = project / relative
    # Inspect only the requested path and its ancestors, never the project tree.
    for part in (path, *path.parents):
        if part == project:
            break
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError(f"Refusing linked project target: {part}")
    if not path.resolve().is_relative_to(project):
        raise ValueError(f"Target escapes project: {relative}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a file: {relative}")
    for parent in path.parents:
        if parent == project:
            break
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Expected a directory: {parent}")
    return path


def append_block(data, start, content, end):
    if start in data or end in data:
        if data.count(start) != 1 or data.count(end) != 1 or data.index(start) > data.index(end):
            raise ValueError("Incomplete or duplicate teamPNew marker; inspect existing rules")
        return data
    return data + b"\n\n" + start + b"\n" + content + b"\n" + end + b"\n"


def plan_install(project, skill_root, day):
    bundle = verify_bundle(skill_root)
    names = [p.name for p in project.iterdir() if p.name.casefold() == "agents.md"]
    if len(names) > 1:
        raise ValueError("Multiple AGENTS.md case variants found; choose the canonical file first")
    agent_name = names[0] if names else "AGENTS.md"
    targets = [checked_target(project, rel) for rel in (
        agent_name, "memory/INDEX.md", "memory/workflows/route-first.md")]
    before = [p.read_bytes() if p.exists() else None for p in targets]
    # Decode before preparing any writes so incompatible text fails without changes.
    for data in before:
        if data is not None:
            data.decode("utf-8-sig")
    original = (bundle / "template/AGENTS.md").read_bytes()
    agent = before[0] if before[0] is not None else original
    if normalized(original) not in normalized(agent):
        if PROTOCOL_START in agent:
            raise ValueError("Existing marked protocol differs; merge it manually without overwriting")
        agent = append_block(agent, PROTOCOL_START, original, PROTOCOL_END)
    agent = append_block(agent, ROUTE_START, ROUTING_SUPPLEMENT, ROUTE_END)
    # A damaged routing block must not silently be accepted as an installation.
    if ROUTING_SUPPLEMENT not in agent:
        raise ValueError("Existing routing supplement differs; inspect and merge it manually")
    policy = before[2]
    if policy is None:
        policy = (skill_root / "assets/route-first.md").read_bytes().replace(b"{{DATE}}", day.encode("ascii"))
    entry = (f"- [每轮必读：目录路由规则](workflows/route-first.md) — 类型：workflow；"
             f"范围：当前项目；触发：每轮全部任务；摘要：先匹配目录位置与名称，文件变化后维护路由；"
             f"状态：active；更新：{day}\n").encode("utf-8")
    if before[1] is None:
        index = (bundle / "template/memory/INDEX.md").read_bytes()
        index = index.replace("目前还没有持久项目记忆。".encode("utf-8"), entry.rstrip())
    else:
        index = before[1]
        if b"(workflows/route-first.md)" not in index:
            index += "\n\n## teamPNew 每轮必读\n\n".encode("utf-8") + entry
    return list(zip(targets, before, (agent, index, policy)))


def install(project, skill_root, day, dry_run=False):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("Project must be an existing directory")
    skill_root = Path(skill_root).resolve()
    if project == skill_root or project.is_relative_to(skill_root):
        raise ValueError("Use a target project separate from the skill package")
    date.fromisoformat(day)
    plan = plan_install(project, skill_root, day)
    results = []
    for path, before, after in plan:
        action = "preserved" if before == after else "created" if before is None else "appended"
        if not dry_run and before != after:
            checked_target(project, path.relative_to(project))
            current = path.read_bytes() if path.exists() else None
            if current != before:
                raise ValueError(f"Concurrent edit detected: {path}; review partial results before retry")
            path.parent.mkdir(parents=True, exist_ok=True)
            if before is None:
                with path.open("xb") as handle:
                    handle.write(after)
            else:
                if not after.startswith(before):
                    raise ValueError(f"Refusing to replace existing contents: {path}")
                with path.open("ab") as handle:
                    handle.write(after[len(before):])
        results.append({"path": path.relative_to(project).as_posix(), "action": action})
    return {"status": "dry_run" if dry_run else "memory_scaffold_ready",
            "files": results, "next": "Verify existing policy and add real Feishu context/routes per the selected mode."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--date", default=date.today().isoformat(), help="User-local date, YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = install(args.project, Path(__file__).resolve().parents[1], args.date, args.dry_run)
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
