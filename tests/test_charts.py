"""Tests for the charts skill scripts. Run with: python3 -m unittest discover -s tests"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "skills" / "charts"
FIX = ROOT / "tests" / "fixtures"


def load(name):
    spec = importlib.util.spec_from_file_location(name, CHARTS / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check = load("chart_check")

try:
    import matplotlib  # noqa: F401
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def messages(path):
    return [m for _, _, m in check.check(check.read(Path(path)))]


class ChartCheckTests(unittest.TestCase):
    def test_clean_fixtures_score_100(self):
        for name in ["chart_clean.py", "chart_clean.vl.json"]:
            issues = check.check(check.read(FIX / name))
            self.assertEqual(check.score(issues), 100, (name, issues))

    def test_style_kit_is_clean(self):
        issues = check.check(check.read(CHARTS / "scripts" / "chart_style.py"))
        self.assertEqual(issues, [])

    def test_python_slop_is_caught(self):
        found = " ".join(messages(FIX / "chart_slop.py"))
        for words in ["Pie", "Exploded", "shadow", "Emoji", "Topic title", "start at zero",
                      "Gridlines", "Rotated", "Dual y-axes", "Rainbow colour list", "Legend"]:
            self.assertIn(words, found)
        self.assertEqual(check.score(check.check(check.read(FIX / "chart_slop.py"))), 0)

    def test_chartjs_slop_is_caught(self):
        found = " ".join(messages(FIX / "chart_slop.js"))
        for words in ["Pie or donut", "Rainbow colour list", "Emoji", "Topic title", "Legend"]:
            self.assertIn(words, found)

    def test_finding_titles_pass(self):
        ok = 'ax.set_title("Google Ads brought 42% of all leads")\nax.set_title(f"{share:.0%} came from ads")'
        self.assertEqual(check.check(ok), [])
        self.assertTrue(check.check('ax.set_title("Revenue Analysis")'))

    def test_big_figure_text_is_a_title(self):
        self.assertTrue(check.check("fig.text(0.08, 0.94,\n    'Leads by Channel',\n    fontsize=24, color=c)"))
        self.assertEqual(check.check("fig.text(0.08, 0.04, 'Total Leads', fontsize=12)"), [])

    def test_axis_titles_are_ignored(self):
        self.assertEqual(check.check('fig.update_layout(xaxis=dict(title="Month"))'), [])

    def test_grid_off_is_not_flagged(self):
        self.assertEqual(check.check("ax.grid(False)"), [])

    def test_zero_based_bars_pass(self):
        self.assertEqual(check.check("ax.bar(x, y)\nax.set_ylim(0, 100)"), [])
        self.assertTrue(check.check("ax.bar(x, y)\nax.set_ylim(50, 100)"))

    def test_one_accent_is_not_rainbow(self):
        self.assertEqual(check.check('colors = ["#d9480f", "#d8d3c8", "#d8d3c8", "#d8d3c8"]'), [])

    def test_cli_json(self):
        out = subprocess.run([sys.executable, str(CHARTS / "scripts" / "chart_check.py"),
                              str(FIX / "chart_slop.js"), "--json"], capture_output=True, text=True, check=True)
        data = json.loads(out.stdout)
        self.assertEqual(data[0]["file"].split("/")[-1], "chart_slop.js")
        self.assertLess(data[0]["score"], 60)


@unittest.skipUnless(HAS_MPL, "matplotlib not installed")
class ChartStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.style = load("chart_style")

    def test_spread_keeps_min_gap(self):
        pos = self.style._spread([10, 10.5, 11, 40], 3)
        ordered = sorted(pos)
        self.assertTrue(all(b - a >= 3 - 1e-9 for a, b in zip(ordered, ordered[1:])), pos)
        self.assertEqual(self.style._spread([1, 50], 3), [1, 50])

    def test_every_chart_renders(self):
        s = self.style
        charts = {
            "hbar": lambda: s.hbar(["A", "B", "C"], [3, 9, 5], highlight="B"),
            "bar": lambda: s.bar(["Q1", "Q2", "Q3"], [3, 9, 5], highlight="Q2", theme="ink"),
            "line": lambda: s.line(["J", "F", "M"], {"A": [1, 2, 3], "B": [1, 1, 2]}, highlight="A"),
            "slope": lambda: s.slope(["A", "B"], [41, 28], [17, 26], highlight="A", fmt="${}"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, make in charts.items():
                fig, ax = make()
                path = Path(tmp) / f"{name}.png"
                s.finish(fig, title="Cost per lead fell from $41 to $17", kicker="Test",
                         source="Sample data.", path=path)
                self.assertGreater(path.stat().st_size, 10_000, name)

    def test_bars_start_at_zero(self):
        fig, ax = self.style.bar(["A", "B"], [80, 90])
        self.assertEqual(ax.get_ylim()[0], 0)

    def test_dollar_signs_stay_text(self):
        self.assertEqual(self.style._plain("$41 to $17"), r"\$41 to \$17")


if __name__ == "__main__":
    unittest.main()
