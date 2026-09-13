# Scatter Chart

Use this template for a compact Nivo-inspired scatter chart when the relationship between two numeric measures is the main story.

This template follows the Nivo ScatterPlot data model at the content level:

- `data` is an array of series.
- Each series has an `id` and a `data` array.
- Each point has numeric `x` and `y` values, with an optional numeric `size` value for a third quantitative dimension.
- `chartConfig` maps series ids to visible labels and Dynamic UI chart color tokens.

The implementation is not React, JSX, Nivo, or a full chart package embed. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses Chart.js inside the allowed final script phase.

Chart.js is only a progressive enhancement in this template. The first visible chart state is the inline SVG fallback, and the fallback remains visible if the external script fails.

## Use When

- Two numeric measures need correlation, clustering, or outlier comparison.
- The chart has 1-4 peer series and a visible legend.
- The optional third measure can be represented by point size without becoming the main story.
- The visual can fit in one inline card with one focal point.
- The data has roughly 6-80 valid points after filtering.

## Avoid When

- The reader needs a trend over ordered time. Use `line-trend` instead.
- The reader needs category ranking or direct magnitude comparison. Use a bar pattern instead.
- Exact point labels are more important than the x/y relationship. Use a table or compact list instead.
- The x-axis uses dates or strings that require custom scale formatting. Normalize to numeric values first or create a dedicated variant.
- There are more than four peer series. Group into top series plus `Other`, use small multiples, or switch to a table/list.
- There are thousands of points. A sampled or aggregated view is safer for an inline widget.

## Data Shape

```json
{
  "title": "Scatter Chart",
  "axis": {
    "x": "Reach score",
    "y": "Conversion rate (%)"
  },
  "scale": {
    "x": { "min": 0, "max": 100 },
    "y": { "min": 0, "max": 20 }
  },
  "sizeKey": "size",
  "data": [
    {
      "id": "paid",
      "data": [
        { "x": 18, "y": 5.5, "size": 52, "label": "Paid A" },
        { "x": 42, "y": 8.9, "size": 72, "label": "Paid B" }
      ]
    }
  ],
  "chartConfig": {
    "paid": {
      "label": "Paid search",
      "color": "var(--chart-series-1)"
    }
  }
}
```

## Visual Rules

- Keep the chart focused on the x/y relationship; do not add fitted trend lines unless the source data supports that claim.
- Use `--chart-series-1` through `--chart-series-4` for peer series.
- Do not use `--accent`, `--success`, `--warning`, or `--danger` for ordinary peer sources such as channels, cohorts, models, teams, or regions.
- Use `--chart-other` only when a de-emphasized grouped remainder is intentionally present.
- Include a compact legend because color distinguishes the series.
- Use both x and y grid lines, but render repeated grid lines lighter than `--border`.
- Show axis titles because scatter plots need both measures named.
- Use explicit `scale.x` and `scale.y` bounds when the measure has a known domain, such as a 0-100 score.
- Scale optional point size within a bounded radius range; size must not make small points unreadable or large points overlap the plot edge.
- Render a real static SVG fallback before the canvas enhancement. The fallback must include grid context, axis titles, all sample points, and the legend around the chart.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="scatter-chart"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.
- Keep the chart height near `clamp(240px, 34vw, 340px)`.

## Chart Source Color Rules

- One primary series uses `--chart-series-1`.
- Two peer sources use `--chart-series-1` and `--chart-series-2`.
- Three peer sources use `--chart-series-1` through `--chart-series-3`.
- Four peer sources may use `--chart-series-4` as one nearby hue expansion.
- Grouped leftovers, long-tail points, or an overflow source must use `--chart-other` consistently across points, legend swatch, tooltip dot, and fixture.
- `--accent`, `--success`, `--warning`, and `--danger` are not valid colors for ordinary peer scatter sources.

## Required Interaction

- Preserve the hover tooltip when adapting this template. It is part of the template contract, not an optional enhancement.
- Do not use the default Chart.js canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with the point label, a circular series color dot, x value, y value, and optional size value.
- Configure Chart.js tooltip as `enabled: false` with an `external` tooltip handler.
- Use nearest-point hover with a generous hit radius to approximate Nivo's mesh interaction.
- Clamp tooltip x position inside chart bounds and flip placement below the point when the hover point is near the top.
- Keep hover points surface-filled with a series-colored stroke.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, or infinite `x` or `y` values are skipped.
- Missing or invalid `size` values fall back to the minimum point radius.
- If every point is invalid, leave the SVG fallback visible and do not initialize Chart.js.
- If x or y values are all equal, expand the scale slightly so points do not collapse onto an axis edge.
- If explicit scale bounds are missing or invalid, derive a padded numeric domain from valid points.
- If labels are long, keep the visible point label only in the tooltip and use short series labels in the legend.
- If Chart.js fails to load, the static SVG fallback, legend must remain readable.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.
- If the chart needs date, string, or log scales, normalize the values before using this template or create a dedicated variant that documents the scale.

## Implementation Assumptions

- The sandbox allows loading `https://cdn.jsdelivr.net/npm/chart.js@4`.
- The widget is rendered as one inline fragment, not as a page or React component.
- The runtime may execute the final script after DOM injection, so root lookup must not depend on the script node.
- Data is small and embedded directly in the fragment.
- The template author updates both the sample `data` and the fallback SVG when replacing the data.
- Point size is optional and represents one quantitative measure, not a categorical state.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, or export UI appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is not canvas-only; static SVG fallback is visible before Chart.js renders.
- A visible legend exists for every rendered peer series.
- Tooltip markup exists in the widget HTML and Chart.js uses `tooltip.enabled: false` plus an external tooltip handler.
- `templates/manifest.json` marks `scatter-chart` as ready.
