#!/usr/bin/env python3
"""Find AI-slop patterns in chart code and score it out of 100.

Usage: python3 scripts/chart_check.py FILE [FILE ...] [--json]
  FILE can be .py or .ipynb (matplotlib, seaborn, Plotly), .js, .ts, .jsx or
  .tsx (Chart.js, Recharts, ECharts, Plotly.js), .json (Vega-Lite, Chart.js
  config) or .html (any of these inside <script>).

Flags pies, exploded slices, shadows, 3D, rainbow colour lists and colour maps,
truncated bar axes, dual axes, rotated labels, gridlines, legends, topic titles
and emoji in titles. It reads code, not images, so it can be wrong: a pie with
two slices is fine. Standard library only.
"""

import json
import re
import sys
from pathlib import Path

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U00002B50\U00002B55]")
HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
NAMED = {"red", "blue", "green", "orange", "purple", "yellow", "pink", "cyan", "magenta",
         "teal", "violet", "brown", "lime", "indigo", "gold", "crimson", "turquoise"}
TOPIC_WORDS = re.compile(
    r"\b(overview|distribution|breakdown|analysis|comparison|summary|trends?|performance|"
    r"insights?|metrics|statistics|dashboard|report)\b", re.I)

# (penalty, message, pattern). Patterns run on the whole file, so they can span lines.
RULES = [
    (15, "Pie or donut chart: use sorted horizontal bars, or say the share in words. "
         "Fine only for 2 or 3 parts, labelled directly.",
     r"\.pie\(|\bpx\.pie\b|\bgo\.Pie\b|type\s*:\s*['\"](?:pie|doughnut)['\"]|<PieChart\b|"
     r"['\"]mark['\"]\s*:\s*(?:\{\s*['\"]type['\"]\s*:\s*)?['\"]arc['\"]|\bPieChart\(|\bDoughnutChart\("),
    (10, "Exploded pie slice: remove explode/pull.", r"\bexplode\s*=|\bpull\s*=\s*\["),
    (10, "Drop shadow on chart marks: remove it.",
     r"\bshadow\s*=\s*True|\bshadowBlur\b|\bshadowColor\b|\bdropShadow\b"),
    (20, "3D chart: 3D distorts every value. Use a flat chart.",
     r"projection\s*=\s*['\"]3d['\"]|\bbar3d\(|\bAxes3D\b|\b(?:Bar|Pie|Line|Area)3DChart\b|"
     r"\b(?:Bar|Pie|Line|Area)Chart3D\b|\bScatter3d\b|\bgo\.Surface\b|\bbar3D\b|['\"]bar3D['\"]"),
    (12, "Rainbow colour map or palette: use grey plus one accent colour.",
     r"cmap\s*=\s*['\"](?:jet|rainbow|hsv|gist_rainbow|nipy_spectral|turbo|Spectral|tab10|tab20|"
     r"Set[123]|Paired|Accent)['\"]|\bplt\.cm\.(?:jet|rainbow|hsv|gist_rainbow|turbo|tab10|tab20)\b|"
     r"color_palette\(\s*['\"](?:husl|hls|Set[123]|Paired|tab10|bright|deep|muted|pastel|colorblind)['\"]|"
     r"\bpalette\s*=\s*['\"](?:husl|hls|Set[123]|Paired|tab10|bright|deep|pastel|rainbow)['\"]|"
     r"px\.colors\.qualitative\.\w+|colorscale\s*=\s*['\"](?:Rainbow|Jet|Turbo|Portland)['\"]|"
     r"['\"]scheme['\"]\s*:\s*['\"](?:category10|category20|tableau10|tableau20|rainbow|sinebow)['\"]"),
    (15, "Dual y-axes: they make any two trends look related. Use two charts side by side.",
     r"\.twinx\(|\.twiny\(|secondary_y\s*=\s*True|overlaying\s*=\s*['\"]y|yAxisId\s*=\s*['\"]right|"
     r"['\"]y['\"]\s*:\s*['\"]independent['\"]|position\s*:\s*['\"]right['\"][^}]*\bgrid\b"),
    (8, "Rotated axis labels: use horizontal bars so long labels read straight.",
     r"rotation\s*=\s*-?(?:[1-9]\d?)\b|labelrotation\s*=\s*-?[1-9]|\b(?:max|min)Rotation\s*:\s*[1-9]|"
     r"tickangle\s*=\s*-?[1-9]|['\"]tickangle['\"]\s*:\s*-?[1-9]|\bangle\s*=\s*\{\s*-?[1-9]|"
     r"['\"]labelAngle['\"]\s*:\s*-?[1-9]|autofmt_xdate\("),
    (6, "Gridlines: remove them and label the values directly.",
     r"\.grid\(\s*(?:True|visible\s*=\s*True|b\s*=\s*True|axis\s*=|which\s*=|color\s*=|alpha\s*=|ls\s*=|"
     r"linestyle\s*=|\))|['\"]axes\.grid['\"]\s*:\s*True|set_style\(\s*['\"](?:whitegrid|darkgrid)['\"]|"
     r"style\.use\(\s*['\"](?:ggplot|seaborn[-\w]*grid|fivethirtyeight|bmh)['\"]|<CartesianGrid\b|"
     r"showgrid\s*=\s*True|['\"]showgrid['\"]\s*:\s*true"),
    (4, "Legend: label lines or bars directly at their ends, and drop the legend.",
     r"\.legend\(|<Legend\b|legend\s*:\s*\{\s*display\s*:\s*true"),
]
COMPILED = [(p, m, re.compile(r)) for p, m, r in RULES]

