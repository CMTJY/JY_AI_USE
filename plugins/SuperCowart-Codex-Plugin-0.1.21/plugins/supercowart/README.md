# SuperCowart

SuperCowart 是一个面向 Codex 的原生无限画布插件，基于 tldraw。它可以在 Codex 中直接打开项目画布，并将数据保存到用户当前项目的 `canvas/` 目录。

## 主要能力

- 使用原生 Codex widget 打开无限画布，不需要 localhost 服务。
- 通过 `edit_cowart_canvas` 让 AI 创建矩形、椭圆、菱形、文本、frame、流程图连接线和 AI Slides frame。
- 生成图片并放入 AI 图片 holder。
- 生成单文件 HTML，并嵌入 AI HTML holder 或 AI Slides。
- 根据画布标注生成修改后的图片或 Slides。
- 每个项目独立保存页面、选择状态、视图状态与本地资源。

## 环境要求

- Codex Desktop 或支持 Codex 插件与 MCP widget 的 Codex 环境。
- Node.js `20.19.0` 或更高版本。
- npm。

首次启动时，如果插件目录没有 `node_modules/`，SuperCowart MCP 会自动执行 `npm install`。随后会自动构建 CSP 兼容的原生 widget。

## 安装

本目录是便携包中的实际插件目录。请从便携包根目录阅读 `INSTALL_WITH_CODEX.md`，并让 Codex 注册随包提供的本地 marketplace。

安装完成后请新建一个 Codex 任务，再让 Codex：

```text
请使用 SuperCowart 原生组件打开当前项目画布，不要启动 localhost。
```

## 验证

```bash
npm ci
npm run quality
```

`quality` 会执行语法检查、生产构建和 MCP 端到端探针。探针会在临时目录中创建流程图、AI Slides frame，并验证 HTML 页面可写入该 frame。

## 项目数据

SuperCowart 不会把用户画布保存进插件目录。每个用户项目的数据位于：

```text
canvas/pages/<page-id>/cowart-canvas.json
canvas/pages/<page-id>/assets/
canvas/cowart-selection.json
canvas/cowart-view-state.json
```

## 隐私

本便携包不包含 Git 历史、开发机路径、用户画布、日志、依赖缓存、构建缓存、个人邮箱或个人网站信息。

## 许可证

MIT。SuperCowart 使用 tldraw 作为画布基础能力。
