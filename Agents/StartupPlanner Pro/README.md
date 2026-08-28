# StartupPlanner Pro v3

StartupPlanner Pro v3 是一个平台无关的可移植智能体团队框架。它用同一套 Markdown/YAML 角色契约服务 Codex、Cursor 和 TRAE，支持团队自动调度，也支持把任意专业 Agent 单独打包到其他项目使用。

项目不是模型运行时，不要求额外模型 API。Python 工具只用于维护、离线路由实验、配置验证和 Agent 打包；日常使用只需 AI 工具能够读取项目文件。

## 这次解决了什么

- 39 个 active Agent 不再只靠宽泛关键词选择；
- 复合请求先拆任务，再给每个任务选择一个权威生产者；
- 小红书、抖音、视频剪辑、私域、国内/跨境电商、直播和 LinkedIn 等细分角色都有明确入口；
- “从0到1”默认是生命周期 `launch`，不再单独触发创业战略角色；
- 工作流使用能力槽位，根据渠道和产物选择最聚焦角色；
- 每个专业 Agent 使用统一 v3 契约，既支持团队模式也支持独立模式；
- 提供 Codex、Cursor、TRAE 薄适配器和可重复路由评测。

## 运行原理

```text
短平台入口
→ core/BOOTSTRAP.md
→ 请求槽位提取与复合任务拆分
→ 精简路由目录召回候选
→ 硬过滤与可解释评分
→ 只加载命中 Agent 和 1–3 个技能
→ 执行、审核、返工、汇总
```

这种渐进加载避免把 35 个专业角色和 100 个技能全部塞进上下文。完整原理见 [团队架构](docs/architecture.md)。

## 两种工作模式

### 团队模式

主控生成 Task Packet，专业 Agent 只执行分配任务，关键产物由独立 reviewer 审核。宿主支持原生子 Agent 时执行真实委派；否则公开降级为“单 Agent 串行角色模拟”。

### 独立模式

把某个专业 Agent 打包或复制到其他项目。没有 Task Packet 时，它自行确认关键输入、执行专业任务和验证，但不声称其他团队成员已经参与。

```powershell
python "Agents/StartupPlanner Pro/tools/package_agent.py" marketing-xiaohongshu-operator --output C:\temp\portable-agents
```

详见 [独立 Agent 指南](docs/portable-agent-guide.md)。

## 三平台快速开始

### 人工新建项目文件夹后接入

把 [`PROJECT_AGENTS_TEMPLATE.md`](PROJECT_AGENTS_TEMPLATE.md) 交给 Codex、Cursor 或 TRAE，并让 AI 在人工已经创建和打开的项目文件夹中执行。模板会指导 AI：

1. 根据当前项目需求生成或安全合并根目录 `AGENTS.md`；
2. 通过 Git sparse clone 将最新版 StartupPlanner Pro 安装到项目内 `startupplanner-pro/`；
3. 写入统一的团队调用入口，并验证远程仓库、分支、commit 和核心协议路径。

模板不会创建项目根目录，也不会默认生成业务代码、初始化外层 Git、安装业务依赖、提交、推送或部署。

### Codex

把 [Codex 入口片段](adapters/codex/AGENTS.snippet.md) 合并到目标项目根目录 `AGENTS.md`，或在本子项目目录中启动任务。

### Cursor

复制 `adapters/cursor/startupplanner.mdc` 到目标项目 `.cursor/rules/`，可选复制 `startupplanner-command.md` 到 `.cursor/commands/`。

### TRAE

使用 `adapters/trae/AGENTS.snippet.md`，或把 `startupplanner-bootstrap` 放到目标项目 `.agents/skills/`。

完整步骤见 [三平台安装](docs/platform-setup.md)。

## 目录

```text
PROJECT_AGENTS_TEMPLATE.md  人工新建项目后的 AGENTS 初始化入口
core/        平台无关启动、路由、编排和质量协议
registry/    taxonomy、路由、工作流索引和生成的 Agent 目录
agents/      角色正文与角色私有技能
workflows/   v3 能力槽位 DAG
adapters/    Codex、Cursor、TRAE 和独立包入口
evals/       路由用例与回归基线
tools/       验证、评测、Token 预算和打包工具
tests/       自动化回归测试
docs/        架构、路由、平台、打包与实验说明
```

## 当前路由实验

离线规则实验包含 117 条用例，实际走 `route-index + 最多两个领域分片` 的发布路径：117/117 通过，原子精确准确率 100.00%，专业 Agent 漏调率 0.00%，不必要调用率 0.00%，方向门误触发率 0.00%，BP 门禁漏检为 0。

这些是本仓库确定性路由器的离线规则结果，不等于三平台实机模型表现。平台实机需要用同一语料抽测，结果单独记录在 [实验报告](docs/evaluation-report.md)。

## 维护验证

```powershell
python -m unittest discover -s "Agents/StartupPlanner Pro/tests" -v
python "Agents/StartupPlanner Pro/tools/validate.py"
python "Agents/StartupPlanner Pro/tools/route_eval.py"
python "Agents/StartupPlanner Pro/tools/token_budget.py"
python "Agents/StartupPlanner Pro/tools/generate_runtime_routes.py"
```

新增或调整 Agent 后必须同步更新契约正反例、路由信号和评测语料；修改 `registry/routes.yaml` 后还要重新生成运行时路由分片。不要靠“感觉”修改提示词。
