# v3 质量门禁

- 非代码关键产物：`core-quality-reviewer` 按 Task Packet 验收标准和证据审核。
- 代码：实现者自验 → `tech-code-reviewer` 规格审查 → 代码质量审查 → `tech-qa` 集成与验收 → `tech-devops` 发布就绪。
- reviewer 不能是执行者，审核者不直接改写原产物。
- `revision` 只退回责任角色，默认最多 2 次；达到上限公开缺口并请求决策。
- Aggregator 只整合 `passed` 产物；冲突由 Orchestrator 创建 reconciliation 任务。

