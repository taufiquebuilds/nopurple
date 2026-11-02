# Contributing to nopurple

Thanks for helping. The most useful contributions:

1. **New slop patterns:** something that marks a deck as AI-made, with what a designer would do instead. Open a "New slop pattern" issue with an example.
2. **Themes:** a new `[data-theme="..."]` block in `templates/deck.html`. Keep the background neutral, use one accent and check contrast.
3. **Layouts:** a new layout class, its snippet in `references/layouts.md`, and a rendered screenshot in the pull request.

## Rules for changes

- `SKILL.md` is read on every use, so keep it short. Put detail in `references/`.
- Keep the template's CSS plain ASCII. Use `"\201C"` rather than a literal curly quote, because agents sometimes flatten them while copying.
- Scripts use the Python standard library only.
- Render your change (`python3 scripts/render.py templates/deck.html`) and look at it before opening a pull request.

## Before you open a pull request

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

If you bump the version, change it in `SKILL.md`, both `plugin.json` files and the first `CHANGELOG.md` heading.

By contributing, you agree that your contributions are licensed under the MIT License.
