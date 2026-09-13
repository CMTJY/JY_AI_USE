# Data Visualization

Shared contracts: apply `SKILL.md`, this scene file, `templates/manifest.json`, selected `templates/<id>/template.md`, and `tokens/visual-tokens.md`.

## When to enter this scene

The user's intent involves **expressing numerical relationships** of any of the following types:

- Trends (time-series changes, growth/decay)
- Comparisons (grouped contrasts, rankings)
- Composition (proportions, stacked breakdown)
- Distribution (scatter, density)
- Correlation (multi-dimensional profiles, radar)
- Flow (directional paths, traffic distribution)
- Intensity (heatmaps, density matrices)
- Funnel (conversion rates, stage attrition)

Typical trigger words: trend chart, bar chart, pie chart, funnel chart, heatmap, comparison chart, visualize data, chart, plot.

## When to reject

Do NOT generate a visualization in the following cases — reply with Markdown text instead:

- Data points <= 2 with no comparative dimension (a single sentence suffices)
- User is asking for a single value (e.g., "what is xx")
- Data lacks a clear quantitative source and relies entirely on guesswork
- User explicitly requests plain text/table output

## Mandatory generation workflow

This workflow is mandatory after routing into this scene. Do not hand-write a chart, SVG, or HTML fragment until the material audit below is complete.

1. Confirm that an inline visual is clearer than Markdown.
2. Identify the primary data relationship from the user's verb and evidence need: trend, grouped comparison, composition, distribution, correlation, flow magnitude, intensity, funnel, or profile. Also identify whether the user is asking a second evidence question, such as growth source, segment difference, drop-off reason, outlier list, stage total, or priority rationale.
3. Check `templates/manifest.json` for implemented materials where `scene` is `data-visualization` and `status` is `ready`.
4. Shortlist up to three candidate materials from the selection matrix below.
5. Reject a candidate only for a concrete reason: its avoid rule applies, the data shape is outside its boundary, the needed interaction is unsupported, the material is not ready in `manifest.json`, or Markdown is clearer.
6. If one ready material matches the primary relationship, read `templates/<template-id>/template.md`, then adapt from its `widget-code.html` and `fixture.json`. Preserve the material's fallback, tooltip, hover, legend, and root-selector contract unless the selected template explicitly allows variation.
7. If the prompt contains two complementary evidence questions, compose them inside one `PureShowWidget` call instead of emitting separate widgets one after another. Use one primary material first, then add at most two supporting visuals, and name the question each block answers.
8. Generate a custom chart only after every plausible ready material has been rejected for a concrete reason.
9. Before custom chart output, choose `chart-card`, `metric-strip-chart`, or `compact-table-visual`, and keep the same neutral-surface, chart-series color, typography, spacing, radius, legend, fallback, and focal-point contract. Missing a ready template does not allow a new palette, font scale, spacing scale, or radius value.

Invalid reasons for skipping a ready material:

- "Handwritten is faster."
- "This is simple."
- "A custom SVG is lighter."
- "I already know how to draw this."

## Material selection matrix

Choose by intent, not by loose chart keywords.

| Data relationship / Intent | Reference material | Use when | Avoid when |
|---|---|---|---|
| Trend over time | `line-trend` | Continuous change across ordered time points needs slope, inflection, or multi-series comparison | Only one current value matters, or categories are unordered |
| Grouped magnitude comparison | `bar-chart-multiple` | Exactly two peer series need side-by-side comparison across the same categories | Trend shape, stacked contribution, exact distribution, or three-plus peer series is the main story |
| Stacked part-to-whole | `bar-stacked-legend` | Parts contribute to each category total and both total and composition matter | Direct side-by-side comparison matters more than totals |
| Composition with center metric | `pie-donut-text` | Category share wraps around one meaningful total or headline percentage | Exact ranking, negative values, long labels, or more than five categories are required |
| Part-to-whole label list | `pie-chart-label-list` | A small category set needs slice labels plus a compact side label list | Exact ranking, long labels, center totals, or more than five categories are required |
| Correlation / scatter | `scatter-chart` | Two numeric measures need correlation, clustering, outlier, or optional bubble-size comparison | Trend over time, exact category ranking, date/string scales, or thousands of points are required |
| Multi-dimensional profile | `radar-chart-legend` | Two peer sources need filled shape comparison across the same small dimension set | Exact value ranking, long labels, or trend over time is the main story |
| Minimal profile outline | `radar-chart-lines-only` | Two peer sources need no-fill outline comparison across the same small dimension set | Filled radar areas, exact ranking, long labels, or trend over time is the main story |
| Intensity / density | `heatmap-chart` | Values should be scanned by row/column density, calendar bins, or contribution intensity | Exact ranking, continuous trend shape, or multiple peer sources are the main story |
| Funnel / conversion | `funnel-bar-chart` | Ordered stages need drop-off and baseline conversion context | Stages are independent categories, negative values matter, or a decorative funnel body is required |
| Flow / direction | `sankey-chart` | Weighted movement between staged nodes needs path magnitude and node/link inspection | Exact ranking, cyclic graphs, bidirectional edges, or dense many-to-many networks are required |

