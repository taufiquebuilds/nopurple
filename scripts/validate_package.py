#!/usr/bin/env python3
"""Check that the nopurple skill pack is consistent before a release.

Usage: python3 scripts/validate_package.py

For every skill in skills/*/: the SKILL.md frontmatter names it
nopurple-<folder>, has a description, and carries the pack version, every
file it points to exists, and it stays short enough to read on every use.
For the pack: manifests parse, list every skill, and agree on version and
description with each other and with the first CHANGELOG.md heading.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_WORDS = 3000
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    data, current = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\S[^:]*:", line):
            key, _, val = line.partition(":")
            current = key.strip()
            data[current] = val.strip()
        elif current and line.strip():
            k, _, v = line.strip().partition(":")
            data[f"{current}.{k.strip()}"] = v.strip()
    return data


manifests = {}
for rel in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".cursor-plugin/plugin.json"]:
    try:
        manifests[rel] = json.loads((ROOT / rel).read_text())
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{rel}: {e}")

plugin = manifests.get(".claude-plugin/plugin.json", {})
version = plugin.get("version")
description = plugin.get("description")
check(bool(version), ".claude-plugin/plugin.json needs a version")
cursor = manifests.get(".cursor-plugin/plugin.json", {})
check(cursor.get("version") == version, "Cursor plugin version must match the Claude plugin version")
check(cursor.get("description") == description, "Cursor plugin description must match the Claude plugin")
for p in manifests.get(".claude-plugin/marketplace.json", {}).get("plugins", []):
    check(p.get("description") == description, "marketplace.json plugin description must match plugin.json")

changelog = (ROOT / "CHANGELOG.md").read_text()
heading = re.search(r"^## \[?v?([\d.]+)", changelog, re.M)
check(bool(heading) and heading.group(1) == version, f"First CHANGELOG.md heading must be version {version}")

skill_dirs = sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))
check(bool(skill_dirs), "No skills found in skills/*/SKILL.md")
listed = sorted(Path(s).name for s in plugin.get("skills", []))
check(listed == [d.name for d in skill_dirs],
      f"plugin.json skills {listed} must list every folder in skills/: {[d.name for d in skill_dirs]}")

summary = []
for d in skill_dirs:
    text = (d / "SKILL.md").read_text()
    fm = frontmatter(text)
    rel = d.relative_to(ROOT)
    check(fm.get("name") == f"nopurple-{d.name}", f"{rel}/SKILL.md name must be nopurple-{d.name}")
    check(bool(fm.get("description")), f"{rel}/SKILL.md needs a description")
    check(fm.get("metadata.version") == version, f"{rel}/SKILL.md metadata.version must be {version}")
    for ref in sorted(set(re.findall(r"`((?:references|scripts|templates)/[\w./-]+)`", text))):
        check((d / ref).exists(), f"{rel}/SKILL.md points to {ref}, which does not exist")
    words = len(re.findall(r"\S+", text))
    check(words <= MAX_WORDS, f"{rel}/SKILL.md has {words} words; keep it under {MAX_WORDS}")
    summary.append(f"{d.name} ({words} words)")

if errors:
    print("Package check failed:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"Package OK: version {version}, skills: {', '.join(summary)}")
