# Visual Tokens

This file defines the compact color contract for inline widgets. Keep the default generation surface small: neutral tokens, one current brand/theme, fixed semantic tokens, and a small set of chart/diagram classes.

## Generation Mode

Assistant emits token CSS in `widget_code`.

Default behavior:
- Use the purple brand theme unless the user explicitly asks for another color theme.
- If the user asks for a blue, teal, green, amber, coral, or pink visual theme, remap only the brand/theme variables.
- Do not expose the full reference palette during normal generation.
- Do not create extra local alias layers such as `--w-*`.
- Do not choose colors by sequence. Color must encode focus, category, status, intensity, or hierarchy.
- Color contract comes before semantic color guessing. Use neutral, brand, and chart-series tokens first; use semantic tokens only for explicit status/risk/health encoding, not because a label happens to say success, failure, warning, blocked, accepted, or rejected.
- Typography, spacing, and radius contracts come before visual improvisation. Use the role tokens in this file even when output is custom and no ready template matches.
- Charts may use colorful brand series for the data marks themselves; cards, metric blocks, and quiet panels stay neutral in every state.
- Under the default purple theme, complex charts may expand only through nearby brand-adjacent hues such as blue or pink. This is chart-series expansion, not a whole-theme switch. Do not switch to random rainbow, high-saturation, or unrelated preset colors just because more categories appear.
- Host theme is exposed as `:root[data-widget-theme="light"]` or `:root[data-widget-theme="dark"]`. Generate light defaults in `:root` and dark overrides in `:root[data-widget-theme="dark"]`.
- Use tokens for every theme-sensitive visual property. SVG `fill`, `stroke`, axis labels, chart bars/lines, legend text, card surfaces, borders, and connectors must reference `var(...)`.
- Do not use hard-coded light-only values such as `#fff`, `#000`, `#333`, or `rgba(0,0,0,...)` inside component selectors or SVG attributes unless defining tokens.
- Custom or fallback widgets follow the same compact runtime contract as ready templates. They must not introduce local palette aliases, extra category colors, tinted card backgrounds, or a second visual theme.

## Fallback Token Gate

When no ready template matches, apply these rules before writing component CSS:

- Start with neutral surfaces, text, borders, spacing, radius, and typography from this file.
- Use `--font-*`, `--text-*`, `--spacer-*`, and `--radius*` tokens for UI styling before adding component-specific CSS.
- Do not invent local font scales, spacing aliases, radius aliases, or one-off literal visual values for fallback widgets.
- Add `--brand` only for the single focal point: selected path, recommendation, highest value, or primary chart mark.
- For custom/fallback charts, assign ordinary peer categories with `--chart-series-1` through `--chart-series-4` before considering any semantic token.
- Add `--accent` only when a secondary category has real meaning distinct from peer comparison.
- Add semantic colors only when the user explicitly asks for status/risk/health encoding or the data field itself is a status/risk variable.
- Put chart color on data marks and legend dots; keep surrounding cards, metric cells, and panels neutral.
- For ordinary peer categories, stop at `--chart-series-1` through `--chart-series-4` plus optional `--chart-other`.
- If the visual needs more colors to work, change the structure: group into Top N + Other, split into small multiples, or use a compact table/list.
- Reject custom output if it requires gradients, rainbow categories, colored card fills, tiny text, non-token font sizes, non-token spacing, custom radius values, or hard-coded light-only component colors to look acceptable.

## Required CSS Placement

Put token definitions at the top of the first `<style>` block, before component styles:

