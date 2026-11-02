"""Tests for the helper scripts. Run with: python3 -m unittest discover -s tests"""

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


slop = load("slop_check")


def score(path):
    slides, css = slop.load(Path(path))
    per = [slop.check_slide(s) for s in slides]
    deck = slop.check_deck(slides, css)
    return slides, per, deck


class SlopCheckTests(unittest.TestCase):
    def test_template_deck_is_clean(self):
        slides, per, deck = score(ROOT / "templates" / "deck.html")
        self.assertEqual(len(slides), 7)
        # The template's only deck issue is its own example text.
        self.assertTrue(deck and all("Example text" in m for _, m in deck), deck)
        self.assertTrue(all(not i for i in per), per)

    def test_ai_deck_is_flagged(self):
        slides, per, deck = score(ROOT / "examples" / "before-ai-deck.html")
        msgs = " ".join(m for _, m in deck) + " " + " ".join(m for iss in per for _, m in iss)
        for expected in ["Purple gradient", "font families", "Topic title", "Emoji", "bullets",
                         "Hype words", "Vague claim", "Thank you"]:
            self.assertIn(expected, msgs)

    def test_comment_in_template_is_not_a_slide(self):
        slides, _, _ = score(ROOT / "templates" / "deck.html")
        titles = [s["title"] for s in slides]
        self.assertEqual(titles[0], "Retention is our growth engine now")
        self.assertNotIn("LAYOUT", " ".join(s["text"] for s in slides))

    def test_pptx_placeholder_titles(self):
        slides, per, _ = score(FIX / "sample.pptx")
        self.assertEqual([s["title"] for s in slides][:2], ["🚀 Q3 Review", "Agenda"])
        self.assertEqual(slides[1]["bullets"], 7)
        self.assertEqual(per[2], [])

    def test_pptx_textbox_titles_use_largest_text(self):
        slides, per, _ = score(FIX / "recipe.pptx")
        self.assertEqual(slides[0]["title"], "We kept 94% of clients this quarter, up from 81%.")
        self.assertEqual(per, [[], []])

    def test_markdown_deck(self):
        md = "---\nmarp: true\n---\n\n# Overview\n\n- a\n- b\n\n---\n\n# Revenue rose 12% in Q3\n\nTwo enterprise deals closed.\n<!-- note: from CRM -->\n"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(md)
        slides, per, _ = score(f.name)
        self.assertEqual([s["title"] for s in slides], ["Overview", "Revenue rose 12% in Q3"])
        self.assertTrue(per[0])
        self.assertEqual(per[1], [])

    def test_quarter_labels_are_not_evidence(self):
        self.assertTrue(slop.check_slide({"title": "Retention rose sharply in Q3", "bullets": 0,
                                          "text": "Significant improvements in Q4"}))

    def test_purple_detection_by_hue(self):
        self.assertTrue(slop.purple_gradient("background: linear-gradient(90deg, #7a3cf0, #e0e0e0)"))
        self.assertFalse(slop.purple_gradient("background: linear-gradient(90deg, #f6f4ef, #ffffff)"))

    def test_cli_json(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "slop_check.py"),
                            str(ROOT / "examples" / "before-ai-deck.html"), "--json"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn('"score"', r.stdout)


class LeftoverTests(unittest.TestCase):
    def test_flattened_quotes_are_caught(self):
        _, css = ("", '.quote blockquote::before { content: """; }')
        issues = slop.check_deck([{"title": "A point", "text": "x"}], css)
        self.assertTrue(any("Broken CSS" in m for _, m in issues))

    def test_template_css_is_ascii(self):
        html = (ROOT / "templates" / "deck.html").read_text(encoding="utf-8")
        css = html[html.index("<style>"):html.index("</style>")]
        self.assertTrue(all(ord(c) < 128 for c in css))


class TemplateTests(unittest.TestCase):
    def test_bar_heights_are_proportional(self):
        html = (ROOT / "templates" / "deck.html").read_text()
        bars = re.findall(r'style="--v: (\d+)"><b>(\d+)%', html)
        values = [int(v) for _, v in bars]
        for pct, v in bars:
            self.assertEqual(int(pct), round(int(v) / max(values) * 100))

    def test_every_theme_defines_the_tokens(self):
        html = (ROOT / "templates" / "deck.html").read_text()
        for theme in ["ink", "swiss", "forest", "sand", "mono"]:
            block = re.search(r'\[data-theme="%s"\] \{(.*?)\}' % theme, html, re.S).group(1)
            for token in ["--bg", "--fg", "--muted", "--accent"]:
                self.assertIn(token, block, theme)


class PackageTests(unittest.TestCase):
    def test_package_validates(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_package.py")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
