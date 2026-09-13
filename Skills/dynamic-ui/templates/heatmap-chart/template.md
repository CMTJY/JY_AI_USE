# Heatmap Chart

Use this template for a compact Shadcn-inspired contribution heatmap when activity intensity across calendar bins is the main story.

This template follows the source Heatmap Chart composition model at the content level:

- `chartData` supplies one column per week or category.
- Each column contains seven row bins by default.
- `levelStyles` supplies the five visual levels from empty to highest activity.
- The card contains a title, month axis, weekday axis, heatmap cells, tooltip behavior, interactive legend.

The implementation is not React, JSX, visx, motion, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses static SVG for first paint and small scoped JavaScript only for tooltip and legend interaction.

## Use When

- A calendar-like density distribution matters more than exact ranking.
- The data can be binned into columns and rows, usually weeks by weekdays.
- The reader needs to spot active periods, quiet gaps, and intensity clusters.
- The visual can fit in one inline card with one focal point.
- The data has 4-26 visible columns and 5-7 row bins.

## Avoid When

- Exact values need comparison by category. Use a bar chart instead.
- The main story is a continuous trend. Use `line-trend` instead.
- The data has irregular dimensions that cannot be binned into a stable grid.
- More than 26 columns are required in one inline widget. Aggregate, window, or summarize before rendering.
- Multiple peer sources need separate colors. This template encodes intensity, not ordinary series categories.

## Data Shape

```json
{
  "title": "Heatmap Chart",
  "xDataKey": "bin",
  "yDataKey": "bin",
  "valueKey": "count",
  "levelKey": "level",
  "dateKey": "date",
  "chartData": [
    {
      "bin": 0,
      "label": "Week 1",
      "bins": [
        { "bin": 0, "count": 3, "level": 1, "date": "2024-01-01" },
        { "bin": 1, "count": 0, "level": 0, "date": "2024-01-02" }
      ]
    }
  ],
  "axis": {
    "xLabels": [
      { "label": "Jan", "bin": 1.5 },
      { "label": "Feb", "bin": 5.5 },
      { "label": "Mar", "bin": 9.5 },
      { "label": "Apr", "bin": 13.5 },
      { "label": "May", "bin": 17.5 },
      { "label": "Jun", "bin": 21.5 }
    ],
    "yLabels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  },
  "levelStyles": [
    { "level": 0, "label": "None", "color": "var(--surface-muted)", "fillMode": "solid" },
    { "level": 1, "label": "Low", "color": "color-mix(in srgb, var(--chart-series-2) 28%, var(--surface))", "fillMode": "solid" },
    { "level": 2, "label": "Medium", "color": "color-mix(in srgb, var(--chart-series-2) 62%, var(--surface))", "fillMode": "solid" },
    { "level": 3, "label": "High", "color": "var(--chart-series-3)", "fillMode": "solid" },
    { "level": 4, "label": "Peak", "color": "var(--chart-series-1)", "fillMode": "solid" }
  ],
  "legend": {
    "lessLabel": "Less",
    "moreLabel": "More"
  }
}
```

## Visual Rules

- Render a real static SVG heatmap as the first visible chart state.
- Keep the grid rectangular and stable: one column per week or category, one row per weekday or bin.
- Use five visual levels: empty plus levels 1-4.
- Use a single brand-family intensity ramp. The colors encode activity level, not peer source categories.
- Level 0 should stay low-emphasis with `--surface-muted` and a subtle border.
- Levels 1-4 may use brand/chart tokens as an intensity ladder; do not add semantic colors for ordinary activity intensity.
- Do not use texture, hatch, stripe, dot, or pattern fills to distinguish levels. Use solid fills only.
- Keep month labels short and place them on regular period bands unless true month-boundary alignment is explicitly required.
- Show every weekday/bin label when seven rows are present.
- Center the combined weekday axis and cell grid as one chart group; do not center only the cell matrix while leaving the y-axis outside the visual center.
- When the card feels sparse, fill the width by adding visible columns up to the 26-column limit instead of scaling up individual cells.
- Keep SVG `viewBox` width close to the card width so caption text tokens render at their intended visual size instead of being scaled up by a narrow SVG canvas.
- Use `--text-caption` for month and weekday labels; use a medium caption only for month labels when they need slightly stronger hierarchy.
- Shape fixture intensity as deliberate waves or clusters, not random noise, so the template reads as a polished reusable example.
- Keep cells compact and square-like; use token-derived small radii instead of ad hoc large rounding.
- Keep a compact Less-to-More legend below the chart, and keep legend swatches visually identical to cell styles.
- Keep the peak/status badge quiet: use a neutral or very light purple surface, not a saturated blue-looking fill.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="heatmap-chart"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.

## Required Interaction

- Preserve hover and keyboard tooltip behavior when adapting this template.
- Use the widget-scoped `.chartTooltip` HTML tooltip with a circular intensity color dot, date, count, and level label.
- Use `--font-sans` for every tooltip text line. Do not use mono/code typography in this tooltip unless the value is a real code identifier.
- Clamp tooltip x position inside the chart bounds and flip placement below the cell when the hovered cell is near the top.
- Hovering or focusing a cell dims unrelated cells and keeps the active cell readable.
- Hovering or focusing a legend swatch highlights matching cells.
- Clicking a legend swatch toggles a locked level filter; clicking the same swatch clears it.
- Keep legend and cell dimming scoped to the widget root.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative counts become level 0 unless the template author defines a different valid missing-state style.
- Levels outside `0-4` are clamped to the nearest valid level.
- Columns with fewer than seven bins should render empty level-0 cells for missing rows or state the omission in the normal response.
- Columns with more than seven bins require updated y-axis labels and a taller SVG viewBox.
- If every count is `0`, keep the full grid visible without adding conclusion copy.
- If the visible range exceeds 26 columns, aggregate or use a smaller time window before rendering.
- If labels are long, abbreviate axes and keep full dates in the tooltip.
- If JavaScript fails, the SVG heatmap, axes, legend remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.

## Implementation Assumptions

- The widget is rendered as one inline fragment, not as a page or React component.
- Data is small and embedded directly in the fragment.
- The SVG cells in `widget-code.html` and the sample `fixture.json` describe the same fixture data.
- The template author updates both static SVG cell attributes and `fixture.json` when replacing the sample data.
- Pattern IDs are local by convention; if multiple heatmaps appear in the same response, prefix IDs before rendering.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, export UI, or external chart runtime appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The heatmap is visible before JavaScript runs.
- Tooltip markup exists in the widget HTML and all tooltip behavior is native, widget-scoped JavaScript.
- Legend interaction highlights cells by matching `data-level`.
- `templates/manifest.json` marks `heatmap-chart` as ready.
