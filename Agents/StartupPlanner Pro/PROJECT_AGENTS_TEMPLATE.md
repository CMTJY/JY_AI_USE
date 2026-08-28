# StartupPlanner Pro 新项目 AGENTS 初始化模板

> 本文件是一份交给 AI 执行的项目接入指令，不是当前仓库或目标项目最终使用的 `AGENTS.md`。
> 使用前由人工创建并打开目标项目文件夹；AI 不负责创建、移动或重命名项目根目录。

## 目标

在人工已经创建并作为当前工作区打开的项目文件夹中，根据用户需求完成两项工作：

1. 在当前项目根目录生成一份针对该项目的 `AGENTS.md`。
2. 从 GitHub 克隆最新版 StartupPlanner Pro，并让项目 `AGENTS.md` 能够按需调用该团队执行任务。

完成后的默认结构如下：

```text
<人工创建的项目根目录>/
├── AGENTS.md
└── startupplanner-pro/
    ├── .git/
    └── Agents/
        └── StartupPlanner Pro/
            ├── AGENTS.md
            ├── core/
            ├── registry/
            ├── agents/
            ├── workflows/
            └── adapters/
```

`startupplanner-pro/` 是 `AWENAI-TOOL` 仓库的独立 sparse clone，用于保留 Git 来源和后续更新能力。不要把它误认为当前业务项目的源码目录。

除非用户另有明确要求，本初始化只生成或安全合并根目录 `AGENTS.md`，并安装 StartupPlanner Pro；不要生成业务代码、安装业务依赖、初始化外层 Git、提交、推送、部署或调用会产生外部副作用的服务。

## 执行原则

- 将用户当前对话中的明确需求、附件和约束视为项目事实；本模板只定义初始化流程。
- 当前工作区根目录就是人工创建好的目标项目目录。不得在其父目录或其他位置再创建一个项目文件夹。
- 开始前输出当前项目根目录的绝对路径；若当前工作区并非用户预期目录，先停止并请用户切换或确认。
- 先检查当前文件和 Git 状态，保留已有内容，不覆盖、移动、删除或重置用户文件。
- 缺少会实质改变项目级 `AGENTS.md` 的关键信息时，先提出数量最少的问题；不要重复询问已能从上下文或现有文件可靠确定的信息。
- 不得猜测技术栈、开发命令、测试命令、部署方式、业务规则、权限或成功指标。
- 所有新增文本文件使用 UTF-8；不得写入密码、令牌、API Key、私钥或真实敏感数据。
- 外部网络、Git 和文件操作必须限制在本次初始化目标内；遇到冲突或不确定来源时停止，不使用强制覆盖、`reset --hard` 或删除操作。

## 第一步：确认当前目录与项目需求

读取当前对话、用户附件、现有项目文件及适用的仓库规则，提取：

- 项目名称、核心目标、主要用户和当前阶段。
- 已确认的技术栈、运行环境、平台限制和版本要求。
- 已存在或明确规划的关键目录。
- 已确认的安装、开发、构建、格式化、检查和测试命令。
- 编码规范、业务边界、安全要求和完成标准。
- AI 可以自主执行的操作，以及必须先得到用户确认的操作。

创建 `AGENTS.md` 前至少需要知道项目名称和核心目标。人工已经创建好的当前工作区路径视为安装位置，不再询问保存位置；但必须先展示解析出的绝对路径。若项目名称或核心目标无法可靠确定，先询问用户。

当前目录可以是空目录，也可以包含用户已有文件。以下情况必须先停止并说明：

- 当前路径不存在、不可写或不是预期项目根目录。
- 现有 `AGENTS.md` 与本次目标冲突，无法安全合并。
- `startupplanner-pro/` 已存在，但不是预期的 Git 仓库。
- 继续操作会覆盖或破坏用户文件。

## 第二步：安装或更新 StartupPlanner Pro

### 固定来源与安装位置

