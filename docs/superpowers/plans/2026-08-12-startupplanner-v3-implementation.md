# StartupPlanner Pro v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 StartupPlanner Pro 升级为支持 Codex、Cursor、TRAE、准确团队路由、单 Agent 独立导出和可重复评测的 v3 通用框架。

**Architecture:** 保留 Markdown/YAML 作为运行时事实源，新增轻量 Python 标准库工具负责静态验证、离线路由评测、Token 预算和独立 Agent 打包。平台适配器只引导宿主读取统一 Bootstrap，不复制角色或路由逻辑；角色正文继续位于 `agents/`，通过统一 v3 frontmatter 同时支持团队模式和独立模式。

**Tech Stack:** Markdown、YAML 3.0 schema、Python 3.11+、PyYAML 6.x、`unittest`、Codex `AGENTS.md`、Cursor MDC、TRAE `.agents/skills`。

## Global Constraints

- 不要求普通使用者运行 Python 才能使用团队；Python 工具仅用于维护、验证和打包。
- 不要求最终用户配置额外模型 API。
- 角色正文是业务行为唯一事实源，适配器不得复制角色、路由或工作流正文。
- 平台入口目标不超过 1,500 estimated tokens；Bootstrap 与路由阶段累计目标不超过 4,000 estimated tokens。
- 普通单 Agent 任务启动累计目标不超过 6,000 estimated tokens；单次加载 1–3 个技能；默认候选不超过 5 个。
- 无原生子 Agent 能力时明确降级为单 Agent 串行角色模拟。
- 所有 active 专业 Agent 至少具有可达路由、3 个正例和 2 个反例。
- 不推送、部署、合并或修改外部平台状态。

---

### Task 1: v3 Registry, Schema and Core Protocol

**Files:**
- Create: `Agents/StartupPlanner Pro/registry/taxonomy.yaml`
- Create: `Agents/StartupPlanner Pro/registry/routes.yaml`
- Create: `Agents/StartupPlanner Pro/registry/workflows.yaml`
- Create: `Agents/StartupPlanner Pro/core/BOOTSTRAP.md`
- Create: `Agents/StartupPlanner Pro/core/routing.md`
- Create: `Agents/StartupPlanner Pro/core/orchestration.md`
- Create: `Agents/StartupPlanner Pro/core/task-packet.md`
- Create: `Agents/StartupPlanner Pro/core/artifact-envelope.md`
- Create: `Agents/StartupPlanner Pro/core/quality-gates.md`
- Test: `Agents/StartupPlanner Pro/tests/test_registry.py`

**Interfaces:**
- Consumes: v2 `agents/config/capabilities.yaml`, `agents/config/routing-rules.yaml`, existing role IDs.
- Produces: `taxonomy.yaml` canonical enums; `routes.yaml` v3 route records; `workflows.yaml` workflow index; concise platform-independent runtime protocols.

- [ ] Write registry tests asserting schema version 3.0, required taxonomy sections, every route target exists, all previously unreachable specialists have routes, and broad `从0到1` is not a startup trigger by itself.
- [ ] Run `python -m unittest discover -s "Agents/StartupPlanner Pro/tests" -p "test_registry.py" -v`; expect missing v3 files.
- [ ] Add canonical domains, task types, channels, lifecycle stages, artifacts and weighted scoring fields.
- [ ] Add precise routes for all technology, research, strategy, product, marketing, finance, organization, risk and BP roles, including positive signals, negative signals and preconditions.
- [ ] Add concise Bootstrap and split core protocols that mandate progressive loading, compound decomposition and explainable route decisions.
- [ ] Re-run registry tests; expect PASS.
- [ ] Commit `feat(startupplanner): add v3 registry and core protocol`.

### Task 2: Agent Contract Migration and Generated Registry

**Files:**
- Create: `Agents/StartupPlanner Pro/tools/migrate_agents.py`
- Create: `Agents/StartupPlanner Pro/tools/generate_registry.py`
- Create: `Agents/StartupPlanner Pro/registry/agent-overrides.yaml`
- Create: `Agents/StartupPlanner Pro/registry/generated-agents.yaml`
- Modify: all role Markdown files under `Agents/StartupPlanner Pro/agents/`, excluding `skills/` and `templates/`
- Test: `Agents/StartupPlanner Pro/tests/test_agent_contracts.py`

**Interfaces:**
- Consumes: v2 capabilities, role frontmatter, `taxonomy.yaml`, explicit overrides for task types/channels/boundaries.
- Produces: normalized v3 frontmatter and generated compact routing catalog.

- [ ] Write tests requiring `schema_version`, `version`, `visibility`, `portable`, `domains`, `task_types`, `lifecycle_stages`, `when_to_use`, `do_not_use_when`, `required_inputs`, `optional_inputs`, `handoff_targets`, and valid reviewer rules.
- [ ] Run the contract test; expect failures on v2 frontmatter.
- [ ] Implement deterministic migration using exact agent-ID overrides; preserve role body and existing fields.
- [ ] Mark core controls internal/system-only/non-portable; mark deprecated role inactive from routing; mark professional roles specialist/portable.
- [ ] Generate compact `generated-agents.yaml` from role frontmatter and fail on broken handoffs or duplicates.
- [ ] Run migration once, generate registry, and re-run tests; expect PASS.
- [ ] Commit `refactor(startupplanner): migrate agents to portable v3 contracts`.

