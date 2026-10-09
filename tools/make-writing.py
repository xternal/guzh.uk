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
    ./tools/make-writing.py --relay          # through rss2json, as GitHub's machines do
    ./tools/make-writing.py --feed=feed.xml  # from a saved copy

.github/workflows/writing.yml runs it every morning and commits the result when it changed.
Substack's Cloudflare turns GitHub's machines away (a "Just a moment..." challenge, 403, whatever
the request looks like), so when the feed refuses, the script reads it through rss2json instead:
a feed reader Substack does serve, which hands back the same items as JSON. From a home connection
the feed answers directly and rss2json is never asked.
"""

from __future__ import annotations

import datetime
import email.utils
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zoneinfo

FEED = "https://guzhikov.substack.com/feed"
RELAY = "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote(FEED, safe="")
# rss2json answers "Internal error" or "This feed is being processed, please wait" (both a 500)
# while it re-reads a feed, and Substack sometimes turns it away too. So it gets five tries over
# about eight minutes before the run gives up.
RELAY_WAITS = (30, 60, 120, 240)
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


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "guzh.uk writing list (+https://guzh.uk/)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def items():
    """(link, title, subtitle, published) for every post in the feed, as the feed has them."""
    path = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--feed=")), None)
    if path or "--relay" not in sys.argv:
        try:
            raw = pathlib.Path(path).read_bytes() if path else fetch(FEED)
        except urllib.error.HTTPError as e:
            print(f"the feed answered {e.code}; reading it through rss2json", file=sys.stderr)
        else:
            for item in ET.fromstring(raw).iterfind("./channel/item"):
                yield (item.findtext("link"), item.findtext("title"), item.findtext("description"),
                       email.utils.parsedate_to_datetime(item.findtext("pubDate")))
            return
    for item in relay()["items"]:
        published = datetime.datetime.fromisoformat(item["pubDate"]).replace(tzinfo=datetime.timezone.utc)
        yield item.get("link"), item.get("title"), item.get("description"), published


def relay() -> dict:
    """The feed as rss2json has it, trying again while it is busy or failing."""
    for attempt, wait in enumerate((*RELAY_WAITS, None), start=1):
        try:
            data = json.loads(fetch(RELAY))
            if data.get("status") == "ok":
                return data
            problem = data.get("message") or data
        except urllib.error.HTTPError as e:
            try:
                problem = f"{e.code}: {json.loads(e.read()).get('message')}"
            except ValueError:
                problem = str(e.code)
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            problem = str(e)
        if wait is None:
            break
        print(f"rss2json, try {attempt}: {problem}; trying again in {wait} s", file=sys.stderr)
        time.sleep(wait)
    raise SystemExit(f"rss2json could not read the feed after {attempt} tries ({problem}). The page "
                     "keeps the posts it has. To publish from a Mac instead: ./tools/publish-writing.sh")


def clean(text: str | None) -> str:
    """Plain text on one line. The feed's subtitles are plain already; this is for when one isn't."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text or "")).split())


def short(text: str, limit: int = 240) -> str:
    """The CSS shows three lines at most; this only keeps a long subtitle out of the HTML."""
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def posts():
    for link, title, subtitle, published in items():
        link, title = clean(link), clean(title)
        # Only ever link to a post on the Substack itself, whatever the feed says.
        if not link.startswith(POSTS) or not title or link[len(POSTS):].strip("/") in SKIP:
            continue
        yield {
            "link": link,
            "title": title,
            "subtitle": short(clean(subtitle)),
            "date": published.astimezone(LONDON).date(),
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
    newest = sorted(posts(), key=lambda p: p["date"], reverse=True)[:COUNT]
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
