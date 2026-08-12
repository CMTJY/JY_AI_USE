# StartupPlanner Pro v3 通用智能体团队设计规格

日期：2026-08-12  
状态：待用户书面复核  
适用目录：`Agents/StartupPlanner Pro/`

## 1. 背景与目标

StartupPlanner Pro v2 已注册 39 个 active Agent，并使用 Markdown、YAML 和宿主原生委派能力组织工作。现有主要问题不是角色数量不足，而是角色可达性、路由准确度和跨工具入口可靠性不足：

- 9 个细分营销 Agent 没有显式路由或预设工作流入口；
- 宽泛关键词会造成误调，例如“小红书账号从 0 到 1”错误命中创业方向门；
- 复合任务可能只命中一个角色，遗漏必要的架构、开发、审核或验收环节；
- 工作流模板把执行 Agent 写死，无法根据渠道、阶段和目标产物选择更聚焦的角色；
- Codex、Cursor 和 TRAE 的规则发现机制不同，子目录入口不一定自动生效；
- 项目没有可重复的路由评测，配置调整后无法检测回归；
- 单个 Agent 脱离团队复制时，缺少独立运行协议。

v3 的目标是：

1. 同一套业务角色定义可在 Codex、Cursor 和 TRAE 中使用；
2. 团队模式能先拆任务、再准确选择最小充分 Agent 集合；
3. 任意专业 Agent 可以打包复制到其他项目独立使用；
4. 平台适配层保持轻薄，不复制或分叉业务规则；
5. 路由、配置、工作流和 Token 预算均可自动验证；
6. 保留纯 Markdown/YAML 主体，不强制用户配置模型 API 或额外运行时。

## 2. 非目标

- 不实现新的模型服务、长期记忆服务或远程 Agent 平台；
- 不把 Codex、Cursor、TRAE 的专有格式作为业务事实源；
- 不在本阶段盲目删除已有专业 Agent；
- 不要求普通使用者运行 Python 才能使用团队；
- 不承诺不同宿主拥有完全相同的原生并发和子 Agent 能力；宿主不支持时必须明确降级为单 Agent 串行角色模拟。

## 3. Token 消耗评估与预算

### 3.1 当前基线

2026-08-12 对 v2 文件体积的保守估算：

| 内容 | 文件数 | 字符数 | 估算 Token 范围 |
|---|---:|---:|---:|
| 入口与 README | 2 | 8,642 | 2,881–5,761 |
| 路由与能力配置 | 2 | 15,793 | 5,264–10,529 |
| 核心控制角色 | 5 | 8,737 | 2,912–5,825 |
| 专业角色正文 | 35 | 147,359 | 49,120–98,239 |
| 工作流模板 | 4 | 19,425 | 6,475–12,950 |
| 角色本地技能 | 100 | 1,067,972 | 355,991–711,981 |

估算范围用于无指定模型 tokenizer 时的预算管理，不代表某一具体模型的精确计费。实际 Token 因模型分词器、宿主注入规则和对话历史而变化。

### 3.2 v3 加载策略

v3 使用渐进加载：

1. 启动只加载短入口、Bootstrap 和压缩路由目录；
2. 先把请求拆成原子任务并提取结构化槽位；
3. 只读取候选 Agent 的路由契约，不读取全部角色正文；
4. 选定后只加载执行角色正文；
5. 只加载 Task Packet 明确要求或触发条件直接命中的 1–3 个技能；
6. 工作流只在任务类型命中时读取；
7. 审核角色只在产物进入对应质量门时加载。

### 3.3 预算门禁

| 阶段 | 目标预算 |
|---|---:|
| 平台入口 | ≤ 1,500 estimated tokens |
| Bootstrap + 路由阶段累计 | ≤ 4,000 estimated tokens |
| 普通单 Agent 任务启动累计 | ≤ 6,000 estimated tokens |
| 单个专业 Agent 正文 | 建议 ≤ 8,000 estimated tokens |
| 单次加载技能数量 | 1–3 个 |
| 默认候选 Agent 数量 | ≤ 5 个 |

验证器必须报告字符数、估算 Token 范围和超预算项。预算超限默认是警告；平台入口、全量预加载和技能数量上限违规是错误。

## 4. 总体架构

```text
StartupPlanner Pro/
├── AGENTS.md
├── README.md
├── core/
│   ├── BOOTSTRAP.md
│   ├── orchestration.md
│   ├── routing.md
│   ├── task-packet.md
│   ├── artifact-envelope.md
│   └── quality-gates.md
├── registry/
│   ├── taxonomy.yaml
│   ├── routes.yaml
│   ├── workflows.yaml
│   └── generated-agents.yaml
├── agents/
├── workflows/
├── adapters/
│   ├── codex/
│   ├── cursor/
│   └── trae/
├── evals/
│   ├── routing-cases.yaml
│   ├── workflow-cases.yaml
│   └── regression-baseline.yaml
├── docs/
│   ├── architecture.md
│   ├── routing-guide.md
│   ├── platform-setup.md
│   ├── portable-agent-guide.md
│   └── evaluation-report.md
└── tools/
    ├── validate.py
    ├── route_eval.py
    ├── token_budget.py
    └── package_agent.py
```