### Task 3: Deterministic Router and Routing Eval Corpus

**Files:**
- Create: `Agents/StartupPlanner Pro/tools/routing.py`
- Create: `Agents/StartupPlanner Pro/tools/route_eval.py`
- Create: `Agents/StartupPlanner Pro/evals/routing-cases.yaml`
- Create: `Agents/StartupPlanner Pro/evals/regression-baseline.yaml`
- Test: `Agents/StartupPlanner Pro/tests/test_routing.py`

**Interfaces:**
- Produces: `extract_intent(text) -> dict`, `decompose_request(text) -> list[dict]`, `rank_agents(intent, catalog) -> list[dict]`, `route_request(text) -> dict`, and CLI evaluation summary.
- Route result fields: `tasks`, each containing `task_id`, `selected`, `confidence`, `matched`, `fallbacks`, `rejected`, `clarification_required`, and `clarification_question`.

- [ ] Write failing regression tests for 小红书从0到1、抖音、剪辑、私域、Amazon/Shopify、直播、LinkedIn、产品发布就绪、架构+后端、PRD+MVP、代码审查+QA and BP direction gate.
- [ ] Run routing tests; expect import/file failures.
- [ ] Implement normalization, multilingual signal matching, negative signals, compound action detection, lifecycle extraction, hard filters and weighted ranking.
- [ ] Ensure `从0到1` alone maps to lifecycle launch and only triggers direction discovery with business/startup evidence.
- [ ] Build at least 80 declarative routing cases with expected and forbidden Agent IDs, dependencies and clarification flags.
- [ ] Implement eval CLI and write `regression-baseline.yaml` from actual results only when all hard safety cases pass.
- [ ] Run unit tests and complete corpus; target ≥90% atomic accuracy, ≤5% miss rate, ≤10% unnecessary calls, ≤2% direction false positives, zero BP gate misses.
- [ ] Commit `feat(startupplanner): add explainable router and routing evals`.

### Task 4: Dynamic Capability-Slot Workflows

**Files:**
- Create: `Agents/StartupPlanner Pro/workflows/business-plan.yaml`
- Create: `Agents/StartupPlanner Pro/workflows/product-development.yaml`
- Create: `Agents/StartupPlanner Pro/workflows/software-delivery.yaml`
- Create: `Agents/StartupPlanner Pro/workflows/marketing-campaign.yaml`
- Create: `Agents/StartupPlanner Pro/workflows/channel-operation.yaml`
- Create: `Agents/StartupPlanner Pro/workflows/research-project.yaml`
- Test: `Agents/StartupPlanner Pro/tests/test_workflows.py`

**Interfaces:**
- Consumes: taxonomy and generated Agent catalog.
- Produces: DAGs whose professional tasks use `assignment.required`, `assignment.conditional`, `assignment.fallback`, `assignment.selection`; fixed IDs allowed only for control and reviewer duties.

- [ ] Write tests for DAG acyclicity, unique producers, valid capability slots, valid fallbacks, independent reviewers and channel specialization.
- [ ] Run workflow tests; expect missing v3 workflows.
- [ ] Migrate six workflows, preserving direction gates and technical quality chains.
- [ ] Add channel conditional slots for Xiaohongshu, Douyin, private domain, domestic ecommerce, cross-border ecommerce, social B2B, livestream and editing.
- [ ] Run workflow tests; expect PASS.
- [ ] Commit `refactor(startupplanner): use capability slots in v3 workflows`.

### Task 5: Validation and Token Budget Tooling

**Files:**
- Create: `Agents/StartupPlanner Pro/tools/common.py`
- Create: `Agents/StartupPlanner Pro/tools/validate.py`
- Create: `Agents/StartupPlanner Pro/tools/token_budget.py`
- Test: `Agents/StartupPlanner Pro/tests/test_validation.py`

**Interfaces:**
- `validate.py --json` emits `{status, errors, warnings, checks}` and exits 0 only without errors.
- `token_budget.py --json` emits per-layer `{files, chars, estimated_tokens_low, estimated_tokens_high, budget, status}`.

- [ ] Write failing tests for broken ID, unreachable Agent, invalid handoff, workflow cycle, duplicate producer, copied adapter logic and hard Token violations.
- [ ] Run validation tests; expect failures.
- [ ] Implement shared YAML/frontmatter/path helpers and all static checks from the design.
- [ ] Implement conservative character-based Token estimates and hard/soft budgets.
- [ ] Run full validator and budget report; resolve every error and document any warning.
- [ ] Commit `test(startupplanner): add static validation and token budgets`.

### Task 6: Portable Agent Packaging

**Files:**
- Create: `Agents/StartupPlanner Pro/tools/package_agent.py`
- Create: `Agents/StartupPlanner Pro/adapters/portable/BOOTSTRAP.md`
- Test: `Agents/StartupPlanner Pro/tests/test_package_agent.py`

