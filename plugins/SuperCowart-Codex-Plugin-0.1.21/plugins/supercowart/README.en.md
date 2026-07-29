# SuperCowart

SuperCowart is a native infinite-canvas plugin for Codex, powered by tldraw. It opens a project-backed canvas directly inside Codex and stores data under the active user's project `canvas/` directory.

## Capabilities

- Open an infinite canvas through a native Codex widget without localhost.
- Let AI create rectangles, ellipses, diamonds, text, frames, flowchart connectors, and AI Slides frames through `edit_cowart_canvas`.
- Generate images into AI image holders.
- Generate standalone HTML and embed it in AI HTML holders or AI Slides.
- Revise images or Slides from canvas annotations.
- Keep pages, selection state, view state, and local assets isolated per project.

## Requirements

- Codex Desktop, or a Codex environment that supports plugins and MCP widgets.
- Node.js `20.19.0` or newer.
- npm.

If `node_modules/` is absent, the SuperCowart MCP automatically runs `npm install` on first launch and then builds its CSP-compatible native widget.

## Installation

This directory is the actual plugin inside the portable package. Read `INSTALL_WITH_CODEX.md` from the package root and ask Codex to register the bundled local marketplace.

After installation, start a new Codex task and ask:

```text
Open the current project's canvas with the native SuperCowart widget. Do not start localhost.
```

## Verification

```bash
npm ci
npm run quality
```

The quality command runs syntax checks, a production build, and an end-to-end MCP probe. The probe creates a flowchart and AI Slides frame in a temporary directory and verifies that an HTML page can be inserted into that frame.

## Project Data

SuperCowart never stores user canvases in the plugin directory. Each user project stores its data at:

```text
canvas/pages/<page-id>/cowart-canvas.json
canvas/pages/<page-id>/assets/
canvas/cowart-selection.json
canvas/cowart-view-state.json
```

## Privacy

This portable package contains no Git history, development-machine paths, user canvases, logs, dependency caches, build caches, personal email addresses, or personal website information.

## License

MIT. SuperCowart uses tldraw as its canvas foundation.
