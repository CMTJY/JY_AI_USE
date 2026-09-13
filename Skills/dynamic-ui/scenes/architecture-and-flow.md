# Architecture & Flow

Shared contracts: apply `SKILL.md`, this scene file, `templates/manifest.json`, selected `templates/<id>/template.md`, and `tokens/visual-tokens.md`.

## When to enter this scene

The user's intent involves visualizing any of the following structural relationships:

- Module relationships (how system components are organized and depend on each other)
- Dependency graphs (reference directions between packages/services/classes)
- Flowcharts (business processes, algorithm steps, decision branches)
- State transitions (state machines, lifecycle changes)
- Call chains (request propagation paths across services)
- Schedule progress (task timelines, Gantt charts)

Typical trigger words: architecture diagram, flowchart, dependency graph, call chain, state machine, Gantt chart, timeline, flow, diagram.

## When to reject

Do NOT generate a visualization in the following cases — reply with Markdown text instead:

- Nodes <= 2 with a single relationship (a sentence suffices)
- Pure linear list with no branching or parallelism (a Markdown ordered list is clearer)
- User requests a code implementation rather than a visual representation
- Relationships are too complex (>20 nodes) making single-screen readability impossible — in this case, suggest layering or an interactive approach
- The diagram would require tiny text, hidden overflow, overlapping labels, connector lines through text, or more than 2 unrelated subflows in one inline widget
- The source relationship is a dense many-to-many graph where exact topology matters more than explanation; summarize first or use a table/list

## Generation principles

- Optimize for legibility before completeness. A smaller diagram that explains the focal relationship is better than a complete diagram that needs cramped nodes or tangled connectors.
- Treat every node, label, connector label, badge, legend, phase chip, and boundary as a real box before drawing. If the boxes cannot fit, reduce the scope before emitting SVG.
- Do not use visual tricks to hide layout failure: no tiny text, no clipped overflow, no white rectangles over connector collisions, no labels placed on top of strokes, and no decorative connector dots to imply precision.
- Use structural hierarchy instead of density. Group related modules into one boundary, show the critical path, then move secondary dependencies to response text or a compact relationship list.

## Mandatory generation workflow

This workflow is mandatory after routing into this scene.

1. Confirm that an inline visual is clearer than Markdown.
2. Identify the relationship type: hierarchy, component map, process flow, state transition, call chain, or schedule.
3. Create a fit budget: visible nodes, connectors, connector labels, legends, boundaries, and any external inputs/outputs.
4. Check `templates/manifest.json` for ready `architecture-and-flow` materials.
5. Use `sequence-diagram`, `tree-flow`, `architecture-elements`, or `gantt-chart` when their usage boundary fits.
6. Reject a ready material only when its boundary does not match, the relationship is outside its scale, or Markdown is clearer.
7. If no ready material matches, choose `node-flow` or `explanation-panel`, then apply the SVG layout rules below.
8. Before writing SVG, choose one skeleton: horizontal flow, vertical flow, swimlane/sequence, grouped architecture, or schedule. Do not mix skeletons unless each has its own panel.
9. Apply color priority before styling nodes or connectors: neutral structure first, then `--brand` for the main path, then `--chart-series-*` for explicit peer categories. Semantic colors are allowed only for explicit status/risk/health diagrams.
10. Apply the typography, spacing, and radius tokens from `tokens/visual-tokens.md` before adding scene-specific geometry. Do not invent local font sizes, line heights, padding values, gaps, or radius values.
11. If the node count, label length, or connector count cannot fit without overlap, group, split, convert the relationships to a table/list, or answer in Markdown instead of shrinking text, compressing spacing, clipping overflow, or adding decorative color.

### Hard readability gates

