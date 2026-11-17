#!/usr/bin/env python3
"""Write /pe/: the page for private equity owners of British brands (outreach hook "Day 101").

    ./tools/make-pe-page.py

Same design, picker and proof as the /defence/ pages (it reuses tools/make-defence-pages.py); only the words
differ. The offer: precise management and execution inside a company the fund has just bought, hands-on
beside management. Share card: tools/make-pe-og.py. Pavel, 17 Nov 2026.
"""
import html
import importlib.util
import json
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("defence", SITE / "tools" / "make-defence-pages.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

D.PLANS = [
    ("bought", "Just bought", [
        ("Week 1", "Turn the investment case into a weekly scorecard: the handful of numbers that prove the plan is working, and who owns each."),
        ("Week 2", "The scorecard running from real data, the first weekly review held with management, the three biggest blockers named with owners."),
    ], "a plan you can read every Monday, not a deck you reread at the next board."),
    ("founder", "Founder-run brand", [
        ("Week 1", "Find where the business lives in one person's head or one spreadsheet: stock, orders, suppliers, cash."),
        ("Week 2", "The worst of those moved into a simple system the team runs, with the founder's blessing."),
    ], "the brand keeps its founder's taste and loses its single point of failure."),
    ("stock", "Scaling stock and production", [
        ("Week 1", "Map suppliers, lead times, stock and the season ahead: what sells out, what sits."),
        ("Week 2", "Stock and production planning live, with reorder points set and late supply flagged early."),
    ], "fewer sell-outs on the winners and less cash sitting in the wrong stock."),
    ("bolton", "Adding a bolt-on", [
        ("Week 1", "List what has to become one: finance, stock, customer data, people, reporting."),
        ("Week 2", "An integration plan with dates and owners, and the first shared report running across both companies."),
    ], "one view of the combined business within weeks, not after the next audit."),
]

TAKE = """<h2>What I take on</h2>
<div class="grid">
  <div class="card"><p class="kicker">Execution</p><h3>The 100-day plan, run weekly</h3><p class="muted">Owners, dates, a scorecard, and someone on site who makes sure it happens.</p></div>
  <div class="card"><p class="kicker">Operations</p><h3>Stock, supply and production</h3><p class="muted">Planning that matches the season, suppliers who deliver on time, and fewer surprises.</p></div>
  <div class="card"><p class="kicker">Numbers</p><h3>Reporting you trust from month one</h3><p class="muted">Monthly close, KPIs and the board pack from one source, not five spreadsheets.</p></div>
  <div class="card"><p class="kicker">Systems</p><h3>Software that fits the business</h3><p class="muted">I pick or build the tools myself, so 40 people work like 400.</p></div>
</div>"""

STAYS = """<h2>What stays yours</h2>
<p>The thesis, the board and the brand. Management stays in charge: I work beside them as one of the team, not as the fund's auditor. You get a short weekly note: what moved, what is stuck, what needs a decision.</p>"""

HOW = """<h2>How we start</h2>
<ol class="steps">
  <li><h3>30 minutes</h3><p class="muted">Which company, what the plan says, and where it is already slipping.</p></li>
  <li><h3>Two weeks in one company</h3><p class="muted">The scorecard running, the worst bottleneck mapped and a working fix live.</p></li>
  <li><h3>Then, the shape that fits</h3><p class="muted">An interim operating role, a part-time seat, or work across the portfolio.</p></li>
</ol>"""

WHO = """<h2>Who I am</h2>
<p>Pavel Guzhikov, London. Twenty years of building companies, as founder and as the person who makes them run. I was on the founding team at Uzum, Uzbekistan's first unicorn: lending, payments, cards and a marketplace, millions of users and 1,000+ people in two years, in a market with no digital infrastructure. Before that I built fintech products with more than 100 banks, and founded and sold two companies. I like businesses where a good product meets messy operations: that is where precise management pays back fastest.</p>"""

FAQ = """<h2>Questions</h2>
<dl class="faq">
  <dt>Interim manager, adviser or consultant?</dt>
  <dd>A hands-on operator. I run the work with management and write the software where it helps. No decks: processes that run differently the following week.</dd>
  <dt>Which companies?</dt>
  <dd>British brands from about 20 to a few hundred people, usually in the first year after an investment or during a buy-and-build.</dd>
  <dt>Why someone from fintech?</dt>
  <dd>Because the arithmetic of growth is the same everywhere: too much to do, too few people, and processes built for ten carrying a hundred. I have run it at 1,000+ people in two years.</dd>
  <dt>Who do I report to?</dt>
  <dd>We agree that at the start: usually the operating partner, with management as my day-to-day team.</dd>
</dl>"""

PAGE = {
    "path": "pe/index.html", "url": "https://guzh.uk/pe/", "slug": "pe",
    "title": "I make the 100-day plan happen in the British brands you buy",
    "description": "For private equity owners of British brands: precise management and execution inside the company you have just bought, hands-on beside management and measured weekly. Pavel Guzhikov: 1,000+ people in two years at Uzum.",
    "image_alt": "I make the 100-day plan happen. Hands-on, beside management, measured weekly. For private equity owners of British brands.",
    "hero": f"""<div>
  <p class="kicker">For private equity owners of British brands</p>
  <h1>I make the 100-day plan happen.</h1>
  <p class="sub">Precise management and execution inside the company you have just bought: hands-on beside management, measured weekly, so your deal team doesn't have to chase it.</p>
  {D.buttons()}
  {D.FACTS}
</div>""",
    "picker": "Your first two weeks with me",
    "order": [TAKE, D.PROOF, WHO, STAYS, HOW, FAQ],
    "cta": "Which company is on day 101? 30 minutes.",
}

NAV_OLD = """    <a href="/defence/" aria-current="page">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""
NAV_NEW = """    <a href="/pe/" aria-current="page">For PE owners</a>
    <a href="/defence/">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""


def main():
    assert NAV_OLD in D.HEAD, "defence nav changed; update NAV_OLD"
    head = D.HEAD.replace(NAV_OLD, NAV_NEW).replace("/assets/defence/{slug}-og.png", "/assets/pe/{slug}-og.png") \
        .replace("Generated by tools/make-defence-pages.py", "Generated by tools/make-pe-page.py")
    p = PAGE
    ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": p["title"],
                     "description": p["description"], "url": p["url"], "areaServed": "GB",
                     "serviceType": "Interim operating and execution partner for private equity portfolio companies",
                     "provider": {"@type": "Person", "name": "Pavel Guzhikov", "url": "https://guzh.uk/"}},
                    ensure_ascii=False)
    page = head.format(title=html.escape(p["title"]), description=html.escape(p["description"]), url=p["url"],
                       slug=p["slug"], image_alt=html.escape(p["image_alt"]), jsonld=ld, style=D.STYLE,
                       hero=p["hero"], picker=D.picker(p["picker"]), body="\n\n".join(p["order"]),
                       cta=D.cta(p["cta"]), book=D.BOOK, script=D.SCRIPT, page_js=D.PAGE_JS)
    bad = sorted({c for c in page if c in "—·"})
    if bad:
        raise SystemExit(f"{p['path']}: contains {bad}; no em dashes or middle dots (Pavel's rule)")
    out = SITE / p["path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("wrote", p["path"])


if __name__ == "__main__":
    main()
