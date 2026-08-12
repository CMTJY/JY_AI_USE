# StartupPlanner Pro v3 Bootstrap

本文件是平台无关的最小启动协议。不要在启动时读取全部 Agent 或技能。

1. 读取 `registry/taxonomy.yaml`、`registry/routes.yaml` 和 `registry/generated-agents.yaml`。
2. 把用户请求解析为领域、任务类型、渠道、生命周期、目标产物和约束。
3. 复合请求先拆成可独立验收且依赖明确的原子任务。
4. 对每个原子任务执行硬过滤与评分，只加载最多 5 个候选的精简契约。
5. 选择后才读取该 Agent 正文和 Task Packet 所需的 1–3 个技能。
6. 输出可解释的 `route_decision`，再由宿主原生子 Agent 执行；宿主不支持时标记“单 Agent 串行角色模拟”。
7. 关键产物按 `core/quality-gates.md` 审核，最终只整合通过产物。

权限、删除、部署、推送和外部写入仍以用户明确授权为边界。

