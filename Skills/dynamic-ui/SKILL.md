---
name: dynamic-ui
description: "Show visual content inline alongside your text response — diagrams, charts, interactive demos, comparisons. Use only when a compact visual makes the answer clearer. Not for websites, apps, reports, dashboards, or slides."
description_zh: "在文字回答旁边内联展示可视化内容 — 图表、架构图、交互 demo、对比分析。仅当紧凑可视化能让回答更清晰时使用。不用于网站、应用、报告、看板或幻灯片。"
description_ja: "テキスト応答にインラインで視覚コンテンツを表示 — 図表、アーキテクチャ図、インタラクティブデモ、比較。コンパクトな視覚化が回答を明確にする場合のみ使用。Web サイト、アプリ、レポート、ダッシュボード、スライドには使用しない。"
user-invocable: true
disable-model-invocation: false
---

# dynamic-ui — Inline Visualization

## Scope

Use when a compact inline visual makes relationships, magnitudes, choices, or one local interaction clearer — diagrams, charts, interactive demos, comparisons.

Do NOT use for standalone websites, apps, long reports, dashboards, slides, short facts, one-step commands, content that Markdown can scan better, content with no visible focal point, or decorative visuals that do not explain anything.

## File Map

`{{SKILL_DIR}}` is the directory containing this `SKILL.md` file.

```
{{SKILL_DIR}}/
├── SKILL.md              ← Single entrypoint (this file)
├── scenes/               ← Scene guidance (one file per scene)
│   ├── data-visualization.md
│   ├── architecture-and-flow.md
│   ├── comparison-and-decision.md
│   ├── mechanism-explanation.md
│   └── micro-interaction.md
├── tokens/
│   └── visual-tokens.md  ← Full CSS token definitions (read on demand)
└── templates/            ← Material library (reusable primitive examples)
    ├── manifest.json
    └── <template-id>/
        ├── template.md   ← Material description (20-30 lines)
        ├── widget-code.html  ← Complete working example
        └── fixture.json  ← Sample data
```

## Tool Contract

You MUST call `PureShowWidget` to render the visual. Do not pass `mode` unless the runtime requires it; never choose `panel`.

When you decide to render a widget, do the layout/code reasoning silently and call `PureShowWidget` with the final `widget_code` directly. Prefer calling the tool as the next user-visible action. Do not stream planning notes, draft code, partial snippets, final-check lists, or transition phrases about assembling or finalizing the code. Any text around the tool call must be concise and must not describe implementation steps. The widget code itself must appear only inside the tool call.

## Rendering Contract

The rules below are the hard runtime contract. Scene files decide what to draw.

Rules:
- Output order: `<style>` → content HTML/SVG → `<script>` (only when interaction needed).
- No `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`, meta tags, comments, routers, export flows, page shells, or app shells.
- Token definitions at top of `<style>`, before component selectors.
- Emit runtime color tokens inside `widget_code`; do not rely on host app CSS for generated widget readability.
- Theme contract: sandbox sets `:root[data-widget-theme="light"|"dark"]`. Generated CSS must support light defaults and dark overrides with `:root[data-widget-theme="dark"]`; optional `@media (prefers-color-scheme: dark)` may be added only as standalone fallback.
- All theme-sensitive colors must reference CSS tokens: text, axes, borders, surfaces, chart series, connectors, labels, badges. Do not put hard-coded light-only colors in component selectors or SVG attributes.
- Scripts execute after streaming completes. Use one final script block. Load external libs in final `<script>` from allowlisted CDNs only: `cdnjs.cloudflare.com`, `esm.sh`, `cdn.jsdelivr.net`, `unpkg.com`.
- Widget must remain useful if external library fails to load.
- Root element: `data-dynamic-ui-widget` + `data-template="<id>"`. Init via stable selector, set `data-mounted="true"` before binding. Scope all DOM queries to root.
- Do NOT use `document.currentScript`, `previousElementSibling`, sibling traversal, global selectors, inline event handlers, or `position: fixed`.
- Bind local behavior with `addEventListener` or event delegation inside the root. Allowed local behavior: toggle, filter, sort, step, hover, focus, inspect, or simple calculations.
- `window.sendPrompt('...')` only for follow-up questions requiring model reasoning. Not for local UI behavior.
- No nested scrolling. Body text ≥14px, never below 11px.