```html
<style>
:root {
  color-scheme: light;
  --surface: #F7F7F8;
  --surface-muted: #EFEFF2;
  --text: #171717;
  --text-muted: #52525B;
  --border: rgba(23, 23, 23, 0.12);

  --brand: #4B3FE3;
  --brand-soft: #F2F7FF;
  --brand-soft-strong: #E5EAFF;
  --brand-text: #1A1759;
  --brand-on: #FFFFFF;
  --chart-series-1: #3C2ECA;
  --chart-series-2: #A9AEFF;
  --chart-series-3: #6F6FFF;
  --chart-series-4: #22A5F7;
  --chart-other: #D3D4DA;

  --accent: #27D2BF;
  --accent-2: #F87454;
  --accent-soft: #EAFBF8;
  --accent-text: #0F766E;
  --success: #1DC981;
  --warning: #EFAA17;
  --danger: #E8463A;

  --radius: 8px;
  --radius-card: 12px;
  --radius-full: 999px;
  --spacer-4: 4px;
  --spacer-8: 8px;
  --spacer-12: 12px;
  --spacer-16: 16px;
  --spacer-20: 20px;
  --spacer-24: 24px;
  --font-sans: "SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-metric: "Inter", "SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-strong: 600;
  --text-caption: 12px/18px;
  --text-body: 14px/20px;
  --text-title: 16px/24px;
  --text-code: 13px/20px;
}

:root[data-widget-theme="dark"] {
  color-scheme: dark;
  --surface: #171717;
  --surface-muted: #262626;
  --text: #E5E5E5;
  --text-muted: #A1A1AA;
  --border: rgba(229, 229, 229, 0.12);

  --brand: #6054F1;
  --brand-soft: #1A1759;
  --brand-soft-strong: #3C2ECA;
  --brand-text: #CFD8FF;
  --chart-series-1: #4B3FE3;
  --accent-2: #F87454;
  --accent-soft: #123F3C;
  --accent-text: #CCFBF1;
}

.widget {
  color: var(--text);
  background: transparent;
  font: var(--weight-regular) var(--text-body) var(--font-sans);
  letter-spacing: 0;
}
</style>
```

Optional standalone fallback: if the widget is likely to be downloaded and opened outside Trae, duplicate the same dark overrides under `@media (prefers-color-scheme: dark)` after the `data-widget-theme` block.

## Runtime Color Contract

Use only these color tokens in normal generated widgets:

Neutral:

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--surface` | `#F7F7F8` | `#171717` | Card, table, chip, and quiet panel surface |
| `--surface-muted` | `#EFEFF2` | `#262626` | Nested or secondary surface |
| `--text` | `#171717` | `#E5E5E5` | Primary text and primary icon color through `currentColor` |
| `--text-muted` | `#52525B` | `#A1A1AA` | Secondary text, axis labels, captions, quiet icons, leader lines |
| `--border` | `rgba(23, 23, 23, 0.12)` | `rgba(229, 229, 229, 0.12)` | Normal dividers and card borders |

Brand/theme:

| Token | Light default | Dark default | Purpose |
|---|---|---|---|
| `--brand` | `#4B3FE3` | `#6054F1` | Primary focus, selected state, primary chart series, recommended path |
| `--brand-soft` | `#F2F7FF` | `#1A1759` | Light brand background for non-card nodes, badges, or chart fills; never a card surface |
| `--brand-soft-strong` | `#E5EAFF` | `#3C2ECA` | Stronger brand background for non-card emphasis only |
| `--brand-text` | `#1A1759` | `#CFD8FF` | Text on brand soft surfaces |
| `--brand-on` | `#FFFFFF` | `#FFFFFF` | Text or icons on solid brand fill |
| `--chart-series-1` | `#3C2ECA` | `#4B3FE3` | First chart source; strongest readable brand step per mode |
| `--chart-series-2` | `#A9AEFF` | `#A9AEFF` | Second chart source; high-contrast light brand step |
| `--chart-series-3` | `#6F6FFF` | `#6F6FFF` | Third chart source; separated mid brand step |
| `--chart-series-4` | `#22A5F7` | `#22A5F7` | Fourth chart source; adjacent hue near the active brand |
| `--chart-other` | `#D3D4DA` | `#D3D4DA` | De-emphasized grouped remainder such as Other, long tail, residual, or low-priority overflow |

Secondary accent:

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--accent` | `#27D2BF` | `#27D2BF` | One genuinely different secondary category; not ordinary A/B/C/D chart sources |
| `--accent-2` | `#F87454` | `#F87454` | Second secondary accent for templates that need a bounded extra category color |
| `--accent-soft` | `#EAFBF8` | `#123F3C` | Secondary category surface |
| `--accent-text` | `#0F766E` | `#CCFBF1` | Text on secondary category surface |

