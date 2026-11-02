# Guide for agents working on this repo

nopurple is an agent skill. `SKILL.md` is the prompt, `references/` holds detail it loads on demand, `templates/deck.html` is the deck template, and `scripts/` holds standard-library Python helpers.

- Keep `SKILL.md` under 3,000 words. `scripts/validate_package.py` enforces it and checks that versions and descriptions match across manifests.
- Keep the template's CSS ASCII-only (a test enforces it).
- The skill must never invent numbers, quotes, names or dates. Keep that rule intact in any edit.
- Run `python3 scripts/validate_package.py` and `python3 -m unittest discover -s tests` before committing.