Chart.js is allowed only as progressive enhancement: load from `https://cdn.jsdelivr.net/npm/chart.js@4`, wrap `<canvas>` in an explicit-height relative container, use `responsive: true` and `maintainAspectRatio: false`, keep a visible fallback before script execution, hide fallback only after chart creation, use widget-scoped HTML tooltip instead of canvas tooltip, clamp tooltip placement within chart bounds, and keep at most two canvases in one widget.

Motion is optional and must clarify state, flow, or interaction. Prefer `transform`, `opacity`, `stroke-dashoffset`, or `animation-play-state`; wrap continuous/decorative motion in `@media (prefers-reduced-motion: no-preference)`; keep chart first-render animation around 120-220ms and hover/active transitions at or below 120ms. Avoid heavy filters, blur, glow, 3D transforms, physics engines, long loops, and layout animations that repeatedly change widget height.

## Visual Design

Core principles:
- **Seamless** — Users shouldn't notice where the APP ends and your widget begins.
- **Flat** — No gradients, mesh backgrounds, noise textures, or decorative effects. Clean flat surfaces.
- **Compact** — Show the essential inline. Explain the rest in text.
- **Separation** — Explanatory text goes in your response; visual evidence goes in the widget.
- **Chart-only** — Chart widgets show the chart, optional short title, and necessary readout aids such as axes, legends, labels, or tooltips. Do not add insight, conclusion, analysis, recommendation, or footer copy inside chart widgets, whether using a ready template or custom fallback.

Token source: Read `{{SKILL_DIR}}/tokens/visual-tokens.md` for full CSS definitions.

Material source: Read `{{SKILL_DIR}}/templates/manifest.json` and the selected `templates/<id>/template.md` before adapting a ready material. Materials are guidance and examples, not rigid fixed layouts.

Fallback rule: Whenever no ready template matches, a custom widget must still choose one compact primitive (`chart-card`, `metric-strip-chart`, `node-flow`, `decision-cards`, `compact-table-visual`, or `explanation-panel`) and follow the same token, surface, density, color-priority, typography, spacing, radius, and focal-point rules as the templates. Custom output must not invent a palette, font scale, spacing scale, or radius value to compensate for missing material coverage. For SVG, flowchart, architecture, framework, or relationship diagrams, fallback is allowed only after a simple coordinate plan proves that nodes, labels, connector tracks, legends, and badges fit without overlap.

**Theme adaptation**: Every widget must be readable in both light and dark host themes. Use light values in `:root`, override only changed tokens in `:root[data-widget-theme="dark"]`, then consume tokens everywhere. Treat `dark-blue` hosts as dark. Standalone exports without `data-widget-theme` must still be readable from light defaults.

**Brand baseline**: Purple is the default. Do not infer a non-purple theme from domain wording. Use another theme only when the user explicitly requests it.

**Color priority**: The token color contract is stronger than semantic color guessing. Start with neutral surfaces/connectors plus `--brand` and `--chart-series-*`; use `--accent` or semantic tokens only when the user explicitly asks for status/risk/health encoding or the data field itself is a status/risk variable. Words such as success, failure, warning, blocked, accepted, or rejected do not automatically justify green/yellow/red in an ordinary chart, flowchart, or framework diagram.

**Token priority**: Typography, spacing, and radius defaults come from `tokens/visual-tokens.md` even when no ready template matches. Use role tokens instead of literal CSS values for text, card padding, gaps, controls, tags, chart labels, legends, tooltips, and compact containers. Literal numbers are allowed for SVG geometry, viewBox coordinates, chart canvas dimensions, and data-driven shape positions, but not for visual defaults that already have tokens.