Semantic:

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--success` | `#1DC981` | `#1DC981` | Positive result, healthy status, completion, accepted path |
| `--warning` | `#EFAA17` | `#EFAA17` | Attention, trade-off, cost, risk, pending state |
| `--danger` | `#E8463A` | `#E8463A` | Failure, blocker, rejected option, hot risk |

## Theme Presets

Theme presets are a reference table for remapping the four runtime brand tokens. Semantic colors do not change with the theme.

Use `purple` by default. Use another preset only when the user explicitly asks for that visual theme or provides a brand color; do not infer a non-purple theme from domain wording alone.

| Theme | 50 | 100 | 200 | 500 | 600 | 700 | 900 | Use when |
|---|---|---|---|---|---|---|---|---|
| `purple` default | `#F2F7FF` | `#E5EAFF` | `#A9AEFF` | `#6F6FFF` | `#4B3FE3` | `#3C2ECA` | `#1A1759` | Default brand / TraeWork feel |
| `blue` | `#EFF6FF` | `#DBEAFE` | `#BFDBFE` | `#3B82F6` | `#2563EB` | `#1D4ED8` | `#1E3A8A` |  |
| `teal` | `#ECFDF9` | `#CCFBF1` | `#99F6E4` | `#14B8A6` | `#0D9488` | `#0F766E` | `#134E4A` |  |
| `green` | `#F0FDF4` | `#DCFCE7` | `#BBF7D0` | `#22C55E` | `#16A34A` | `#15803D` | `#14532D` |  |
| `amber` | `#FFFBEB` | `#FEF3C7` | `#FDE68A` | `#F59E0B` | `#D97706` | `#B45309` | `#78350F` |  |
| `coral` | `#FFF1ED` | `#FFDAD1` | `#FFB8A8` | `#FF6B4A` | `#E0523F` | `#B73B2F` | `#6F211B` |  |
| `pink` | `#FDF2F8` | `#FCE7F3` | `#FBCFE8` | `#EC4899` | `#DB2777` | `#BE185D` | `#831843` |  |

Theme mapping:

| Theme column | Runtime token |
|---|---|
| `50` | `--brand-soft` |
| `100` | `--brand-soft-strong` |
| `600` | `--brand` in light mode |
| `900` | `--brand-text` |

Default purple uses a mode-specific dark brand override: `--brand: #6054F1`.

Chart series mapping for same-kind source comparisons:

| Runtime token | Default source |
|---|---|
| `--chart-series-1` | Active theme 700 in light mode; mode-specific primary brand step in dark mode |
| `--chart-series-2` | Active theme 200/500 mix or a clearly lighter readable brand step |
| `--chart-series-3` | Active theme 500 or another separated mid brand step |
| `--chart-series-4` | Adjacent hue medium step near the active brand |
| `--chart-other` | Neutral low-emphasis remainder color, not another primary category |

In dark mode, invert the soft surface mapping and apply explicit mode-specific primary color overrides:

| Source | Runtime token |
|---|---|
| Dark brand override | `--brand` |
| Dark primary chart step | `--chart-series-1` |
| `900` | `--brand-soft` |
| `700` | `--brand-soft-strong` |
| `100` | `--brand-text` |

Remapping template:

```css
:root {
  --brand: <theme-600>;
  --brand-soft: <theme-50>;
  --brand-soft-strong: <theme-100>;
  --brand-text: <theme-900>;
}
:root[data-widget-theme="dark"] {
  --brand: <dark-brand-or-theme-600>;
  --chart-series-1: <dark-primary-series-or-theme-600>;
  --brand-soft: <theme-900>;
  --brand-soft-strong: <theme-700>;
  --brand-text: <theme-100>;
}
```

## Icon Color Usage

Use icons through `currentColor`; set `color` on the button, chip, row, or wrapper.

- Default icons: `color: var(--text-muted)`.
- Quiet or disabled icons: `color: var(--text-muted); opacity: .64`.
- Primary action, selected, or focus icons: `color: var(--brand)`.
- Icons inside solid brand fills: `color: var(--brand-on)`.
- Success, warning, and danger icons: use the matching semantic token.
- Diagram icons or shape indicators follow the diagram class or explicit semantic stroke. Do not add separate icon-specific colors inside diagrams.

