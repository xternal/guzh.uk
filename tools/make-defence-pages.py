#!/usr/bin/env python3
"""Write the three /defence/ pages: one plain design, three angles on the same offer, for an A/B/C test.

    ./tools/make-defence-pages.py

  /defence/        delivery partner: what I take off your plate after a raise or a contract
  /defence/brief/  proof: loss to profit in six months, and what I am building now
  /defence/route/  the offer: two weeks, one bottleneck, fixed and running

Each email in the outreach links one of them (the CRM records which), so replies and bookings can be tied
to an angle. The pages share the layout, the "your first two weeks" picker and the proof; only the first
screen and the order differ. Rerun after changing anything here; the share cards come from
tools/make-defence-og.py. Pavel, 16 Nov 2026: purpose first, no decorative type.
"""
import html
import json
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent
REB = SITE / "tools" / "rebuild"
BOOK = "https://calendar.app.google/RG3g5WzxB3y9tXu39"

STYLE = (REB / "rebuild.css").read_text(encoding="utf-8") + """
/* /defence/ additions */
main{max-width:1120px}
.top{padding:12px max(16px,calc((100% - 1120px)/2))}
.hero{display:grid;gap:32px;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);align-items:start;padding:24px 0 8px}
@media (max-width:860px){.hero{grid-template-columns:1fr}}
.hero h1{font-size:clamp(30px,4.2vw,48px);max-width:20ch;margin:10px 0 16px}
.hero .sub{font-size:clamp(17px,1.8vw,20px);color:var(--ink-2);max-width:46ch;margin:0 0 18px}
.facts{display:grid;gap:10px;grid-template-columns:repeat(3,minmax(0,1fr));margin:18px 0 6px}
@media (max-width:520px){.facts{grid-template-columns:1fr}}
.fact{border-top:2px solid var(--accent);padding-top:8px}
.fact b{display:block;font-size:24px;font-weight:600;line-height:1.15}
.fact span{font-size:14px;color:var(--ink-2)}
.picker{background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:18px}
.picker h2{font-size:18px;margin:0 0 4px}
.picker .small{margin:0 0 12px}
.opts{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.opts button{font:inherit;font-size:14px;border:1px solid var(--rule);background:transparent;color:var(--ink-2);border-radius:999px;padding:7px 12px;cursor:pointer}
.opts button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.plan{margin-bottom:16px}
.js .plan{display:none;margin:0}
.js .plan.on{display:block}
.plan ol{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.plan li{display:grid;grid-template-columns:72px 1fr;gap:10px;font-size:15px}
.plan li b{font-size:13px;color:var(--ink-3);font-weight:500;padding-top:2px}
.plan .get{margin:14px 0 0;padding:10px 12px;border-radius:10px;background:var(--paper);border:1px solid var(--rule-soft);font-size:15px}
.plan .get b{color:var(--ink)}
@media (prefers-reduced-motion:no-preference){.js .plan.on{animation:rise .25s ease-out}@keyframes rise{from{opacity:0;transform:translateY(4px)}}}
.shots{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.shot{display:block;background:var(--card);border:1px solid var(--rule);border-radius:14px;overflow:hidden;color:var(--ink);text-decoration:none}
.shot:hover{border-color:var(--accent)}
.shot img{display:block;width:100%;height:auto;aspect-ratio:1280/520;object-fit:cover;object-position:top;border-bottom:1px solid var(--rule-soft)}
.shot div{padding:14px 16px}
.shot p{margin:.3em 0}
.gh{font-size:15px;color:var(--ink-2);margin:14px 0 0}
.gh b{color:var(--ink)}
.cta{margin:56px 0 8px;padding:24px;border:1px solid var(--rule);border-radius:16px;background:var(--card)}
.cta h2{margin:0 0 8px}
"""
SCRIPT = (REB / "rebuild.js").read_text(encoding="utf-8").split("/* Shared helpers for the demos. */")[0]