**Surfaces**: Cards, chart panels, metric blocks, tables use `--surface` (neutral). Nested regions use `--surface-muted`. Never use brand/accent/semantic colors as card fills. Focus shown by border treatment only.

**Chart series**: Same-kind sources in ready and custom charts use `--chart-series-1` through `--chart-series-4`. Overflow/Other uses `--chart-other`. Do not use random rainbow, accent, or semantic colors for ordinary sources. For 4 sources, use only the documented fourth brand-adjacent chart token. For 5+ peer sources, group to Top N + Other, use small multiples, or switch to a table/list. Template-specific color exceptions, such as the 628 Sankey sample, are local to that template and must not be copied into other chart types. Two-source charts need visibly separated steps.

**Diagram classes**: `c-neutral` for structure, `c-brand` for focus/recommendation, `c-accent` for secondary category. For ordinary flowcharts, architecture diagrams, framework maps, and dependency views, prefer neutral + brand or the chart-series scale before semantic classes. Max 1-2 meaning colors per compact diagram. Do not apply diagram classes to connector paths.

**Connectors**: Default neutral `--text-muted` or `--border`. Use `--brand` for the main path and `--chart-series-*` only for explicitly labeled peer paths; use semantic connector colors only when status/risk is the primary encoded variable. Flowchart connectors use gentle curves/rounded L-bends, `stroke-linecap="round"`, `stroke-linejoin="round"`. Use one standard SVG marker primitive for ordinary directed connectors: define a compact marker with `viewBox="0 0 8 8"`, `refX="7"`, `refY="4"`, `markerWidth="8"`, `markerHeight="8"`, `markerUnits="userSpaceOnUse"`, `orient="auto"`, then attach it with `marker-end`; the marker path should be a small triangle such as `M1 1 L7 4 L1 7 Z`. This makes rightward, leftward, upward, diagonal, and curved arrows follow the path direction without scaling into a large wedge. Do not build arrowheads from decorative bracket curves, separate chevrons, oversized polygons, copied right-facing triangles, or filled connector paths. If a hand-drawn triangle is truly needed, its tip must sit on the target end and the stroke must stop at the triangle base.

**Radius**: `--radius` (8px) default, `--radius-card` (12px) for cards, `--radius-full` (999px) for pills/circles. No ad hoc values.

**Spacing**: Use `--spacer-4`, `--spacer-8`, `--spacer-12`, `--spacer-16`, `--spacer-20`, and `--spacer-24` for UI gaps, padding, legend rows, tooltip spacing, and card layout. No ad hoc spacing values such as `10px`, `14px`, `18px`, `22px`, or `28px` for visual layout.

**Typography**: `--text-caption` (12px/18px), `--text-code` (13px/20px), `--text-body` (14px/20px baseline), and `--text-title` (16px/24px maximum). No ad hoc font sizing or line-height values.

**Card information hierarchy**: Every card, metric block, comparison option, table cell panel, and supporting card in a multi-chart widget must use the same role hierarchy. Card titles use `font: var(--weight-medium) var(--text-title) var(--font-sans)` and must not become hero headings. Descriptions, row values, and normal facts use `--text-body`; metadata, row labels, captions, legends, tags, and badges use `--text-caption`; code-like values and compact numeric counters use `--text-code`. A true primary KPI may use `font: var(--weight-strong) var(--text-title) var(--font-metric)`, but no text may exceed `--text-title`. If many values compete, convert them to rows, compact bars, a table/list, or response text instead of increasing font sizes or adding colored cards.

## Content Rules

Every widget needs ONE visible focal point (recommendation, critical path, bottleneck, highest value, phase boundary, risk marker). Make it obvious with position, label, or one accent color. Do not rely on color alone.

For data-visualization widgets, encode the focal point through chart structure, mark emphasis, direct labels, axis/legend design, or tooltip behavior. Keep conclusions and analysis in the surrounding text response, not in the generated UI.

