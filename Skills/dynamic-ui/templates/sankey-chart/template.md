# Sankey Chart

Use this template for a compact Bklit SankeyChart-inspired flow diagram when the relationship between staged nodes and weighted movement is the main story.

This template follows the source component at the content level:

- `nodes` supplies named nodes with a `category`, total `value`, and tokenized color.
- `links` supplies d3-sankey-style `source`, `target`, and `value` fields.
- The card contains a title, summary metrics, SVG Sankey body, node labels, tapered flow ribbons, hover tooltip behavior.

The implementation is not React, JSX, @visx/sankey, d3-sankey, or a package component. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses inline data, generated SVG, CSS transitions, and scoped vanilla JavaScript.

## Use When

- Flow magnitude across 2-4 ordered stages is the main story.
- The data can be represented with roughly 5-18 nodes and 6-42 visible links after grouping.
- Source, landing, and outcome labels are short enough to fit near the node columns.
- Hover or keyboard focus inspection helps connect one node or ribbon to its adjacent flows.
- The visual can fit in one inline card with one focal point.

## Avoid When

- Exact ranking matters more than staged movement. Use a bar chart instead.
- The flow has cycles, many-to-many loops, or bidirectional edges that would cross heavily.
- There are more than seven peer sources or seven peer outcomes. Group long-tail categories into `Other` or use a table/list. For non-Sankey charts, do not use this seven-color exception; follow the four-series chart contract instead.
- Link values include negative numbers. Normalize or explain signed movement in a different pattern.
- Every node needs a long explanation. Keep explanations in the assistant response.
- The graph requires automatic layout, drag, zoom, or pan. This template uses a bounded inline layout.

## Data Shape

```json
{
  "title": "Sankey Chart",
  "aspectRatio": "840 / 860",
  "nodeWidth": 16,
  "nodePadding": 24,
  "animationDuration": 700,
  "valueUnit": "sessions",
  "nodes": [
    {
      "name": "Organic Search",
      "category": "source",
      "value": 3200,
      "color": "var(--brand)"
    },
    {
      "name": "Pricing",
      "category": "landing",
      "value": 3495,
      "color": "var(--brand)"
    },
    {
      "name": "Converted",
      "category": "outcome",
      "value": 4067,
      "color": "var(--chart-series-4)"
    }
  ],
  "links": [
    { "source": 0, "target": 1, "value": 800 },
    { "source": 1, "target": 2, "value": 1748 }
  ],
  "chartConfig": {
    "organic": {
      "label": "Organic Search",
      "color": "var(--brand)"
    },
    "converted": {
      "label": "Converted",
      "color": "var(--chart-series-4)"
    }
  }
}
```

## Visual Rules

- Render a real SVG Sankey body inside the widget; JavaScript may generate the SVG elements, but the result must not be canvas-only.
- Preserve the source defaults conceptually: `nodeWidth: 16`, `nodePadding: 24`, compact node bars, readable ribbon thickness, and linked hover inspection.
- Keep the Sankey SVG bounded inside one inline card. The 628 material uses `viewBox="0 0 840 860"` because the sample has 17 nodes and 42 links; simpler Sankey variants should stay closer to `0 0 720 H`.
- Keep columns ordered by stage: source -> landing -> outcome. Do not sort nodes automatically unless the prompt explicitly asks for ranking.
- Use weighted ribbon width with a readable minimum so small flows remain inspectable; disclose that minimum as a readability floor, not exact area encoding.
- Use tapered cubic Bezier ribbons, not straight bars, for dense staged flows.
- Use compact direct labels near nodes, not paragraphs inside the chart.
- If an intermediate column is too cramped for two-line labels, show the node name directly and keep the value in the tooltip.
- Use grid or axis chrome sparingly; Sankey weight is encoded by flow width and node height.
- Use shared neutral surface tokens for summary cards and the Sankey shell; do not define template-local panel color tokens or blue-/purple-tinted panel backgrounds.
- Use existing typography roles for summary values, such as `--font-metric` with `--text-title`; do not define template-local font or text-size tokens.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="sankey-chart"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Do not add conclusion, recommendation, or analysis copy inside the widget; keep that text in the surrounding response.

## Sankey Color Rules

