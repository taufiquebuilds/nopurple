# Contributing to nopurple

Thanks for helping. The most useful contributions:

1. **New slop patterns:** something that marks a deck or chart as AI-made, with what a designer would do instead. Open a "New slop pattern" issue with an example.
2. **Themes:** a new `[data-theme="..."]` block in `skills/slides/templates/deck.html` and the same colours in `THEMES` in `skills/charts/scripts/chart_style.py`. Keep the background neutral, use one accent and check contrast.
3. **Layouts and chart types:** a new slide layout with its snippet in `skills/slides/references/layouts.md`, or a new chart function in `chart_style.py`, with a rendered screenshot in the pull request.

## Rules for changes

- Each `SKILL.md` is read on every use, so keep it short. Put detail in the skill's `references/`.
- Keep the deck template's CSS plain ASCII. Use `"\201C"` rather than a literal curly quote, because agents sometimes flatten them while copying.
- The checkers use the Python standard library only. `chart_style.py` may use matplotlib.
- Render your change and look at it before opening a pull request: `python3 skills/slides/scripts/render.py skills/slides/templates/deck.html` for slides, or run a chart through `chart_style.py`.

## Before you open a pull request

```sh
pip install matplotlib   # for the chart tests; they are skipped without it
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

If you bump the version, change it in every `skills/*/SKILL.md`, both `plugin.json` files and the first `CHANGELOG.md` heading.

By contributing, you agree that your contributions are licensed under the MIT License.
