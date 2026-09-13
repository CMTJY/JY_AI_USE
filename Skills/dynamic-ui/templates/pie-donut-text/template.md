# Pie Chart - Donut with Text

Use this template for a compact Shadcn-inspired donut chart when the main story is a total value plus proportional category slices.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies rows with a category name, numeric value, and fill token.
- `chartConfig` supplies visible labels and category colors.
- The card contains a centered title, donut body, center metric, Shadcn-like tooltip behavior, compact legend.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js only in the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- Category composition matters more than exact rank.
- The reader needs one total value in the middle of the chart.
- The visual can fit in one inline card with one focal point.
- The data has 2-5 slices and all values share the same unit.

## Avoid When

- Exact category comparison is the main story. Use a bar chart instead.
- Values include negatives or mixed units. Use a table or signed bar pattern instead.
- There are more than five categories. Group small categories into `other` before rendering.
- The total is not meaningful. Use a ranking or proportion bar instead.
- The chart needs nested composition. Use a dedicated breakdown pattern instead.

## Data Shape

```json
{
  "title": "Pie Chart - Donut with Text",
  "nameKey": "browser",
  "dataKey": "visitors",
  "centerLabel": "Visitors",
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
    }
  }
}
```

## Visual Rules

- Keep the donut centered and square, near the Shadcn `max-h-[250px]` scale.
- Show the total value as the center metric and the unit label below it.
- Use `--chart-series-1` and `--chart-series-2` for the first two peer slices.
- When there are 3 peer slices, use `--chart-series-3` so the active brand family stays visually dominant.
- When there are 4 peer slices, use `--chart-series-4` as the single nearby hue expansion instead of forcing a fourth barely distinguishable brand shade.
- Use semantic colors only when a slice means success, warning, or danger; use `--chart-other` for `other` or long-tail slices.
- The `other` slice, legend swatch, and tooltip dot must resolve to the same `--chart-other` token.
- Include a compact legend when there are three or more slices because color alone is not enough.
- Use a visible static SVG fallback before the canvas enhancement. The fallback must include the donut segments, center metric, and category legend.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="pie-donut-text"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with a small circular category color dot, muted category label, and tabular numeric value.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside the chart bounds and flip placement below the pointer when the pointer is near the top.
- Use segment hover emphasis through a small `hoverOffset`, matching the Recharts pie hover affordance without adding persistent labels inside the chart.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative values become `0`.
- If every value is invalid or `0`, leave the SVG fallback visible and do not initialize Chart.js.
- If one slice is much larger than the others, keep the legend visible so small slices remain identifiable.
- If category labels are long, keep full labels in tooltip and shorten visible legend labels before rendering.
- If the total exceeds four digits, use locale formatting and keep the center label short.
- If Chart.js fails to load, the static SVG fallback, legend, center value must remain readable.
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
- `templates/manifest.json` marks `pie-donut-text` as ready.