- GitHub 仓库：`https://github.com/CMTJY/AWENAI-TOOL.git`
- 分支：`main`
- 当前项目内的克隆目录：`startupplanner-pro/`
- 团队根目录：`startupplanner-pro/Agents/StartupPlanner Pro/`
- 启动协议：`startupplanner-pro/Agents/StartupPlanner Pro/core/BOOTSTRAP.md`

Git 不能直接克隆仓库中的单个子目录，因此默认使用 sparse clone，仅检出 StartupPlanner Pro，同时保留独立 `.git` 目录。

### 首次安装

确认当前项目中不存在 `startupplanner-pro/` 后，在当前项目根目录执行：

```bash
git clone --depth 1 --filter=blob:none --sparse --branch main --single-branch https://github.com/CMTJY/AWENAI-TOOL.git "startupplanner-pro"
git -C "startupplanner-pro" sparse-checkout set "Agents/StartupPlanner Pro"
```

若本机 Git 不支持 sparse checkout，说明限制并征求用户同意后，才可退回完整单分支克隆：

```bash
git clone --depth 1 --branch main --single-branch https://github.com/CMTJY/AWENAI-TOOL.git "startupplanner-pro"
```

### 已存在时更新

若 `startupplanner-pro/` 已存在，先只读检查：

```bash
git -C "startupplanner-pro" remote get-url origin
git -C "startupplanner-pro" branch --show-current
git -C "startupplanner-pro" status --short
```

只有同时满足以下条件时才更新：

- `origin` 指向 `CMTJY/AWENAI-TOOL`；
- 当前分支为 `main`；
- 工作区没有会被更新覆盖的本地修改。

满足条件后执行：

```bash
git -C "startupplanner-pro" pull --ff-only origin main
git -C "startupplanner-pro" sparse-checkout set "Agents/StartupPlanner Pro"
```

若来源、分支或本地修改不符合条件，不得重置、切分支、清理或覆盖；向用户报告实际状态并等待决定。

### 安装失败处理

如果 Git 不可用、网络失败、仓库无权限、目标目录冲突或检出不完整：

1. 保留用户原有文件。
2. 不创建一个声称已接入团队但引用路径不存在的 `AGENTS.md`。
3. 报告失败命令、简要错误和可重试建议。
4. 不擅自改用非官方镜像、压缩包或未知来源。

## 第三步：生成或安全合并项目级 `AGENTS.md`

### 文件处理

- 根目录没有 `AGENTS.md`：创建一份针对当前项目的成品。
- 已有 `AGENTS.md`：先读取并保留现有项目规则，再把 StartupPlanner Pro 接入规则合并到合适位置。
- 现有规则与本模板冲突：指出具体冲突并请求用户决定，不直接覆盖。
- 不要把本初始化模板原样复制成项目 `AGENTS.md`。

### 项目内容要求

根据实际信息选择以下章节；没有可靠内容的部分应省略或明确写为尚未确定，不得虚构命令和路径：

1. `# AGENTS.md`
2. `## 项目概览`：项目名称、目标用户、核心目标、当前阶段和交付边界。
3. `## 项目结构`：已有关键路径及用途；把 `startupplanner-pro/` 标记为外部团队框架克隆，而非业务源码。
4. `## 环境与命令`：只写已确认且可执行的安装、开发、构建、检查和测试命令。
5. `## 开发规范`：语言、格式、类型、错误处理、日志、依赖与文档规则。
6. `## 工作流程`：范围控制、工作区保护、实施步骤和风险相匹配的验证。
7. `## StartupPlanner Pro 协作`：使用下面规定的团队入口与执行规则。
8. `## 测试与完成标准`：可执行验证、未执行项披露和验收要求。
9. `## 安全与权限边界`：敏感信息、外部副作用和高风险操作限制。
10. `## 沟通与交付`：结果、关键文件、验证证据、实际角色和剩余风险。
11. `## Git 约定`：仅保留用户已经确认的外层项目 Git 工作流；不得把嵌套框架仓库当作业务代码修改或提交。

项目根 `AGENTS.md` 通常控制在约 200 行以内，记录跨任务长期有效的事实和规则，不记录一次性聊天内容。