## Chart Color Usage

Use the smallest useful series set:

- Primary single series or recommended option: `--chart-series-1` or `--brand`.
- Same-kind source comparisons such as A/B/C/D, channels, models, versions, browsers, regions, teams, or departments use the chart series scale.
- For 2 peer sources, use `--chart-series-1` and `--chart-series-2`; they must be visibly separated, not neighboring mid-tone steps.
- For 3 peer sources, use `--chart-series-1` through `--chart-series-3` so the active brand family remains the majority.
- For 4 peer sources, use `--chart-series-4` as the only nearby hue expansion instead of forcing a fourth barely distinguishable brand shade.
- For complex charts that need more visible contrast, prefer grouping, small multiples, or a table/list before expanding color. Do not add extra peer colors beyond the four chart-series tokens.
- If the active brand is not purple, derive the adjacent hue steps from the user's brand hue neighborhood instead of hardcoding purple/blue.
- Grouped leftovers, long-tail items, residual buckets, or low-priority overflow use `--chart-other`.
- Do not use `--accent`, `--success`, `--warning`, or `--danger` just to distinguish ordinary chart sources.
- Use `--accent` only when the second series is a genuinely different semantic category, not another peer source.
- Use semantic tokens only when status/risk/health is the primary encoded variable or the user explicitly requests that encoding.
- Explicit positive status: `--success`.
- Explicit attention or medium risk status: `--warning`.
- Explicit failure, blocker, or hot risk status: `--danger`.
- Chart grid and axes: `--border`.
- Chart labels and legend: `--text-muted`, with key values in `--text`.

Do not use more than 4 brand chart source colors in one inline widget, plus one optional `--chart-other` bucket. If the data needs more peer categories, group them into Top N + Other, use small multiples, or switch to a table/list. Do not add dark gray fallback categories; gray means lower importance. Keep a visible legend or direct labels, and use the same token for the slice, bar, swatch, and tooltip dot.

The `sankey-chart` 628 sample is a documented template-local exception because it demonstrates a bounded source/outcome flow palette. That exception must not be treated as a generic chart palette. Outside `templates/sankey-chart`, ordinary peer chart sources must not use `--accent`, `--accent-2`, `--success`, `--warning`, or `--danger`.

## Surface Color Usage

Default card, chart panel, metric block, table, and quiet panel backgrounds use `--surface`; nested or secondary card regions use `--surface-muted`. Normal cards use `--border`; focused cards may use `--brand` as the border only.

Rules:
- Put color in the chart body, not the card body. Bars, lines, points, slices, heat cells, legend swatches, and tooltip dots may use `--chart-series-*`, `--brand`, or the documented semantic tokens.
- Allowed card styles are neutral border + neutral/light-gray fill, or brand border + neutral/light-gray fill. Do not pair a brand border with a colored card fill.
- Do not use `--brand-soft`, `--brand-soft-strong`, `--accent-soft`, semantic soft fills, chart-series colors, gradients, or hue-tinted color-mixes as card backgrounds.
- If a card needs to show selection, recommendation, category, or status, use border treatment and text hierarchy first. Keep the card fill neutral.
- Success, warning, and danger cards should use semantic color only for stroke, icon, tag text, or secondary label emphasis. The card fill still stays neutral.
- Dark mode follows the same roles: card surfaces remain neutral, chart marks carry color.

## Diagram Palette

Normal diagrams use only these classes:

- `c-neutral`: structure, containers, inactive nodes, and non-focus steps.
- `c-brand`: primary path, selected node, recommendation, focus, or model/AI concept.
- `c-accent`: one secondary category or comparison path.
- `c-success`: explicit accepted, healthy, complete, or positive status in a status/risk diagram.
- `c-warning`: explicit pending, attention, cost, or medium risk status in a status/risk diagram.
- `c-danger`: explicit failure, blocker, rejected option, or hot state in a status/risk diagram.

