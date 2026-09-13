# Pie Chart - Label List

Use this template for a compact Shadcn-inspired pie chart when part-to-whole share is the main story and the source chart uses labels inside slices.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies category rows.
- `chartConfig` supplies visible labels and color tokens for each category.
- The card contains a centered title, square chart body, Shadcn-like tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- A small set of categories should show composition or share of a total.
- Slice labels are short enough to fit inside the pie.
- The visual can fit in one inline card with one focal point.
- The data has 3-5 positive categories and one value metric.

## Avoid When

- Exact ranking is more important than composition. Use a bar pattern instead.
- The data has more than five categories. Group the long tail into one `Other` category or use a table.
- Labels are long, translated into long phrases, or need multi-line annotations.
- Values include negative numbers. Use a diverging bar or table pattern instead.
- Small differences between slices need precise comparison. Use a sorted bar chart instead.

## Data Shape

```json
{
  "title": "Pie Chart - Label List",
  "categoryKey": "browser",
  "valueKey": "visitors",
  "chartData": [
    { "browser": "chrome", "visitors": 275, "fill": "var(--chart-series-1)" },
    { "browser": "safari", "visitors": 200, "fill": "var(--chart-series-2)" }
  ],
  "chartConfig": {
    "visitors": {
      "label": "Visitors"
    },
    "chrome": {
      "label": "Chrome",
      "color": "var(--chart-series-1)"
    },
    "safari": {
      "label": "Safari",
      "color": "var(--chart-series-2)"
    }
  }
}
```

## Visual Rules

- Keep the chart body square and centered, matching Shadcn's `aspect-square max-h-[250px]` intent.
- Keep the card header centered and compact.
- Render labels inside slices, equivalent to the Recharts `LabelList` behavior.
- Use label text only for short category names; truncate long labels in the live canvas.
- Use `--chart-series-1` and `--chart-series-2` for the first two peer slices.
- When there are 3 peer slices, use `--chart-series-3` so the active brand family stays visually dominant.
- When there are 4 peer slices, use `--chart-series-4` as the single nearby hue expansion instead of forcing a fourth barely distinguishable brand shade.
- Use `--chart-other` for `Other`.
- Do not use `--accent` or semantic colors for ordinary peer sources; reserve semantic colors for slices that explicitly mean success, warning, or danger.
- Do not use stroked, outlined, or per-slice label colors. Use white text for all inside slice labels.
- Render a real static SVG fallback before the canvas enhancement. The fallback must include all slices and inside labels.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="pie-chart-label-list"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with a small circular slice color dot, active category label, and tabular numeric value.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside chart bounds and flip placement below the pointer when the hover point is near the top.
- Use a small hover offset to make the active slice inspectable without changing the card layout.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, zero, or negative values are excluded from the live pie.
- If every value is invalid or the total is `0`, leave the SVG fallback visible and do not initialize Chart.js.
- If Chart.js fails to load, the static SVG fallback must remain readable.
- If labels are long, truncate labels in the live canvas and keep full labels in the tooltip.
- If a slice is too small for readable inside text, omit the live canvas label for that slice and rely on the tooltip.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `chartData` and the fallback SVG when replacing the data.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static SVG fallback is visible before Chart.js renders.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `pie-chart-label-list` as ready.
