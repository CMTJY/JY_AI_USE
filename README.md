# AWENAI-TOOL

<p align="center">
  <strong>AI 智能体团队配置方案与技能工具集</strong><br>
  <em>让 AI 按专业流程工作，而不是凭感觉回答。</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/platform-通用-6C5CE7" alt="Platform: Universal">
  <img src="https://img.shields.io/badge/StartupPlanner_Agents-39_active-orange" alt="StartupPlanner Agents: 39 active">
  <img src="https://img.shields.io/badge/StartupPlanner_Skills-100-green" alt="StartupPlanner Skills: 100">
</p>

---

## 项目简介

**AWENAI-TOOL** 是一套通用的 **AI 智能体（Agent）配置库**和 **AI 技能（Skill）工具箱**。智能体日常执行依赖宿主 AI 工具读取 Markdown/YAML，不需要额外模型服务；仓库中的 Python 工具用于离线路由评测、配置验证、Token 预算和独立 Agent 打包。它的核心产物是：

- **智能体规则文件**（`.md` / `.yaml`）：定义 AI 角色的身份、工作流、交付物标准和质检标准
- **技能模块**（`SKILL.md`）：封装可复用的 AI 能力，按方法论执行而非凭直觉回答
- **方法论文档**：指导智能体如何系统化地分析问题、产出可交付的结果

### 核心理念

> **"先检索技能库 → 找最匹配的方法论 → 按流程执行 → 边做边教"**

每个智能体都不是"通用聊天机器人"，而是经过了特定领域方法论武装的**专业角色**。它们手握 `SKILL_INDEX.md` 技能索引，能根据用户意图自动匹配最佳技能并执行。

---

## 项目架构

```
AWENAI-TOOL/
│
├── Agents/                           # 🤖 AI 智能体团队
│   ├── ProjectExpert/                #   全行业 AI 项目专家
│   ├── StartupPlanner Pro/           #   创业规划平台（旗舰）
│   └── E-debbug agent/               #   嵌入式代码修改助手
│
├── Skills/                           # 🧩 AI 技能模块
│   ├── agent-team-builder/           #   通用智能体团队搭建
│   ├── intent-recognition/           #   需求意图识别
│   ├── infra-module-decoupler/       #   嵌入式模块解耦器
│   ├── lark-doc-local-publish/       #   本地 MD → 飞书文档
│   ├── lark-doc-precision/           #   飞书文档精准修改
│   ├── model-up/                     #   多模态代理（文字模型看图）
│   ├── skill-creator/                #   自定义技能创建工厂
│   └── superpowers/                  #   开发工作流超能力系列
│
└── LICENSE                           # MIT License
```

---

## 🤖 Agents — AI 智能体团队

### 1. StartupPlanner Pro（创业规划平台）⭐ 旗舰项目

v3 是一个面向 **Codex、Cursor、TRAE** 的平台无关智能体团队框架：包含 **39 个 active Agent（34 个专业角色 + 5 个内部控制角色）、100 个本地技能、35 条可验证路由**。它既能按任务自动调度，也能把任意专业 Agent 单独打包到其他项目。

```
指挥层  _director/  创业总指挥 · BP总编
战略层  strategy/   OPC战略师 · 战略分析师 · 市场调研员
产品层  product/    产品经理(54 Skills) · 产品总监(6 Skills) · MVP设计师
营销层  marketing/  增长黑客 · 内容创作者 · 私域运营 · 电商运营
财务层  finance/    财务分析师 · 融资顾问
组织层  organization/ 组织架构师 · 人才规划师
风险层  risk/       风险管理师
```

<details>
<summary><b>📋 完整部门说明（点击展开）</b></summary>

| 部门 | 智能体 | 核心能力 |
|------|--------|---------|
| **指挥层** | 创业总指挥、BP总编 | 项目诊断 → 三阶段调度 → 质量门禁 → BP整合输出 |
| **战略层** | OPC战略师 | "7步+1闸"创业验证方法论（假设→反证→情报→访谈→综合分析→原型→GO/NO-GO） |
| | 战略分析师 | PEST分析、商业模式画布、竞争格局 |
| | 市场调研员 | TAM/SAM/SOM测算、用户画像、需求验证 |
| **产品层** | 产品经理 | 封装 [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) 全部 **54 个PM技能** |
| | 产品总监 | 软件MVP/发布/规模化 + 硬件MVP/合规 共6个统筹技能 |
| | MVP设计师 | 最小可行产品设计 |
| **营销层** | 4大分类×多智能体 | 增长黑客、活动策划、内容创作、抖音/小红书运营、私域运营、电商/跨境电商、直播教练 |
| **财务层** | 财务分析师、融资顾问 | 3年财务预测、盈亏平衡、LTV/CAC、融资方案 |
| **组织层** | 组织架构师、人才规划师 | 团队架构、股权设计、招聘策略 |
| **风险层** | 风险管理师 | 六大维度风险识别、评估矩阵、三级退出机制 |
</details>

