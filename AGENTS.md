# Guide for agents working on this repo

nopurple is a pack of agent skills. Each folder in `skills/` is one skill: `SKILL.md` is the prompt, `references/` holds detail it loads on demand, and `scripts/` holds Python helpers. `skills/slides/templates/deck.html` is the deck template.

- Keep every `SKILL.md` under 3,000 words. `scripts/validate_package.py` enforces it and checks that names, versions and descriptions match across the skills and manifests.
- A new skill goes in `skills/<name>/`, is named `nopurple-<name>`, and is listed in `.claude-plugin/plugin.json`.
- Keep the deck template's CSS ASCII-only (a test enforces it).
- Checkers (`slop_check.py`, `chart_check.py`) use the standard library only. `chart_style.py` needs matplotlib.
- The skills must never invent numbers, quotes, names or dates. Keep that rule intact in any edit.
- Run `python3 scripts/validate_package.py` and `python3 -m unittest discover -s tests` before committing.
