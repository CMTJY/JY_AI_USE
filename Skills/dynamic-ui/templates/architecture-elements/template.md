# Architecture Elements

Use this template as the reusable element palette for architecture and framework diagrams. It is a style and primitive source, not a finished architecture diagram.

When generating an architecture diagram, prefer composing from these elements before drawing a one-off custom style:

- Neutral module blocks for normal systems, services, stores, adapters, and support modules.
- Brand module blocks for the central capability, selected system, recommended path, or AI/model concept.
- Boundary blocks for runtime, ownership, trust, package, product, or deployment scope.
- External blocks for user, third-party system, upstream input, and downstream output.
- Tokenized connector lines for normal dependency, primary route, optional relationship, and labeled edge.

The `widget-code.html` file intentionally shows the elements separately instead of rendering a complete system diagram. The goal is to keep architecture visuals consistent while still letting each generated diagram choose its own layout.

## Use When

- The user asks for an architecture diagram, framework diagram, module map, capability map, or structural diagram and the generator needs a consistent visual vocabulary.
- A finished diagram should be composed from reusable blocks and lines instead of copying a fixed example.
- The answer needs to clarify which block and connector styles are available.
- The architecture has a central focus, boundary, external input/output, or module relationships.

## Avoid When

- The user needs an ordered workflow, lifecycle, request sequence, or React Flow-style tree. Use `tree-flow` or a custom flowchart instead.
- The user needs weighted movement between stages. Use `sankey-chart`.
- The user needs numeric trend, ranking, correlation, composition, or schedule evidence. Use a chart template.
- The user explicitly asks for the final architecture diagram. In that case, use these elements as primitives and generate a custom diagram, rather than rendering the palette itself.
- The architecture requires exact topology, ERD detail, or dense many-to-many relationships. Summarize first or use a table/list.

## Data Shape

```json
{
  "title": "Architecture Elements",
  "blocks": [
    {
      "id": "neutral-module",
      "label": "Neutral module",
      "caption": "default block",
      "role": "neutral"
    },
    {
      "id": "brand-module",
      "label": "Brand module",
      "caption": "main focus",
      "role": "brand"
    }
  ],
  "lines": [
    {
      "id": "neutral-solid",
      "label": "Dependency",
      "role": "neutral",
      "style": "solid"
    },
    {
      "id": "primary-dashed",
      "label": "Primary path",
      "role": "primary",
      "style": "dashed"
    }
  ],
  "rules": [
    "Start from the boundary",
    "Pick one focus block",
    "Connect only real dependencies"
  ]
}
```

## Visual Rules

- Render this template as an element board, not as a system architecture.
- Keep every block on a neutral surface. Use brand as border, text, or connector emphasis instead of colored card fills.
- Use the gray neutral module for ordinary systems and supporting modules.
- Use the purple brand module for exactly one primary focus unless the prompt explicitly needs a second highlighted path.
- Use boundary blocks to represent scope. Do not over-nest beyond 2-3 levels.
- Use external blocks for users, vendors, upstream sources, and downstream outputs.
- Use neutral solid lines for normal dependencies, calls, reads, writes, and containment references.
- Use brand dashed lines for the primary route or recommended path only.
- Use neutral dashed lines for optional, weak, planned, or async relationships.
- Use the standard `marker-end` arrow primitive for directed edges. Define the marker in the same SVG as the path, use `orient="auto"` and `markerUnits="userSpaceOnUse"`, and attach it to the connector path. This is the default for reverse or leftward arrows; do not hand-build arrowheads from decorative curves or detached polygons.
- Use labeled edges sparingly. Labels should be 1-2 words.
- Use port dots only when the source architecture needs handle-like attachment points or mixed edge directions.
- Do not color modules by sequence. Color must encode focus, boundary, category, status, or hierarchy.
- Do not generate a fixed architecture from this template. Use the elements as building blocks for a custom layout that matches the user's system.

## Required Interaction

- No JavaScript interaction is required.
- No animation is required for the palette view.
- Generated diagrams may use reduced-motion-safe dashed stroke animation only for a meaningful primary path, following `tree-flow` conventions.
- Do not add drag, zoom, pan, edit, expand/collapse, hover cards, or selection behavior.

## Edge Cases

- Missing element ids are invalid and should be cleaned before rendering a derived diagram.
- Null labels should be replaced with short role labels such as `Module`, `Boundary`, or `External`.
- Long labels should be shortened before drawing. Move explanations into the normal response.
- More than 6 modules should be grouped before rendering.
- More than 8 connectors usually needs summarization or a relationship table.
- Multiple primary paths reduce focus; choose one unless comparison is the explicit goal.
- Cycles should be shown only when the cycle is the focal point.
- If every element appears equally important, the generated diagram needs a clearer focal point before rendering.

## Implementation Assumptions

- This template provides static HTML/SVG primitives and does not compute layout.
- The generated architecture diagram should choose its own positions, boundary size, and connector routing.
- The template author keeps `fixture.json`, `template.md`, and `widget-code.html` aligned when adding or removing element types.
- The widget is rendered as one inline fragment, not a page, React component, or Mermaid renderer.
- The palette is intentionally compact; it should not become a full design system page.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment with `data-dynamic-ui-widget` and `data-template="architecture-elements"`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, export UI, or app shell appears.
- No `position: fixed`, inline event handlers, `document.currentScript`, or `previousElementSibling` appears.
- The board lists reusable block styles and connector styles separately.
- The visible rules say architecture diagrams should be composed from these elements, not copied from a fixed architecture.
- The board includes a directed arrow primitive using `marker-end` with `orient="auto"` so generated diagrams do not invent custom arrowheads.
- Every SVG connector path has `fill="none"`.
- Text remains readable at desktop and narrow mobile widths.
- `templates/manifest.json` marks `architecture-elements` as ready.

## Related Templates

- Use `tree-flow` when the main story is a left-to-right workflow or node tree.
- Use `sankey-chart` when weighted flow magnitude matters.
- Use a custom structural diagram when a user asks for the final architecture; compose that diagram from these elements.