PAGE_JS = r"""
(function () {
  /* The picker: one situation at a time; without JS every plan shows. */
  var btns = document.querySelectorAll(".opts button");
  btns.forEach(function (b) {
    b.addEventListener("click", function () {
      btns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      document.querySelectorAll(".plan").forEach(function (p) { p.classList.toggle("on", p.id === b.dataset.plan); });
    });
  });
  /* Public GitHub activity, counted in the browser: pushes in the last 30 days. Counts only. */
  var out = document.getElementById("gh");
  if (!out || !window.fetch) return;
  var since = Date.now() - 30 * 864e5;
  fetch("https://api.github.com/users/xternal/events/public?per_page=100")
    .then(function (r) { if (!r.ok) throw 0; return r.json(); })
    .then(function (ev) {
      var pushes = 0, commits = 0, repos = {};
      ev.forEach(function (e) {
        if (e.type !== "PushEvent" || Date.parse(e.created_at) < since) return;
        pushes++; repos[e.repo.name] = 1;
        commits += (e.payload && e.payload.size) || 0;
      });
      if (!pushes) return;
      var n = Object.keys(repos).length;
      out.innerHTML = "Hands on this month: <b>" + pushes + " pushes" + (commits ? ", " + commits + " commits," : "") +
        "</b> to " + n + " public repositor" + (n === 1 ? "y" : "ies") + " in the last 30 days, counted live from " +
        '<a href="https://github.com/xternal">github.com/xternal</a>.';
    })
    .catch(function () {});
})();
"""

FACTS = """<div class="facts">
  <div class="fact"><b>6 months</b><span>from loss to profit, by fixing how the business runs</span></div>
  <div class="fact"><b>From zero</b><span>processes rebuilt in a new country, with no infrastructure to lean on</span></div>
  <div class="fact"><b>One team</b><span>out of people from different countries and cultures</span></div>
</div>"""

PLANS = [
    ("raised", "Just raised", [
        ("Week 1", "Tie the hiring plan to the delivery plan: which roles block which milestone, in what order."),
        ("Week 2", "Hiring pipeline, interview loop and onboarding pack running, the first critical roles in process."),
    ], "a hiring plan your board can read against the delivery dates, and a pipeline that runs without a founder in every step."),
    ("contract", "Won a contract", [
        ("Week 1", "Break the contract into deliverables, dates, acceptance tests and the reports you owe."),
        ("Week 2", "A delivery tracker the whole team uses, and the first customer report drafted from it."),
    ], "one place that shows whether you are on time, and reports that write themselves from the work."),
    ("factory", "Scaling production", [
        ("Week 1", "Map suppliers, lead times, quality and test paperwork for the parts that gate a build."),
        ("Week 2", "Supplier onboarding and parts tracking live, with late parts flagged before they are late."),
    ], "you know which part will hold up the next batch while there is still time to fix it."),
    ("trials", "Running trials", [
        ("Week 1", "Gather what the last trials produced: operator notes, logs, videos, emails, the things said in the debrief."),
        ("Week 2", "A trial-to-backlog flow: every trial ends in a short, ranked list for engineering."),
    ], "feedback from the field reaches the product before the next trial, not after the next round."),
]


def picker(heading):
    opts = "\n".join(f'    <button type="button" data-plan="p-{k}" aria-pressed="{"true" if i == 0 else "false"}">{html.escape(label)}</button>'
                     for i, (k, label, _, _) in enumerate(PLANS))
    plans = ""
    for i, (k, label, steps, get) in enumerate(PLANS):
        lis = "".join(f"<li><b>{w}</b><span>{html.escape(t)}</span></li>" for w, t in steps)
        plans += (f'  <div class="plan{" on" if i == 0 else ""}" id="p-{k}" role="region" aria-label="{html.escape(label)}">'
                  f'<ol>{lis}</ol><p class="get"><b>You get:</b> {html.escape(get)}</p></div>\n')
    return f"""<section class="picker" aria-labelledby="pick-h">
  <h2 id="pick-h">{heading}</h2>
  <p class="small">Pick where you are. This is what I would do with you in the first two weeks.</p>
  <div class="opts" role="group" aria-label="Where you are">
{opts}
  </div>
{plans}</section>"""