### 必须写入的 StartupPlanner Pro 协作规则

项目 `AGENTS.md` 必须使用当前项目根目录的相对路径写入以下等价规则，文字可根据项目调整，但不得改变含义：

```markdown
## StartupPlanner Pro 协作

- 团队框架位于 `startupplanner-pro/Agents/StartupPlanner Pro/`；它是独立 Git 克隆，不是本项目业务源码。
- 当用户明确要求使用 StartupPlanner Pro，或任务需要创业、调研、战略、产品、营销、技术、财务、组织、风险等跨领域协作时，先读取 `startupplanner-pro/Agents/StartupPlanner Pro/AGENTS.md`，再读取 `startupplanner-pro/Agents/StartupPlanner Pro/core/BOOTSTRAP.md`。
- 按 Bootstrap 渐进加载 `registry/route-index.yaml`、最多两个领域分片、命中 Agent 和 1–3 个必要 Skill；禁止启动时读取全部角色或全部技能。
- 复合请求先拆成有明确依赖和验收标准的原子任务，再为每个任务选择一个权威生产者。
- 宿主支持原生子 Agent 时按 Task Packet 真实委派；不支持时必须标记“单 Agent 串行角色模拟”。
- 关键产物遵守 Artifact Envelope 和独立质量门禁；reviewer 不得同时充当原产物生产者。
- 不得伪造联网研究、测试、部署、并行委派、外部操作或独立审核。
- 未经用户明确要求，不修改 `startupplanner-pro/` 内的框架文件，不自动更新、提交或推送该嵌套仓库。
- 最终交付说明实际调用的 Agent、加载的 Skill、验证证据以及真实委派或降级状态。
```

项目的具体业务规则、文件范围和验证命令应写在该章节之外。不要把 StartupPlanner Pro 的全部路由、角色正文或 Skill 复制进项目 `AGENTS.md`。

## 第四步：验证接入结果

完成后必须逐项检查：

### 当前项目

- 没有创建、移动或重命名项目根目录。
- 根目录 `AGENTS.md` 存在、文件名大小写正确，并能按 UTF-8 读取。
- `AGENTS.md` 与用户需求和已有项目事实一致，不含 `TODO`、未填写占位符、虚构命令或敏感信息。
- 若原先已有 `AGENTS.md`，其无冲突规则得到保留。

### StartupPlanner Pro

执行并检查：

```bash
git -C "startupplanner-pro" remote get-url origin
git -C "startupplanner-pro" branch --show-current
git -C "startupplanner-pro" rev-parse HEAD
git -C "startupplanner-pro" status --short
```

同时确认以下文件真实存在：

```text
startupplanner-pro/Agents/StartupPlanner Pro/AGENTS.md
startupplanner-pro/Agents/StartupPlanner Pro/core/BOOTSTRAP.md
startupplanner-pro/Agents/StartupPlanner Pro/registry/route-index.yaml
```

### 引用与边界

- 项目 `AGENTS.md` 中的团队路径与实际检出路径完全一致。
- 项目 `AGENTS.md` 明确要求渐进加载，不会启动时全量读取角色和 Skill。
- 项目 `AGENTS.md` 明确披露真实委派或串行降级状态。
- 没有初始化外层 Git、生成业务代码、安装业务依赖、提交、推送或部署，除非用户另外授权。

任何检查失败时，先修正并重新验证；无法安全修正时停止扩展操作并报告阻塞。

## 第五步：交付汇报

向用户简洁说明：

- 当前项目根目录的绝对路径。
- 新建或合并后的 `AGENTS.md` 绝对路径。
- StartupPlanner Pro 的安装路径、远程地址、分支和当前 commit。
- `AGENTS.md` 中写入的项目规则与团队调用入口。
- 已执行的验证及结果。
- 尚未确定的技术栈、命令、测试方式或其他剩余风险。

若初始化被阻塞，只报告已确认事实、阻塞原因和需要用户决定的事项，不得声称工程框架已经完成。
