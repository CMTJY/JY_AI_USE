# StartupPlanner Pro v3 团队架构

## 四层结构

1. **通用核心层**：`core/` 定义 Bootstrap、任务交接、产物、状态和质量门禁。
2. **角色与路由层**：`agents/` 是角色行为事实源；`registry/` 提供精简候选目录和语义 taxonomy。
3. **工作流层**：`workflows/` 用能力槽位表达 DAG，不把专业 Agent 全部写死。
4. **平台适配层**：`adapters/` 只让 Codex、Cursor、TRAE 发现同一个 Bootstrap。

## 数据流

```text
user request
→ intent {domain, task_type, channel, lifecycle, artifact}
→ atomic tasks
→ route_decision
→ task_packet
→ specialist artifact
→ independent review
→ aggregation
→ final delivery
```

控制角色使用 `visibility: internal` 与 `invocation: system-only`，不参与普通专业排名。专业角色使用 `visibility: specialist` 与 `portable: true`。

## Token 模型

系统采用渐进加载：一次只加载当前平台入口、核心 Bootstrap、精简路由索引、命中 Agent，以及 1–3 个技能。完整角色库和技能库可以很大，但不应同时进入上下文。

维护工具以字符数给出保守 Token 区间。该估算用于发现膨胀，不代表某个模型的精确计费。

## 降级

宿主有原生多 Agent 能力时使用真实委派；没有时按相同 Task Packet 串行切换角色，明确标注“单 Agent 串行角色模拟”，不虚报并行或独立上下文。

