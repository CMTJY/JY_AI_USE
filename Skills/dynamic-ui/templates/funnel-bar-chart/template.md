# Funnel Bar Chart

Use this template for a compact horizontal bar chart when ordered pipeline stages need drop-off and baseline conversion context.

This template follows the existing bar chart composition model at the content level:

- `chartData` supplies ordered pipeline rows.
- The first row is treated as the 100% baseline.
- `chartConfig` supplies the visible label and base brand color token; the template derives a top-to-bottom intensity ramp from it.
- The card contains a title, a centered stage-flow column, horizontal bar chart body, Shadcn-like tooltip behavior.

The implementation is not React, JSX, Recharts, or a Shadcn component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- A pipeline has 3-7 ordered stages and the reader needs drop-off context.
- The first stage can be treated as the denominator for percentages.
- The reader needs a bar-chart treatment rather than a decorative funnel body.
- The visual can fit in one inline card with one focal point.

## Avoid When

- The stages are independent categories rather than a sequential funnel. Use a ranking bar chart instead.
- Two peer series need comparison across stages. Use `bar-chart-multiple` or create a grouped horizontal variant.
- The data contains negative values or bidirectional movement. Use a table or diverging bar pattern instead.
- There are more than seven stages. Group stages or summarize the funnel before rendering.
- A ribbon or flow volume story matters more than stage conversion. Use `sankey-chart` instead.

## Data Shape

```json
{
  "title": "Funnel Bar Chart",
  "xDataKey": "conversion",
  "yDataKey": "stage",
  "valueDataKey": "value",
  "chartData": [
    { "stage": "Visitors", "value": 12400, "displayValue": "12.4k", "conversion": 100 },
    { "stage": "Leads", "value": 6800, "displayValue": "6.8k", "conversion": 55 }
  ],
  "chartConfig": {
    "conversion": {
      "label": "Baseline share",
      "color": "var(--chart-series-1)"
    }
  }
}
```

## Source Prop Mapping

| Source concept | Dynamic UI template handling |
|---|---|
| Ordered stages | Inline `chartData` array; keep ordered stages intact. |
| Stage value | `value` plus optional `displayValue`; compute baseline percentage against the first row. |
| Baseline percentage | `conversion` can be supplied in fixture data, but runtime recomputes from `value` to keep sample replacement safe. |
| Color | Use a single-brand intensity ramp from the baseline stage downward. Color reinforces funnel hierarchy; bar length remains the primary conversion encoding. |
| Funnel shape | Intentionally represented as horizontal bars, not trapezoids, ribbons, halos, or multi-layer outlines. |
| Stage flow | Use a centered stage label column with subtle light-gray `5x5` chevrons between labels to show top-to-bottom progression. |
| Tooltip | Use the same widget-scoped HTML tooltip pattern as the bar chart templates. |

## Visual Rules

- Match the existing bar chart template structure: card, header, fixed chart shell, SVG fallback, Chart.js enhancement, tooltip.
- Use one horizontal bar per stage, sorted in source order from top to bottom.
- Include subtle light-gray `5x5` downward chevrons between centered stage labels so the reader can perceive the ordered funnel progression without adding decorative nodes.
- Use `--chart-series-1` as the base hue and fade each lower stage slightly to express drop-off without introducing unrelated categorical colors.
- Use subtle vertical grid lines at 0%, 25%, 50%, 75%, and 100%.
- Keep the stage labels short, centered, and separate from the chart axis; put longer explanations in the assistant response.
- Do not add a legend for the default single-series chart.
- Do not use a decorative funnel body, halo rings, nested chart frame, black value pills, or arbitrary multi-hue stage sequence.
- Render a real static SVG fallback and visible centered stage-flow column before the canvas enhancement. The fallback must include bars, grid context, x-axis labels, stage labels, arrows.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="funnel-bar-chart"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart height near `clamp(240px, 34vw, 320px)`.

## Required Interaction

- Preserve hover tooltip inspection when adapting this template.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with the stage title, value, and baseline percentage.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Clamp tooltip x position inside chart bounds and flip placement below the pointer when the hover row is near the top.
- Use horizontal bar hover behavior so each stage row can be inspected independently.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative stage values are treated as `0` for percentage calculation.
- If the first stage is invalid or `0`, percentages resolve to `0%`; keep conclusions in the surrounding response.
- If a later stage is larger than an earlier stage, keep the source order and show the computed percentage; do not sort automatically.
- If every value is invalid, leave the HTML fallback visible and do not initialize Chart.js.
- If values are all `0`, keep `beginAtZero: true` and preserve a readable zero-baseline chart without adding conclusion copy.
- If labels are long, shorten y-axis labels and keep full wording in the tooltip or response text.
- If Chart.js fails to load, the static SVG fallback must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the funnel has more stages than the default intensity ramp, reuse the softest bar color instead of inventing extra hues.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `chartData` and the fallback SVG when replacing the data.
- The color ramp is a hierarchy cue only; conversion magnitude is still encoded by normalized bar length.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static SVG fallback is visible before Chart.js renders.
- Static SVG fallback bars and Chart.js bars use the same top-to-bottom brand intensity ramp.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `funnel-bar-chart` as ready.