PROOF = f"""<h2>Hands on, now</h2>
<p class="muted">I write and ship the software myself. Two things I am building alongside, for society and the state:</p>
<div class="shots">
  <a class="shot" href="https://ruminator.xyz/">
    <img src="/assets/defence/ruminator.jpg" width="1280" height="520" loading="lazy" alt="Ruminator's home page: Understand Russia through its local press, with live figures for regions, outlets, articles and claims checked.">
    <div><h3>Ruminator</h3><p class="muted">Reads Russia's regional and local press every day, from state television to residents' channels, and shows what each kind of outlet reports and how it frames it. Every claim is checked word for word against the source. For analysts, journalists and diplomats.</p></div>
  </a>
  <a class="shot" href="https://ledgergov.uk/">
    <img src="/assets/defence/ledgergov.jpg" width="1280" height="520" loading="lazy" alt="LedgerGov.UK's home page: the UK's income, spending, borrowing and debt, and political promises tracked against the money.">
    <div><h3>LedgerGov.UK</h3><p class="muted">An open P&amp;L of the UK state: where public money comes from, where it goes and what every political promise would cost, each number linked to its official source.</p></div>
  </a>
</div>
<p class="gh" id="gh">My code is public at <a href="https://github.com/xternal">github.com/xternal</a>.</p>"""

TAKE = """<h2>What I take off your plate</h2>
<div class="grid">
  <div class="card"><p class="kicker">Delivery</p><h3>Prototype to production, on the date</h3><p class="muted">Production tracking, supplier onboarding, quality and test paperwork.</p></div>
  <div class="card"><p class="kicker">Product</p><h3>Trial feedback into the next release</h3><p class="muted">What operators and customers say, captured and ranked for engineering.</p></div>
  <div class="card"><p class="kicker">Scale</p><h3>Hiring and systems that hold</h3><p class="muted">The first operations team, hiring at speed, and the internal software that keeps 40 people working like 400.</p></div>
  <div class="card"><p class="kicker">Paperwork</p><h3>The admin around every contract</h3><p class="muted">Bid packs, contract reporting and customer documents, drafted and tracked.</p></div>
</div>"""

STAYS = """<h2>What stays yours</h2>
<p>The technology, the defence know-how, the clearances and the customer relationships. I work on the unclassified side: the machinery that turns funding and contracts into delivery. Where any part needs vetting, we say so plainly at the start.</p>"""

HOW = """<h2>How we start</h2>
<ol class="steps">
  <li><h3>30 minutes</h3><p class="muted">Where delivery is slowest right now, and what the next 18 months need.</p></li>
  <li><h3>Two weeks on one bottleneck</h3><p class="muted">Mapped, a working fix for the worst of it, and a plain plan for the rest.</p></li>
  <li><h3>Then, together</h3><p class="muted">A project, a part-time role inside your team, or something closer. We pick the shape that fits.</p></li>
</ol>"""

WHO = """<h2>Who I am</h2>
<p>Pavel Guzhikov, London. Twenty years of building companies, as founder and as the person who makes them run. I've rebuilt a company's processes from zero in a new country, brought teams from different cultures together into one, and taken a business from loss to profit in six months. I was on the founding team at Uzum, Uzbekistan's first unicorn: lending, payments, cards and a marketplace for millions of users, in a market with no digital infrastructure. Before that I built fintech products with more than 100 banks, and founded and sold two companies. I am most interested now in problems where the technology is hard, the deployment is political and the stakes are national: defence and dual-use, sovereign infrastructure, public systems.</p>"""

