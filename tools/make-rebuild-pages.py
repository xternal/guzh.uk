#!/usr/bin/env python3
"""Write the /rebuild/ pages: the offer, and two working demos of a back-office process rebuilt as software.

    ./tools/make-rebuild-pages.py

Writes rebuild/index.html, rebuild/block-requests/index.html and rebuild/lending-intake/index.html from
the shared layout here and each page's body in tools/rebuild/. The demos run entirely in the reader's browser
on invented sample data: nothing is sent anywhere. Rerun after changing anything in tools/rebuild/ or here.
"""
import html
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent
SRC = SITE / "tools" / "rebuild"

PAGES = [
    {
        "path": "rebuild/index.html", "url": "https://guzh.uk/rebuild/", "nav": "overview",
        "title": "The same back-office work, with fewer people",
        "description": "Your team stops copying, checking and chasing by hand in one process it runs every day. The same people handle more work, without new hires and with fewer mistakes, and you see the hours saved, counted before and after.",
        "image": "rebuild-og.png",
        "image_alt": "One back-office process, rebuilt as working software in 4 to 6 weeks.",
        "body": "index.html",
    },
    {
        "path": "rebuild/block-requests/index.html", "url": "https://guzh.uk/rebuild/block-requests/",
        "nav": "block", "title": "Demo: block-management requests, triaged in seconds",
        "description": "Your team stops reading, sorting and forwarding every resident email by hand. Each one is routed and answered as it arrives, emergencies first, so the same team can run more blocks.",
        "image": "block-requests-og.png",
        "image_alt": "A block manager's inbox triaged: each request tagged by kind, urgency, block and contractor.",
        "body": "block-requests.html",
    },
    {
        "path": "rebuild/lending-intake/index.html", "url": "https://guzh.uk/rebuild/lending-intake/",
        "nav": "lending", "title": "Demo: an SME loan pack to a draft credit memo",
        "description": "Your underwriters stop keying bank statements and start every application from a drafted memo with the checks already done. When the facility grows, the same team decides more loans.",
        "image": "lending-intake-og.png",
        "image_alt": "An SME loan pack turned into checks and a draft credit memo with affordability figures.",
        "body": "lending-intake.html",
    },
    {
        "path": "rebuild/legal-intake/index.html", "url": "https://guzh.uk/rebuild/legal-intake/",
        "nav": "legal", "title": "Demo: new matters from every acquired firm, one intake",
        "description": "Your teams stop searching each acquired firm’s old system for conflicts. Every new matter at every firm you buy is checked against the whole group before work starts, from the first week.",
        "image": "legal-intake-og.png",
        "image_alt": "New legal matters from three acquired firms checked against one group conflict index.",
        "body": "legal-intake.html",
    },
    {
        "path": "rebuild/broker-submissions/index.html", "url": "https://guzh.uk/rebuild/broker-submissions/",
        "nav": "insurance", "title": "Demo: a client's renewal information to a market-ready submission",
        "description": "Your handlers stop rekeying renewals and chasing missing details by hand. Every submission reaches insurers complete, and only the ones that will quote, so the same team places more business.",
        "image": "broker-submissions-og.png",
        "image_alt": "A renewal turned into a submission: details found and missing, loss ratio, and the markets in appetite.",
        "body": "broker-submissions.html",
    },
    {
        "path": "defence/index.html", "url": "https://guzh.uk/defence/", "nav": "defence", "navset": "defence",
        "title": "Defence tech: you build the thing that flies, I build the company that delivers it",
        "description": "For UK defence and dual-use startups after a raise or a first contract: Pavel Guzhikov takes on delivery, product feedback, hiring and paperwork, so your engineers stay on the product.",
        "image": "defence-og.png",
        "image_alt": "You build the thing that flies. I'll build the company that delivers it: delivery, product, scale, paperwork.",
        "body": "defence.html",
        "footer": 'Pavel Guzhikov. <a href="https://calendar.app.google/RG3g5WzxB3y9tXu39" target="_blank" rel="noopener noreferrer">Book 30 minutes</a>, or write to <a href="mailto:pavel@guzh.uk">pavel@guzh.uk</a>.',
    },
]