Rules:
- Use `c-neutral` plus at most 1-2 meaning colors in a compact diagram.
- Default to `c-brand` for the main story, not a random categorical or semantic color.
- The default posture for flowcharts and architecture diagrams is neutral surfaces + neutral connectors + one visible brand focal point. When peer categories need color, use the chart-series scale before semantic classes.
- Use `c-success`, `c-warning`, or `c-danger` only when the diagram is explicitly about status, health, risk, approval, or failure. Ordinary process labels with words like success/failure/blocked stay neutral, brand, or chart-series unless the user asks for a status view.
- Treat color count as meaning count. If three nodes have three unrelated colors, the diagram is claiming three distinct meanings and needs labels or a legend; otherwise keep them neutral.
- Do not color steps as a rainbow.
- Do not apply diagram classes to connector paths. Use `arr` or `leader` for normal light-gray connectors; reserve `--brand` or `--chart-series-*` for labeled focus/category paths, and semantic strokes only for explicit status/risk paths.
- Default flowchart connector color is tokenized light gray through `--text-muted` or `--border`; avoid arbitrary saturated connector colors.
- Text on brand or accent soft surfaces must use the matching text token. Text on semantic soft surfaces uses `--text`; semantic color itself is reserved for stroke, icon, or secondary label emphasis.
- Exceptions are allowed for state machines, risk maps, or mechanism diagrams when color directly encodes status, temperature, pressure, activity, or another explained variable. In those cases, keep the palette tokenized and add direct labels or a concise legend.

Class CSS template:

```css
.t { fill: var(--text); font: var(--weight-regular) var(--text-body) var(--font-sans); }
.th { fill: var(--text); font: var(--weight-medium) var(--text-body) var(--font-sans); }
.ts { fill: var(--text-muted); font: var(--weight-regular) var(--text-caption) var(--font-sans); }
.arr { stroke: var(--text-muted); stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; fill: none; }
.leader { stroke: var(--text-muted); stroke-width: .5; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 4 4; fill: none; }

g.c-neutral > rect,
g.c-neutral > ellipse,
g.c-neutral > circle,
g.c-neutral > polygon,
rect.c-neutral,
ellipse.c-neutral,
circle.c-neutral,
polygon.c-neutral {
  fill: var(--surface);
  stroke: var(--border);
}

g.c-brand > rect,
g.c-brand > ellipse,
g.c-brand > circle,
g.c-brand > polygon,
rect.c-brand,
ellipse.c-brand,
circle.c-brand,
polygon.c-brand {
  fill: var(--brand-soft);
  stroke: var(--brand);
}

.c-brand > .th,
.c-brand > .t { fill: var(--brand-text); }
.c-brand > .ts { fill: var(--brand); }

g.c-accent > rect,
g.c-accent > ellipse,
g.c-accent > circle,
g.c-accent > polygon,
rect.c-accent,
ellipse.c-accent,
circle.c-accent,
polygon.c-accent {
  fill: var(--accent-soft);
  stroke: var(--accent);
}

.c-accent > .th,
.c-accent > .t { fill: var(--accent-text); }
.c-accent > .ts { fill: var(--accent); }

g.c-success > rect,
g.c-success > ellipse,
g.c-success > circle,
g.c-success > polygon,
rect.c-success,
ellipse.c-success,
circle.c-success,
polygon.c-success {
  fill: color-mix(in srgb, var(--success) 14%, transparent);
  stroke: var(--success);
}

.c-success > .th,
.c-success > .t { fill: var(--text); }
.c-success > .ts { fill: var(--success); }

g.c-warning > rect,
g.c-warning > ellipse,
g.c-warning > circle,
g.c-warning > polygon,
rect.c-warning,
ellipse.c-warning,
circle.c-warning,
polygon.c-warning {
  fill: color-mix(in srgb, var(--warning) 14%, transparent);
  stroke: var(--warning);
}

.c-warning > .th,
.c-warning > .t { fill: var(--text); }
.c-warning > .ts { fill: var(--warning); }

g.c-danger > rect,
g.c-danger > ellipse,
g.c-danger > circle,
g.c-danger > polygon,
rect.c-danger,
ellipse.c-danger,
circle.c-danger,
polygon.c-danger {
  fill: color-mix(in srgb, var(--danger) 14%, transparent);
  stroke: var(--danger);
}

.c-danger > .th,
.c-danger > .t { fill: var(--text); }
.c-danger > .ts { fill: var(--danger); }
```