- Custom architecture/framework diagrams should stay at <=6 ungrouped modules and <=8 connectors in one panel. Use group boundaries for larger systems.
- Flowcharts should show 3-5 primary steps. More steps require grouping, vertical stacking, or multiple panels.
- Sequence diagrams should show 3-5 participants and 4-8 ordered messages. Larger protocols require phase grouping or splitting.
- One panel must have one focal path, component, phase boundary, or risk. If everything is equally important, choose the focal point before drawing.
- Labels must fit at the token sizes. Shorten labels or move details to the response text; do not shrink type to make long labels fit.
- Legends, phase chips, and side notes count against the layout budget. Reserve space for them before routing connectors.

### SVG canvas specification

- Preferred viewBox: `0 0 720 H` (H calculated based on content), set `width="100%"` + `height="auto"`
- Safe area: >= 40 design units from edges or 6% of viewBox width (whichever is larger)
- Do not use fixed pixel width; ensure responsive scaling
- Compute `H` from the lowest visible object plus bottom padding. Do not crop, clip, or leave unexplained empty space to compensate for bad geometry.

### Text size and node width

| Purpose | Font size | Estimated width |
|---------|-----------|-----------------|
| Labels/titles | 14px | ~8px/char |
| Metadata/annotations | 12px | ~7px/char |

Node width calculation: `max(title_chars * 8, subtitle_chars * 7) + 24`

Do not reduce label or metadata font sizes below this table to force fit. For Chinese, mixed script, code-like labels, equations, or long identifiers, shorten the label first or increase the node width estimate by 30-50%.

### Flowchart rules

- Main path: 3–5 steps, maintain a single direction (horizontal or vertical, never mixed)
- Spacing between nodes >= 60px
- Process nodes use rounded rectangles (rx=8)
- Decision nodes use softened diamonds (rounded corners rather than sharp points)
- Start/end nodes use pill shapes
- Internally allocate coordinates in tiers/rows before emitting SVG. Compute total row width before placing boxes; if it exceeds the safe width, wrap, stack vertically, or split into another visual.
- Use separate tracks for connectors and labels. A connector label must be above/below the line, never centered on the stroke.
- If a step needs both a title and details, use a 2-line node with height >= 56px rather than placing extra text beside the arrow.
- For branch decisions, reserve one clear outbound track per branch. If branch labels collide, move the labels into the destination node subtitles or split the decision into a second panel.

### Sequence and state-flow rules

Use these for protocols, handshakes, lifecycles, and state transitions between two or more actors.

- Prefer swimlanes/lifelines for two-sided flows such as TCP handshakes: actors stay in fixed columns, messages occupy distinct horizontal rows.
- Minimum row pitch: 72 units for message rows with labels; 56 units for compact state-only rows.
- Message arrows may be horizontal or diagonal. Use diagonal arrows when sender and receiver states are on different rows; do not flatten state rows just to keep arrows horizontal.
- Put state labels beside the actor lifeline, not on the message arrow. Keep message labels in a capsule centered between actors and offset 14–20 units above or below the arrow.
- Never reuse the same y coordinate for a state marker, message line, and message label. Each needs its own vertical slot.
- For bidirectional request/response pairs, alternate label offsets above/below the line or increase row pitch. Do not stack labels in the middle lane.
- Route crossing/back arrows with shallow curves that stay outside node and label bounding boxes. If the curve needs to cross multiple rows, reserve an empty corridor.
- For dense protocol explanations, separate phases into multiple compact diagrams or vertically stacked panels. TCP three-way handshake and four-way teardown should not share one cramped coordinate system unless each phase has its own panel and safe padding.

### Connector specifications

