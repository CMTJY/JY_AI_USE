# Gantt Chart

Use this template for a compact Frappe Gantt-inspired project schedule when task timing, progress, dependencies, and a critical path are the main story.

Source inspiration:

- `https://frappe.io/gantt`
- `https://github.com/frappe/gantt`

The implementation is not a Frappe runtime embed. Dynamic UI templates must output a PureShowWidget-compatible fragment, so `widget-code.html` translates the source behavior into static HTML/SVG plus scoped vanilla JavaScript for weekly tick rendering, dependency routing, and popup inspection.

## Use When

- A project plan has 3-8 tasks with start and end dates.
- Dependencies or phase sequencing matter more than a simple date list.
- Progress is useful context but not the only metric.
- The visual can fit in one inline card with one local control concept.
- The reader needs a schedule view similar to a lightweight Gantt chart, not a full project management app.

## Avoid When

- The user needs editing, drag-rescheduling, resource assignment, or baseline comparison. Use a real planning tool instead.
- There are more than eight visible tasks. Group phases first or summarize the critical path.
- Exact daily capacity, resource allocation, or earned-value analysis is required. Use a table or a dedicated project report.
- Tasks have no meaningful dates. Use a flowchart or checklist instead.
- Multiple projects need comparison. Use a grouped bar or table pattern instead.

## Data Shape

```json
{
  "title": "Launch schedule",
  "start": "2026-07-01",
  "end": "2026-08-16",
  "today": "2026-07-24",
  "tasks": [
    {
      "id": "ux-spec",
      "name": "UX spec",
      "owner": "Design",
      "start": "2026-07-10",
      "end": "2026-07-19",
      "progress": 72,
      "status": "In progress",
      "dependencies": ["discovery"],
      "critical": true
    }
  ],
  "holidays": [
    { "start": "2026-07-04", "end": "2026-07-06", "label": "Weekend" }
  ]
}
```

## Visual Rules

- Keep one focal point: the critical path or the schedule risk.
- Use a left task rail and a right timeline grid; do not turn the template into a kanban board or app shell.
- Use `--chart-series-1` or `--brand` for the primary critical path.
- Use softer brand steps for non-critical tasks; color should encode emphasis, not arbitrary task order.
- Keep summary cards on neutral gray surfaces. Emphasis may use a brand border or text only; do not use blue-, purple-, semantic-, or chart-tinted auxiliary card fills.
- Use one solid fill per task bar. Do not encode progress as a second purple fill unless a future variant adds an explicit legend.
- Do not add colored glows or shadows to task bars. The critical path should read through fill, label, and position.
- Keep progress in the popup or nearby text when it is useful context.
- Render weekend, holiday, or blocked bands as low-emphasis neutral overlays.
- Align vertical grid dividers to the same tick weights used by the date header; overlays must not introduce extra divider borders.
- Render the current date as a single vertical line when it falls inside the range.
- Use dependency arrows only where a real finish-to-start or phase dependency exists.
- Draw dependencies as light rounded connector lines without arrowheads, dots, or endpoint markers.
- Extend dependency line endpoints slightly under task bars so the bars cover line caps and no endpoint artifact appears beside the bar.
- Use the normal sans text font for dates and numeric labels; reserve mono/code font for real code identifiers only.
- Keep task names short enough for the left rail; put owner and dates in the popup.
- Render a real static schedule before JavaScript runs. The fallback must include task rows, bars, time labels, and at least the main dependency context.
- Locate the widget root with a stable `[data-dynamic-ui-widget][data-template="gantt-chart"]` selector. Do not use `document.currentScript` or DOM sibling traversal.
- Keep the chart compact. If the schedule needs horizontal scrolling to be useful, reduce scope before using this inline template.

## Required Interaction

- Preserve the hover and keyboard-focus popup when adapting this template. It is part of the contract.
- Use the widget-scoped `.chartTooltip` HTML popup with a circular task color dot, task name, owner, date window, progress, status, and dependency count.
- Keep the tooltip mounted at the outer `.ganttCard` layer, above the clipped timeline grid, so hover content is not cropped by the chart frame.
- Clamp popup placement inside the outer card and flip placement below the bar when needed.
- Keep the timeline fixed to weekly granularity; do not add day, month, tab, page, or hidden app-view controls.
- Re-route dependency arrows after viewport resize.
- Do not add drag-and-drop editing. That belongs to the original Frappe library, not this inline template.

## Edge Cases

- `null`, missing, unparsable, or inverted task dates mark the task as invalid and keep the rest of the schedule readable.
- Progress is clamped to `0-100`.
- Tasks outside the visible range are clamped to the chart edge; disclose the actual dates in the popup.
- Dependencies that point to missing task ids are ignored instead of drawing broken arrows.
- If every task is invalid, keep the static layout readable and show a compact status note.
- If `today` is outside the visible range, hide the line by setting it to low opacity rather than shifting the timeline.
- Long task names should truncate in the rail and remain available in the popup.
- If JavaScript fails, the static bars, labels remain readable; only dynamic arrows and popup behavior are lost.
- If the final script executes after fragment injection and `document.currentScript` is `null`, initialization must still find the widget root.

## Implementation Assumptions

- The widget is rendered as one inline fragment, not as a page or Frappe component.
- Data is small and embedded directly in the fragment.
- The sample schedule covers one bounded project window.
- The template author updates task rows, static bar positions, dependency fallback paths, and fixture data together when replacing the sample.
- Timeline granularity is fixed to week; the template does not fetch or recalculate external project data.

## Acceptance Checks

- `widget-code.html` starts with `<style>`.
- The middle block is one `.widget` fragment.
- The final block is the only executable `<script>`.
- No `DOCTYPE`, `<html>`, `<head>`, `<body>`, React, JSX, router, export UI, or external package dependency appears.
- No `document.currentScript`, `previousElementSibling`, or root lookup by source adjacency appears.
- The chart area is real HTML/SVG, not canvas-only first paint.
- Task bars, dependency arrows, today marker are visible before JavaScript runs.
- Tooltip markup exists in the widget HTML and is driven by scoped vanilla JavaScript.
- Hover and keyboard focus activate the corresponding task bar.
- `templates/manifest.json` marks `gantt-chart` as ready.
