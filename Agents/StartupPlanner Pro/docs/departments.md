# StartupPlanner Pro v3 部门与角色索引

本页是 StartupPlanner Pro v3 的部门导航。角色是否可用、能力、真实文件位置和可路由状态以 [`generated-agents.yaml`](../registry/generated-agents.yaml) 为生成事实源，以各角色 Markdown 的 v3 frontmatter 为最终源；[`routes.yaml`](../registry/routes.yaml) 决定请求到角色的可达路径。旧 [`capabilities.yaml`](../agents/config/capabilities.yaml) 仅用于兼容和迁移。

## v3 可达性约束

- 所有 `active` 专业 Agent 必须至少被一个显式路由或能力槽位引用；验证器会阻止“已经安装但永远不会调用”的死角色。
- 路由先按领域、任务类型、产物、渠道和生命周期硬过滤，再按正向信号、负向信号与上下文评分。
- 渠道专员优先于泛化角色；缺少可信度或证据时必须报告候选角色和选择理由。
- 工作流只引用能力槽位，不把角色 ID 固化在编排图里，因此可按项目覆盖默认角色。
- 单独复制角色时，角色依靠自身 v3 契约运行，不声称主控、审核员或其他成员已参与。

## 控制面（core）

| Agent ID | 角色 | 文件 | 职责 |
|---|---|---|---|
| `core-orchestrator` | 通用主控 | [orchestrator.md](../agents/core/orchestrator/orchestrator.md) | 状态、调度、技能选择、委派与返工 |
| `core-task-planner` | 任务规划器 | [task-planner.md](../agents/core/task-planner.md) | 任务 DAG、依赖、产物与验收标准 |
| `core-router` | 能力路由器 | [router.md](../agents/core/router.md) | 能力匹配、约束过滤与备选角色 |
| `core-quality-reviewer` | 独立质量审核员 | [quality-reviewer.md](../agents/core/quality-reviewer.md) | 非代码产物和最终交付验收 |
| `core-aggregator` | 结果整合器 | [aggregator.md](../agents/core/aggregator.md) | 整合已经通过审核的产物 |

## 技术部（tech）

| Agent ID | 角色 | 文件 | 职责 |
|---|---|---|---|
| `tech-architect` | 技术负责人兼架构师 | [architect.md](../agents/tech/architect/architect.md) | 架构、契约、实现 DAG 与文件边界 |
| `tech-backend-dev` | 后端工程师 | [backend-dev.md](../agents/tech/backend-dev/backend-dev.md) | 服务端、API、数据、测试与可观测性 |
| `tech-frontend-dev` | 前端工程师 | [frontend-dev.md](../agents/tech/frontend-dev/frontend-dev.md) | Web 体验、状态、可访问性与前端测试 |
| `tech-mobile-dev` | 移动端工程师 | [mobile-dev.md](../agents/tech/mobile-dev/mobile-dev.md) | 移动平台实现、适配与真机验证 |
| `tech-code-reviewer` | 独立代码审查员 | [code-reviewer.md](../agents/tech/code-reviewer/code-reviewer.md) | 规格符合性与代码质量双门审 |
| `tech-qa` | 质量与测试工程师 | [qa.md](../agents/tech/qa/qa.md) | 测试策略、集成、E2E、性能与验收 |
| `tech-devops` | 平台与可靠性工程师 | [devops.md](../agents/tech/devops/devops.md) | 构建、CI/CD、可观测性、回滚与发布就绪 |

标准链路：架构与测试策略先行，开发角色在无冲突文件范围内实现，代码审查员依次执行规格和质量审核，QA 再做集成验收，DevOps 最后给出发布就绪结论。详细任务图见 [software-dev.yaml](../agents/templates/software-dev.yaml)。

技术角色的 `skills/` 是独立物理副本；每个角色通过本地 `SKILL_INDEX.md` 选择技能，运行时不读取 StartupPlanner Pro 外部的 Superpowers 源包。

## 调研部（research）

