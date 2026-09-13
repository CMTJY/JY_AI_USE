# Line Trend Chart

Use this template for a compact Shadcn-inspired line chart when continuous change over time is the main story.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies rows.
- `chartConfig` supplies the visible label and color token for the series.
- The card contains a title, chart body, tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- A single metric changes across ordered time points.
- The reader needs the trend shape, not only the current value.
- The visual can fit in one inline card with one focal point.
- The data has 4-12 points and one primary series.

## Avoid When

- The answer only needs one current number. Use a KPI summary pattern instead.
- Categories need ranking or magnitude comparison. Use a bar comparison pattern instead.
- Two or more series are the main story. Use a grouped or multi-line pattern instead.
- The series represents cumulative volume where fill area matters. Use an area trend pattern instead.
- There are more than 24 time points. Aggregate or summarize before rendering.

## Data Shape

```json
{
  "title": "Line Chart",
  "xDataKey": "month",
  "seriesKey": "desktop",
  "chartData": [
    { "month": "January", "desktop": 186 },
    { "month": "February", "desktop": 305 }
  ],
  "chartConfig": {
    "desktop": {
      "label": "Desktop",
      "color": "var(--chart-series-1)"
    }
  }
}
```

## Visual Rules

- Keep one series by default.
- Use `--chart-series-1` for the primary line.
- Keep the x-axis label short; month names should be abbreviated to three characters.
- Use horizontal grid lines only, and render them lighter than `--border` because repeated chart grid lines feel heavier than a single divider.
- Hide the y-axis labels unless exact scale reading is required.
- Show persistent data nodes as compact brand-filled dots with a surface stroke, so the data points remain readable before hover.
- Render a real static SVG fallback before the canvas enhancement. The fallback must include the trend line, grid context, visible data nodes, and any fill area used by the live chart.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="line-trend"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart height near `clamp(220px, 32vw, 320px)`.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with a small circular series color dot, muted series label, and tabular numeric value.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside chart bounds and flip placement below the point when the hover point is near the top.
- Keep the hover dot surface-filled with brand stroke, matching the template behavior.
- Keep enough chart safe padding and disabled dataset clipping so the first and last hover dots render fully instead of being cut by the chart area.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, or infinite series values become `null` in the chart and are skipped by the line.
- If every value is invalid, leave the HTML fallback visible and do not initialize Chart.js.
- If values are all `0`, keep `beginAtZero: true` and preserve a readable zero-baseline chart without adding conclusion copy.
- If labels are long, abbreviate x-axis ticks and keep full labels for tooltip titles.
- If the first or last point is active, the hover marker must remain fully visible inside the canvas.
- If Chart.js fails to load, the static HTML fallback must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the chart needs multiple series, use at most 2-4 total series and add a visible legend. This template intentionally stays single-series.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `chartData` and the fallback text when replacing the data.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static SVG fallback is visible before Chart.js renders.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `line-trend` as ready.
