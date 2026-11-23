#!/usr/bin/env python3
"""Keep the search-engine and AI-search details of every page in step with sitemap.xml.

    python3 tools/seo.py           # write the changes
    python3 tools/seo.py --check   # change nothing; exit 1 and say what is out of date (CI)

For every page in sitemap.xml it does two things, both safe to run again and again:

1. Writes one JSON-LD block just before </head>, between the BEGIN/END tools/seo.py comments: the
   page's dateModified, and on every page but the home page a BreadcrumbList back to it. It is a
   block of its own, so the hand-written JSON-LD above it and the generators that write a page's
   body (tools/make-*.py) never have to know about it. The date is the page's own visible "Last
   updated: …" line when it has one (the policies), and its <lastmod> in sitemap.xml otherwise:
   so when a page's copy changes, set its <lastmod> to that day and run this. A "Last updated"
   newer than the page's <lastmod> moves the <lastmod> up to it.
2. Wraps a visible "Last updated: 20 October 2026" in <time datetime="2026-10-20">, so machines
   read the same date people do.

A generator that rewrites a page drops both; the SEO check on every pull request then fails and
says to run this. tools/make-writing.py's daily run is followed by this in .github/workflows/
writing.yml, so the home page's dateModified moves with its <lastmod>.
"""

import datetime
import json
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
ORIGIN = "https://guzh.uk"

# The short name each page goes by in a breadcrumb trail. Every page in sitemap.xml needs one.
NAMES = {
    "/": "Pavel Guzhikov",
    "/weather/privacy/": "Always Weather privacy policy",
    "/weather/support/": "Always Weather help",
    "/weather/ideas/": "Suggest an idea for Always Weather",
    "/today/privacy/": "Always Today privacy policy",
    "/today/support/": "Always Today help",
    "/today/terms/": "Always Today terms of use",
    "/goat-rodeo/": "Goat Rodeo",
    "/goat-rodeo/race/": "Race links",
    "/goat-rodeo/privacy/": "Privacy policy",
    "/rebuild/": "Rebuild one back-office process",
    "/pe/": "For private equity owners",
    "/exit/": "For owners who will sell",
    "/defence/": "Defence tech",
    "/defence/brief/": "The proof",
    "/defence/route/": "The two-week offer",
    "/rebuild/block-requests/": "Demo: block-management requests",
    "/rebuild/lending-intake/": "Demo: SME loan pack to credit memo",
    "/rebuild/legal-intake/": "Demo: legal matter intake",
    "/rebuild/broker-submissions/": "Demo: broker renewal to submission",
    "/rebuild/block-requests/app/": "Hallkeeper",
    "/rebuild/lending-intake/app/": "Keelson",
    "/rebuild/legal-intake/app/": "Clerkwell",
    "/rebuild/broker-submissions/app/": "Tidemark",
}

BEGIN = "<!-- BEGIN tools/seo.py: dateModified and breadcrumbs from sitemap.xml; run it, don't edit this -->"
END = "<!-- END tools/seo.py -->"
BLOCK = re.compile(r"\n?" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
UPDATED = re.compile(r"Last updated: (\d{1,2} [A-Z][a-z]+ \d{4})(?!</time>)")
UPDATED_DONE = re.compile(r'Last updated: <time datetime="(\d{4}-\d{2}-\d{2})">')


def sitemap():
    text = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    pages = re.findall(r"<loc>(https://guzh\.uk[^<]*)</loc>\s*<lastmod>([^<]+)</lastmod>", text)
    if len(pages) != text.count("<url>"):
        sys.exit("sitemap.xml: every <url> needs a <loc> on guzh.uk and a <lastmod>")
    return [(loc[len(ORIGIN):], lastmod) for loc, lastmod in pages]


def file_for(path):
    return SITE / path.lstrip("/") / "index.html"


def trail(path, listed):
    """The breadcrumb trail to a page: the home page, then each parent that is a page of its own."""
    steps, parts = ["/"], [p for p in path.split("/") if p]
    for i in range(1, len(parts) + 1):
        sub = "/" + "/".join(parts[:i]) + "/"
        if sub in listed:
            steps.append(sub)
    return steps


def block(path, date, listed):
    url = ORIGIN + path
    page = {
        "@context": "https://schema.org",
        "@type": "ProfilePage" if path == "/" else "WebPage",
        "@id": url,
        "url": url,
        "dateModified": date,
    }
    if path != "/":
        page["breadcrumb"] = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": NAMES[step], "item": ORIGIN + step}
                for i, step in enumerate(trail(path, listed))
            ],
        }
    body = json.dumps(page, ensure_ascii=False, separators=(", ", ": "))
    return f'{BEGIN}\n<script type="application/ld+json">{body}</script>\n{END}\n'


def iso(day):
    return datetime.datetime.strptime(day, "%d %B %Y").date().isoformat()


def main():
    check = "--check" in sys.argv[1:]
    pages = sitemap()
    listed = {path for path, _ in pages}
    missing = sorted(listed - NAMES.keys())
    if missing:
        sys.exit(f"tools/seo.py: give these pages a short name in NAMES: {', '.join(missing)}")
    stale, bumps = [], {}
    for path, lastmod in pages:
        f = file_for(path)
        old = f.read_text(encoding="utf-8")
        new = UPDATED.sub(lambda m: f'Last updated: <time datetime="{iso(m[1])}">{m[1]}</time>', old)
        shown = UPDATED_DONE.search(new)
        date = shown[1] if shown else lastmod
        if date > lastmod:  # a policy updated without its <lastmod>: the sitemap follows the page
            bumps[path] = date
        new = BLOCK.sub("\n", new)
        new = new.replace("</head>", block(path, date, listed) + "</head>", 1)
        if new != old:
            stale.append(str(f.relative_to(SITE)))
            if not check:
                f.write_text(new, encoding="utf-8")
    if bumps:
        smap = SITE / "sitemap.xml"
        text = smap.read_text(encoding="utf-8")
        for path, date in bumps.items():
            text = re.sub(rf"(<loc>{re.escape(ORIGIN + path)}</loc>\s*<lastmod>)[^<]+", rf"\g<1>{date}", text)
        stale.append("sitemap.xml")
        if not check:
            smap.write_text(text, encoding="utf-8")
    if check and stale:
        print("Out of date, run `python3 tools/seo.py` and commit:\n  " + "\n  ".join(stale))
        sys.exit(1)
    print(("Up to date: " if not stale else "Updated: ") + (", ".join(stale) if stale else f"{len(pages)} pages"))


if __name__ == "__main__":
    main()