FAQ = """<h2>Questions</h2>
<dl class="faq">
  <dt>Why someone from outside defence?</dt>
  <dd>Because the problems after a raise are the same in every fast-growing company: too much to do, too few people, and processes built for ten staff carrying a hundred. Defence adds rules on top; it doesn't change the arithmetic.</dd>
  <dt>Is this a consultancy?</dt>
  <dd>No decks. Working software and processes that run differently the following week.</dd>
  <dt>Do you need a clearance?</dt>
  <dd>Not for the unclassified work. Where a task needs vetting, we agree at the start who does it and how.</dd>
  <dt>Who is it for?</dt>
  <dd>UK defence and dual-use companies from about 15 to a few hundred people, usually just after a funding round, a first big contract or a new site.</dd>
</dl>"""


def cta(text):
    return f"""<section class="cta">
  <h2>{text}</h2>
  <div class="row"><a class="btn" href="{BOOK}" target="_blank" rel="noopener noreferrer">Book 30 minutes</a><a class="btn ghost" href="mailto:pavel@guzh.uk">pavel@guzh.uk</a></div>
</section>"""


def buttons():
    return f'<div class="row"><a class="btn" href="{BOOK}" target="_blank" rel="noopener noreferrer">Book 30 minutes</a><a class="btn ghost" href="mailto:pavel@guzh.uk">pavel@guzh.uk</a></div>'


PAGES = [
    {   # A: delivery partner
        "path": "defence/index.html", "url": "https://guzh.uk/defence/", "slug": "delivery",
        "title": "I help UK defence startups turn a raise or a contract into delivery",
        "description": "Hiring, suppliers, production and paperwork, taken on hands-on from day one so your engineers stay on the product. Pavel Guzhikov: took a business from loss to profit in six months.",
        "image_alt": "I help UK defence startups turn a raise or a contract into delivery: hiring, suppliers, production, paperwork.",
        "hero": f"""<div>
  <p class="kicker">Defence and dual-use, UK</p>
  <h1>I help defence startups turn a raise or a contract into delivery.</h1>
  <p class="sub">Hiring, suppliers, production and paperwork, hands-on from day one, so your engineers stay on the product.</p>
  {buttons()}
  {FACTS}
</div>""",
        "picker": "Your first two weeks with me",
        "order": [TAKE, PROOF, WHO, STAYS, HOW, FAQ],
        "cta": "Tell me where delivery is slowest. 30 minutes.",
    },
    {   # B: proof
        "path": "defence/brief/index.html", "url": "https://guzh.uk/defence/brief/", "slug": "proof",
        "title": "From loss to profit in six months. Now for defence startups",
        "description": "Pavel Guzhikov has taken a business from loss to profit in six months and rebuilt a company's processes from zero in a new country, and still ships his own code. He now helps UK defence and dual-use startups deliver after a raise or a contract.",
        "image_alt": "From loss to profit in six months. Now I do it for defence startups.",
        "hero": f"""<div>
  <p class="kicker">Defence and dual-use, UK</p>
  <h1>I've taken a business from loss to profit in six months. Now I do it for defence startups.</h1>
  <p class="sub">After a raise or a contract, the hard part is everything around the product. I've run that part in a new country with a mixed team, and I still write the software myself.</p>
  {buttons()}
  {FACTS}
</div>""",
        "picker": "What I would do first, with you",
        "order": [WHO, PROOF, TAKE, STAYS, HOW, FAQ],
        "cta": "Want the same speed after your raise? 30 minutes.",
    },
    {   # C: the two-week offer
        "path": "defence/route/index.html", "url": "https://guzh.uk/defence/route/", "slug": "twoweeks",
        "title": "Two weeks. One bottleneck. Fixed and running",
        "description": "For UK defence and dual-use startups: pick what slows your delivery most. In two weeks Pavel Guzhikov maps it, ships a working fix and leaves a plain plan for the rest.",
        "image_alt": "Two weeks. One bottleneck. Fixed and running. For UK defence and dual-use startups.",
        "hero": f"""<div>
  <p class="kicker">Defence and dual-use, UK</p>
  <h1>Two weeks. One bottleneck. Fixed and running.</h1>
  <p class="sub">Pick the thing slowing your delivery most: hiring, a contract, production or trials. In two weeks it's mapped, a working fix is live, and you have a plain plan for the rest.</p>
  {buttons()}
  {FACTS}
</div>""",
        "picker": "Pick your bottleneck",
        "order": [HOW, TAKE, PROOF, WHO, STAYS, FAQ],
        "cta": "Which bottleneck first? 30 minutes to pick it.",
    },
]

