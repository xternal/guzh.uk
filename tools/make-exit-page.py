#!/usr/bin/env python3
"""Write /exit/: the page for founder-owners who will sell one day (outreach hook "Worth more without you").

    ./tools/make-exit-page.py

Same design, picker and proof as /pe/ and /defence/ (reuses tools/make-defence-pages.py); only the words differ.
The offer: fix what buyers mark down (dependence on the owner, numbers, processes, management). Share card:
tools/make-exit-og.py. Pavel, 23 Nov 2026.
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
    ("selling", "Selling in two or three years", [
        ("Week 1", "List what a buyer will ask for in due diligence, and where each answer lives today: a system, a spreadsheet or your head."),
        ("Week 2", "The three things most likely to cut the price, named with owners and dates, and the first one already being fixed."),
    ], "you learn what costs you money in the sale years before a buyer tells you."),
    ("me", "It all runs through me", [
        ("Week 1", "Map the decisions and knowledge only you hold: pricing, key customers, suppliers, the jobs nobody else can quote."),
        ("Week 2", "The first of them handed to a person or a simple system, with you checking the work instead of doing it."),
    ], "the business keeps its pace in the weeks you are not there."),
    ("numbers", "Numbers take a week to pull", [
        ("Week 1", "Trace where the monthly numbers really come from, and which spreadsheets disagree with each other."),
        ("Week 2", "A monthly close and a short scorecard running from one source, ready to show a buyer as they are."),
    ], "numbers a buyer can trust without sending in a team to rebuild them."),
    ("team", "No second layer of management", [
        ("Week 1", "Who could run what: sales, operations, finance. Where the gaps are and what each role would own."),
        ("Week 2", "Roles agreed, a weekly meeting with a scorecard, and the first decisions made without you in the room."),
    ], "a team a buyer can see and wants to keep, not a business that leaves with its founder."),
]

TAKE = """<h2>What I take on</h2>
<div class="grid">
  <div class="card"><p class="kicker">Independence</p><h3>A business that runs without you</h3><p class="muted">Decisions, customers and know-how moved out of one head and into the team.</p></div>
  <div class="card"><p class="kicker">Numbers</p><h3>Figures a buyer trusts</h3><p class="muted">Monthly close, margins and KPIs from one source, not five spreadsheets.</p></div>
  <div class="card"><p class="kicker">Operations</p><h3>Processes that don't need heroes</h3><p class="muted">Quoting, orders, stock and delivery that work the same on a bad day.</p></div>
  <div class="card"><p class="kicker">Systems</p><h3>Software that fits the business</h3><p class="muted">I pick or build the tools myself, so 40 people work like 400.</p></div>
</div>"""

STAYS = """<h2>What stays yours</h2>
<p>The company, the decisions and the timing. I am not a broker and I don't sell your company: I make it worth more, whoever you sell to and whenever you choose. Your team needs to know only that we are making the business run better, which is true. You get a short weekly note: what moved, what is stuck, what needs your decision.</p>"""

HOW = """<h2>How we start</h2>
<ol class="steps">
  <li><h3>30 minutes</h3><p class="muted">Your business, your plans for it, and what a buyer would see today.</p></li>
  <li><h3>Two weeks inside</h3><p class="muted">The price risks named, the worst bottleneck mapped and a working fix live.</p></li>
  <li><h3>Then, the shape that fits</h3><p class="muted">A part-time operating role, an interim seat, or one project at a time.</p></li>
</ol>"""

WHO = """<h2>Who I am</h2>
<p>Pavel Guzhikov, London. Twenty years of building companies, as founder and as the person who makes them run. I've built companies at every stage: from zero, through scaling and profit, to a sale. I founded and sold two companies myself, so I know what a buyer looks for and what makes them take money off the price. I was on the founding team at Uzum, Uzbekistan's first unicorn: lending, payments, cards and a marketplace for millions of users. Along the way I've rebuilt a company's processes from zero in a new country and taken a business from loss to profit in six months. I'm hands-on in the technology, the product and the business.</p>"""

FAQ = """<h2>Questions</h2>
<dl class="faq">
  <dt>When should I start?</dt>
  <dd>Two or three years before a sale is best: long enough for the changes to show in the accounts a buyer reads. Later still helps, but a buyer sees the last two or three years.</dd>
  <dt>Do you help with the sale itself?</dt>
  <dd>No. Your corporate finance adviser runs the sale. I make the business worth more and easier to buy, and I'm happy to work alongside them.</dd>
  <dt>Which companies?</dt>
  <dd>Owner-run British businesses from about 20 to a few hundred people: manufacturers, distributors, contractors, producers, service firms.</dd>
  <dt>Interim manager, adviser or consultant?</dt>
  <dd>A hands-on operator. I run the work with your team and write the software where it helps. No decks: processes that run differently the following week.</dd>
  <dt>Is it confidential?</dt>
  <dd>Yes. Nobody outside needs to know you are thinking about a sale.</dd>
</dl>"""

PAGE = {
    "path": "exit/index.html", "url": "https://guzh.uk/exit/", "slug": "exit",
    "title": "Worth more without you: get your business ready to sell",
    "description": "For founders and owners who will sell one day: buyers pay more for a business that runs without its owner. Pavel Guzhikov works beside you to fix what buyers mark down: processes, numbers and a second layer of management, measured weekly.",
    "image_alt": "Worth more without you. Getting an owner-run business ready to sell: processes, numbers and a team that run without the founder.",
    "hero": f"""<div>
  <p class="kicker">For founders who will sell one day</p>
  <h1>Worth more without you.</h1>
  <p class="sub">Buyers pay for a business that runs without its owner, and take money off for one that doesn't. I work beside you to fix what they mark down: processes, numbers and a second layer of management, measured weekly.</p>
  {D.buttons()}
  {D.FACTS}
</div>""",
    "picker": "Your first two weeks with me",
    "order": [TAKE, D.PROOF, WHO, STAYS, HOW, FAQ],
    "cta": "What would a buyer see today? 30 minutes.",
}

NAV_OLD = """    <a href="/defence/" aria-current="page">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""
NAV_NEW = """    <a href="/exit/" aria-current="page">For owners</a>
    <a href="/pe/">For PE owners</a>
    <a href="/defence/">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""


def main():
    assert NAV_OLD in D.HEAD, "defence nav changed; update NAV_OLD"
    head = D.HEAD.replace(NAV_OLD, NAV_NEW).replace("/assets/defence/{slug}-og.png", "/assets/exit/{slug}-og.png") \
        .replace("Generated by tools/make-defence-pages.py", "Generated by tools/make-exit-page.py")
    p = PAGE
    ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": p["title"],
                     "description": p["description"], "url": p["url"], "areaServed": "GB",
                     "serviceType": "Exit readiness and operating partner for owner-run businesses",
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
