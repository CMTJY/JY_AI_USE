# Tree Flow

Use this template for a compact React Flow-inspired node tree when the visual needs to show modules, nodes, and directional relationships on a simple canvas.

This template follows the React Flow Horizontal Flow example at the content level:

- `nodes` is a flat array of positioned nodes.
- Each node has an `id`, `label`, optional `type`, optional `position`, and optional `sourcePosition` or `targetPosition`.
- `edges` is a flat array of relationships.
- Each edge has `source`, `target`, optional `type`, optional `label`, and optional `animated`.

The implementation is not React, JSX, React Flow, or a full canvas editor. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` uses static HTML and SVG.

## Use When

- The user asks for a tree, flow, dependency map, module graph, or canvas node layout.
- A left-to-right hierarchy is the main story.
- The graph needs clean branch paths more than visible connection handles.
- The graph has roughly 4-10 visible nodes and 3-10 edges after summarization.
- The visual can fit in one inline card with one focal point.

## Avoid When

- The user needs an editable workflow builder, drag-and-drop canvas, connection creation, zoom controls, or node selection state.
- The graph has dense many-to-many relationships or cycles. Summarize first or use a different structure.
- The main story is numeric magnitude, trend, ranking, or proportion. Use a chart template instead.
- Exact layout is generated dynamically by Dagre, Elkjs, or another layout engine. Precompute positions before using this template.
- Labels are long paragraphs or require rich node content.

## Data Shape

```json
{
  "title": "Horizontal Flow",
  "source": "https://reactflow.dev/examples/layout/horizontal",
  "nodes": [
    {
      "id": "horizontal-1",
      "type": "input",
      "label": "Input",
      "position": { "x": 0, "y": 80 },
      "sourcePosition": "right"
    }
  ],
  "edges": [
    {
      "id": "horizontal-e1-2",
      "source": "horizontal-1",
      "target": "horizontal-2",
      "type": "smoothstep",
      "animated": true
    }
  ]
}
```

## Visual Rules

- Use an SVG canvas with a subtle background grid when the source is a React Flow or node-canvas example.
- Keep the primary direction left-to-right unless the user explicitly asks for top-to-bottom.
- Prefer a wide horizontal composition inside `viewBox="0 0 720 H"` with clear column spacing; do not expand the SVG coordinate system to make room.
- If the tree feels crowded inside 720, reduce node width, node height, and node label typography before removing nodes or changing the viewBox.
- Keep branch paths visually clean. Do not render port dots or handle markers unless the prompt specifically asks to explain handle positions.
- Preserve `smoothstep` edges as rounded orthogonal connector paths, not straight diagonal lines.
- Preserve `animated` edges with a reduced-motion-safe dashed stroke animation.
- Use one neutral node style for ordinary nodes and one brand node style for the root, selected path, or focal node.
- Use `--brand` for the main active relationship and `--text-muted` for static or secondary edges.
- Do not color every tree level differently. Color should encode focus or status, not sequence.
- Keep node labels short enough to fit. Shorten labels before rendering instead of relying on SVG text wrapping.
- Use edge labels sparingly. Keep edge labels to 1-3 words and place them in a padded pill with enough clearance from adjacent node and connector paths.
- Put explanatory caveats outside the widget, not inside the node canvas.

## Required Interaction

- No JavaScript interaction is required for the default template.
- CSS edge animation is allowed only for source edges marked `animated`.
- Respect `prefers-reduced-motion` by disabling continuous dash animation.
- Do not add drag, zoom, pan, edit, connect, hover cards, or selection behavior unless a separate template documents that interaction.

## Edge Cases

- Missing, null, or duplicate node ids are invalid and should be cleaned before rendering.
- Edges with missing `source` or `target` nodes are skipped.
- Unknown handle positions fall back to `right` for source and `left` for target when calculating connector endpoints.
- Labels that do not fit the node should be shortened or moved to normal response text.
- More than 10 visible nodes should be grouped, wrapped deliberately, or split into multiple visuals.
- More than 10 visible edges usually needs summarization or a table of relationships.
- Cycles should be marked with a return edge only when the cycle is the focal point.
- Animation must not be the only indication of direction or importance.

## Implementation Assumptions

- Node positions are already known. This template does not compute automatic layouts.
- The SVG is static and renders without external libraries.
- The widget is rendered as one inline fragment, not as a page or React component.
- The template author updates both the visible SVG geometry and `fixture.json` when replacing the sample data.
- The source example can be mapped visually without preserving React Flow runtime behavior.
- The 628 implementation intentionally omits visible handle dots to keep the branch paths cleaner.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment with `data-dynamic-ui-widget` and `data-template="tree-flow"`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, export UI, or app shell appears.
- No `position: fixed`, inline event handlers, `document.currentScript`, or `previousElementSibling` appears.
- The SVG viewBox contains every visible node, connector, label.
- The SVG viewBox uses `0 0 720 H` and keeps visible content inside `x=0..720`.
- Every connector path has `fill="none"` and avoids unrelated node interiors.
- Edge-label capsules do not sit directly on top of connector strokes.
- The graph remains readable at inline chat width.
- `templates/manifest.json` marks `tree-flow` as ready.

## Related Templates

- Use `architecture-elements` when the main need is reusable module, boundary, and connector styles.
- Use `gantt-chart` when the relationships are primarily schedule or dependency timing.
- Use `sankey-chart` when weighted flow magnitude matters more than node topology.