NAVSETS = {"defence": [("defence", "/defence/", "Defence tech"), ("overview", "/rebuild/", "Back-office rebuild")]}
FOOTER = 'Empatiq Limited. <a href="https://calendar.app.google/RG3g5WzxB3y9tXu39" target="_blank" rel="noopener noreferrer">Book a free 30-minute teardown of one process</a>, or write to <a href="mailto:pavel@guzh.uk">pavel@guzh.uk</a>.'
NAV = [("overview", "/rebuild/", "Overview"), ("block", "/rebuild/block-requests/", "Property"),
       ("lending", "/rebuild/lending-intake/", "Lending"), ("legal", "/rebuild/legal-intake/", "Legal"),
       ("insurance", "/rebuild/broker-submissions/", "Insurance")]

STYLE = (SRC / "rebuild.css").read_text(encoding="utf-8")
SCRIPT = (SRC / "rebuild.js").read_text(encoding="utf-8")

HEAD = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by tools/make-rebuild-pages.py from tools/rebuild/. Edit there, not here. -->
<title>{title} | Pavel Guzhikov</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Pavel Guzhikov">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://guzh.uk/assets/rebuild/{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{image_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://guzh.uk/assets/rebuild/{image}">
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
/* The reader's explicit choice from guzh.uk's switcher (shared localStorage), else the OS. */
try {{ var t = localStorage.getItem("theme"); if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t); }} catch (e) {{}}
</script>
<style>
{style}</style>
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<header class="top">
  <a class="home" href="/">Pavel Guzhikov</a>
  <nav class="tabs" aria-label="{navlabel}">
{nav}
  </nav>
  <button class="theme" type="button" aria-label="Switch light or dark">
    <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 1.8a6.2 6.2 0 0 1 0 12.4z" fill="currentColor"/></svg>
  </button>
</header>
<script>
{script}</script>
<main id="main">
{body}
</main>
<footer class="foot">
  <p>{footer}</p>
  <p class="credit"><a href="https://guzh.uk">Made by Pavel Guzhikov</a> <a href="https://ko-fi.com/pavelg" target="_blank" rel="noopener noreferrer">Buy me a matcha 🍵</a></p>
</footer>
</body>
</html>
"""


def jsonld(p):
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage" if p["nav"] != "overview" else "Service",
        "name": p["title"],
        "description": p["description"],
        "url": p["url"],
        "provider": ({"@type": "Person", "name": "Pavel Guzhikov", "url": "https://guzh.uk/"} if p["nav"] == "defence" else
                     {"@type": "Organization", "name": "Empatiq Limited", "url": "https://guzh.uk/",
                      "founder": {"@type": "Person", "name": "Pavel Guzhikov", "url": "https://guzh.uk/"}}),
        "areaServed": "GB",
    }
    if p["nav"] == "defence":
        data["@type"] = "Service"
        data["serviceType"] = "Delivery, product and scale-up partner for defence and dual-use technology companies"
    if p["nav"] == "overview":
        data["serviceType"] = "Back-office process re-engineering and software build"
    return json.dumps(data, ensure_ascii=False)


def nav(current, navset=None):
    out = []
    for key, href, label in NAVSETS.get(navset, NAV):
        cur = ' aria-current="page"' if key == current else ""
        out.append(f'    <a href="{href}"{cur}>{label}</a>')
    return "\n".join(out)


def main():
    for p in PAGES:
        body = (SRC / p["body"]).read_text(encoding="utf-8")
        page = HEAD.format(
            title=html.escape(p["title"]), description=html.escape(p["description"]), url=p["url"],
            image=p["image"], image_alt=html.escape(p["image_alt"]), jsonld=jsonld(p), style=STYLE,
            nav=nav(p["nav"], p.get("navset")), body=body.rstrip(), script=SCRIPT,
            footer=p.get("footer", FOOTER), navlabel="Defence" if p.get("navset") else "Rebuild")
        bad = sorted({c for c in page if c in "\u2014\u00b7"})
        if bad:
            raise SystemExit(f"{p['path']}: contains {bad}; no em dashes or middle dots anywhere (Pavel's rule)")
        out = SITE / p["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"wrote {p['path']}")


if __name__ == "__main__":
    main()