| Agent ID | 文件 | 职责 |
|---|---|---|
| `research-analyst` | [analyst.md](../agents/research/analyst.md) | 通用调研、证据整理、事实核查与综合报告 |
| `research-market` | [market.md](../agents/research/market.md) | 市场规模、细分、用户洞察与画像 |
| `research-competitor` | [competitor.md](../agents/research/competitor.md) | 竞品矩阵、基准比较、SWOT 与差异化 |

## 战略部（strategy）

| Agent ID | 文件 | 职责 |
|---|---|---|
| `strategy-opc` | [opc-strategist.md](../agents/strategy/opc-strategist/opc-strategist.md) | 创业假设验证与 GO/PIVOT/NO-GO 门禁 |
| `strategy-analyst` | [strategy-analyst.md](../agents/strategy/strategy-analyst.md) | 行业、商业模式与竞争战略 |
| `strategy-market-researcher` | [market-researcher.md](../agents/strategy/market-researcher.md) | 访谈设计、需求验证与用户研究 |

## 产品部（product）

| Agent ID | 文件 | 职责 |
|---|---|---|
| `product-pm` | [product-manager.md](../agents/product/product-manager/product-manager.md) | 产品发现、PRD、用户故事、优先级与路线图 |
| `product-mvp-designer` | [mvp-designer.md](../agents/product/mvp-designer.md) | MVP 范围、原型与验证实验 |
| `product-director` | [product-director.md](../agents/product/product-director/product-director.md) | 产品治理、发布就绪和规模化统筹 |

## 营销部（marketing）

营销角色按工作对象分为四组，角色真实状态和能力仍以注册表为准。

| 分组 | Agent IDs | 主要职责 |
|---|---|---|
| `Product-EVENT` | `marketing-growth-hacker`, `marketing-campaign-planner`, `marketing-social-strategist` | 增长、活动、发布和社交渠道策略 |
| `media-content` | `marketing-content-creator`, `marketing-douyin-strategist`, `marketing-video-editing-coach`, `marketing-xiaohongshu-operator`, `marketing-xiaohongshu-specialist` | 内容、短视频和平台运营 |
| `fans-domain` | `marketing-private-domain` | 私域、社群、留存与 SCRM |
| `product-sales` | `marketing-ecommerce`, `marketing-cross-border-ecommerce`, `marketing-livestream-coach` | 电商、跨境、本地化与直播转化 |

## 财务、组织与风险

| 部门 | Agent ID | 文件 | 职责 |
|---|---|---|---|
| finance | `finance-financial-analyst` | [financial-analyst.md](../agents/finance/financial-analyst.md) | 财务模型、预测、定价和单位经济 |
| finance | `finance-fundraising` | [fundraising-advisor.md](../agents/finance/fundraising-advisor.md) | 融资、估值、投资者沟通和资金用途 |
| organization | `org-architect` | [org-architect.md](../agents/organization/org-architect.md) | 组织设计、治理和股权结构 |
| organization | `org-talent-planner` | [talent-planner.md](../agents/organization/talent-planner.md) | 招聘、人才、薪酬与文化 |
| risk | `risk-manager` | [risk-manager.md](../agents/risk/risk-manager.md) | 风险、合规、监管和缓释方案 |

## 最终编辑（_director）

| Agent ID | 状态 | 文件 | 职责 |
|---|---|---|---|
| `director-bp` | active | [director-bp.md](../agents/_director/director-bp.md) | 只整合已经通过审核的商业计划产物 |
| `director-startup` | deprecated | [director-startup.md](../agents/_director/director-startup.md) | 兼容旧入口，不参与自动路由；由 `core-orchestrator` 替代 |

## 维护规则

- 新增或移动角色时先修改角色文件，再同步 `capabilities.yaml` 和本页链接。
- 角色职责写在角色 Markdown，不在本索引复制完整提示词。
- 路由规则写在 `routing-rules.yaml`，固定协作顺序写在 `agents/templates/`。
- 不在部门目录新增 README；需要跨角色说明时更新本页。