TITLE = re.compile(
    r"(?:set_title|\btitle|suptitle|title_text)\s*\(\s*[rfbu]?(['\"])(.+?)\1|"
    r"(?<![\w.])title\s*=\s*[rfbu]?(['\"])(.+?)\3|"
    r"title\s*:\s*\{[^{}]*?text\s*:\s*(['\"`])(.+?)\5|"
    r"['\"]title['\"]\s*:\s*(['\"])(.+?)\7|"
    r"['\"]title['\"]\s*:\s*\{[^{}]*?['\"]text['\"]\s*:\s*(['\"])(.+?)\9")
BAR = re.compile(r"\.barh?\(|\bpx\.bar\b|\bgo\.Bar\b|type\s*:\s*['\"]bar['\"]|<BarChart\b|"
                 r"['\"]mark['\"]\s*:\s*(?:\{\s*['\"]type['\"]\s*:\s*)?['\"]bar['\"]|\bbarplot\(|countplot\(|"
                 r"\.plot\.barh?\(|kind\s*=\s*['\"]barh?['\"]|\bBarChart\(")
TRUNCATED = re.compile(r"set_[xy]lim\(\s*(?:bottom\s*=\s*|left\s*=\s*)?[1-9][\d_.]*\s*[,)]|"
                       r"\b[xy]lim\(\s*[1-9][\d_.]*\s*,|beginAtZero\s*:\s*false|"
                       r"['\"]zero['\"]\s*:\s*false|range\s*=\s*\[\s*[1-9]|\bmin\s*:\s*[1-9]")


def hue(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.25:  # greys and muted tones don't count as rainbow colours
        return None
    if mx == r:
        return (60 * ((g - b) / (mx - mn)) + 360) % 360
    if mx == g:
        return 60 * ((b - r) / (mx - mn)) + 120
    return 60 * ((r - g) / (mx - mn)) + 240


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def read(path):
    text = path.read_text(errors="replace")
    if path.suffix == ".ipynb":
        try:
            nb = json.loads(text)
            return "\n".join("".join(c.get("source", [])) for c in nb.get("cells", [])
                             if c.get("cell_type") == "code")
        except json.JSONDecodeError:
            pass
    return text


def rainbow_lists(text):
    """Lists or arrays of 4+ saturated colours spread across 4+ hue families."""
    found = []
    for m in re.finditer(r"\[[^\[\]]{0,600}\]", text):
        body = m.group(0)
        hues = {int(h // 60) for h in (hue(x) for x in HEX.findall(body)) if h is not None}
        names = {w.lower() for w in re.findall(r"['\"](\w+)['\"]", body)} & NAMED
        if len(hues) >= 4 or len(names) >= 4:
            found.append(line_of(text, m.start()))
    return found


# fig.text(x, y, "Leads by Channel", fontsize=24): big free text is a title too.
FIG_TEXT = re.compile(r"\.text\(\s*[\w.]+\s*,\s*[\w.]+\s*,\s*[rfbu]?(['\"])(.+?)\1([^()]*(?:\([^()]*\)[^()]*)*)\)", re.S)


def titles(text):
    for m in TITLE.finditer(text):
        yield m.start(), next(g for g in m.groups()[1::2] if g is not None).strip()
    for m in FIG_TEXT.finditer(text):
        size = re.search(r"fontsize\s*=\s*(\d+)", m.group(3))
        if size and int(size.group(1)) >= 18:
            yield m.start(), m.group(2).strip()


def check_titles(text):
    issues = []
    for start, title in titles(text):
        before = text[max(0, start - 40):start].lower()
        if not title or "axis" in before or "legend" in before or "colorbar" in before:
            continue
        ln = line_of(text, start)
        if EMOJI.search(title):
            issues.append((5, ln, f'Emoji in title "{title}": remove it.'))
        if re.search(r"\d|\{|\$\{|%", title):
            continue  # has a number, or one filled in from the data
        words = title.split()
        if TOPIC_WORDS.search(title) or len(words) <= 5:
            issues.append((8, ln, f'Topic title "{title}": write the finding as a sentence with its '
                                  'number, e.g. "Google Ads brought 42% of all leads".'))
    return issues


def check(text):
    """Return a list of (penalty, line, message)."""
    issues = []
    for penalty, msg, rx in COMPILED:
        m = rx.search(text)
        if m:
            issues.append((penalty, line_of(text, m.start()), msg))
    for ln in rainbow_lists(text)[:1]:
        issues.append((12, ln, "Rainbow colour list: make everything grey except the one thing the "
                               "title is about."))
    if BAR.search(text):
        m = TRUNCATED.search(text)
        if m:
            issues.append((15, line_of(text, m.start()),
                           "Bar axis may not start at zero: bars must start at zero. Show the change "
                           "itself if it is small."))
    issues.extend(check_titles(text))
    return sorted(issues, key=lambda i: i[1])


def score(issues):
    return max(0, 100 - sum(p for p, _, _ in issues))


def main(argv):
    as_json = "--json" in argv
    paths = [Path(a) for a in argv if a != "--json"]
    if not paths:
        print(__doc__.strip())
        return 2
    results = []
    for path in paths:
        if not path.is_file():
            print(f"No such file: {path}", file=sys.stderr)
            return 2
        issues = check(read(path))
        results.append((path, score(issues), issues))

    if as_json:
        print(json.dumps([{"file": str(p), "score": s,
                           "issues": [{"line": ln, "message": m} for _, ln, m in iss]}
                          for p, s, iss in results], indent=2))
        return 0

    for path, s, issues in results:
        label = "clean" if s >= 85 else "some slop" if s >= 60 else "AI slop"
        print(f"Chart check: {s}/100 ({label}), {path.name}")
        for _, ln, m in issues:
            print(f"  line {ln}: {m}")
        if not issues:
            print("  No chart slop found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
