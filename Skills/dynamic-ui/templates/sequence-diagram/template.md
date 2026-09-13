# Sequence Diagram

Use this template for compact ZenUML-inspired sequence diagrams when the answer needs to show ordered calls, returns, async handoffs, activations, or a short protocol between actors.

Source inspiration:

- `https://docs.zenuml.com/`
- `https://docs.zenuml.com/customizing.html`

The implementation is not a ZenUML runtime embed or parser. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` translates ZenUML sequence concepts into static HTML/SVG with tokenized participant, lifeline, message, return, and occurrence styles.

## Use When

- A call chain, request lifecycle, protocol handshake, or service interaction has 3-5 participants.
- Message order matters more than module topology or numeric magnitude.
- Request and return pairs need to be visible in one inline card.
- One critical message, participant, phase boundary, or risk path can be made the focal point.

## Avoid When

- The user needs to paste arbitrary ZenUML DSL and have it parsed. Use the ZenUML tool itself or generate Mermaid/ZenUML text instead.
- The flow has more than 8 visible messages or more than 5 participants. Group phases or split into multiple diagrams.
- The relationship is a dependency tree or architecture map. Use `tree-flow` or `architecture-elements`.
- The user needs editing, drag/drop, zoom, export, or a full diagramming app.

## Data Shape

```json
{
  "title": "Checkout auth sequence",
  "source": "https://docs.zenuml.com/",
  "participants": [
    { "id": "client", "label": "Client", "role": "external" },
    { "id": "gateway", "label": "Gateway", "role": "focus" }
  ],
  "messages": [
    {
      "id": "m1",
      "from": "client",
      "to": "gateway",
      "label": "POST /checkout",
      "type": "request",
      "focus": true
    }
  ],
  "activations": [
    { "participant": "gateway", "start": "m1", "end": "m6" }
  ]
}
```

## Visual Rules

- Use a neutral card with a participant row, vertical lifelines, horizontal message rows, and short label capsules.
- Use ZenUML-style participant, lifeline, message, and occurrence concepts, but keep colors on Dynamic UI tokens.
- Keep lifelines neutral. Use `--brand` for one focal participant or one focal message only.
- Use solid arrows for calls and dashed arrows for returns or async/optional handoffs.
- Use compact arrowheads: each message arrowhead should be an approximately `8x8` filled triangle, matching the global connector rule.
- Keep message labels to 1-4 words or a short endpoint such as `POST /checkout`.
- Place message label capsules directly on the message line; the capsule surface may cover the line behind it.
- Use the shared `marker-end` pattern with `orient="auto"` and `markerUnits="userSpaceOnUse"` for sequence arrows. Do not emit separate polygon arrowheads in generated sequence diagrams.
- Put phase notes in compact chips above or below the diagram, not on top of message arrows.
- Do not color every participant differently. Sequence order is encoded by vertical position, not color.
- On narrow widths, switch to a compact participant grid plus ordered message list instead of shrinking the SVG until labels become unreadable.

## Required Interaction

- No JavaScript interaction is required.
- CSS hover or focus may emphasize a message row, but the static diagram must carry the full meaning without interaction.
- Do not add drag, zoom, pan, collapsible branches, copy buttons, or code editors.

## Edge Cases

- Missing participant ids are invalid; drop the broken message before rendering.
- Null message labels should become `call`, `return`, or another short generic label.
- Long labels should be shortened in the diagram and explained in normal response text.
- Self calls need a compact loop arrow beside the participant; do not draw a line across the whole diagram.
- Dense nested `if`, `loop`, or `par` fragments should be grouped as a phase chip or split into another visual.
- If every message is equally important, choose a focal message before rendering.

## Implementation Assumptions

- Participant x positions are precomputed; this template does not parse source DSL or auto-layout arbitrary code.
- The template is static SVG/HTML and does not load external libraries.
- The sample sequence is small enough for one inline card.
- Template authors keep participant labels, message geometry, activation bars, and fixture data synchronized.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment with `data-dynamic-ui-widget` and `data-template="sequence-diagram"`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, export UI, or app shell appears.
- No `position: fixed`, inline event handlers, `document.currentScript`, or `previousElementSibling` appears.
- The SVG viewBox contains every participant, lifeline, activation, arrow, label capsule.
- Every connector path has `fill="none"` and labels do not sit directly on top of strokes.
- The diagram remains readable at desktop width and the compact message list remains readable at narrow inline widths.
- `templates/manifest.json` marks `sequence-diagram` as ready.

## Related Templates

- Use `tree-flow` for dependency trees and left-to-right node flows.
- Use `architecture-elements` for system/module architecture diagrams.
- Use `gantt-chart` for schedule and dependency timing.
