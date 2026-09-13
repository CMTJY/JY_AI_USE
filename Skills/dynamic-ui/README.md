# dynamic-ui

这是从 TRAE 当前全局内置 Skill 独立保存的 `dynamic-ui` 快照，适合在对话中生成紧凑的图表、程序框图、模块关系图、调用链、机制示意图和嵌入式接线示意图。

## 目录结构

```text
dynamic-ui/
├── SKILL.md              # 唯一运行入口
├── scenes/               # 五类可视化场景规则
├── tokens/               # 视觉设计令牌
├── templates/            # 16 个可复用图表/图示模板
├── README.md             # 独立使用说明
└── UPSTREAM_NOTICE.md     # 来源与许可边界
```

原始快照包含 57 个文件：

- `scenes/architecture-and-flow.md`：程序框图、架构图、模块关系、调用链和状态流。
- `scenes/mechanism-explanation.md`：物理结构、工作原理和嵌入式连接机制示意。
- `templates/architecture-elements/`：模块、边界、外部设备和连接器样式。
- `templates/tree-flow/`：层级和依赖关系图。
- `templates/sequence-diagram/`：协议、时序和调用过程。
- `tokens/visual-tokens.md`：明暗主题、颜色、字号、间距和圆角规则。

## 使用方式

在能够发现项目 Skill 的 AI 工具中，让工具读取 `Skills/dynamic-ui/SKILL.md`，然后提出明确的可视化请求，例如：

```text
使用 dynamic-ui 绘制 ESP32、DHT22、OLED 和 5V 电源的接线图，标出 GPIO、I²C 地址、电源电压和共地关系。
```

```text
使用 dynamic-ui 绘制固件启动、自检、联网、数据采集、异常恢复的程序框图。
```

## 运行依赖

原始 Skill 要求宿主提供 TRAE 的 `PureShowWidget` 工具，并以 inline widget 形式渲染 `widget_code`。仅复制文件不会让其他 AI 工具自动获得该渲染器：

- 在 TRAE 中：可按原始 `SKILL.md` 调用 `PureShowWidget`。
- 在 Codex、Cursor 或其他工具中：可以读取其构图规则和模板，但若没有兼容的 widget 渲染工具，需要由宿主另行提供 HTML/SVG 预览能力。

`SKILL.md` 的 frontmatter 还包含 `description_zh`、`description_ja`、`user-invocable` 和 `disable-model-invocation` 等 TRAE 扩展字段。严格只接受通用 Agent Skills 字段的校验器可能因此报告不兼容；为保持 TRAE 原版行为，本快照不删除这些字段。

## 快照信息

- 来源：本机 TRAE CN 全局内置 Skill `builtin/global/skills/dynamic-ui`
- 快照日期：2026-09-13
- 上游文件：57 个，580,872 字节
- 上游内容：原样复制，未与旧版 `TRAE-dynamic-ui` 合并

来源与许可说明见 [UPSTREAM_NOTICE.md](UPSTREAM_NOTICE.md)。
