# Codex、Cursor、TRAE 安装说明

## 共同要求

三个平台都必须读取 `Agents/StartupPlanner Pro/core/BOOTSTRAP.md`，而不是复制全部角色内容。路径以目标项目根目录为基准。

## Codex

将 `adapters/codex/AGENTS.snippet.md` 合并到目标项目根目录 `AGENTS.md`。若工作目录直接位于 StartupPlanner Pro 内，本目录的 `AGENTS.md` 可作为入口。

Codex 有原生子 Agent 时执行真实委派；没有时使用单 Agent 串行角色模拟。

## Cursor

将：

```text
adapters/cursor/startupplanner.mdc → .cursor/rules/startupplanner.mdc
adapters/cursor/startupplanner-command.md → .cursor/commands/startupplanner.md
```

Cursor 根目录 `AGENTS.md` 也可作为简单入口，但 `.cursor/rules` 更适合按需触发。

## TRAE

将 `adapters/trae/AGENTS.snippet.md` 合并到项目或子仓库 `AGENTS.md`，或复制：

```text
adapters/trae/startupplanner-bootstrap/ → .agents/skills/startupplanner-bootstrap/
```

TRAE Multi Agents 可用时按 Task Packet 委派；不可用时执行同一降级协议。

## 验收

在每个平台分别用 `evals/routing-cases.yaml` 中的人工 curated 用例抽测，记录选择角色、是否拆任务、是否误触发方向门和是否真实委派。离线规则通过不代表宿主模型必然遵循。

