# StartupPlanner Pro v3 — TRAE 入口

需要 StartupPlanner Pro 时，读取 `Agents/StartupPlanner Pro/core/BOOTSTRAP.md` 并遵守渐进加载：先路由目录，后命中角色，再按需读取技能。

TRAE 原生 Multi Agents 可用时，将每个 Task Packet 交给对应独立 Agent；不可用时标记“单 Agent 串行角色模拟”。不得为了制造团队感调用无关角色。最终披露实际角色、技能、验证和降级状态。

将本片段加入目标项目根或子仓库的 `AGENTS.md`，业务规则仍由 StartupPlanner Pro 核心文件提供。