**v3 渐进调度：**

```
短平台入口 → 领域路由分片 → 原子任务拆解 → 专业 Agent
→ Task Packet → 独立审核/返工 → 结果整合
```

离线回归语料当前为 117 条，总通过率与原子精确路由准确率均为 100%，不必要调用率 0%；实验走真实运行时分片，但仍是确定性规则实验，不代表三个 AI 工具的实机模型表现。完整架构、安装方式、实验边界和复现命令见 [StartupPlanner Pro v3 README](Agents/StartupPlanner%20Pro/README.md)。

> 📂 位置：[Agents/StartupPlanner Pro/](Agents/StartupPlanner%20Pro/)

#### StartupPlanner Pro v3 快速接入

| AI 工具 | 接入文件 | 建议位置 |
|---|---|---|
| Codex | [`adapters/codex/AGENTS.snippet.md`](Agents/StartupPlanner%20Pro/adapters/codex/AGENTS.snippet.md) | 合并到目标项目 `AGENTS.md` |
| Cursor | [`adapters/cursor/startupplanner.mdc`](Agents/StartupPlanner%20Pro/adapters/cursor/startupplanner.mdc) | 复制到 `.cursor/rules/` |
| TRAE | [`adapters/trae/AGENTS.snippet.md`](Agents/StartupPlanner%20Pro/adapters/trae/AGENTS.snippet.md) | 合并到项目 `AGENTS.md`，或使用配套 Skill |

团队模式从 [`core/BOOTSTRAP.md`](Agents/StartupPlanner%20Pro/core/BOOTSTRAP.md) 启动，按“路由索引 → 最多两个领域分片 → 命中 Agent → 1–3 个必要技能”渐进加载。宿主支持原生子 Agent 时执行真实委派；不支持时明确降级为“单 Agent 串行角色模拟”。

单独导出某个专业 Agent：

```powershell
python "Agents/StartupPlanner Pro/tools/package_agent.py" marketing-xiaohongshu-operator --output C:\temp\portable-agents
```

导出包会改写为独立模式，移除团队角色依赖，检查相对链接，并在 `manifest.yaml` 中记录角色文本与全包 Token 估算。完整说明见：

- [架构与渐进加载](Agents/StartupPlanner%20Pro/docs/architecture.md)
- [三平台安装](Agents/StartupPlanner%20Pro/docs/platform-setup.md)
- [路由规则与诊断](Agents/StartupPlanner%20Pro/docs/routing-guide.md)
- [独立 Agent 打包](Agents/StartupPlanner%20Pro/docs/portable-agent-guide.md)
- [实验与限制](Agents/StartupPlanner%20Pro/docs/evaluation-report.md)

---

### 2. ProjectExpert（全行业 AI 项目专家）

覆盖 **软件、游戏、硬件、建筑、金融、制造、医疗、教育** 8 大行业的项目分析智能体团队。

**四阶段工作流程：**

```
需求引导 → 情报检索 → 规划分析 → 降智输出
```

| 阶段 | 部门 | 智能体 |
|------|------|--------|
| 1. 需求引导 | 需求引导部 | 意图探针（逐个问题轮询）+ 项目定位师 |
| 2. 情报检索 | 情报检索部 | 全域侦察兵（6维度检索）+ 知识图谱师 |
| 3. 规划分析 | 规划分析部 | 技术架构师 + 需求规划师 |
| 4. 降智输出 | 降智输出部 | 降智翻译官（30秒版 + 3分钟速读版） |

**交付物：**
- 完整项目分析报告
- 技术栈图谱
- 学习推进计划
- 需求分析文档
- 降智总结（大白话版）

> 📂 位置：[Agents/ProjectExpert/](Agents/ProjectExpert/)

---

### 3. E-debbug Agent（嵌入式代码修改助手）

针对嵌入式开发的代码修改智能体，支持 ESP-IDF / STM32 / RT-Thread / FreeRTOS / Linux 驱动 / Arduino 等多平台。

**核心原则：** 方案先行 → 用户审批 → 可逆可查

> 📂 位置：[Agents/E-debbug agent/](Agents/E-debbug%20agent/)

---

## 🧩 Skills — AI 技能模块

### 通用技能

| 技能 | 描述 | 核心能力 |
|------|------|---------|
| [agent-team-builder](Skills/agent-team-builder/) | 通用智能体团队搭建 | 需求识别 → 框架规划 → 实际搭建 三阶段流程 |
| [intent-recognition](Skills/intent-recognition/) | 需求意图识别 | 逐个问题引导，区分表面需求 vs 真正意图 |
| [model-up](Skills/model-up/) | 多模态代理（图片/音频/视频→文本分析） | OpenAI 兼容接口，多模型自动降级 |
| [skill-creator](Skills/skill-creator/) | 自定义技能工厂 | 新建 Skill / 将对话封装为 Skill |

