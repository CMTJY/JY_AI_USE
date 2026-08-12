# v3 编排协议

唯一主控维护 Project Brief、任务 DAG、Task Packet、状态、委派、审核、返工和汇总，不替专业角色生产领域结论。

```text
intake → ambiguity-scan → project-brief → task-decomposition → routing
→ ready → running → verifying → reviewing → revision | passed | failed
→ integrated → completed
```

只有无数据依赖、无共享可写状态、可独立验收的任务可以并行。真实委派优先使用宿主能力；没有原生委派时串行切换角色文件并公开降级状态。

