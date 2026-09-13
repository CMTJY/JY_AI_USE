# Comparison & Decision

Shared contracts: apply `SKILL.md`, this scene file, `templates/manifest.json`, selected `templates/<id>/template.md`, and `tokens/visual-tokens.md`.

## When to enter this scene

The user's intent involves any of the following decision-oriented needs:

- Option comparison (A vs B vs C)
- Technology selection (choosing between frameworks/tools/libraries)
- Risk summary (risk level + impact + mitigation matrix)
- Decision matrix (multi-dimensional weighted scoring)
- Pros/cons analysis (advantages and disadvantages side by side)

Typical trigger words: compare, selection, which is better, difference, recommend, trade-off, comparison, decision matrix, pros and cons.

## When to reject

Do NOT generate a visualization in the following cases — reply with Markdown text instead:

- Only 1 option exists (nothing to compare against)
- Comparison dimensions <= 1 (a single sentence suffices to explain the difference)
- User requests a detailed discussion rather than a summary-style comparison
- Cannot provide a clear recommendation or differentiation focus (all options are essentially identical across all dimensions)
- Options > 4 or dimensions > 7 (information density too high — a Markdown table is more appropriate)

## Generation principles

## Mandatory generation workflow

This workflow is mandatory after routing into this scene.

1. Confirm that a compact visual is clearer than a Markdown table.
2. Identify the comparison shape: matrix, cards, or pros/cons.
3. Check `templates/manifest.json` for ready materials that can provide structure or block styles.
4. Use a ready material as the skeleton when its boundary fits; otherwise choose a fallback primitive.
5. For custom output, choose `decision-cards` or `compact-table-visual` and keep the recommendation, trade-off, neutral-surface, typography, spacing, radius, and focus rules intact.
6. If there is no recommendation or meaningful differentiator, do not render a widget.

### Layout paradigms

**Decision Matrix**: suitable for >= 3 dimensions x >= 3 options
- Rows = comparison dimensions, Columns = options
- Cells use concise markers (icon + short text), no lengthy paragraphs
- Recommended option column uses brand border-left or brand header highlight

**Decision Cards**: suitable for 2–4 options x 3–5 dimensions
- One standalone card per option, arranged horizontally
- Each card lists shared dimensions as divider-separated rows
- Recommended option uses a badge/text cue by default; hover/focus may emphasize any inspected card
- Start from `templates/comparison-cards` when the user wants product, source, vendor, plan, framework, or solution comparison cards
- Keep row content flat: label + right-aligned value or compact bar, without nested row cards
- Keep every option card on the card information hierarchy: title as `--text-title`, row values as `--text-body` or `--text-code`, row labels/tags as `--text-caption`, and no numeric headline beyond `--text-title`

**Pros/Cons Layout**: suitable for binary choices with only 2 options
- Left/right or top/bottom split
- Positive items use `--success` or `--brand` markers only when the meaning is explicit; negative or trade-off items use `--warning`, `--danger`, or `--text-muted` markers

### Information density constraints

- Number of options: 2–4 (filter to the most representative if exceeded)
- Comparison dimensions: 3–5 (split into core and secondary dimensions if exceeded)
- Text per cell: <= 15 words or 1 icon + keyword
- If a dimension can be normalized, use a small bar with a value label; keep qualitative dimensions as text
- Tags are summary cues only: max 1-2 per option

### Recommendation and focus

- **Must have a clear recommendation** or **differentiation focus** — if all options are equal and no recommendation is possible, do not enter this scene
- Recommended option uses brand text/badge emphasis by default; reserve card border emphasis for hover/focus or explicit selection
- Non-recommended options maintain neutral surface
- Do not render a default selected card; recommendation is a badge/text cue, while hover/focus provides inspected-state emphasis
- Do not append recommendation rationale or conclusion text below the matrix/cards; keep rationale in the surrounding response.

### Trade-off presentation

- Do not show only advantages (pros) — trade-offs/cons must also be displayed
- Icons may distinguish: check mark (advantage) / warning triangle (trade-off) / neutral dot (neutral)
- Avoid one-sided presentation

### Style specifications

- Card/cell backgrounds: neutral surface (`--surface` or `--surface-muted`)
- Recommendation marker: `--brand` border or badge
- Text hierarchy: titles use `--text-title` with medium weight, content uses the `--text-body` baseline, and annotations use `--text-caption` with muted color
- Metric hierarchy: row values use `--text-body` or `--text-code`; KPI-first comparison may use one `--text-title` numeric emphasis per option, not for every value
- Keep labels short: dimension names 2–5 words, option titles 6–10 words
- Radius roles: option cards use `--radius-card`; cells, tags, and compact controls use `--radius`
- Spacing roles: use `--spacer-*` tokens for card padding, row gaps, grid gutters, tags, legends, and compact controls
- Internal rows should use dividers, bars, and tokenized spacing before adding containers

### Responsiveness

- 2 options: side by side (flex-row)
- 3–4 options: auto-wrap on narrow viewports (flex-wrap) or switch to vertical stacking
- Matrix layout uses grid with `min-width` to prevent columns from compressing too narrow
- Card layout uses grid with `minmax(0, 1fr)` and switches to vertical stacking on narrow viewports

### Decision silent pre-output constraints

- Use this scene only when there are 2–4 options and 3–5 meaningful dimensions.
- Choose the layout first: matrix, cards, or pros/cons.
- Mark one recommendation or one key differentiating dimension before styling.
- Show both advantages and trade-offs; avoid one-sided comparison.
- Keep cell text <= 15 words and use responsive wrapping/stacking.
- Verify every card title, metadata, row label, row value, tag, badge, and optional metric uses the card information hierarchy from `tokens/visual-tokens.md`.
- Do not add rationale or conclusion text below the visual.

## Reference materials

| Data relationship / Intent | Reference material | Usage notes |
|---|---|---|
| Product/source/vendor/plan comparison cards | `comparison-cards` | Use for 2-4 standalone option cards with divider rows, compact bars, max 2 tags, and an optional recommendation badge |
| Card container styles | `architecture-elements` (block styles) | Borrow neutral/brand block border, radius, and padding specifications |

## Composition guidelines

1. **Assess options x dimensions**: Decide whether to use Matrix, Cards, or Pros/Cons layout
2. **Determine recommendation/focus**: First clarify which option is recommended or which dimension is the key differentiator
3. **Build skeleton**:
   - Matrix → `<table>` or CSS Grid
   - Cards → `<div>` flex container
   - Pros/Cons → two-column flex or grid
4. **Fill content**: Each cell uses icon + keyword, no more than 15 words
5. **Apply emphasis**: Add brand border/badge to the recommended option; bold/highlight the key differentiating dimension
6. **Keep rationale out of UI**: Put recommendation summaries and rationale in the response text, not below the diagram
7. **Fallback discipline**: Custom decision visuals must use `decision-cards` or `compact-table-visual`; do not introduce pricing-page cards, hero sections, colorful status-card fills, non-token font sizes, non-token spacing, or custom radius values.