### 嵌入式专项

| 技能 | 描述 | 核心能力 |
|------|------|---------|
| [infra-module-decoupler](Skills/infra-module-decoupler/) | 嵌入式模块解耦器 | 依赖分析 → 违规识别 → 3种策略（死代码删除/系统API替换/业务归还）→ 逐步执行 |

> 真实案例：成功解耦 ESP-IDF 项目 3 个模块（logger / flash_cache / nvs_storage），清理违规依赖 5 处，总计净减 550 行。

### 飞书集成

| 技能 | 描述 |
|------|------|
| [lark-doc-local-publish](Skills/lark-doc-local-publish/) | 本地 Markdown → 飞书云文档发布，支持标题自动编号 |
| [lark-doc-precision](Skills/lark-doc-precision/) | 飞书文档精准修改——定位目标 block，只改目标，其余不动 |

### 开发超能力系列（Superpowers）

17 个开发工作流技能，覆盖现代软件开发的完整链路：

| 技能 | 用途 |
|------|------|
| brainstorming | 创意激发与设计 |
| writing-plans | 执行计划制定 |
| test-driven-development | 测试驱动开发 |
| executing-plans | 计划执行 |
| subagent-driven-development | 子智能体驱动开发 |
| dispatching-parallel-agents | 并行智能体调度 |
| systematic-debugging | 系统化调试 |
| verification-before-completion | 完成前验证 |
| requesting-code-review | 请求代码审查 |
| receiving-code-review | 接收代码审查 |
| finishing-a-development-branch | 完成开发分支 |
| frontend-design | 前端设计 |
| ui-ux-pro-max | UI/UX 专业版 |
| using-git-worktrees | Git Worktree 使用 |
| using-superpowers | 超能力使用指南 |
| superpowers-bootstrap | 超能力引导启动 |
| writing-skills | 技能编写指南 |

> 📂 位置：[Skills/superpowers/](Skills/superpowers/)

---

## 使用方式

### 前提条件

- 安装支持项目规则或智能体体系的 AI 工具，如 Codex、Cursor、TRAE
- 将本项目克隆到本地
- 仅在运行 StartupPlanner Pro 维护/评测工具时需要 Python 3 与 PyYAML

### 如何调用智能体

**方式一：通过 Agent 入口**

在支持智能体的工具中，使用 `@Agent名称` 调用智能体：

```
@ProjectExpert 我想了解一下 LangChain 这个项目
@StartupPlanner 我想做一个 AI 宠物社交平台
```

**方式二：通过 Skill 调用**

```
Use Skill: agent-team-builder
Use Skill: intent-recognition
```

### 文件格式说明

智能体规则文件采用 **YAML Front Matter + Markdown** 格式，遵循通用约定：

```yaml
---
name: 智能体名称
description: 一句话描述
emoji: 🎯
color: "#FF6B35"
---

# 智能体名称

## 身份与记忆
## 核心使命
## 关键规则
## 工作流程
## 沟通风格
## 成功指标
```

每个智能体配备了 `SKILL_INDEX.md` 技能索引表，运行时自动检索匹配最佳技能并执行。

### StartupPlanner Pro v3 验证命令

从仓库根目录运行：

```powershell
python -m unittest discover -s "Agents/StartupPlanner Pro/tests" -v
python "Agents/StartupPlanner Pro/tools/validate.py"
python "Agents/StartupPlanner Pro/tools/route_eval.py"
python "Agents/StartupPlanner Pro/tools/token_budget.py"
```

当前发布基线：52 项测试通过；117/117 条离线分片路由用例通过；静态验证和 Token 预算均为 0 错误、0 警告。以上是确定性离线验证，不等同于 Codex、Cursor、TRAE 三个平台的实机模型表现。

---

## 技术特点

- **方法论驱动** — 每个智能体背后都有经过实战验证的方法论（OPC 7步+1闸、PM 54 Skills、Mom Test 等）
- **自包含技能库** — 产品经理封装了 deanpeters 开源的全部 54 个 PM 技能，无需联网即可执行
- **多智能体协作** — 创业总指挥编排六大部门协同工作，跨部门数据引用有统一规范
- **质量门禁体系** — 每个阶段均有明确的检查清单和通过标准
- **教学式输出** — 智能体执行任务时同步解释"为什么这样做"（ABC — Always Be Coaching）
- **对话引导式交互** — 逐个问题轮询，降低用户认知负担

---

## 开源技能来源

本项目中的产品经理智能体集成了以下开源项目的技能：

- [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) v0.80 — 54 个 PM 技能 · CC BY-NC-SA 4.0

---

## 许可

[MIT License](LICENSE) © 2026 AWEN

---

## 维护者

- **AWEN Team** — 核心开发与维护

---

*最后更新：2026-08-07*
