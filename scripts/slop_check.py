#!/usr/bin/env python3
"""Find AI-slop patterns in a slide deck and score it out of 100.

Usage: python3 scripts/slop_check.py DECK [--json]
  DECK can be .pptx (PowerPoint, Keynote export, Google Slides download),
  .html (nopurple, reveal.js or any <section> slides) or .md (Marp or plain,
  slides separated by a line with ---).

Checks each slide for topic titles instead of claims, emoji, walls of bullets,
too many words, hype words and vague claims with no number, plus the purple
gradient and font sprawl across the deck. Standard library only.
"""

import html as htmllib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

GENERIC_TITLES = {
    "overview", "agenda", "introduction", "intro", "summary", "key takeaways", "takeaways",
    "conclusion", "conclusions", "thank you", "thanks", "questions", "q&a", "any questions",
    "background", "results", "next steps", "about us", "our solution", "the problem",
    "the solution", "key findings", "highlights", "recap", "executive summary", "discussion",
}
HYPE = re.compile(
    r"\b(unlock\w*|synerg\w+|leverag\w+|robust|seamless\w*|journey|comprehensive|"
    r"revolutioni[sz]\w*|game[- ]chang\w*|cutting[- ]edge|empower\w*|delve\w*|"
    r"innovative|transformative|holistic|best[- ]in[- ]class|world[- ]class|"
    r"next[- ]level|supercharg\w+|paradigm|elevate\w*|harness\w*|dynamic)\b", re.I)
VAGUE = re.compile(r"\b(significant(ly)?|substantial(ly)?|various|numerous|many|dramatic(ally)?|"
                   r"massive(ly)?|considerabl[ey]|improved?|improvements?)\b", re.I)
NUMBER = re.compile(r"(?<![QqHh])\d")  # "Q3" or "H1" is a label, not evidence
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U00002B50\U00002B55"
    "\U0000203C\U00002049\U000023E9-\U000023FA]")
PURPLE_GRADIENTS = re.compile(r"#(667eea|764ba2|6a11cb|2575fc|8e2de2|4a00e0|7f00ff|e100ff|a18cd1|fbc2eb|9d50bb|6e48aa)\b", re.I)
GRADIENT = re.compile(r"linear-gradient\(([^;]+)\)", re.I)

MAX_BULLETS = 5
MAX_WORDS = 50


def hex_hue(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn or mx - mn < 0.15:
        return None
    if mx == r:
        hue = (60 * ((g - b) / (mx - mn)) + 360) % 360
    elif mx == g:
        hue = 60 * ((b - r) / (mx - mn)) + 120
    else:
        hue = 60 * ((r - g) / (mx - mn)) + 240
    return hue


def purple_gradient(css):
    """True if any linear-gradient uses a violet/purple stop (hue 250-320)."""
    if PURPLE_GRADIENTS.search(css):
        return True
    for g in GRADIENT.findall(css):
        for h in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", g):
            hue = hex_hue(h)
            if hue is not None and 250 <= hue <= 320:
                return True
    return False


# ---------- parsers: each returns (slides, deck_css) where slide = dict(title, bullets, text)

def strip_tags(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", s))


def parse_html(text):
    css = " ".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, flags=re.S | re.I))
    css += " ".join(re.findall(r'style="([^"]*)"', text))
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    sections = re.findall(r"<section\b[^>]*>(.*?)</section>", body, flags=re.S | re.I)
    slides = []
    for sec in sections:
        m = re.search(r"<h[12]\b[^>]*>(.*?)</h[12]>", sec, flags=re.S | re.I)
        title = " ".join(strip_tags(m.group(1)).split()) if m else ""
        bullets = len(re.findall(r"<li\b", sec, flags=re.I))
        notes = re.findall(r'<aside\b[^>]*class="[^"]*notes[^"]*"[^>]*>.*?</aside>', sec, flags=re.S | re.I)
        for n in notes:
            sec = sec.replace(n, " ")
        slides.append({"title": title, "bullets": bullets, "text": " ".join(strip_tags(sec).split())})
    return slides, css


def parse_markdown(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # Marp front matter
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)        # speaker notes
    slides = []
    for chunk in re.split(r"^\s*---\s*$", text, flags=re.M):
        if not chunk.strip():
            continue
        lines = chunk.strip().splitlines()
        title = next((l.lstrip("#").strip() for l in lines if l.startswith("#")), "")
        bullets = sum(1 for l in lines if re.match(r"\s*([-*+]|\d+\.)\s+", l))
        slides.append({"title": title, "bullets": bullets, "text": " ".join(" ".join(lines).split())})
    css = " ".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, flags=re.S | re.I))
    return slides, css


NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


