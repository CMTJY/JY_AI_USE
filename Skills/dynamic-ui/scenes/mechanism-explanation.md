# Mechanism Explanation

Shared contracts: apply `SKILL.md`, this scene file, `templates/manifest.json`, selected `templates/<id>/template.md`, and `tokens/visual-tokens.md`.

## When to enter this scene

The user's intent is to **understand how something works**, involving any of the following types:

- Physical processes (heat conduction, electromagnetic fields, fluid dynamics, optics, mechanics)
- Abstract mechanisms (algorithm internals, protocol handshakes, scheduling strategies, data pipelines)
- Causal chains (the internal path by which event A leads to result B)
- Conceptual models (attention mechanisms, GC collection process, lock contention, cache coherence)
- State evolution (how internal system state changes with input/time)

Typical trigger words: principle, mechanism, how it works, internal process, under the hood, why does this happen.

**Distinction from architecture-and-flow**: The architecture scene shows "relationships between components"; the mechanism scene shows "how a single thing operates internally."

## When to reject

Do NOT generate a visualization in the following cases — reply with Markdown text instead:

- The mechanism can be explained clearly in 3 sentences with no spatial/temporal dimension
- User requests a code implementation rather than a conceptual explanation
- The concept is too abstract to visualize (e.g., a pure mathematical proof)
- Dynamic simulation is needed but the widget environment cannot support the required complexity

## Generation principles

## Mandatory generation workflow

This workflow is mandatory after routing into this scene.

1. Confirm that the mechanism has spatial, temporal, causal, or state structure worth visualizing.
2. Identify whether the visual language is physical or abstract.
3. Because this scene normally has no fixed template, choose a fallback primitive before output.
4. Choose `explanation-panel` for cross-sections/mechanisms or `node-flow` for staged causal chains.
5. Apply the mechanism-specific composition rules below after the fallback primitive is chosen.
6. Apply tokenized typography, spacing, and radius from `tokens/visual-tokens.md` to labels, panels, callouts, controls, and grouped regions. Literal numbers are allowed for mechanism geometry, not for UI defaults.
7. If the graphic would rely mostly on labels, answer in Markdown or simplify the mechanism instead.

### Core methodology: Mechanism First

**Draw the mechanism itself, not "a diagram about the mechanism"**

- Wrong approach: Drawing a box labeled "Hash Function" with an arrow pointing to "Output"
- Correct approach: Drawing a key being hash-mapped to a specific position in a bucket array, showing how collisions are stored via chaining

### Physical process vs Abstract mechanism

| Type | Visual language | Typical elements |
|------|----------------|------------------|
| Physical | Cross-sections, field lines, pressure gradients, heat flow, molecular interactions | Tokenized surfaces, arrow fields, particles, and gradients only for continuous variables |
| Abstract | Attention matrices, scheduling queues, protocol timelines, pipeline stages | Grids, queue containers, timeline axes, pipes |

### Composition order (outside-in)

1. **Outline/boundary** — Draw the outer shape or system boundary first
2. **Internal structure** — Fill in internal components/layers
3. **Input/Output** — Annotate entry and exit paths
4. **State indicators** — Use color/size/position to express current state
5. **Labels** — Add concise labels last

### Color and meaning

- **Warm tones** (red/orange/yellow) = active / high temperature / high energy / high frequency
- **Cool tones** (blue/cyan/purple) = static / low activity / low energy / cooling
- **Gradients are used only for continuous variables** (temperature, pressure, capacity, concentration) — not for categorical distinctions
- Non-continuous category distinctions use chart-series colors or brand/accent from the token system
- Background remains neutral to let the mechanism stand out

### Annotation specifications

- Use short nouns or verb phrases (e.g., "compress", "distribute", "reclaim")
- **Explanatory text goes in the response text** — only place positioning labels in the diagram
- If numbered steps are needed, use circled numbers (1 2 3), limited to <= 6 steps

### Animation principles

- **Add animation only when the mechanism has inherent motion** (e.g., rotation, flow, oscillation)
- Prefer `stroke-dashoffset` animation (flow sensation) or `opacity` pulse (flash/activation)
- Avoid transform displacement animations (may cause layout jitter in the widget environment)
- Animations must be wrapped in `@media (prefers-reduced-motion: no-preference)`

### SVG practices

- viewBox `0 0 720 H`, width="100%", height="auto"
- Safe area >= 40 units
- Use `<defs>` to define markers and reusable elements; define gradients only when they encode a continuous physical variable
- Group structures using `<g>` with semantic class/id attributes
- For arrows that explain direction, prefer a compact `marker-end` arrowhead with `orient="auto"` and `markerUnits="userSpaceOnUse"` on the same path as the connector. Do not use decorative bracket curves, detached chevrons, reused right-facing triangles, or filled connector paths for reverse/leftward arrows.

### Mechanism silent pre-output constraints

- Draw the mechanism itself, not only boxes and labels.
- Internally choose physical or abstract visual language before emitting SVG.
- Compose in this order: outline → internal structure → input/output → state indicators → labels.
- Use color only for meaning: warm = active/high energy, cool = static/low activity, gradients = continuous variables.
- Keep step numbering <= 6 and labels short; put detailed explanation in the text response.
- Use animation only for inherent motion, and wrap it in `prefers-reduced-motion`.
- Remove decorative elements. If the graphic depends entirely on labels to make sense, simplify or redraw the mechanism.

## Reference materials

| Data relationship / Intent | Reference material | Usage notes |
|---|---|---|
| — | No dedicated template | This scene is methodology-driven; each mechanism requires custom SVG/HTML |

> Do not reference fixed templates as finished layouts. Each mechanism sketch may be custom, but it must first choose `explanation-panel` or `node-flow` from the fallback contract and then follow the composition order and color rules above.

## Composition guidelines

1. **Identify mechanism type**: Physical or Abstract? This determines the visual language
2. **Determine key frames**: Is this a "static cross-section" or a "process sequence"?
   - Single-frame cross-section → one SVG diagram
   - Multi-stage process → 2–3 side-by-side state frames (left→right or top→bottom), or a single diagram with numbered steps
3. **Compose**: Build layer by layer following "outline → structure → I/O → state → labels"
4. **Color**: Use tokenized neutral, brand, accent, or semantic roles by default. Choose warm/cool or gradients only for physical quantities or continuous variables.
5. **Simplify**: Remove details that do not aid understanding; if details are important, split into "overview + zoomed detail"
6. **Verify**: If all labels were removed, would the graphic still convey the general meaning?
7. **Fallback discipline**: Even unique mechanism sketches use neutral surfaces, tokenized meaning colors, tokenized typography, tokenized spacing, and tokenized radius. Warm/cool or gradient exceptions must encode a physical continuous variable, not decoration. If the mechanism does not fit at tokenized text and spacing sizes, simplify, split, or answer in Markdown instead of shrinking below the token scale.
