# StartupPlanner Pro v3 文档导航

本目录集中保存面向维护者和使用者的说明。v3 的运行规则以项目根目录 `AGENTS.md`、`core/` 协议、`registry/` 注册表和角色文件为准；`agents/config/` 与 `agents/templates/` 仅保留为 v2 兼容与迁移参考。

## 核心入口

| 文档 | 用途 |
|---|---|
| [项目总览](../README.md) | 项目定位、使用方式、目录和关键约束 |
| [运行入口](../AGENTS.md) | 三平台共享的短启动入口 |
| [团队架构](architecture.md) | 渐进加载、路由、编排、审核和降级机制 |
| [路由指南](routing-guide.md) | 路由事实源、评分、硬过滤与诊断方法 |
| [平台安装](platform-setup.md) | Codex、Cursor、TRAE 接入方法 |
| [独立 Agent 指南](portable-agent-guide.md) | 单角色复制、打包与验证方法 |
| [实验评估报告](evaluation-report.md) | 离线路由实验、Token 预算与适用边界 |
| [部门与角色](departments.md) | 所有部门、角色 ID、文件位置和职责边界 |
| [v3 核心协议](../core/BOOTSTRAP.md) | Task Packet、Artifact、质量门禁与渐进加载入口 |
| [方向发现门](methodology/direction-discovery.md) | 开放式创业 / BP 请求的重大歧义扫描、用户确认和放行规则 |
| [v3 工作流](../workflows/) | 能力槽位驱动的工作流定义 |

## 方法论

- [创业阶段](methodology/startup-phases.md)
- [商业计划书写作指南](methodology/bp-writing-guide.md)
- [智能体协作规范](methodology/agent-collaboration.md)
- [方向发现与用户确认门](methodology/direction-discovery.md)

## 交付模板

- [商业计划书模板](templates/bp-template.md)
- [财务模型模板](templates/financial-model-template.md)
- [市场报告模板](templates/market-report-template.md)
- [路线图模板](templates/roadmap-template.md)

## 兼容文档

`methodology/`、`templates/` 和 `agents/templates/` 中的 v2 内容仍可作为业务方法论和迁移参考，但不得覆盖 `core/`、`registry/` 与 `workflows/` 的 v3 运行时事实。

## 文档放置规则

- 项目根 `README.md` 只做面向用户的总览和入口。
- 项目根 `AGENTS.md` 只做短启动入口，不承载完整协议或角色清单。
- 部门说明统一维护在 `docs/departments.md`，不在各部门目录重复创建 README。
- 新工作流写入 `workflows/`；`agents/templates/` 仅维护 v2 兼容内容。
- 角色自己的能力、输入输出和边界写在角色 Markdown；技能说明写在角色的 `skills/SKILL_INDEX.md`。