为了降低迁移风险，实施时可先兼容读取 v2 路径，完成验证后再删除或归档旧配置。`agents/` 中角色 Markdown 仍是角色行为的唯一事实源。

## 5. Agent v3 契约

每个 Agent 使用统一 frontmatter，团队和独立模式读取同一文件：

```yaml
schema_version: "3.0"
id: marketing-xiaohongshu-operator
name: 小红书运营专家
version: "3.0.0"
status: active
visibility: specialist
portable: true
domains: [marketing]
task_types: [channel-strategy, account-operation, influencer-campaign]
channels: [xiaohongshu]
lifecycle_stages: [launch, growth, optimization]
capabilities: [content-operations, influencer-marketing, channel-analytics]
produces: [xiaohongshu-operation-plan, content-calendar, influencer-campaign-plan]
when_to_use:
  - 规划小红书账号从 0 到 1 运营
do_not_use_when:
  - 只创作一篇具体笔记
required_inputs: [offering, target_audience, objective]
optional_inputs: [budget, current_account_data]
handoff_targets: [marketing-xiaohongshu-specialist, marketing-growth-hacker]
reviewer: core-quality-reviewer
```

正文必须包含：

- 核心职责与非职责；
- 团队模式：收到 Task Packet 后只完成已分配任务；
- 独立模式：没有 Task Packet 时自行完成必要澄清、执行和验证；
- 输入、输出和完成标准；
- 工具和证据要求；
- 交接条件；
- 至少 3 个正向路由示例和 2 个反向示例。

控制角色使用：

```yaml
visibility: internal
invocation: system-only
portable: false
```

控制角色不参与普通专业候选排名。

## 6. 路由设计

### 6.1 五阶段流程

```text
请求理解与槽位提取
→ 原子/复合任务判定与任务拆分
→ 候选召回
→ 硬过滤
→ 多维评分与冲突裁决
→ 执行或澄清
```

### 6.2 结构化意图

```yaml
intent:
  objects: []
  actions: []
  domains: []
  channels: []
  task_types: []
  lifecycle_stages: []
  expected_artifacts: []
  constraints: []
  compound: false
```

“从 0 到 1”默认只表示 `lifecycle_stage: launch`。只有同时存在创业、商业模式、赛道、公司或 BP 等业务方向信号时，才能触发创业方向门。

### 6.3 复合任务拆分

当请求包含多个可独立验收的动作、产物或依赖阶段时，Task Planner 先生成任务 DAG。Router 为每个任务分别选人，不能用单个“最接近”Agent 承包整个复合任务。

### 6.4 硬过滤

候选必须同时满足：

- `status: active`；
- 角色文件存在并通过 schema 校验；
- 领域、渠道和产物无明确冲突；
- 满足必要工具和权限；
- 未命中 `do_not_use_when`；
- 调用方式符合 `visibility` 和 `invocation`；
- reviewer 与执行者不同。

### 6.5 评分

| 维度 | 权重 |
|---|---:|
| task_types | 30% |
| capabilities | 25% |
| domains | 15% |
| produces | 15% |
| channels | 10% |
| lifecycle_stages | 5% |

规则：

- 命中 `do_not_use_when`：淘汰；
- 全覆盖相同时，范围更聚焦的 Agent 优先；
- 最高得分低于 0.70：澄清；
- 第一、第二候选分差低于 0.10 且职责存在实质差异：澄清；
- 一个请求可以生成多个任务，但每个原子任务默认只有一个权威生产者；
- 最多返回 1 个主执行者和 2 个备选者。

### 6.6 路由输出

```yaml
route_decision:
  task_id: string
  selected: agent-id
  confidence: 0.0
  matched: {}
  assumptions: []
  fallbacks: []
  rejected: []
  clarification_required: false
  clarification_question: null
```

所有选择必须可解释，不允许只返回 Agent 名称。

## 7. 工作流设计

固定模板从 `agent: id` 改为能力槽位：

```yaml
assignment:
  required:
    domains: [marketing]
    task_types: [channel-growth]
  conditional:
    channel: ${project.channels}
  fallback: marketing-growth-hacker
  selection: most-specific
```

只有控制任务、独立审核和唯一职责角色可固定指定 Agent。专业执行任务优先按能力、渠道和产物动态选择。

初始工作流：

- business-plan；
- product-development；
- software-delivery；
- marketing-campaign；
- channel-operation；
- research-project。

## 8. 平台适配

### 8.1 通用原则

适配器只负责：

1. 让平台发现 StartupPlanner Pro；
2. 指向 `core/BOOTSTRAP.md`；
3. 声明宿主能力映射；
4. 要求输出路由决定和真实委派状态。

适配器不得复制 Agent 正文、路由规则或工作流内容。

### 8.2 Codex

提供可复制到目标项目根目录的 `AGENTS.md` 片段或安装说明。入口保持简短，指向团队核心目录。Codex 支持原生多 Agent 时使用真实委派；否则串行角色模拟。

### 8.3 Cursor

提供：

