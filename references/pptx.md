# PowerPoint, Keynote and Google Slides

When the user needs an editable `.pptx` (their company uses PowerPoint, they'll edit it in Google Slides, or they'll present from Keynote), build it with `python-pptx`, using the same layouts and theme as the HTML template. Google Slides and Keynote both open `.pptx` files.

If they only need to present or share, the PDF from `render.py` is enough and keeps the design exact.

## Setup

```sh
pip install python-pptx
```

## Recipe

Start from a blank 16:9 presentation, not a built-in template: built-in templates bring their own fonts, bullets and colours. Draw every element yourself at fixed positions. The grid below matches the HTML template (1280×720 px maps to 13.333×7.5 in).

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

THEME = {  # "paper"; swap in another theme's colours from references/design.md
    "bg": RGBColor(0xF6, 0xF4, 0xEF), "fg": RGBColor(0x1B, 0x1B, 0x1B),
    "muted": RGBColor(0x6F, 0x6A, 0x61), "faint": RGBColor(0xD8, 0xD3, 0xC8),
    "accent": RGBColor(0xD9, 0x48, 0x0F), "font": "Helvetica Neue",
}
M = Inches(0.92)            # side margin (88 px)
W = Inches(13.333) - 2 * M  # content width

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = THEME["bg"]
    return s


def text(s, x, y, w, h, value, size, bold=False, color="fg", align=PP_ALIGN.LEFT):
    box = s.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = value
    run.font.size, run.font.bold, run.font.name = Pt(size), bold, THEME["font"]
    run.font.color.rgb = THEME[color]
    return box


def notes(s, value):
    s.notes_slide.notes_text_frame.text = value


# number layout
s = slide()
text(s, M, Inches(0.75), W, Inches(0.4), "CLIENT RETENTION", 14, True, "muted")
text(s, M, Inches(1.15), W, Inches(1.6), "We kept 94% of clients this quarter, up from 81%.", 38, True)
text(s, M, Inches(4.0), Inches(5.2), Inches(2.4), "+13", 160, True, "accent")
text(s, Inches(6.6), Inches(5.4), Inches(5.5), Inches(1.0),
     "points of retention since Q1, after monthly calls began in July.", 20, False, "muted")
notes(s, "Source: CRM export, 30 Sep.")

# bars layout: heights proportional to value, starting at zero
s = slide()
text(s, M, Inches(0.75), W, Inches(0.4), "RETENTION BY QUARTER", 14, True, "muted")
text(s, M, Inches(1.15), W, Inches(1.2), "The jump came the quarter the calls started", 38, True)
values, labels, hi = [81, 87, 94], ["Q1", "Q2", "Q3 · calls began"], 2
chart_h, base = Inches(3.4), Inches(6.6)
gap = Inches(0.4)
bw = (W - gap * (len(values) - 1)) / len(values)
for i, (v, lab) in enumerate(zip(values, labels)):
    h = int(chart_h * v / max(values))
    x = M + i * (bw + gap)
    bar = s.shapes.add_shape(1, x, base - h, bw, h)   # 1 = rectangle
    bar.fill.solid()
    bar.fill.fore_color.rgb = THEME["accent"] if i == hi else THEME["faint"]
    bar.line.fill.background()
    text(s, x, base - h - Inches(0.5), bw, Inches(0.4), f"{v}%", 20, True, align=PP_ALIGN.CENTER)
    text(s, x, base + Inches(0.1), bw, Inches(0.4), lab, 14, False, "muted", PP_ALIGN.CENTER)

prs.save("deck.pptx")
```

Build the other layouts the same way from the positions in `templates/deck.html`: kicker at 0.75 in, headline at 1.15 in, content anchored towards the bottom, and 0.92 in side margins.

## Checks

- Run `python3 <skill-dir>/scripts/slop_check.py deck.pptx`. It reads `.pptx` directly.
- To look at the result, convert to PDF if LibreOffice is installed: `soffice --headless --convert-to pdf deck.pptx`. Then view the pages. Otherwise ask the user to open it and send a screenshot of anything that looks off.
- Fonts: `Helvetica Neue` exists on Mac. For Windows audiences, use `Segoe UI` or `Arial` so the deck doesn't fall back to a random font.
