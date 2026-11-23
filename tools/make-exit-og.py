#!/usr/bin/env python3
"""Draw the 1200x630 share card for /exit/ into assets/exit/ (needs rsvg-convert).

    ./tools/make-pe-og.py

Each card says its page's angle in plain words, in the dark brown palette."""
import pathlib, subprocess, tempfile
SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "exit"
BG, LIFT, INK, INK2, INK3, ACC = "#241F1A", "#2E2822", "#EFE7DA", "#C0B5A4", "#A59A88", "#E2B26F"
FONT = "Geist, Helvetica Neue, Helvetica, Arial, sans-serif"

def card(title, sub, facts):
    t = "".join(f'<text x="64" y="{160 + i * 64}" font-size="54" font-weight="600" fill="{INK}">{l}</text>' for i, l in enumerate(title))
    y = 160 + len(title) * 64 + 10
    s = "".join(f'<text x="64" y="{y + i * 38}" font-size="28" fill="{INK2}">{l}</text>' for i, l in enumerate(sub))
    f = ""
    for i, (b, l) in enumerate(facts):
        x = 64 + i * 360
        f += (f'<rect x="{x}" y="452" width="330" height="3" fill="{ACC}"/>'
              f'<text x="{x}" y="494" font-size="30" font-weight="600" fill="{INK}">{b}</text>'
              f'<text x="{x}" y="526" font-size="20" fill="{INK2}">{l}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" font-family="{FONT}">'
            f'<rect width="1200" height="630" fill="{BG}"/>'
            f'<text x="64" y="84" font-size="22" letter-spacing="2" fill="{INK3}">FOR FOUNDERS WHO WILL SELL ONE DAY</text>{t}{s}{f}'
            f'<text x="64" y="594" font-size="22" fill="{INK2}">Pavel Guzhikov, guzh.uk/exit</text></svg>')

FACTS = [("Sold two", "my own companies, zero to sale"), ("A unicorn", "founding team at Uzum"), ("Hands-on", "tech, product and business")]
cards = {
    "exit-og.png": card(["Worth more without you."],
                      ["Buyers pay for a business that runs without its owner.", "I help you build one, hands-on, measured weekly."], FACTS),
}
for name, svg in cards.items():
    if "—" in svg or "·" in svg:
        raise SystemExit(f"{name}: em dash or middle dot")
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630", "-o", str(OUT / name), fh.name], check=True)
    print("wrote assets/exit/" + name)
