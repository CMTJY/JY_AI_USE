# Radar Chart With Legend

Use this template for a compact Shadcn-inspired radar chart when two peer sources need comparison across the same small set of dimensions.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies rows.
- `chartConfig` supplies visible labels and color tokens for each source.
- The card contains a centered title, radar body, visible legend, tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses a readable SVG fallback plus Chart.js radar enhancement in the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG radar, and the SVG remains visible if the external script fails.

## Use When

- Two peer series need comparison across 3-8 shared dimensions.
- The reader needs a compact shape comparison, not exact ranking.
- The dimensions form a balanced profile such as months, capabilities, categories, channels, or segments.
- The visual can fit in one inline card with one focal point.

## Avoid When

- Exact value comparison is more important than profile shape. Use `bar-chart-multiple` instead.
- The main story is trend over time. Use `line-trend` instead.
- There is only one current metric or KPI.
- The dimensions are long labels that cannot fit around a compact polar chart.
- There are more than 4 peer sources. Group, split into small multiples, or use a table/list.

## Data Shape

```json
{
  "title": "Radar Chart - Legend",
  "angleDataKey": "month",
  "seriesKeys": ["desktop", "mobile"],
  "chartData": [
    { "month": "January", "desktop": 186, "mobile": 80 },
    { "month": "February", "desktop": 305, "mobile": 200 }
  ],
  "chartConfig": {
    "desktop": {
      "label": "Desktop",
      "color": "var(--chart-series-1)"
    },
    "mobile": {
      "label": "Mobile",
      "color": "var(--chart-series-2)"
    }
  }
}
```

## Visual Rules

- Keep two radar series by default.
- Use the high-contrast pair `--chart-series-1` and `--chart-series-2` for ordinary peer sources such as devices, channels, teams, regions, or models.
- Do not pick two neighboring mid-tone brand shades; overlapping radar fills must remain distinguishable at small inline sizes.
- Do not use `--accent` or semantic colors for ordinary peer source separation.
- Keep angle labels short. Month labels should be abbreviated to three characters in the chart while the fixture can keep full month names.
- Use a subtle polar grid derived from `--border`, not full-strength dividers.
- Keep the radar body square and centered with a visible legend below the chart.
- The card or background may fill the chat width, but the polar chart itself must stay bounded and centered. Do not set the radar shell to `width: 100%` of a wide card or let Chart.js stretch the polygon across the whole widget; use an explicit max inline size with a square/near-square shell.
- Preserve the Shadcn fill-first behavior: both radar series use translucent fills, with the primary source slightly stronger.
- Render a real static SVG fallback before the canvas enhancement. The fallback must include the polar grid, angle labels, radar areas, and legend around the chart.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="radar-chart-legend"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart body near Shadcn's `aspect-square max-h-[250px]` feel.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with one circular color-dot row per active radar series.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Use two-dimensional `axis: "xy"` hit testing so diametrically opposed radar points, such as January and April on the same vertical axis, do not steal each other's tooltip state.
- Clamp tooltip x position inside chart bounds and flip placement below the pointer near the top edge.
- Show the active angle label and both series values in tabular numeric format.
- Keep enough chart safe padding so first and last hover states do not clip.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative series values become `null` and do not render as radar values.
- If every row is invalid or has no label, leave the SVG fallback visible and do not initialize Chart.js.
- If all valid values are `0`, keep the grid readable without adding conclusion copy.
- If one series is missing for a dimension, show the remaining series and omit the invalid tooltip row.
- If two dimensions share the same x or y coordinate on the polar grid, hover selection must still choose the closest point by full x/y distance.
- If labels are long, abbreviate point labels and keep full labels available in the data layer.
- If Chart.js fails to load, the static SVG fallback and legend must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the chart needs more than 2-4 total series, do not extend this template blindly; simplify the data or create a dedicated multi-series radar pattern.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `chartData` and the SVG fallback polygon points when replacing the data.
- All series use the same radial scale.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static SVG fallback is visible before Chart.js renders.
- A visible legend exists for both series.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `radar-chart-legend` as ready.
