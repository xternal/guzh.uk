#!/usr/bin/env python3
"""Check the colours on every page, in light and in dark.

    ./tools/check-colours.py

Reads the palette straight out of each page's <style> and fails if:

- a text colour (--ink, --ink-2, --ink-3, --accent) is under WCAG AA (4.5:1) on either background
  (--paper, or --paper-lift, the warm lift in the top corners), in either mode;
- dark mode is not Pavel's dark brown (#241F1A, chosen 12 Oct 2026), drifts back towards black or
  navy, or makes the body text glare (above 14:1);
- the two dark blocks in a page differ (the media query and the switcher's data-theme="dark" must
  agree, see the README);
- the browser bar colour (the theme-color tags and the switcher script that rewrites them) is not
  the page's own background;
- a page's palette has drifted from the home page's;
- the favicon's square is not the dark brown, or its mark is drawn in anything but the dark --ink
  and --accent (which are checked against that same brown above, so the mark passes too).

Standard library only, so it runs anywhere python3 does, and on every pull request that touches a
page (.github/workflows/colours.yml).
"""

import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "weather/index.html", "weather/privacy/index.html", "weather/support/index.html",
         "weather/ideas/index.html"]
DARK_BROWN = "#241F1A"
TEXT = ["ink", "ink-2", "ink-3", "accent"]
BACKGROUNDS = ["paper", "paper-lift"]
SHARED = BACKGROUNDS + TEXT


def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def block(css, selector):
    m = re.search(re.escape(selector) + r"\{(.*?)\}", css, re.S)
    if not m:
        raise SystemExit(f"no {selector} block")
    return [d.strip() for d in m.group(1).split(";") if d.strip()]


def tokens(declarations):
    out = {}
    for d in declarations:
        m = re.fullmatch(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", d)
        if m:
            out[m.group(1)] = m.group(2).upper()
    return out


def check(path):
    page = (SITE / path).read_text(encoding="utf-8")
    css = page[page.index("<style>"):page.index("</style>")]
    light = tokens(block(css, "\n:root"))
    dark_media = block(css, ':root:not([data-theme="light"])')
    dark_forced = block(css, ':root[data-theme="dark"]')
    dark = tokens(dark_media)
    errors = []

    if dark_media != dark_forced:
        errors.append("the two dark blocks differ")

    for mode, p in (("light", light), ("dark", dark)):
        for fg in TEXT:
            for bg in BACKGROUNDS:
                r = ratio(p[fg], p[bg])
                if r < 4.5:
                    errors.append(f"{mode}: --{fg} on --{bg} is {r:.2f}:1, under AA")

    paper = dark["paper"]
    if paper != DARK_BROWN:
        errors.append(f"dark --paper is {paper}, not the dark brown {DARK_BROWN}")
    if luminance(paper) < 0.012:
        errors.append(f"dark --paper {paper} reads as black")
    if int(paper[1:3], 16) <= int(paper[5:7], 16):
        errors.append(f"dark --paper {paper} is not warm")
    if ratio(dark["ink"], paper) > 14:
        errors.append(f"dark body text is {ratio(dark['ink'], paper):.2f}:1, glaring above 14:1")

    metas = dict((m, c.upper()) for c, m in re.findall(
        r'<meta name="theme-color" content="(#[0-9A-Fa-f]{6})" media="\(prefers-color-scheme: (light|dark)\)">', page))
    script = re.search(r'dark \? "(#[0-9A-Fa-f]{6})" : "(#[0-9A-Fa-f]{6})"', page)
    for mode, p in (("light", light), ("dark", dark)):
        if metas.get(mode) != p["paper"]:
            errors.append(f"{mode} theme-color tag is {metas.get(mode)}, not {p['paper']}")
    if not script or (script.group(1).upper(), script.group(2).upper()) != (dark["paper"], light["paper"]):
        errors.append("the switcher's theme-color is not the two backgrounds")
    return light, dark, errors


def main():
    failed = False
    home = None
    for path in PAGES:
        light, dark, errors = check(path)
        home = home or (light, dark)
        for mode, p, h in (("light", light, home[0]), ("dark", dark, home[1])):
            for t in SHARED:
                if p[t] != h[t]:
                    errors.append(f"{mode} --{t} is {p[t]}, the home page has {h[t]}")
        worst = min(ratio(dark[fg], dark[bg]) for fg in TEXT for bg in BACKGROUNDS)
        print(f"{path}: {'ok' if not errors else 'FAILED'} (dark body text {ratio(dark['ink'], dark['paper']):.1f}:1, "
              f"weakest dark pair {worst:.1f}:1)")
        for e in errors:
            print(f"  {e}")
        failed |= bool(errors)

    favicon = (SITE / "favicon.svg").read_text(encoding="utf-8")
    square = re.search(r'<rect[^>]*fill="(#[0-9A-Fa-f]{6})"', favicon)
    mark = {c.upper() for c in re.findall(r'(?:fill|stroke)="(#[0-9A-Fa-f]{6})"', favicon)} - {DARK_BROWN}
    errors = []
    if not square or square.group(1).upper() != DARK_BROWN:
        errors.append(f"square is {square and square.group(1)}, not {DARK_BROWN}")
    for c in sorted(mark - {home[1]["ink"], home[1]["accent"]}):
        errors.append(f"the mark uses {c}, not the dark --ink {home[1]['ink']} or --accent {home[1]['accent']}")
    print(f"favicon.svg: {'ok' if not errors else 'FAILED'}")
    for e in errors:
        print(f"  {e}")
    failed |= bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