Copy density:
- Node labels: 2-5 words. Card titles: 6-10 words. Subtitles: ≤5 words.
- Connector labels: 1-3 words; omit obvious labels.
- Use sentence case. Code style only for identifiers/commands/paths.

Complexity budget:
- 1 focal point, 2-5 main nodes, 2-4 options/KPI/series, 1 interaction concept.
- Horizontal tier: max 4 boxes. For 5+ items: group, wrap, or split.
- Max 2 non-neutral meaning colors without legend.
- If content exceeds budget: summarize visually, put details in response text.
- When appropriate, combine multiple chart types in one widget to increase information density.
- For custom SVG diagrams, keep to <=6 ungrouped nodes and <=8 connectors unless a ready material explicitly supports more. Larger structures must be grouped, split into panels, represented as a compact table/list, or answered in Markdown.

Structure primitives (prefer these over decoration):
- Cards with dividers, tags for status, simple SVG connectors, bars/dots/labels for data, tables for 3+ dimensions.

Avoid: hero sections, slide navigation, export buttons, kanban/editor controls, decorative illustration, nested cards inside cards.

Data honesty: Label estimates as estimates. Round displayed values consistently. Show units next to numbers. Avoid precise-looking values when the source is approximate. Never render maps — use bar/table/matrix by region instead.

## Streaming-First Planning

Widget code streams in order, so do not rely on after-the-fact acceptance checklists. Internally decide the layout and runtime plan before emitting the first `<style>`, SVG, HTML, or `<script>`.

This planning is silent. Never expose intermediate reasoning, pseudo-code, JavaScript snippets, TODOs, or validation notes in the user-visible response.

Silent pre-output constraints:
- Choose the scene, focal point, primary visual, and any supporting visual blocks.
- Reserve layout slots for titles, legends, labels, controls, tooltips, and fallback content.
- For any SVG diagram, reserve a coordinate plan before output: canvas, safe area, rows/columns, node boxes, connector tracks, label capsules, legend, and any badges.
- Top-level widget cards should fill the available chat width. Do not cap the outer card width with fixed max-width or `width: min(...)`.
- If a visual primitive should stay compact, constrain and center the inner chart/SVG area instead of shrinking the whole card.
- Non-cartesian charts and polar visuals such as radar, pie, donut, gauges, and compact mechanism sketches must not stretch to the full card width. The outer card or background fills `width: 100%`; the inner chart shell uses an explicit max inline size, stays centered, and preserves its natural aspect ratio.
- Keep all text, labels, badges, legends, controls, and connector paths inside the planned layout bounds.
- Every bordered or filled container must have internal padding. Do not let text, icons, legend keys, or pills touch the container border.
- If the content cannot fit cleanly, simplify, group, split into panels, or move details to the text response. Do not solve fit problems by shrinking below token font sizes, squeezing gaps below the geometry rules, clipping overflow, hiding collisions with background fills, or moving text outside the visible bounds.
- For interactive or Chart.js widgets, prepare fallback content and final script initialization as part of the silent pre-output plan.
- Prefer fewer, stronger constraints over long post-generation checklists.

## SVG Fundamentals

Apply these geometry rules whenever the output contains SVG, connectors, flowcharts, architecture diagrams, structural diagrams, or mechanism illustrations.

ViewBox: Prefer `viewBox="0 0 720 H"`, `width="100%"`, `height="auto"`. Safe area ≥40 design units or 6% of the viewBox width, whichever is larger. Set `H` from the lowest visible shape, text baseline, or connector plus bottom padding. Do not use negative coordinates, shrink the viewBox to hide long labels, leave large unexplained blank space below the final element, or depend on clipping/background fills to hide invalid geometry.

