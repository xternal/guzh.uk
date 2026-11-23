#!/usr/bin/env python3
"""Write /dd/: technology and operations due diligence for investors (outreach hook "What breaks after you buy it").

    ./tools/make-dd-page.py

Same design as /exit/ and /pe/ (reuses tools/make-defence-pages.py). Share card: tools/make-dd-og.py. Pavel, 23 Nov 2026.
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
    ("fintech", "Buying a fintech or lender", [
        ("Week 1", "The platform, the ledgers, the credit and risk stack, the regulator's obligations, and who really holds the keys to each."),
        ("Week 2", "A plain report: the red flags with time and cost to fix, and the first 100 days in order of risk."),
    ], "you price the deal on what the business can run, not on what the deck says."),
    ("software", "Buying a marketplace or software company", [
        ("Week 1", "Architecture, data and security; which metrics are real and which are assembled by hand each month."),
        ("Week 2", "What scales with the plan, what breaks first, and what the tech debt will cost in people and months."),
    ], "no surprise rebuild six months after completion."),
    ("round", "Backing a founder after a round", [
        ("Week 1", "Can the operations carry the growth in the plan: hiring, onboarding, support, reporting, finance."),
        ("Week 2", "The two or three things to fix before the money goes into growth, with owners and dates."),
    ], "the round buys growth, not firefighting."),
    ("carve", "Carve-out or buy-and-build", [
        ("Week 1", "Every system, contract and process that must be separated or merged, and who depends on what."),
        ("Week 2", "An integration or separation plan with dates, owners and the true cost of the transition period."),
    ], "day one works, and the synergies in the model are ones you can actually reach."),
]

TAKE = """<h2>What I look at</h2>
<div class="grid">
  <div class="card"><p class="kicker">Technology</p><h3>Architecture, security, debt</h3><p class="muted">What the platform can carry, where it is fragile, and what a rebuild would cost.</p></div>
  <div class="card"><p class="kicker">Operations</p><h3>How the work really gets done</h3><p class="muted">Processes, manual work behind the dashboards, and who holds the knowledge.</p></div>
  <div class="card"><p class="kicker">Product and data</p><h3>Numbers you can trust</h3><p class="muted">Which metrics come from the system and which are rebuilt in a spreadsheet each month.</p></div>
  <div class="card"><p class="kicker">People</p><h3>Key-person risk</h3><p class="muted">Who the business can't lose in the first year, and how to keep it running if it does.</p></div>
</div>"""

STAYS = """<h2>What stays yours</h2>
<p>The investment decision. I tell you what I see in plain words, including what you would rather not hear. Fixing it afterwards is a separate choice, never a condition: if you want me on day 101, we agree that on its own.</p>"""

HOW = """<h2>How it works</h2>
<ol class="steps">
  <li><h3>30 minutes</h3><p class="muted">The target, the thesis and the questions the investment committee will ask.</p></li>
  <li><h3>One or two weeks</h3><p class="muted">Data room, systems and the people who run them, on site where it helps.</p></li>
  <li><h3>A report and a call</h3><p class="muted">Red flags with cost and time to fix, and the first 100 days in order of risk.</p></li>
</ol>"""

WHO = """<h2>Who I am</h2>
<p>Pavel Guzhikov, London. I have built and run the kind of companies investors buy. I was on the founding team at Uzum, Uzbekistan's first unicorn, and ran Uzum Bank: banking, payments, cards and lending, built from zero with acquisitions integrated along the way. I founded and sold Worki, a jobs marketplace acquired by Mail.Ru Group, co-founded Dengi Vpered, an earned-wage access business backed by Target Global, and delivered more than 100 banking solutions for banks across Europe. I read the code and I read the P&amp;L, so the report covers both.</p>"""

FAQ = """<h2>Questions</h2>
<dl class="faq">
  <dt>Instead of a Big Four technology review?</dt>
  <dd>Beside it, or instead of it on smaller deals. It is an operator's view: faster, closer to the floor, and focused on what will break after you own it.</dd>
  <dt>How fast?</dt>
  <dd>One week for a focused question, two for a full review. I can start within days of an NDA.</dd>
  <dt>Which companies?</dt>
  <dd>Fintech, lending, payments, marketplaces and B2B software, from about 20 to a few hundred people.</dd>
  <dt>Confidential?</dt>
  <dd>Yes. I sign your NDA before the data room opens.</dd>
</dl>"""

PAGE = {
    "path": "dd/index.html", "url": "https://guzh.uk/dd/", "slug": "dd",
    "title": "What breaks after you buy it: technology and operations due diligence",
    "description": "For investors in fintech, lending, payments, marketplaces and software: technology and operations due diligence in one to two weeks by an operator who has built and run such companies. A plain report on what breaks after the deal and what it costs to fix.",
    "image_alt": "What breaks after you buy it. Technology and operations due diligence in one to two weeks, by an operator.",
    "hero": f"""<div>
  <p class="kicker">For investors in fintech and software</p>
  <h1>What breaks after you buy it.</h1>
  <p class="sub">Technology and operations due diligence in one to two weeks, by someone who has built and run the kind of company you are buying. A plain report: what breaks after the deal, what it costs to fix, and what to do first.</p>
  {D.buttons()}
  {D.FACTS}
</div>""",
    "picker": "Your two weeks with me",
    "order": [TAKE, D.PROOF, WHO, STAYS, HOW, FAQ],
    "cta": "Which deal is on the table? 30 minutes.",
}

NAV_OLD = """    <a href="/defence/" aria-current="page">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""
NAV_NEW = """    <a href="/dd/" aria-current="page">For investors</a>
    <a href="/exit/">For owners</a>
    <a href="/pe/">For PE owners</a>
    <a href="/defence/">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>"""


def main():
    assert NAV_OLD in D.HEAD, "defence nav changed; update NAV_OLD"
    head = D.HEAD.replace(NAV_OLD, NAV_NEW).replace("/assets/defence/{slug}-og.png", "/assets/dd/{slug}-og.png") \
        .replace("Generated by tools/make-defence-pages.py", "Generated by tools/make-dd-page.py")
    p = PAGE
    ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": p["title"],
                     "description": p["description"], "url": p["url"], "areaServed": "GB",
                     "serviceType": "Technology and operations due diligence for investors",
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
