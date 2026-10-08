#!/usr/bin/env python3
"""Put the newest Substack posts on the home page, in the page's own type.

Substack's embed is an iframe in Substack's styling: it can't take the page's fonts or dark mode,
and it sets year-long cookies and loads Sentry and a dozen script bundles, which the footer
promises the page does not do. So the posts are copied in as plain HTML instead. This script reads
the public feed and rewrites the one generated region in index.html:

    <!-- BEGIN generated from the Substack feed ... -->
    <!-- END generated -->

with the newest COUNT posts, leaving out any listed in SKIP. Everything around it (the section,
its heading, the two links under it, the CSS) is hand-written. When the posts change it also moves
the home page's <lastmod> in sitemap.xml to today.

    ./tools/make-writing.py                  # from the live feed
    ./tools/make-writing.py --feed=feed.xml  # from a saved copy

.github/workflows/writing.yml runs it every morning and commits the result when it changed.
"""

from __future__ import annotations

import datetime
import email.utils
import html
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zoneinfo

FEED = "https://guzhikov.substack.com/feed"
POSTS = "https://guzhikov.substack.com/p/"
COUNT = 3
SITE = pathlib.Path(__file__).resolve().parent.parent
LONDON = zoneinfo.ZoneInfo("Europe/London")
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

# Posts that stay on Substack but don't appear on the home page, by the slug at the end of their
# URL. Delete a line to let that post back in.
SKIP = {
    "they-washed-the-pavement-by-morning",  # its subtitle is "A bit with 18+ photo"
}

REGION = re.compile(r"(<!-- BEGIN generated from the Substack feed[^\n]*-->\n)(.*?)(^[ \t]*<!-- END generated -->)",
                    re.S | re.M)
LASTMOD = re.compile(r"(<loc>https://guzh\.uk/</loc>\s*<lastmod>)[^<]+(</lastmod>)")


def read_feed() -> bytes:
    path = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--feed=")), None)
    if path:
        return pathlib.Path(path).read_bytes()
    req = urllib.request.Request(FEED, headers={"User-Agent": "guzh.uk writing list (+https://guzh.uk/)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def clean(text: str | None) -> str:
    return " ".join((text or "").split())


def short(text: str, limit: int = 240) -> str:
    """The CSS shows three lines at most; this only keeps a long subtitle out of the HTML."""
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def posts(raw: bytes):
    for item in ET.fromstring(raw).iterfind("./channel/item"):
        link, title = clean(item.findtext("link")), clean(item.findtext("title"))
        # Only ever link to a post on the Substack itself, whatever the feed says.
        if not link.startswith(POSTS) or not title or link[len(POSTS):].strip("/") in SKIP:
            continue
        yield {
            "link": link,
            "title": title,
            "subtitle": short(clean(item.findtext("description"))),
            "date": email.utils.parsedate_to_datetime(item.findtext("pubDate")).astimezone(LONDON).date(),
        }


def render(post: dict) -> str:
    e, d = html.escape, post["date"]
    lines = [
        '        <li class="project">',
        f'          <time class="post-date" datetime="{d.isoformat()}">{d.day} {MONTHS[d.month - 1]} {d.year}</time>',
        f'          <a href="{e(post["link"])}" target="_blank" rel="noopener noreferrer">{e(post["title"])}</a>',
    ]
    if post["subtitle"]:
        lines.append(f'          <p>{e(post["subtitle"])}</p>')
    lines.append("        </li>")
    return "\n".join(lines) + "\n"


def main() -> None:
    newest = sorted(posts(read_feed()), key=lambda p: p["date"], reverse=True)[:COUNT]
    if not newest:
        raise SystemExit("no posts in the feed; leaving the page as it is")

    page = SITE / "index.html"
    before = page.read_text(encoding="utf-8")
    if not REGION.search(before):
        raise SystemExit("index.html has no '<!-- BEGIN generated from the Substack feed' region")
    after = REGION.sub(lambda m: m[1] + "".join(map(render, newest)) + m[3], before, count=1)
    if after == before:
        print("posts unchanged")
        return
    page.write_text(after, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    today = datetime.datetime.now(LONDON).date().isoformat()
    sitemap.write_text(LASTMOD.sub(rf"\g<1>{today}\g<2>", sitemap.read_text(encoding="utf-8")), encoding="utf-8")
    print("posts updated:", *(p["title"] for p in newest), sep="\n  ")


if __name__ == "__main__":
    main()