- `fill="none"`, use `stroke` rather than solid fill
- Paths route around unrelated nodes, never crossing through them
- Use straight horizontal/vertical lines, diagonal lines, gentle curves, or rounded L-bends as appropriate (`stroke-linejoin="round"`, `stroke-linecap="round"`)
- Prefer a standard `marker-end` arrowhead with `orient="auto"` and `markerUnits="userSpaceOnUse"` for directed edges. Put the marker on the same path as the connector, keep the marker around `8x8`, and let the path direction determine whether the arrow points left, right, up, down, or along a curve.
- Do not draw arrowheads as separate decorative curves, brackets, detached chevrons, or copied right-facing polygons. If manual triangles are used, their tip must sit on the target endpoint and the visible line must meet the triangle base.
- Connector labels are optional. If used, reserve a clear label capsule above or below the connector. The capsule must not sit directly on the stroke and must not intersect any connector, node, boundary, or legend.
- Connector colors:
  - Default: `--text-muted` or `--border` (neutral)
  - Use `--brand` for the primary path or focal relationship
  - Use `--chart-series-*` for explicitly labeled peer path categories before reaching for accent or semantic colors
  - Use semantic connector colors only when status/risk/health is the primary encoded variable, not just because a connector label sounds positive or negative

### Structural containers

- Grouping containers use larger rounded rects with comfortable internal padding around their content
- Maximum 2–3 nesting levels; beyond that, split into multiple diagrams or use expand/collapse
- Container borders use dashed style to differentiate from node solid lines
- Legends and inset explanation panels are structural containers too. Size them from their content and keep marker, label, and row spacing visibly separated from each other and from the panel border. If the content does not fit, widen the panel, wrap to the next row, move it below the diagram, or simplify it.
- Place legends outside main boundary boxes unless the boundary has explicit unused space. A legend overlapping a boundary, connector, or module invalidates the diagram.

### Label conciseness

- Node labels: 2–5 words
- Connector labels: 1–3 words (obvious relationships may be omitted)
- Detailed explanations go in the response text outside the diagram

## Reference materials

| Data relationship / Intent | Reference material | Usage notes |
|---|---|---|
| Module/dependency tree | `tree-flow` | Horizontal node-tree layout; suitable for dependency hierarchies <= 4 levels |
| Call chain or protocol sequence | `sequence-diagram` | ZenUML-inspired participant/lifeline/message layout; suitable for 3-5 actors and 4-8 ordered messages |
| Module components and boundaries | `architecture-elements` | Provides neutral/brand/boundary/external block styles + connector styles (neutral solid, brand dashed, neutral dashed, labeled edge) |
| Schedule/timeline | `gantt-chart` | Timeline + bar layout; suitable for task/milestone progress display |

### architecture-elements detailed style reference

- **Block types**: neutral (regular module), brand (core module), boundary (logical boundary container), external (external system)
- **Connector types**: neutral solid (standard call), brand dashed (highlighted data flow), neutral dashed (weak dependency), labeled edge (annotated connection)

## Composition guidelines

1. **Determine direction**: First decide whether information flows top-to-bottom (hierarchy/process) or left-to-right (time/dependency chain)
2. **Select primary material**:
   - Hierarchical relationships → `tree-flow` as skeleton
   - Component architecture → `architecture-elements` as skeleton
   - Time dimension → `gantt-chart` as skeleton
3. **Mix styles**: You may render `tree-flow` nodes using `architecture-elements` block styles; you may attach a simplified flow below a Gantt chart
4. **Color restraint**: Use neutral structure plus one brand focal meaning. If multiple peer categories need color, use `--chart-series-1` through `--chart-series-4` before accent or semantic colors; do not create rainbow level-by-level coloring.
5. **Legend**: If more than 2 connector styles or more than 2 block styles are used, add a concise legend in a reserved corner or below the diagram; never float it over modules or connector corridors.
6. **Silent layout planning**: Internally treat every node, label capsule, badge, legend, boundary, and actor label as a bounding box. If any box would overlap or any connector would cross text, move it, simplify it, convert it to a table/list, or split the diagram. Do not solve overlap with non-token tiny text, squeezed spacing, hidden overflow, or background masks.
7. **Fallback discipline**: Custom architecture diagrams still use the fallback contract. Start from neutral containers and connectors, then add one brand focal node/path. Add chart-series colors only for named peer categories. Add semantic colors only for explicit status/risk/health encodings. Use tokenized typography, spacing, and radius for nodes, labels, legends, and panels.