## Physical Color Scenes

Physical-color scenes are rare exceptions. If a scene depicts materials that should not invert semantically across themes, such as sky, water, grass, skin, metal, fire, or heat, use a small set of explicit colors inside that illustrative SVG only.

Keep text, borders, controls, and UI chrome on the token contract. Do not mix hardcoded material fills with theme-responsive foreground text unless the contrast is explicitly controlled.

## Non-Color Tokens

Use these compact role tokens directly when needed.

Spacing:

| Token | Value | Purpose |
|---|---|---|
| `--spacer-4` | `4px` | Tight internal gap |
| `--spacer-8` | `8px` | Dense control gap |
| `--spacer-12` | `12px` | Input / popover padding |
| `--spacer-16` | `16px` | Compact card padding / grid gutter |
| `--spacer-20` | `20px` | Default card padding |
| `--spacer-24` | `24px` | Group gap |

## Spacing Usage

- Use `--spacer-4` for tight marker/text gaps and compact inline groups.
- Use `--spacer-8` for dense control gaps, legend row gaps, and tooltip internal gaps.
- Use `--spacer-12` for input, popover, badge-row, and compact panel padding.
- Use `--spacer-16` for compact card padding, chart inner gutters, and grid gaps.
- Use `--spacer-20` for default card and chart-panel padding.
- Use `--spacer-24` for separated visual groups or section gaps.
- Do not invent intermediate spacing values such as `6px`, `10px`, `14px`, `18px`, `22px`, or `28px` for visual layout. If the layout feels cramped or loose, choose the nearest spacer token or change the structure.
- SVG coordinates, viewBox dimensions, chart canvas heights, arc radii, bar positions, and data-driven geometry may use literal numeric values. Surrounding UI padding, gaps, text offsets, legend spacing, tooltip spacing, and card layout must use spacer tokens.

Radius:

| Token | Value | Purpose |
|---|---|---|
| `--radius` | `8px` | Default controls, tags, chart labels, compact containers, normal SVG nodes |
| `--radius-card` | `12px` | Cards, grouped metric blocks, chart panels, popovers, large SVG containers |
| `--radius-full` | `999px` | Circles and pills only |

Typography:

| Token | Value | Purpose |
|---|---|---|
| `--font-sans` | `"SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | Default text and titles |
| `--font-metric` | `"Inter", "SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | Numeric emphasis at tokenized text sizes |
| `--font-mono` | `"JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace` | Code, IDs, compact numeric values |
| `--weight-regular` | `400` | Default text |
| `--weight-medium` | `500` | Emphasized text and small titles |
| `--weight-strong` | `600` | Strong metric or primary data label |
| `--text-caption` | `12px/18px` | Captions, legends, axis labels, helper text |
| `--text-body` | `14px/20px` | Base font size; default body text, controls, and normal chart labels |
| `--text-title` | `16px/24px` | Card titles, compact section titles, and the maximum allowed text size |
| `--text-code` | `13px/20px` | Code snippets, IDs, compact numbers |

## Radius Usage

- Use `--radius` for most generated UI and SVG nodes.
- Use `--radius-card` only when the element is a card, chart panel, grouped metric block, or large container.
- Use `--radius-full` only for circles and pills.
- Do not invent intermediate radius values. If a shape feels too sharp or too soft, choose `--radius` or `--radius-card` instead of adding `4px`, `6px`, `10px`, `16px`, or custom values.

## Typography Usage

Use typography as role-based sets:

