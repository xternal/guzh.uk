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

    ./tools/make-writing.py                   # from the live feed
    ./tools/make-writing.py --relay           # through the relays, as GitHub's machines do
    ./tools/make-writing.py --relay=feed2json # through that one relay only
    ./tools/make-writing.py --feed=feed.xml   # from a saved copy

.github/workflows/writing.yml runs it every morning and commits the result when it changed.
Substack's Cloudflare turns GitHub's machines away (a "Just a moment..." challenge, 403, whatever
the request looks like), so when the feed refuses, the script reads it through a relay instead:
rss2json, and feed2json when rss2json can't. Both are feed readers Substack does serve, and both
hand back the same items as JSON. From a home connection the feed answers directly and neither is
asked.
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
# Two feed readers on different machines, asked in this order. rss2json answers "Internal error"
# or "This feed is being processed, please wait" (both a 500) while it re-reads a feed, and on
# 12 and 14 Oct 2026 it could not download Substack's feed for longer than all its tries (on the
# 14th feed2json read it fine at the same time). Each round asks both; five rounds over about
# eight minutes before the run gives up.
RELAYS = {
    "rss2json": "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote(FEED, safe=""),
    "feed2json": "https://feed2json.org/convert?url=" + urllib.parse.quote(FEED, safe=""),
}
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


def option(name: str) -> str | None:
    """The value of --name=value, "" for a bare --name, None when it isn't given."""
    for a in sys.argv[1:]:
        if a == f"--{name}" or a.startswith(f"--{name}="):
            return a.partition("=")[2]
    return None


def items():
    """(link, title, subtitle, published) for every post in the feed, as the feed has them."""
    path, only = option("feed"), option("relay")
    if path or only is None:
        try:
            raw = pathlib.Path(path).read_bytes() if path else fetch(FEED)
        except urllib.error.HTTPError as e:
            print(f"the feed answered {e.code}; reading it through a relay", file=sys.stderr)
        else:
            for item in ET.fromstring(raw).iterfind("./channel/item"):
                yield (item.findtext("link"), item.findtext("title"), item.findtext("description"),
                       email.utils.parsedate_to_datetime(item.findtext("pubDate")))
            return
    yield from relay(only)


def unpack(name: str, data: dict) -> list:
    """The items a relay sent, in the feed's terms. A relay that fails says why in place of the
    items, rss2json in "message" and feed2json in "err" (and still with a 200)."""
    if "items" not in data or name == "rss2json" and data.get("status") != "ok":
        raise ValueError(data.get("message") or data.get("err") or "no items")
    if name == "rss2json":  # "pubDate": "2026-10-12 06:15:54", in UTC
        return [(i.get("link"), i.get("title"), i.get("description"),
                 datetime.datetime.fromisoformat(i["pubDate"]).replace(tzinfo=datetime.timezone.utc))
                for i in data["items"]]
    # feed2json, a JSON Feed: "date_published": "2026-10-12T06:15:54.000Z"
    return [(i.get("url"), i.get("title"), i.get("summary"),
             datetime.datetime.fromisoformat(i["date_published"].replace("Z", "+00:00")))
            for i in data["items"]]


def relay(only: str = "") -> list:
    """The feed as the first relay that can read it has it, trying again while all are failing."""
    names = [only] if only else list(RELAYS)
    if not set(names) <= set(RELAYS):
        raise SystemExit(f"--relay is one of: {', '.join(RELAYS)}")
    for attempt, wait in enumerate((*RELAY_WAITS, None), start=1):
        problems = []
        for name in names:
            try:
                found = unpack(name, json.loads(fetch(RELAYS[name])))
                if found:
                    after = f" ({'; '.join(problems)})" if problems else ""
                    print(f"read the feed through {name}{after}", file=sys.stderr)
                    return found
                problem = "no posts"
            except urllib.error.HTTPError as e:
                try:
                    problem = f"{e.code}: {json.loads(e.read()).get('message')}"
                except ValueError:
                    problem = str(e.code)
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError, AttributeError) as e:
                problem = str(e)
            problems.append(f"{name} {problem}")
        problem = "; ".join(problems)
        if wait is None:
            break
        print(f"try {attempt}: {problem}; trying again in {wait} s", file=sys.stderr)
        time.sleep(wait)
    raise SystemExit(f"no relay could read the feed after {attempt} tries ({problem}). The page "
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
