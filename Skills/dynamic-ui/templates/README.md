# Templates

This directory stores reusable Dynamic UI generation materials.

Templates are not frontend components. They are source examples and behavior contracts for PureShowWidget-compatible `widget_code` fragments.

Templates are materials, not rigid constraints. The model may reference one material, mix CSS or interaction patterns from multiple materials, or generate a custom fragment when no material fits and the scene contract allows it.

Every ready template folder must contain:

```text
templates/<template-id>/
  template.md
  widget-code.html
  fixture.json
```

Template folders sit directly under `templates/`. Do not add another family or category directory.

Only keep folders that contain an implemented template. Do not keep empty placeholder folders for future templates.

## File Roles

`template.md`

- Explains when to use the template.
- Explains when to avoid the template and which existing template or custom path to use instead.
- Defines the expected data shape.
- Lists visual rules and limits.
- Lists required interaction behavior, including tooltip, hover, legend, focus, or selection rules.
- Documents boundary and edge cases such as null values, empty data, long labels, dense data, missing libraries, and unsupported scale types.
- Lists implementation assumptions.
- Lists acceptance checks that can be verified before upload.
- Points to related templates to use instead.

`widget-code.html`

- Contains the real HTML/SVG/CSS/JS fragment.
- Starts with `<style>`.
- Contains widget markup after styles.
- Ends with `<script>` only when needed.
- Does not include `<!DOCTYPE html>`, `<html>`, `<head>`, or `<body>`.
- Uses `.widget` with `data-dynamic-ui-widget` and `data-template="<template-id>"` on the root.
- Uses a stable root selector in scripts; never rely on `document.currentScript`, `previousElementSibling`, or source adjacency.
- Sets `data-mounted="true"` before binding events or loading external libraries.
- Keeps DOM reads and writes scoped to the widget root.
- For charts, renders a visible HTML/SVG fallback or SVG output before relying on external libraries.
- Treats Chart.js as progressive enhancement when Chart.js is used; the widget must remain useful if Chart.js or the CDN fails.
- Preserves every required interaction declared by `template.md`; do not drop tooltip, hover, focus, or legend behavior while adapting data.
- For Shadcn-like chart tooltips, uses widget-scoped HTML tooltip markup and disables the default Chart.js canvas tooltip.
- Uses an 8px circular `.tooltipDot` for every tooltip color marker; do not use line, square, pill, or text-only category markers.

`fixture.json`

- Provides sample data for direct browser checks and tuning.
- Should be small, realistic, and easy to replace.
- Must not contain private or production data.
- Should stay aligned with the visible data and fallback geometry in `widget-code.html`.

## Template IDs

The folder name is the template ID used by `manifest.json` and `data-template`.

Current implemented templates:

- `templates/line-trend`
- `templates/bar-chart-multiple`
- `templates/scatter-chart`
- `templates/gantt-chart`
- `templates/funnel-bar-chart`
- `templates/sankey-chart`
- `templates/heatmap-chart`
- `templates/pie-donut-text`
- `templates/bar-stacked-legend`
- `templates/pie-chart-label-list`
- `templates/radar-chart-legend`
- `templates/radar-chart-lines-only`
- `templates/comparison-cards`
- `templates/tree-flow`
- `templates/architecture-elements`
- `templates/sequence-diagram`

Use `../scenes/*.md` for scene-level routing and composition guidance. Use `manifest.json` to verify implemented template IDs, status, kind, scene, and machine-readable intent. When no ready template matches, custom output must choose a fallback primitive instead of freehand styling. Do not encode the category in the folder path. When adding a future template, create its folder and update scene references plus the manifest in the same change.

## Cross-File Sync

Use the scene files as the human-readable routing layer. Use `templates/manifest.json` as the machine-readable implemented-template list.

When adding, renaming, removing, or changing the intent of a template, update the folder, manifest, relevant scene file, and README inventory together. Do not leave a manifest entry, scene reference, or README bullet without a matching implemented folder.


## Validation

After changing chart templates, fixtures, or color guidance, manually verify ordinary chart data mappings do not use accent or semantic colors as peer-source colors. The Sankey seven-color sequence is allowed only inside `templates/sankey-chart`.