## Generation principles

### Chart.js loading and initialization

1. Load via UMD: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>`, placed before the final script at the bottom of the widget
2. Canvas must be wrapped in a container with **explicit height** and `position: relative`
3. Chart instantiation config must include:
   ```js
   responsive: true,
   maintainAspectRatio: false
   ```
4. Default height: `clamp(220px, 32vw, 360px)`; maximum height 600px
5. Each widget may contain at most **2 Chart.js canvases**. A third supporting visual may be HTML/SVG only (metric strip, compact bars, mini table, legend matrix), not another canvas.

### Visible fallback

- Before `<script>` executes, retain a visible HTML/SVG fallback (e.g., a simple data table, static SVG, or compact data list)
- Hide the fallback only after the chart is successfully created (`fallbackEl.style.display = 'none'`)

### Tooltip

- Disable Chart.js built-in canvas tooltip: `plugins.tooltip.enabled = false`
- Use an `external` handler to render an HTML tooltip (Shadcn-like styling)
- Tooltip DOM must reside inside the widget root; placement is constrained within chart bounds

### Animation

- Initial render animation: 120–220ms
- Hover transitions: <=120ms

### Color palette

- Series colors use `--chart-series-1` through `--chart-series-4` in order
- Beyond 4 series or an "other" category, use `--chart-other`
- Same-kind sources use the brand chart-series scale. Four sources may use `--chart-series-4` as the only brand-adjacent expansion. Five or more peer sources must be grouped into Top N + `Other`, split into small multiples, or moved to a table/list.
- Custom charts follow the same chart-series order as ready templates. Do not create local palette arrays, extra CSS color variables, or hard-coded category colors.
- Do not use `--accent`, `--accent-2`, `--success`, `--warning`, or `--danger` for ordinary peer series. These tokens require explicit status/risk/health encoding requested by the user or present as the primary data field.
- Category labels such as success, failure, warning, blocked, accepted, or rejected do not automatically make a normal comparison chart semantic. Keep them on `--chart-series-*` unless the chart is explicitly a status/risk view.
- Two-series charts must ensure sufficient visual separation between colors

### Root selector

Initialize using a stable root selector:
```js
document.querySelector('[data-dynamic-ui-widget][data-template="..."]:not([data-mounted])')
```

### Chart silent pre-output constraints

- The canvas container must have explicit height and `position: relative`.
- Chart.js config must set `responsive: true` and `maintainAspectRatio: false`.
- Cartesian charts may use the available horizontal space, but polar/non-cartesian charts such as radar, pie, and donut must use a bounded centered chart shell. Their surrounding card or panel may be `width: 100%`; the chart geometry itself must not be scaled to fill the full card.
- Keep a visible fallback until the chart is successfully created.
- Use HTML external tooltip, not the canvas built-in tooltip.
- Use CSS variables `--chart-series-*` for series colors; do not hardcode chart colors.
- Keep Chart.js canvas count <= 2 and total height <= 600px.

## Composition guidelines

Chart widgets should stay chart-only: include the chart body, optional short title, and necessary readout aids such as axes, legends, labels, controls, or tooltips. Do not place insight, conclusion, recommendation, or analysis text above or below the chart; put that wording in the assistant's surrounding response.

1. **Prefer a single chart**: If one material can fully express the user's intent, use that material's layout + interaction pattern directly.
2. **Use one widget with multiple visual blocks when one chart would hide a second question**:
   - Trend + breakdown: overall change over time plus category contribution
   - Trend + peer driver: trend by city/product/source plus the metric that explains growth quality
   - Ranking + distribution: top/bottom comparison plus spread/outliers
   - Funnel + segment mix: conversion loss plus which source/product/user group drives it
   - Correlation + summary: scatter relationship plus marginal ranking or metric cards
   - Flow + magnitude: Sankey path plus stage totals or top contributors
   - Heatmap + staffing/top slots: density grid plus a compact ranked list or staffing recommendation
3. **Do not combine charts just for variety**. Use multiple charts only when each chart answers a distinct, named question.
4. **Multi-chart budget**: 2-3 visual blocks total inside the same widget. Use one primary chart and 1-2 supporting visuals. At most 2 Chart.js canvases; the third block must be HTML/SVG.
5. **Layout pattern**:
   - Header: optional short non-analytical title only
   - Default chart layout: give each large chart its own full-width row. Prefer stacked chart rows over side-by-side large chart blocks.
   - Desktop/wide card: use a two-column layout only for one large primary chart plus compact support such as metric cards, a ranked list, mini bars, or a small SVG. Do not place two large charts side by side.
   - Single-column card: use full-width primary chart plus a compact supporting row below when the second visual is small
   - Supporting chart(s): 30-40% visual weight, right column or bottom row only when they are compact enough to avoid crowding
   - Three-block layouts: do not rely on auto-wrapped 2+1 rows. Use one full-width primary chart followed by one aligned supporting row, or stack all blocks vertically.
   - Alignment: all visual blocks must share the same grid, gutters, top alignment, and chart-area width rules. Do not create staggered, masonry, or unaligned chart panels.
   - Supporting metric cards, ranked lists, and mini bars follow the card information hierarchy from `tokens/visual-tokens.md`: neutral fills, tokenized titles/body/captions, and at most one `--text-title` numeric headline across the supporting group unless KPI comparison is the primary question.
   - Mobile/narrow layout: stack primary first, then supporting visuals
6. **Recommended combinations**:
   - `line-trend` + `bar-stacked-legend` for trend with contribution
   - `bar-chart-multiple` + `pie-donut-text` for ranking with share
   - `funnel-bar-chart` + compact segment bars for conversion diagnosis
   - `scatter-chart` + metric cards / mini ranking for relationship + extremes
   - `heatmap-chart` + line or bar summary for intensity + trend/top rows
7. **Do not emit sequential chart cards for one analytical question**. If both visuals share the same title or dataset, combine them into one widget card with shared header, shared legend when possible, and coordinated spacing.
8. **No analysis copy in UI**: Do not add supporting insight text above or below the chart. Use chart marks, labels, axes, legend, and tooltip behavior for visual evidence; put max values, inflection points, and interpretation in the response text.
9. **Legend placement**: Embed the legend inline when data series <= 3; place it in a separate bottom or right-side area when > 3
10. **Number formatting**: Use abbreviations for large numbers (1.2K, 3.4M); percentages retain one decimal place

## Data and runtime edge cases

- Empty data: do not render an empty chart. Show Markdown or a visible empty-state fallback with the missing requirement.
- Null / missing values: keep gaps visible for time series; do not silently convert null to zero unless zero is semantically correct. Label unknown categories as `Unknown` only when the source implies an unknown bucket.
- Negative values: use bar or line forms that support negative ranges; do not route negative values to pie, donut, funnel, or stacked share charts.
- Too many categories: reduce to Top N + `Other`, use small multiples, or switch to a compact table/list. Do not create rainbow palettes or unreadable legends.
- Long labels: abbreviate, wrap, rotate only when the template supports it, or move exact labels into tooltip/table text.
- Dense points: aggregate, sample deterministically, bin into heatmap, or explain that a compact inline chart is not suitable.
- Estimates: label estimated values and keep precision lower than measured values.
- Multiple widgets on one page: use a stable root selector with `data-template="<template-id>"`, set `data-mounted="true"` before binding, and scope every DOM query to the root.
- External library failure: keep the HTML/SVG fallback visible and useful; only hide it after successful chart creation.

## Preflight before output

Before calling `PureShowWidget`, silently verify:

- The selected material id exists in `templates/manifest.json`, has `status: "ready"`, and belongs to `scene: "data-visualization"`.
- The selected material's `template.md`, `widget-code.html`, and `fixture.json` informed the output.
- If the output is custom, every plausible ready data-visualization material has a concrete rejection reason.
- If the output is custom, one fallback primitive is clearly driving the layout.
- The chart has one focal data relationship and no more than 2 Chart.js canvases.
- Complementary charts for the same analytical question are inside one widget, not split into sequential widget calls.
- Large chart blocks are not placed side by side; only compact supporting visuals may sit next to a primary chart.
- Multi-block chart layouts do not wrap into uneven 2+1 rows, staggered rows, or unaligned chart panels; the row structure and gutters are explicit.
- Fallback content is visible before JavaScript runs and remains useful if Chart.js fails.
- Tooltip behavior preserves the selected material contract and uses widget-scoped HTML tooltip markup.
- Colors use `--chart-series-1` through `--chart-series-4` plus `--chart-other`; card and panel surfaces remain neutral.
- Custom output has no local palette aliases and does not use accent or semantic tokens for ordinary peer categories.
- Custom output uses `--font-*`, `--text-*`, `--spacer-*`, and `--radius*` tokens for chart titles, labels, legends, tooltips, card padding, panel gaps, and compact controls.
- Supporting cards use the card information hierarchy and do not introduce oversized titles, multiple competing KPI numbers, colored card fills, or non-token typography.
- Custom output does not use tiny non-token text or compressed non-token spacing to force a chart to fit; reduce content, wrap, group, split, or answer in Markdown instead.
- Any template-specific color exception is explicitly documented in that template and has not been applied to other chart types.
- Numeric labels include units, consistent rounding, and explicit estimate markers when needed.
