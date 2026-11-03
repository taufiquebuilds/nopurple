#!/usr/bin/env python3
"""Render a nopurple HTML deck to one PNG per slide and a PDF, using Chrome.

Usage: python3 scripts/render.py deck.html [--out DIR] [--theme NAME] [--no-pdf]

Looking at the rendered slides is part of the workflow: text that overflows,
a chart that misleads or a slide that's too busy only shows up in pixels.
Needs Google Chrome, Chromium or Microsoft Edge. Standard library only.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "chrome"]


def find_chrome():
    env = os.environ.get("CHROME")
    if env and Path(env).exists():
        return env
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    return None


def run_chrome(chrome, args):
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--no-first-run", "--no-default-browser-check", "--force-device-scale-factor=1",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=3000"] + args
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=False)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("deck")
    p.add_argument("--out", help="Output folder (default: <deck>-render next to the deck)")
    p.add_argument("--theme", help="Override the theme: paper, ink, swiss, forest, sand, mono")
    p.add_argument("--no-pdf", action="store_true")
    args = p.parse_args(argv)

    deck = Path(args.deck).resolve()
    if not deck.is_file():
        print(f"No such file: {deck}", file=sys.stderr)
        return 2
    chrome = find_chrome()
    if not chrome:
        print("Chrome, Chromium or Edge is needed to render. Set CHROME=/path/to/browser.", file=sys.stderr)
        return 1

    html = re.sub(r"<!--.*?-->", "", deck.read_text(errors="replace"), flags=re.S)
    count = len(re.findall(r'<section\s+class="slide\b', html))
    if count == 0:
        print("No slides found. Each slide is <section class=\"slide LAYOUT\">.", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else deck.with_name(deck.stem + "-render")
    out.mkdir(parents=True, exist_ok=True)

    url = deck.as_uri()
    theme = f"&theme={args.theme}" if args.theme else ""
    pngs = []
    for i in range(1, count + 1):
        png = out / f"slide-{i:02d}.png"
        run_chrome(chrome, ["--window-size=1280,720", f"--screenshot={png}", f"{url}?slide={i}{theme}"])
        if png.exists():
            pngs.append(png)
    print(f"Rendered {len(pngs)} of {count} slides to {out}")

    if not args.no_pdf:
        pdf = out / (deck.stem + ".pdf")
        run_chrome(chrome, ["--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                            f"{url}?print=1{theme}"])
        print(f"PDF: {pdf}" if pdf.exists() else "PDF export failed (slides were still rendered)")
    return 0 if len(pngs) == count else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