- Treat `14px` as the baseline font size. The baseline is expressed by `--text-body`.
- Default text uses `font: var(--weight-regular) var(--text-body) var(--font-sans)`.
- Use smaller text only for captions, legends, axis labels, helper text, and secondary table text with `--text-caption`.
- Use larger-than-body text only for card titles, compact section titles, and one primary metric display. `--text-title` is the maximum text size.
- Card titles and compact section titles use `font: var(--weight-medium) var(--text-title) var(--font-sans)`.
- Primary KPI, scorecard, analytics, revenue, usage, and conversion numbers use `font: var(--weight-strong) var(--text-title) var(--font-metric)` with tabular figures.
- Code snippets, IDs, compact numeric values, table numbers, and technical counters use `font: var(--weight-medium) var(--text-code) var(--font-mono)` with tabular figures.
- Do not use ad hoc `font-size`, `line-height`, or font-family values such as `11px`, `13px`, `15px`, `18px`, `22px`, `font-family: Inter`, or `line-height: 1.2` in component CSS. Use the role token that matches the text purpose.
- If content does not fit at the tokenized size, reduce content, wrap labels, move detail into tooltip/table text, split the visual, or answer in Markdown. Do not shrink below `--text-caption` to force a dense widget.

Do not reintroduce old `body-*`, `heading-*`, `code-editor-*`, or `font-family-*` token families unless the skill intentionally expands beyond inline widgets.

## Card Information Hierarchy

Apply this hierarchy to every card, metric block, comparison option, quiet panel, table-cell panel, and supporting card used in multi-chart widgets.

| Role | Required token set | Color role |
|---|---|---|
| Card title / option name | `font: var(--weight-medium) var(--text-title) var(--font-sans)` | `--text` |
| Subtitle / metadata | `font: var(--weight-regular) var(--text-caption) var(--font-sans)` | `--text-muted` |
| Body fact / row value | `font: var(--weight-regular) var(--text-body) var(--font-sans)` | `--text` |
| Row label / helper text | `font: var(--weight-regular) var(--text-caption) var(--font-sans)` | `--text-muted` |
| Compact number / ID / counter | `font: var(--weight-medium) var(--text-code) var(--font-mono)` | `--text` |
| Primary KPI only | `font: var(--weight-strong) var(--text-title) var(--font-metric)` | `--text` or `--brand` only when it is the focal value |
| Badge / tag / legend label | `font: var(--weight-medium) var(--text-caption) var(--font-sans)` | `--text-muted`, `--brand-text`, or an explicit semantic token |

Rules:

- Use `--text-title` for at most one true headline number per card or per supporting metric group. Do not render every numeric value as a headline.
- No text may exceed `--text-title`; if a label needs more emphasis, use position, weight, or a badge instead of a larger font size.
- Supporting metric cards in a combined chart widget must stay subordinate to the primary chart. Use compact rows, bars, or lists before adding large numbers.
- Cards, metric blocks, and quiet panels keep neutral `--surface` or `--surface-muted` fills. Use color on chart marks, borders, badges, icons, or focal text only.
- Null values may show `Unknown`, `N/A`, or be omitted. Do not convert unknown values to zero or make them visually dominant.
- Long labels should be shortened, wrapped, or moved into tooltip/table text. Do not shrink below `--text-caption` or use overflow clipping to hide the problem.
- Mixed metrics with different units should use rows or a compact table. Do not place unrelated KPI numbers side by side as equal visual headlines unless comparing those KPIs is the point.

## Usage Rules

- Start from the default purple theme.
- Switch theme only when the user explicitly requests another visual theme or provides a brand color. Do not infer a non-purple theme from domain wording alone.
- Keep semantic colors fixed across themes.
- Use neutral surfaces for cards, metric blocks, chart panels, tables, and quiet structure; use brand color for chart marks, primary focus, and focused card borders only.
- Use `--chart-series-*` for same-kind chart sources.
- Use `--chart-other` only for one de-emphasized grouped remainder or overflow bucket.
- Use `--accent` only for one genuinely different secondary category after chart-series is not the right encoding.
- Use semantic colors only when status/risk/health is explicitly encoded; do not infer them from ordinary labels, and do not derive semantic soft fills for card backgrounds.
- Do not copy template-local palette exceptions into other templates or generated custom charts.
- Do not invent additional palette variables for a single widget.
- Do not copy the whole theme preset table into `widget_code`; emit only the active runtime token values and classes the widget uses.
- For fallback primitives, treat every extra color as a claim of extra meaning. If that meaning cannot be named in the legend, label, or focal point, remove the color.