Text sizing: 14px for labels (est. 8px/char Latin), 12px for metadata (7px/char). Node width ≥ max(title_chars×8, subtitle_chars×7) + 24px padding. Chinese labels: keep shorter than available width. Increase width estimates by 30-50% for code-like strings, math symbols, long identifiers, or mixed scripts. Use `<tspan>` only for deliberate short two-line labels, not paragraph text.

Hard fit gate: Do not emit custom SVG until every visible text label, node, connector label, legend item, badge, and container has an estimated bounding box. If any required box cannot fit with the spacing rules below, reduce content before drawing: shorten labels, group nodes, split the diagram, convert relationships to a table/list, or answer in Markdown. Do not use lower font sizes, transparent overlaps, `overflow: hidden`, clipping masks, or background rectangles as a substitute for a valid layout.

Connectors: `fill="none"` on every path/polyline. Route around unrelated nodes. Max 2 connector styles per diagram. Connectors may be horizontal/vertical, diagonal, gently curved, or rounded L-bends; choose the route that best expresses the relationship with the fewest crossings. For directed connectors, prefer the standard marker pattern from the connector rule above and put the marker on the same path that represents the line. Do not draw the line and arrowhead as unrelated shapes. If a connector is bidirectional, draw two separate paths with two markers rather than one path plus detached arrowheads. Never use decorative curly braces, double curves, or bracket-like strokes as arrowheads.

Layout before drawing:
- First create a simple coordinate plan: canvas, safe area, rows/columns, node bounding boxes, connector tracks, and label slots.
- Check every same-row pair: `left.x + left.width + gap <= right.x`; use gap ≥32 for unrelated nodes and ≥60 for flow steps.
- Check every same-column pair: `top.y + top.height + gap <= bottom.y`; use gap ≥28 for stacked nodes and ≥56 when a connector label sits between them.
- Place structural containers before inner nodes. Each boundary must contain its children with visible padding and must not collide with the title, legend, external inputs, or downstream outputs.
- Do not force every connector into an orthogonal path. Use diagonal arrows for cross-lane messages or state transitions when endpoints naturally sit on different rows.
- Floating labels are high-risk. Put connector labels in small rounded capsules with surface fill, or move the wording into source/target node subtitles or response text.
- Connector label capsules must not sit on top of a line. Reserve a label slot above/below the connector with ≥8 units from the stroke.
- Do not rely on a white/background rectangle to hide collisions. If a line would pass through text or a node, reroute the line or move the label.
- Legends, phase chips, and explanatory inset panels must sit in reserved slots outside the main connector corridors. If the legend would overlap the diagram, move it below the SVG or remove non-essential styles.
- Use pill shapes for start/end nodes. Make decision or special shapes softened: rounded-corner paths, capsules, ellipses, or subtly rounded custom paths.
- For structural diagrams, keep at least 20px padding between container edges and inner regions, use no more than 2-3 nesting levels, and put external inputs/outputs outside the container.

SVG silent pre-output constraints:
- Compute viewBox height from lowest element + padding.
- All content inside x=0..720.
- Every text label fits with padding.
- For any `<rect>`/panel/card/legend with text inside, size the container from its content and leave clear internal padding on every side. If content feels cramped or touches the border, enlarge the container, wrap/reflow the content, move it, or simplify it.
- No two node/label bounding boxes overlap, including badges, step numbers, legends, and connector labels.
- No connector passes through unrelated nodes.
- No connector passes through text or label capsules.
- Flowchart nodes use rounded rectangles; diamonds/polygons use softened paths.
- If any of the above cannot be satisfied, do not output the SVG. Simplify the visual or use text/table fallback instead.

## Scene Router

Read the user's intent, then route to ONE scene file:

| User intent | Scene file |
|---|---|
| Numeric trends, magnitude comparison, composition/proportion, distribution, flow intensity, heatmap density | `scenes/data-visualization.md` |
| Module relationships, dependency maps, flowcharts, state transitions, call chains, schedules | `scenes/architecture-and-flow.md` |
| Option comparison, tech selection, risk summary, decision matrix | `scenes/comparison-and-decision.md` |
| Explain principles, physical/abstract mechanisms, causal chains | `scenes/mechanism-explanation.md` |
| Local interaction demos, parameter switching, state changes | `scenes/micro-interaction.md` |

