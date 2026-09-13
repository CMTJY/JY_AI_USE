# Bar Chart - Multiple

Use this template for a compact Shadcn-inspired grouped bar chart when two related series need month-by-month magnitude comparison.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies rows.
- `chartConfig` supplies visible labels and color tokens for the two series.
- The card contains a title, chart body, Shadcn-like tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- Two related categories should be compared across the same ordered x-axis.
- The reader needs grouped magnitude comparison, not a continuous trend line.
- The visual can fit in one inline card with one focal point.
- The data has 3-12 groups and exactly two primary series.

## Avoid When

- The answer only needs one current number. Use a KPI summary pattern instead.
- The main story is a continuous trend. Use `line-trend` instead.
- The data needs ranking by category without time or ordered groups. Use a single horizontal bar pattern instead.
- More than four series are needed. Group, summarize, or use a table before rendering.
- Stacked composition is the main story. Use a stacked bar pattern instead.

## Data Shape

```json
{
  "title": "Bar Chart - Multiple",
  "xDataKey": "month",
  "series": ["desktop", "mobile"],
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

- Keep exactly two series by default.
- Use the high-contrast pair `--chart-series-1` and `--chart-series-2` for the two peer comparison sources.
- Do not pick two neighboring mid-tone brand shades; the bars must remain distinguishable at small inline sizes.
- Do not use `--accent` or semantic colors for ordinary peer sources such as channels, devices, models, teams, or regions.
- Include a compact legend because color distinguishes the two series.
- Keep the x-axis label short; month names should be abbreviated to three characters.
- Use horizontal grid lines only, and render them lighter than `--border` because repeated chart grid lines feel heavier than a single divider.
- Hide the y-axis labels unless exact scale reading is required.
- Render a real static SVG fallback before the canvas enhancement. The fallback must include both series, grid context, x-axis labels, legend.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="bar-chart-multiple"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart height near `clamp(220px, 32vw, 320px)`.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with a title label, small circular color dots, muted series labels, and tabular numeric values.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside chart bounds and flip placement below the pointer when the hover group is near the top.
- Use `interaction.mode: "index"` so hovering one month shows both series values together.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, or infinite series values become `null` in the chart and are skipped by the corresponding bar.
- If every value is invalid, leave the HTML fallback visible and do not initialize Chart.js.
- If values are all `0`, keep `beginAtZero: true` and preserve a readable zero-baseline chart without adding conclusion copy.
- If labels are long, abbreviate x-axis ticks and keep full labels for tooltip titles.
- If Chart.js fails to load, the static HTML fallback must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the chart needs more than two series, use at most 2-4 total series with a visible legend and update this template's data contract before reuse.

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
- `templates/manifest.json` marks `bar-chart-multiple` as ready.