HEAD = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by tools/make-defence-pages.py. Edit there, not here. -->
<title>{title} | Pavel Guzhikov</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Pavel Guzhikov">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://guzh.uk/assets/defence/{slug}-og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{image_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://guzh.uk/assets/defence/{slug}-og.png">
<meta name="twitter:image:alt" content="{image_alt}">
<meta name="theme-color" content="#F1EFE9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#241F1A" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&amp;display=swap" rel="stylesheet">
<script type="application/ld+json">{jsonld}</script>
<script>
try {{ var t = localStorage.getItem("theme"); if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t); }} catch (e) {{}}
document.documentElement.classList.add("js");
</script>
<style>
{style}</style>
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<header class="top">
  <a class="home" href="/">Pavel Guzhikov</a>
  <nav class="tabs" aria-label="Pages">
    <a href="/defence/" aria-current="page">Defence tech</a>
    <a href="/rebuild/">Back-office rebuild</a>
  </nav>
  <button class="theme" type="button" aria-label="Switch light or dark">
    <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 1.8a6.2 6.2 0 0 1 0 12.4z" fill="currentColor"/></svg>
  </button>
</header>
<main id="main">
<div class="hero">
{hero}
{picker}
</div>
{body}
{cta}
</main>
<footer class="foot">
  <p>Pavel Guzhikov, London. <a href="{book}" target="_blank" rel="noopener noreferrer">Book 30 minutes</a>, or write to <a href="mailto:pavel@guzh.uk">pavel@guzh.uk</a>. Visits are counted by Cloudflare Web Analytics, without cookies or tracking you.</p>
  <p class="credit"><a href="https://guzh.uk">Made by Pavel Guzhikov</a> <a href="https://ko-fi.com/pavelg" target="_blank" rel="noopener noreferrer">Buy me a matcha 🍵</a></p>
</footer>
<script>
{script}{page_js}</script>
<script>
/* Cloudflare Web Analytics: counts visits and page views, sets no cookies and stores nothing on
   the reader's device. Loaded only on guzh.uk itself, so local previews stay out of the numbers. */
if (location.hostname === "guzh.uk") (function(){{
  var s = document.createElement("script");
  s.src = "https://static.cloudflareinsights.com/beacon.min.js";
  s.setAttribute("data-cf-beacon", '{{"token": "bb18b698dcf74edab4f19890c1fb5005"}}');
  document.body.appendChild(s);
}})();
</script>
</body>
</html>
"""


def main():
    for p in PAGES:
        ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": p["title"],
                         "description": p["description"], "url": p["url"], "areaServed": "GB",
                         "serviceType": "Delivery, product and scale-up partner for defence and dual-use technology companies",
                         "provider": {"@type": "Person", "name": "Pavel Guzhikov", "url": "https://guzh.uk/"}},
                        ensure_ascii=False)
        page = HEAD.format(title=html.escape(p["title"]), description=html.escape(p["description"]), url=p["url"],
                           slug=p["slug"], image_alt=html.escape(p["image_alt"]), jsonld=ld, style=STYLE,
                           hero=p["hero"], picker=picker(p["picker"]), body="\n\n".join(p["order"]),
                           cta=cta(p["cta"]), book=BOOK, script=SCRIPT, page_js=PAGE_JS)
        bad = sorted({c for c in page if c in "—·"})
        if bad:
            raise SystemExit(f"{p['path']}: contains {bad}; no em dashes or middle dots (Pavel's rule)")
        out = SITE / p["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print("wrote", p["path"])


if __name__ == "__main__":
    main()