def parse_pptx(path):
    slides = []
    fonts = set()
    with zipfile.ZipFile(path) as z:
        names = sorted(
            (n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
            key=lambda n: int(re.search(r"(\d+)", n).group(1)))
        for name in names:
            root = ET.fromstring(z.read(name))
            title, bullets, texts = "", 0, []
            biggest = (0, "")  # (font size, text): fallback title when there's no title placeholder
            for sp in root.iter(f"{{{NS['p']}}}sp"):
                ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", NS)
                is_title = ph is not None and ph.get("type") in ("title", "ctrTitle")
                paras = []
                for para in sp.iter(f"{{{NS['a']}}}p"):
                    t = "".join(x.text or "" for x in para.iter(f"{{{NS['a']}}}t")).strip()
                    if t:
                        paras.append(t)
                        sizes = [int(r.get("sz")) for r in para.iter(f"{{{NS['a']}}}rPr") if r.get("sz")]
                        # Big words are titles; skip lone numbers like "+13" or "94%".
                        if sizes and max(sizes) > biggest[0] and re.search(r"[A-Za-z]{3}", t):
                            biggest = (max(sizes), t)
                for latin in sp.iter(f"{{{NS['a']}}}latin"):
                    if latin.get("typeface") and not latin.get("typeface").startswith("+"):
                        fonts.add(latin.get("typeface"))
                if is_title and paras:
                    title = " ".join(paras)
                elif len(paras) > 1:
                    bullets += len(paras)
                texts.extend(paras)
            if not title and biggest[0] >= 2800:  # 28 pt or larger
                title = biggest[1]
            slides.append({"title": title, "bullets": bullets, "text": " ".join(texts)})
    css = " ".join(f"font-family: {f};" for f in fonts)
    return slides, css


def load(path):
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        return parse_pptx(path)
    text = path.read_text(errors="replace")
    if suffix in (".html", ".htm"):
        return parse_html(text)
    return parse_markdown(text)


# ---------- checks

def check_slide(s):
    """Return list of (points, message)."""
    issues = []
    title, text = s["title"], s["text"]
    t = title.lower().strip(" .:!?")
    t_plain = EMOJI.sub("", t).strip()
    if title and (t_plain in GENERIC_TITLES or len(t_plain.split()) <= 2):
        issues.append((4, f"Topic title \"{title}\". Make the title the point, as a sentence."))
    if EMOJI.search(title) or len(EMOJI.findall(text)) >= 2:
        issues.append((3, "Emoji used as decoration."))
    if s["bullets"] > MAX_BULLETS:
        issues.append((4, f"{s['bullets']} bullets. Keep 3 to {MAX_BULLETS}, or split the slide."))
    words = len(re.findall(r"[A-Za-z0-9][\w'%$.,-]*", text))
    if words > MAX_WORDS:
        issues.append((3, f"{words} words on one slide. Aim for under {MAX_WORDS}; move detail to speaker notes."))
    hype = sorted({h[0].lower() if isinstance(h, tuple) else h.lower() for h in HYPE.findall(text)})
    if hype:
        issues.append((min(2 * len(hype), 6), "Hype words: " + ", ".join(hype[:4]) + "."))
    if VAGUE.search(text) and not NUMBER.search(text):
        issues.append((3, f"Vague claim (\"{VAGUE.search(text).group(0)}\") with no number to back it."))
    if re.fullmatch(r"(thank you|thanks)[!.]?\s*(questions\??)?.*", t_plain) and words < 12:
        issues.append((3, "\"Thank you\" ending. End on the decision or next step instead."))
    return issues


# Example text from templates/deck.html. If it shows up in a finished deck, it was copied, not written.
TEMPLATE_LEFTOVERS = ["Acme Studio", "15 November", "Approve by 15", "monthly strategy calls began in July",
                      "Operations lead, retained client", "Three moves to reach 96%", "Deck title"]


def check_deck(slides, css):
    issues = []
    text = " ".join(s["title"] + " " + s["text"] for s in slides)
    left = [t for t in TEMPLATE_LEFTOVERS if t.lower() in text.lower()]
    if left:
        issues.append((10, "Example text copied from the template: " + ", ".join(f'"{t}"' for t in left[:3])
                       + ". Replace it with the user's facts, or [?]."))
    for g in re.findall(r'content\s*:\s*"""', css):
        issues.append((10, 'Broken CSS: content: """ (curly quotes were flattened). Use "\\201C" and "\\201D".'))
        break
    if purple_gradient(css):
        issues.append((10, "Purple gradient background: the most recognisable AI-deck look."))
    fonts = {f.strip().split(",")[0].strip("'\" ").lower()
             for f in re.findall(r"font-family\s*:\s*([^;}]+)", css)}
    fonts = {f for f in fonts if f and not f.startswith("var(")}
    if len(fonts) > 3:
        issues.append((4, f"{len(fonts)} font families. Use one, or two at most."))
    if len(slides) >= 4:
        titles = [s["title"] for s in slides if s["title"]]
        if titles and sum(1 for x in titles if x.istitle() and len(x.split()) > 3) > len(titles) / 2:
            issues.append((2, "Most titles Use Title Case Like This. Sentence case reads faster."))
    return issues


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if not args:
        print(__doc__.strip())
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"No such file: {path}", file=sys.stderr)
        return 2
    try:
        slides, css = load(path)
    except (zipfile.BadZipFile, ET.ParseError) as e:
        print(f"Could not read {path}: {e}", file=sys.stderr)
        return 2
    if not slides:
        print("No slides found.", file=sys.stderr)
        return 2

    per_slide = [check_slide(s) for s in slides]
    deck_issues = check_deck(slides, css)
    penalty = sum(p for issues in per_slide for p, _ in issues) / len(slides) * 4
    penalty += sum(p for p, _ in deck_issues)
    score = max(0, round(100 - penalty))

    if as_json:
        print(json.dumps({
            "file": str(path), "score": score, "slides": len(slides),
            "deck_issues": [m for _, m in deck_issues],
            "slide_issues": [{"slide": i + 1, "title": s["title"], "issues": [m for _, m in iss]}
                             for i, (s, iss) in enumerate(zip(slides, per_slide)) if iss],
        }, indent=2))
        return 0

    label = "clean" if score >= 85 else "some slop" if score >= 60 else "AI slop"
    print(f"Slop check: {score}/100 ({label}), {len(slides)} slides, {path.name}")
    for _, m in deck_issues:
        print(f"  deck: {m}")
    for i, (s, iss) in enumerate(zip(slides, per_slide), 1):
        for _, m in iss:
            print(f"  slide {i}: {m}")
    if score >= 85 and not deck_issues:
        print("  No major slop found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
