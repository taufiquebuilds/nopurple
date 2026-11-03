# Changelog

## 0.2.0 (2026-11-03)

nopurple is now a pack of skills. Slides moved to `skills/slides`, and there is a new charts skill.

- New `nopurple-charts` skill (`skills/charts`): rules for charts that make one point, a guide to choosing the chart, and settings for matplotlib, Plotly, Chart.js, Recharts, Vega-Lite, Excel and Google Sheets.
- `skills/charts/scripts/chart_style.py`: matplotlib kit with `hbar`, `bar`, `line`, `slope` and `finish`, in the same 6 themes as the slides. Labels are spaced so they don't overlap.
- `skills/charts/scripts/chart_check.py`: scores chart code (`.py`, `.ipynb`, `.js`, `.ts`, `.jsx`, `.tsx`, `.json`, `.html`) for pies, 3D, rainbow colours, truncated bars, dual axes, rotated labels, gridlines, legends and topic titles.
- The slides skill is now named `nopurple-slides`. Its scripts moved to `skills/slides/scripts/`.

## 0.1.0 (2026-11-02)

First release.

- `SKILL.md`: the rules and a 7-step workflow, from storyline to rendered, checked deck.
- `templates/deck.html`: one-file HTML deck with 6 themes and 10 layouts, including honest bar charts.
- `scripts/render.py`: renders every slide to PNG plus a PDF with Chrome, Chromium or Edge.
- `scripts/slop_check.py`: scores `.html`, `.pptx` and `.md` decks for AI-slop patterns.
- References for writing, layouts, design, charts and PowerPoint output.
