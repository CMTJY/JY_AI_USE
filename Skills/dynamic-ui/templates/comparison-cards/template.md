# Comparison Cards - Material Description

A clean comparison card group for 2-4 options across shared decision dimensions. widget-code.html contains:
- Three standalone option cards arranged horizontally
- Card header primitives (badge, title, metadata)
- Compact comparison rows using dividers instead of nested row containers
- Numeric/text rows aligned to the right; measurable rows use short horizontal bars
- Tag row limited to 1-2 short attributes per option and aligned to the same content baseline as the header and metric rows
- Recommended state is shown through badge text; hover/focus can emphasize any card

Reusable primitives:
- Responsive card grid for 2-4 options
- Clean card header with badge, title, and metadata
- Divider-based metric rows that avoid card-inside-card nesting
- Right-aligned value slots that can show text or a compact bar
- Hover/focus border using `--brand` with neutral card fill
- Mobile stacking with preserved row rhythm and readable body text

Use when:
- Comparing products, plans, vendors, sources, models, frameworks, or solution options
- The user needs a concise recommendation or clear differentiation focus
- There are 2-4 options and 3-5 shared dimensions

Avoid when:
- There is only one option
- The comparison has more than 4 options or more than 7 dimensions
- Exact numeric matrix analysis is more important than decision readability
- The design would require more than 2 tags per option
- A plain Markdown table is sufficient

Expected data shape:

```json
{
  "title": "Framework Comparison",
  "focus": "Recommended",
  "options": [
    {
      "id": "react",
      "label": "React 19",
      "meta": "Meta - UI library - 2013",
      "badge": "Recommended",
      "recommended": true,
      "metrics": [
        { "label": "Usage rate", "value": "44.7%" },
        { "label": "Performance", "value": "86", "score": 86 }
      ],
      "tags": ["Top ecosystem", "Cross-platform"]
    }
  ]
}
```

Visual rules and limits:
- Use 2-4 option cards and 3-5 visible metric rows by default.
- Keep option cards as neutral `--surface`; do not tint the whole card for recommendation.
- Use brand only for the recommended badge, hover/focus border, or one focal text cue.
- Card titles use `--text-title` with medium weight; metadata, badges, tags, and metric labels use `--text-caption`; row values use `--text-body` or `--text-code`.
- Do not introduce metric-size typography in this template; if each option has one comparable headline KPI, keep it at `--text-title`.
- Use the same metric-bar color across options unless the bar color encodes explicit meaning.
- Keep metric labels 2-5 words and option names 6-10 words or shorter.
- Do not nest cards inside metric rows; use dividers, bars, and aligned text.

Interaction behavior:
- Cards may be keyboard-focusable for inspected-state emphasis.
- Hover/focus changes only the border or a focal text cue subtly; it is not a persistent selected state.
- No inline event handlers are needed for the default material.

Boundary and edge cases:
- Empty options: do not render this template.
- One option: answer in Markdown or use a single recommendation panel, not comparison cards.
- More than 4 options: filter to the strongest 2-4 candidates or switch to `compact-table-visual`.
- More than 7 dimensions: use a Markdown table or compact table visual.
- Null metric value: show `Unknown` or omit the row; do not convert unknown values to zero.
- Long labels: shorten visibly; exact wording can move to response text.
- Long tags: keep max 2 tags and allow wrapping or truncation instead of overflow.
- Missing scores: render the value as text instead of a metric bar.
- Multiple unrelated numeric values: keep them as rows or compact bars; do not promote all of them to large headline numbers.

Implementation assumptions:
- `score` is normalized to 0-100 when present.
- `recommended: true` is optional; if omitted, the visual still needs a clear differentiator.
- `fixture.json` is sample data only and must not be treated as live benchmark truth.
- The root uses `data-dynamic-ui-widget` and `data-template="comparison-cards"`.

Acceptance checks:
- The widget starts with `<style>` and has no page shell.
- Desktop shows separate option cards with aligned row rhythm.
- Narrow width stacks cards vertically without text overflow.
- Recommendation is visible through badge/text, not a default selected border.
- Card typography follows the information hierarchy: no oversized titles, no ad hoc font sizes, and no multiple large KPI numbers.
- Metric bars stay on token colors and do not use raw chart colors outside token definitions.
- Tags do not touch card borders or overflow their card.
- No summary footer, recommendation rationale, or conclusion copy appears below the cards.
