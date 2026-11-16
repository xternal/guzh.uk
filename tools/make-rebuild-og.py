#!/usr/bin/env python3
"""Draw the three 1200x630 share cards for /rebuild/ into assets/rebuild/ (needs rsvg-convert).

    ./tools/make-rebuild-og.py

Each card shows what its page does, not just a logo. Rerun when a page's headline or demo changes."""
import pathlib, subprocess, tempfile
SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "rebuild"
BG, LIFT, INK, INK2, INK3, ACC = "#241F1A", "#2E2822", "#EFE7DA", "#C0B5A4", "#A59A88", "#E2B26F"
RED, RBG, AMB, ABG, GRN, GBG = "#EC9286", "#47322B", "#F0DCAA", "#3D3222", "#A6D49B", "#2F3A2A"
FONT = "Geist, Helvetica Neue, Helvetica, Arial, sans-serif"

def chip(x, y, text, fg, bg):
    w = 20 + len(text) * 11.0
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="34" rx="17" fill="{bg}"/>'
            f'<text x="{x + 16}" y="{y + 23}" font-size="18" fill="{fg}" font-weight="500">{text}</text>'), x + w + 10

def row(x, y, items):
    out = ""
    for text, fg, bg in items:
        c, x = chip(x, y, text, fg, bg)
        out += c
    return out

def frame(kicker, title_lines, inner, foot="guzh.uk/rebuild"):
    t = "".join(f'<text x="64" y="{150 + i * 62}" font-size="54" font-weight="600" fill="{INK}">{l}</text>'
                for i, l in enumerate(title_lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" font-family="{FONT}">'
            f'<rect width="1200" height="630" fill="{BG}"/>'
            f'<text x="64" y="84" font-size="22" letter-spacing="2" fill="{INK3}">{kicker}</text>{t}{inner}'
            f'<text x="64" y="590" font-size="22" fill="{INK2}">Pavel Guzhikov, {foot}</text>'
            f'<path d="M1080 590 h40 v-24 h40" fill="none" stroke="{ACC}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def mail(y, subj, chips):
    s = f'<rect x="64" y="{y}" width="1072" height="84" rx="16" fill="{LIFT}"/>'
    s += f'<text x="88" y="{y + 34}" font-size="22" font-weight="600" fill="{INK}">{subj}</text>'
    x = 88
    for text, fg, bg in chips:
        c, x = chip(x, y + 44, text, fg, bg)
        s += c
    return s

cards = {
    "block-requests-og.png": frame("DEMO: BLOCK MANAGEMENT", ["Residents' requests,", "triaged in seconds"],
        mail(290, "Water pouring through ceiling", [("Emergency", RED, RBG), ("Leak or water", BG, INK), ("Albion Wharf, Flat 22", INK2, "#39322B"), ("→ Plumber on call", INK2, "#39322B")]) +
        mail(386, "Re: Lift out again", [("24 hours", AMB, ABG), ("Lift", BG, INK), ("Marlowe Court, Flat 31", INK2, "#39322B"), ("→ Added to J-1042", INK2, "#39322B")]) +
        ""),
    "lending-intake-og.png": frame("DEMO: SME LENDING", ["A loan pack to a", "draft credit memo"],
        f'<rect x="64" y="290" width="1072" height="250" rx="16" fill="{LIFT}"/>'
        f'<text x="92" y="334" font-size="22" font-weight="600" fill="{INK}">Northgate Coffee Roasters Ltd: £40,000 over 24 months</text>' +
        "".join(f'{chip(92, 356 + i * 44, s, fg, bg)[0]}<text x="{92 + 16 + len(s) * 11.0 + 18:.0f}" y="{379 + i * 44}" font-size="20" fill="{INK2}">{t}</text>'
                for i, (s, fg, bg, t) in enumerate([("pass", GRN, GBG, "Applicant is a director"), ("refer", AMB, ABG, "Statements annualise 22% below stated turnover"),
                                                     ("refer", AMB, ABG, "Debt service cover 1.16x against 1.25x policy"), ("draft", BG, ACC, "Credit memo written for the underwriter")]))),
    "rebuild-og.png": frame("EMPATIQ: PROCESS RE-ENGINEERING", ["The same back-office work,", "with fewer people"],
        f'<text x="64" y="330" font-size="30" fill="{INK2}">No more copying, keying and chasing by hand.</text>'
        f'<text x="64" y="376" font-size="30" fill="{INK2}">Live in 4 to 6 weeks. Fixed price. Hours counted.</text>' +
        row(64, 420, [("Teardown, free", BG, ACC), ("Audit, 2 weeks", INK2, "#39322B"),
                      ("Build, 4 to 6 weeks", INK2, "#39322B"), ("Run and improve", INK2, "#39322B")])),
    "legal-intake-og.png": frame("DEMO: LEGAL GROUPS", ["New matters from every", "acquired firm, one intake"],
        mail(290, "Daniel Shaw: unfair dismissal claim", [("Possible conflict", RED, RBG), ("Employment", BG, INK), ("Kestrel Logistics is a Hollins Partners client", INK2, "#39322B")]) +
        mail(386, "Northwind Analytics Ltd: share sale", [("AML: enhanced", AMB, ABG), ("Corporate", BG, INK), ("No conflict across 3 firms", GRN, GBG)])),
    "broker-submissions-og.png": frame("DEMO: INSURANCE BROKERS", ["Renewal information to a", "market-ready submission"],
        f'<rect x="64" y="290" width="1072" height="250" rx="16" fill="{LIFT}"/>'
        f'<text x="92" y="334" font-size="22" font-weight="600" fill="{INK}">Harbourside Lettings Group Ltd: renewal on 15 Jan 2027</text>' +
        "".join(f'{chip(92, 356 + i * 44, s, fg, bg)[0]}<text x="{92 + 16 + len(s) * 11.0 + 18:.0f}" y="{379 + i * 44}" font-size="20" fill="{INK2}">{t}</text>'
                for i, (s, fg, bg, t) in enumerate([("missing", AMB, ABG, "Values for 3 flats from the acquired Clifton book"), ("39%", INK2, "#39322B", "Loss ratio on the expiring premium"),
                                                     ("out", RED, RBG, "Ashgrove Insurance: no unoccupied buildings"), ("approach", GRN, GBG, "Pennant Specialty (MGA)")]))),
    "defence-og.png": frame("DEFENCE AND DUAL-USE TECH", ["You build the thing that flies.", "I'll build the company that delivers it."],
        f'<text x="64" y="330" font-size="30" fill="{INK2}">After the raise, the hard part is everything around the product.</text>' +
        row(64, 380, [("Delivery", BG, ACC), ("Trial feedback to product", INK2, "#39322B"),
                      ("Hiring at speed", INK2, "#39322B"), ("Paperwork", INK2, "#39322B")]), foot="guzh.uk/defence"),
}
for name, svg in cards.items():
    if "\u2014" in svg or "\u00b7" in svg:
        raise SystemExit(f"{name}: em dash or middle dot in the card text")
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg)
    subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630", "-o", str(OUT / name), f.name], check=True)
    print("wrote assets/rebuild/" + name)
