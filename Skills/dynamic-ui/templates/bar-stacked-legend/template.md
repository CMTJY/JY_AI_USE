# Stacked Bar Chart With Legend

Use this template for a compact Shadcn-inspired stacked bar chart when each category has two contributors and the total size matters as much as the component split.

This template follows the Shadcn chart composition model at the content level:

- `chartData` supplies rows.
- `chartConfig` supplies the visible labels and color tokens for each series.
- The card contains a title, stacked bar body, visible legend, tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline HTML fallback, and the fallback remains visible if the external script fails.

## Use When

- Two series contribute to each category total.
- The reader needs both total magnitude and part-to-whole contribution.
- The visual can fit in one inline card with one focal point.
- The data has 3-12 ordered categories and 2 stacked series.

## Avoid When

- The reader needs direct side-by-side comparison between series. Use `bar-chart-multiple` instead.
- Percent share is the only story. Use a 100% stacked pattern instead.
- There is only one series. Use a simple bar pattern instead.
- Values include meaningful negatives. Use a diverging bar pattern instead.
- There are more than 4 series. Group minor series or use a table/list.

## Data Shape

```json
{
  "title": "Bar Chart - Stacked + Legend",
  "xDataKey": "month",
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

- Keep two stacked series by default.
- Use the high-contrast pair `--chart-series-1` for the lower primary peer segment and `--chart-series-2` for the upper peer segment.
- Do not pick two neighboring mid-tone brand shades; stacked segments must remain clearly separable at small inline sizes.
- Do not use `--accent` or semantic colors for ordinary peer sources such as channels, devices, models, teams, or regions.
- Keep the x-axis label short; month names should be abbreviated to three characters.
- Use horizontal grid lines only, and render them lighter than `--border` because repeated chart grid lines feel heavier than a single divider.
- Hide the y-axis labels unless exact scale reading is required.
- Show a visible legend with the same series order as the stack.
- Preserve the Shadcn rounded-stack behavior: the lower series owns the exposed bottom corners, and the upper series owns the exposed top corners.
- Render a real static HTML fallback before the canvas enhancement. The fallback must include stacked bars, grid context, x labels, and the legend around the chart.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="bar-stacked-legend"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart height near `clamp(220px, 32vw, 320px)`.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with one circular color-dot row per active stacked series.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside chart bounds and flip placement below the stack when the hover point is near the top.
- Keep tooltip rows ordered by the visual stack order and show tabular numeric values.
- Keep enough chart safe padding so first and last hover states do not clip.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative series values become `null` and do not render as a stacked segment.
- If every row is invalid or has no label, leave the HTML fallback visible and do not initialize Chart.js.
- If all valid values are `0`, keep a readable baseline without adding conclusion copy.
- If the top series is missing for a category, the remaining segment should own both exposed top and bottom corners.
- If labels are long, abbreviate x-axis ticks and keep full labels available to the data layer.
- If Chart.js fails to load, the static HTML fallback, legend must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the chart needs more than 2-4 total series, do not extend this template blindly; simplify the data or create a dedicated multi-series stacked pattern.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `chartData` and the fallback bar percentages when replacing the data.
- The lower-to-upper stack order is the same as `seriesKeys`.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static HTML fallback is visible before Chart.js renders.
- A visible legend exists for both series.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `bar-stacked-legend` as ready.