- This template has a special category palette because the 628 sample intentionally shows seven source categories and seven outcome categories. This is a Sankey-only exception, not a generic chart palette.
- Source node colors display at most seven colors in order: `--brand`, `--chart-series-2`, `--accent`, `--chart-series-4`, `--accent-2`, `--warning`, `--chart-other`.
- Outcome node colors display at most seven colors in order: `--chart-series-4`, `--accent`, `--warning`, `--chart-series-2`, `--chart-series-3`, `--accent-2`, `--chart-other`.
- These Sankey-specific source/outcome sequences take precedence over generic chart-series order only inside `templates/sankey-chart`. Do not introduce an eighth category color, and do not copy this sequence into bars, lines, pies, radar, scatter, heatmaps, funnels, or custom generic charts.
- Source and outcome node rectangles use solid `currentColor` fills. Do not tint them with transparent `color-mix()` fills.
- Landing nodes use brand-family fills and should stay visually quieter than source/outcome categories.
- Flow ribbon gradients use the standard stage-based opacity treatment: source -> landing uses source at stronger opacity and landing/brand softer opacity; landing -> outcome uses landing/brand softer opacity and outcome stronger opacity.
- Grouped leftovers, long-tail sources, or overflow buckets must use `--chart-other` consistently across node, link, legend, tooltip dot, and fixture.
- Use `--success` only when the prompt explicitly needs a semantic health or completion state, not as the default converted color.

## Required Interaction

- Preserve hover and keyboard focus inspection when adapting this template.
- Do not use a canvas tooltip.
- Use the widget-scoped `.chartTooltip` HTML tooltip with node/link label, value, and category or direction metadata.
- On link hover, keep the link and its source/target nodes at full opacity while fading unrelated nodes and links.
- On node hover, keep directly connected links and adjacent nodes visible while fading unrelated nodes and links.
- Clamp tooltip x position inside the chart shell and flip placement below the pointer when there is not enough top space.
- Keep transitions short and respect reduced-motion preferences if entrance animation is added.

## Edge Cases

- `null`, missing, non-numeric, `NaN`, infinite, or negative link values are treated as `0` when calculating layout.
- Links with invalid `source` or `target` indexes are skipped.
- Nodes with no incoming or outgoing valid links should be omitted or rendered as a low-emphasis standalone node only when that absence is the story.
- If all links are invalid or `0`, use a compact empty-state list instead of a misleading Sankey.
- If labels are long, shorten visible labels and keep full labels in the tooltip.
- If many small flows would overlap, group them into `Other` using `--chart-other`.
- If more than seven peer sources or seven peer outcomes are needed, group, split into multiple visuals, or switch to a table/list.
- If JavaScript fails before dynamic SVG generation, the title, summary metrics, and empty SVG shell remain visible; for production adaptation, prefer adding static fallback geometry for the most important path.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.

## Implementation Assumptions

- The widget is rendered as one inline fragment, not as a page or React component.
- Data is small and embedded directly in the fragment.
- The template author updates the sample `nodes`, `links`, generated layout constants, tooltip data, summary metrics together when replacing the data.
- The 628 material calculates node columns and tapered ribbons in scoped vanilla JavaScript instead of storing every ribbon path by hand.
- Summary typography stays on the shared Dynamic UI token contract; template-local font stacks are out of scope.
- The bounded layout is intended for staged acyclic flows; complex graph layout is out of scope for this template.
- Link widths include a minimum readable width, so tiny values are visually inspectable but not perfectly proportional.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment with `data-dynamic-ui-widget` and `data-template="sankey-chart"`.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, TSX, router, export UI, or external package dependency appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area renders as SVG paths and nodes, not canvas-only first paint.
- Tooltip markup exists in the widget HTML and is driven by scoped vanilla JavaScript.
- Hover and keyboard focus activate the corresponding node/link and connected elements.
- Node and outcome color sequences do not exceed the documented seven-color Sankey limit.
- Sankey-only accent or semantic category colors are not reused outside this template.
- `fixture.json` describes the same node/link shape used in `widget-code.html`.
- `templates/manifest.json` marks `sankey-chart` as ready.

## Related Templates

- Use `tree-flow` when topology and dependency direction matter more than weighted movement.
- Use `funnel-bar-chart` when the story is linear stage attrition instead of many-to-many flow.
- Use `bar-stacked-legend` when part-to-whole contribution can be shown with fewer crossings.
