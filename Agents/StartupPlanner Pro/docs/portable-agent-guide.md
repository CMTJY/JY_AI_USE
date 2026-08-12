# 独立 Agent 导出指南

## 导出

```powershell
python "Agents/StartupPlanner Pro/tools/package_agent.py" <agent-id> --output <目标目录>
```

输出包含：

```text
<agent-id>/
├── AGENT.md
├── README.md
├── manifest.yaml
└── skills/        仅该角色自身技能，存在时生成
```

控制角色不是专业交付角色，不能导出。输出目录已存在时工具会停止，避免覆盖用户文件。

## 独立模式

Agent 没有 Task Packet 时自行澄清关键输入、执行、验证和交付；它不能声称其他 Agent、团队审核或真实并行已经发生。

## 升级

不要直接在导出包和团队源文件中同时维护角色。应在 StartupPlanner Pro 中更新角色、运行验证，然后重新导出，通过 `manifest.yaml` 比较版本和来源。