```text
.cursor/rules/startupplanner.mdc
.cursor/commands/startupplanner.md
```

根目录 `AGENTS.md` 作为通用入口；`.mdc` 负责 Cursor 自动或手动触发。业务规则仍来自同一核心文件。

### 8.4 TRAE

提供根或子仓库 `AGENTS.md` 使用说明，并提供：

```text
.agents/skills/startupplanner-bootstrap/
```

TRAE 原生多 Agent 可用时映射为真实子 Agent；不可用时执行同一降级协议。

## 9. 独立 Agent 打包

`package_agent.py` 接收 Agent ID，输出一个可复制目录：

```text
portable-agents/<agent-id>/
├── AGENT.md
├── README.md
├── skills/
└── manifest.yaml
```

打包规则：

- 包含角色正文和其直接依赖的本地技能；
- 注入独立模式 Bootstrap，不依赖团队 Orchestrator；
- 保留来源、版本和许可证；
- 不包含其他无关 Agent；
- 校验所有相对链接；
- 输出字符数和估算 Token；
- README 给出 Codex、Cursor、TRAE 的手动安装方法。

## 10. 验证与评测

### 10.1 静态验证

`validate.py` 检查：

- YAML 和 frontmatter schema；
- 注册 ID、文件和角色 ID 一致；
- 路由、工作流和 handoff 只引用存在的 active Agent；
- 每个 active 专业 Agent 至少有一条可达路径；
- DAG 无环、产物生产者唯一；
- reviewer 独立；
- 技能索引、目录、来源和许可证完整；
- 平台适配器没有复制业务规则；
- Token 预算没有硬错误。

### 10.2 路由评测

首版至少 80 条用例，覆盖：

- 每个 active 专业 Agent 至少 3 个正例、2 个反例；
- 中文、英文和中英混合请求；
- 原子任务和复合任务；
- 渠道、生命周期、产物和工具约束；
- 低置信度澄清；
- 方向门正例和误触发反例；
- Agent 禁用和降级；
- Codex、Cursor、TRAE 的入口行为。

目标指标：

| 指标 | 目标 |
|---|---:|
| 原子任务准确率 | ≥ 90% |
| 专业 Agent 漏调率 | ≤ 5% |
| 不必要多 Agent 调用率 | ≤ 10% |
| 方向门误触发率 | ≤ 2% |
| BP 方向门漏检 | 0 |
| 不可达 active 专业 Agent | 0 |

`route_eval.py` 是基于声明式规则的离线回归检查，不调用外部模型。三平台仍需使用同一自然语言用例做实机抽测，并在报告中区分“规则引擎结果”和“宿主模型结果”。

## 11. 文档交付

实施完成后更新或新增：

- 项目 `README.md`：团队定位、架构、快速开始、角色概览、工作模式；
- `docs/architecture.md`：整体团队实现原理和数据流；
- `docs/routing-guide.md`：路由、评分、冲突和调试；
- `docs/platform-setup.md`：Codex、Cursor、TRAE 安装与使用；
- `docs/portable-agent-guide.md`：单 Agent 导出、复制和升级；
- `docs/evaluation-report.md`：用例数量、通过率、已知限制和复现命令；
- `docs/departments.md`：更新后的角色状态、边界和可达入口。

README 必须明确：项目本身是通用协议和可选验证工具，不是模型运行时；没有原生多 Agent 能力时会降级。

## 12. 迁移策略

分阶段实施：

1. 新增 v3 schema、taxonomy、验证器和评测，不改变现有入口行为；
2. 迁移控制角色和路由配置；
3. 迁移专业 Agent 契约，优先处理当前不可达营销角色；
4. 把工作流改成能力槽位；
5. 增加三平台适配器和独立打包器；
6. 更新 README、架构和评测报告；
7. 通过全部验证后，归档 v2 配置并切换入口。

每一步保持仓库可使用，并保留回退点。角色内容优化与路由基础设施分开提交，便于定位回归。

## 13. 验收标准

- Codex、Cursor、TRAE 均有明确且不复制业务逻辑的启动入口；
- 所有 active 专业 Agent 均可由路由或条件工作流到达；
- 两个小红书角色、通用内容角色和增长角色有可验证的边界；
- 代表性误调场景全部加入回归用例并通过；
- 复合请求生成多个有依赖的 Task Packet；
- 路由输出含选择、置信度、理由、淘汰原因和澄清状态；
- 单个专业 Agent 可以打包并在无团队文件时独立运行；
- 静态验证、路由评测和 Token 预算检查成功；
- README 和相关说明反映实际实现，评测报告包含可复现证据；
- 不要求最终用户配置额外模型 API。

## 14. 已知限制

- 纯 Markdown/YAML 无法强制所有宿主模型完全按协议执行，因此必须结合离线规则评测与三平台实机抽测；
- 不同工具的原生子 Agent、并发、审批和规则优先级不同，适配器只能统一语义，不能伪造平台能力；
- 字符数估算不等同于具体模型精确 Token；
- 渠道平台规则会变化，专业 Agent 的事实性平台建议仍需联网核验；
- 路由准确率只能通过持续积累真实失败样本提高，首版评测不是终点。
