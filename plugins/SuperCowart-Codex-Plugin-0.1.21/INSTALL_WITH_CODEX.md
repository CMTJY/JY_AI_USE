# Install SuperCowart with Codex

This folder is a self-contained local Codex marketplace named `supercowart-portable`.

## Give This Folder to Codex

Attach or provide the absolute path to this entire folder, then send Codex the text from `INSTALL_PROMPT.txt`.

Codex should perform these steps:

1. Treat this folder as the package root and inspect:

   - `.agents/plugins/marketplace.json`
   - `plugins/supercowart/.codex-plugin/plugin.json`
   - `plugins/supercowart/package.json`

2. Confirm Node.js `20.19.0` or newer and npm are available.

3. Validate the clean plugin directory:

   ```text
   plugins/supercowart
   ```

   If the `plugin-creator` skill is available, run its `validate_plugin.py` against that directory.

4. From `plugins/supercowart`, run:

   ```bash
   npm ci
   npm run quality
   ```

5. Register this package root as a non-default local marketplace if it is not already registered:

   ```bash
   codex plugin marketplace add "<absolute-package-root>"
   ```

6. Install or refresh the plugin:

   ```bash
   codex plugin add supercowart@supercowart-portable
   ```

7. Confirm that SuperCowart exposes at least:

   - `render_cowart_canvas_widget`
   - `edit_cowart_canvas`
   - `get_cowart_canvas_state`
   - `insert_cowart_html_draft`
   - `insert_cowart_image`

8. Start a new Codex task so the new skills and MCP schema are loaded.

## First Test

In the new task, open a writable project and ask:

```text
请使用 SuperCowart 原生组件打开当前项目画布，不要启动 localhost。
然后使用 edit_cowart_canvas 创建两个矩形和一条连接线。
```

The canvas should open as a native widget and save project data under the project's `canvas/` directory.

## Package Safety

The package intentionally excludes:

- `.git/`
- `node_modules/`
- `dist/`
- user canvas data
- logs and temporary files
- personal email, website, and development-machine paths

Dependencies and the native widget build are recreated during installation.