Workflow:
These workflow steps are internal. Do not narrate them to the user.

1. Determine if a compact visual is clearer than Markdown. If not, skip.
2. Route to the matching scene file.
3. Use material selection as a supplement to scene routing: parse the expression intent, check `templates/manifest.json`, confirm the candidate is `ready`, then read the selected `templates/<id>/template.md` before borrowing from `widget-code.html` or `fixture.json`.
4. Prefer the material that explains the focal point with the least transformation. Prefer scene composition over a near-miss material, and prefer prose when there is no visible focal point.
5. Follow the selected scene's mandatory workflow before writing widget code.
6. Materials are reusable examples, not rigid templates. Borrow layout, CSS, interaction, tooltip, fallback, and token patterns as needed; mix materials only when each block answers a distinct question.
7. When adapting chart materials, preserve the chart color contract from `tokens/visual-tokens.md`. Do not transfer a template-local palette exception into another chart, and do not let semantic label names override the chart-series order.
8. Generate custom output only when no ready material matches, every plausible material has an avoid rule or data boundary conflict, the scene is mechanism-driven and needs a unique diagram, combining primitives is clearer than forcing one complete material, or Markdown is clearer than a widget. "Handwritten is faster", "This is simple", "A custom SVG is lighter", and "I already know how to draw this" are invalid reasons.
9. If no ready material matches, do not freehand from scratch. Choose one fallback primitive (`chart-card`, `metric-strip-chart`, `node-flow`, `decision-cards`, `compact-table-visual`, or `explanation-panel`) and keep the output on the same token/color/typography/spacing/radius/layout contract.
10. Fallback uses neutral structure first, then brand/chart-series color for focus or peer categories. Semantic colors are exceptions for explicit status/risk encodings only. Keep broad card/panel backgrounds neutral, put color in marks/borders/tags/focal paths/icons/labels, and do not combine fallback primitives unless each block answers a distinct named question.
11. If fallback cannot fit without tiny text, nested scrolling, clipped labels, overlapping connectors, connector lines through text, hidden overflow, more than four peer chart colors plus Other, or more than two unrelated visual blocks, answer in Markdown or ask for narrower scope instead.

Ready material intent map: `line-trend` trend; `bar-chart-multiple` grouped comparison; `scatter-chart` correlation/outliers; `gantt-chart` schedule/critical path; `funnel-bar-chart` conversion drop-off; `sankey-chart` weighted staged flow; `heatmap-chart` density; `pie-donut-text` composition with total; `bar-stacked-legend` stacked contribution; `pie-chart-label-list` labeled part-to-whole; `radar-chart-legend` and `radar-chart-lines-only` profile comparison; `comparison-cards` option trade-offs; `sequence-diagram` ordered calls; `tree-flow` hierarchy; `architecture-elements` architecture primitives.

Template file contract: every ready material folder contains `template.md`, `widget-code.html`, and `fixture.json`. `template.md` documents reusable primitives, use/avoid boundaries, data shape, visual/interaction limits, boundary cases, assumptions, and acceptance checks. `widget-code.html` starts with `<style>`, includes content after styles, ends with `<script>` only when needed, avoids page shells, uses `data-dynamic-ui-widget` and `data-template="<template-id>"`, uses a stable root selector, and preserves fallback plus required interaction behavior. `fixture.json` is small, realistic, matches the data shape, and avoids private or production data.

When adding, renaming, removing, or changing a material routing intent, update `templates/<template-id>/template.md`, `widget-code.html`, `fixture.json`, `templates/manifest.json`, relevant `scenes/*.md`, and `templates/README.md` together. Do not mark a material `ready` if the folder or required files are missing. Fallback primitives are not template ids and must not appear in `templates/manifest.json`.
