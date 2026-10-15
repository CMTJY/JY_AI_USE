# Wiki Memory Agent

Wiki Memory Agent 是一个跨 AI 工具的项目级长期记忆模板。它用根目录 `AGENTS.md` 约束智能体在每轮开始时按索引渐进读取记忆，并在最终答复前判断是否需要保存具有长期价值的信息。

模板只依赖 Markdown、相对链接和常规文件操作，不需要数据库、向量检索、MCP 服务或额外模型 API。

## 适用场景

- 需要让 Codex、Cursor、TRAE 等 AI 工具在多次会话之间保留项目决策、约束和交接状态。
- 希望记忆可人工审查、可通过 Git 追踪，并避免把完整聊天记录写入项目。
- 希望先读取短索引，再按任务加载少量相关主题页，控制上下文与 Token 消耗。

## 项目结构

```text
wiki-memory-agent/
├── README.md
└── template/
    ├── AGENTS.md
    └── memory/
        └── INDEX.md
```

- `template/AGENTS.md`：跨工具记忆协议和安全边界。
- `template/memory/INDEX.md`：最小记忆路由索引；初始不创建空分类目录。

## 接入已有项目

1. 把 `template/AGENTS.md` 的内容合并到目标项目根目录的 `AGENTS.md`。如果目标文件已存在，不要直接覆盖，应保留原有规则并处理冲突。
2. 把 `template/memory/INDEX.md` 复制到目标项目的 `memory/INDEX.md`。如果索引已存在，应合并而不是替换。
3. 确认所用 AI 工具会读取根目录 `AGENTS.md`；不能自动识别时，在该工具的项目规则中明确要求先读取它。
4. 将 `memory/` 纳入项目版本控制，方便审查历史变化；包含密钥、凭据或私密数据的内容不得写入记忆。

PowerShell 示例（仅适用于目标项目尚无同名文件）：

```powershell
New-Item -ItemType Directory -Force -Path '.\memory' | Out-Null
Copy-Item '<wiki-memory-agent>\template\AGENTS.md' '.\AGENTS.md'
Copy-Item '<wiki-memory-agent>\template\memory\INDEX.md' '.\memory\INDEX.md'
```

## 运行逻辑

```text
新用户消息
→ 检查 memory/INDEX.md
→ 读取短索引并匹配当前任务
→ 按需读取少量主题页
→ 完成当前任务
→ 最终答复前执行 ADD / MERGE / SUPERSEDE / NOOP 判断
→ 仅在有持久价值时更新主题页和索引
```

记忆分为 `project`、`decision`、`knowledge`、`workflow`、`handoff` 和 `archive` 六类，目录只在首次出现真实内容时按需创建。

## 重要边界

- 当前用户要求、当前工作区和实际验证结果始终高于历史记忆。
- 不保存聊天转录、过程旁白、完整日志、临时尝试或可轻易从代码重新发现的事实。
- 不保存密码、API 密钥、令牌、凭据、私密资料或不必要的个人信息。
- `AGENTS.md` 是文本协议，不是确定性生命周期 Hook；不同 AI 工具的自动发现和遵循能力可能不同。

## 来源说明

本项目由隔离工作树 `.worktrees/agent-memory-wiki/FDE` 中已验证的运行时文件封装而成。源目录中的设计规范和实施计划属于过程资料，未纳入可分发模板。