**Interfaces:**
- CLI: `python tools/package_agent.py <agent-id> --output <dir>`.
- Output: `<agent-id>/AGENT.md`, `README.md`, `manifest.yaml`, and only direct local `skills/` dependencies.

- [ ] Write failing tests for a specialist export, core-role rejection, link integrity, manifest provenance, absence of unrelated roles and token report.
- [ ] Run packaging tests; expect missing implementation.
- [ ] Implement safe output validation, deterministic copying, standalone Bootstrap injection, manifest generation and relative-link checks.
- [ ] Export `marketing-xiaohongshu-operator` into a temporary test directory and verify the package without leaving generated artifacts in Git.
- [ ] Run packaging tests; expect PASS.
- [ ] Commit `feat(startupplanner): add portable agent packaging`.

### Task 7: Codex, Cursor and TRAE Thin Adapters

**Files:**
- Create: `Agents/StartupPlanner Pro/adapters/codex/AGENTS.snippet.md`
- Create: `Agents/StartupPlanner Pro/adapters/cursor/startupplanner.mdc`
- Create: `Agents/StartupPlanner Pro/adapters/cursor/startupplanner-command.md`
- Create: `Agents/StartupPlanner Pro/adapters/trae/AGENTS.snippet.md`
- Create: `Agents/StartupPlanner Pro/adapters/trae/startupplanner-bootstrap/SKILL.md`
- Test: `Agents/StartupPlanner Pro/tests/test_adapters.py`

**Interfaces:**
- Every adapter points to `Agents/StartupPlanner Pro/core/BOOTSTRAP.md` and describes the platform capability map.
- No adapter may contain copied role bodies, route tables or workflows.

- [ ] Write tests for required files, canonical Bootstrap reference, size limits, forbidden copied headings and platform fallback disclosure.
- [ ] Run adapter tests; expect missing files.
- [ ] Add concise Codex root snippet, Cursor MDC/command and TRAE nested rule/skill bootstrap.
- [ ] Run adapter tests and Token budget checks; expect PASS.
- [ ] Commit `feat(startupplanner): add Codex Cursor and TRAE adapters`.

### Task 8: Entry Point, Documentation and Evaluation Report

**Files:**
- Modify: `Agents/StartupPlanner Pro/AGENTS.md`
- Modify: `Agents/StartupPlanner Pro/README.md`
- Modify: `Agents/StartupPlanner Pro/docs/departments.md`
- Create: `Agents/StartupPlanner Pro/docs/architecture.md`
- Create: `Agents/StartupPlanner Pro/docs/routing-guide.md`
- Create: `Agents/StartupPlanner Pro/docs/platform-setup.md`
- Create: `Agents/StartupPlanner Pro/docs/portable-agent-guide.md`
- Create: `Agents/StartupPlanner Pro/docs/evaluation-report.md`
- Modify: `Agents/StartupPlanner Pro/docs/README.md`
- Test: `Agents/StartupPlanner Pro/tests/test_docs.py`

**Interfaces:**
- README is the user-facing team overview and experiment summary.
- `evaluation-report.md` records exact commands, corpus counts, pass rates, Token report, platform verification status and known limitations.

- [ ] Write documentation tests requiring current v3 paths, three platforms, team/standalone modes, reproducible commands and no false claim of runtime behavior.
- [ ] Run docs tests; expect failures.
- [ ] Replace the oversized root protocol with a concise Bootstrap entry while retaining authorization and degraded-mode safeguards.
- [ ] Rewrite README with architecture, quick starts, role boundary matrix, Token loading model, route-debug guide and evaluation summary.
- [ ] Add the five focused guides and update the docs index and department reachability table.
- [ ] Generate the evaluation report only from fresh validator, routing eval, unit-test and Token-budget output.
- [ ] Run docs tests; expect PASS.
- [ ] Commit `docs(startupplanner): document v3 team and evaluation results`.

### Task 9: Full Verification and Release Baseline

**Files:**
- Modify if required: files found inconsistent by verification.
- Update: `Agents/StartupPlanner Pro/evals/regression-baseline.yaml`
- Update: `Agents/StartupPlanner Pro/docs/evaluation-report.md`

**Interfaces:**
- Final verification is reproducible from repository root with Python and PyYAML only.

- [ ] Run `python -m unittest discover -s "Agents/StartupPlanner Pro/tests" -v` and require zero failures.
- [ ] Run `python "Agents/StartupPlanner Pro/tools/validate.py"` and require zero errors.
- [ ] Run `python "Agents/StartupPlanner Pro/tools/route_eval.py"` and verify all hard targets.
- [ ] Run `python "Agents/StartupPlanner Pro/tools/token_budget.py"` and require zero hard budget errors.
- [ ] Package one marketing and one technical Agent into a temporary directory, validate both, then remove the temporary directory.
- [ ] Inspect `git diff --check`, `git status`, and the complete diff for accidental generated artifacts or unrelated changes.
- [ ] Record exact final metrics in `evaluation-report.md` and re-run all verification commands.
- [ ] Commit `chore(startupplanner): establish v3 verified baseline`.

