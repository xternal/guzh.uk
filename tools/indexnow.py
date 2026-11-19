#!/usr/bin/env python3
"""Tell Bing (and through it ChatGPT and Copilot search), Yandex, Seznam and Naver that pages changed.

    python3 tools/indexnow.py --wait <commit> https://guzh.uk/ https://guzh.uk/pe/
    python3 tools/indexnow.py --wait <commit> --changed <old-commit>

IndexNow (https://www.indexnow.org/) is one POST that every engine taking part shares, so a changed
page is fetched again within minutes instead of whenever the crawler next comes by. Google does not
take part; it reads sitemap.xml's <lastmod>.

--wait <commit> first waits, up to ten minutes, for GitHub Pages to finish building that commit, so
the engines fetch the new page and not the old one (it needs GH_TOKEN and GITHUB_REPOSITORY, as in
Actions). --changed <old-commit> pings the pages in sitemap.xml whose files changed since then (and
every page when sitemap.xml or robots.txt did). Only pages in sitemap.xml are ever sent.

The key is the file <key>.txt at the site root, which the engines fetch to check the ping is ours.
It is public by design: it only proves the ping comes from whoever controls guzh.uk.
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.request

SITE = pathlib.Path(__file__).resolve().parent.parent
HOST = "guzh.uk"
ORIGIN = f"https://{HOST}"


def key():
    found = [p.stem for p in SITE.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(found) != 1:
        sys.exit(f"indexnow: expected one <32 hex>.txt key file at the site root, found {found}")
    return found[0]


def listed():
    text = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(https://guzh\.uk[^<]*)</loc>", text)


def changed_since(old):
    names = subprocess.check_output(["git", "diff", "--name-only", old, "HEAD"], cwd=SITE, text=True).split()
    urls = listed()
    if {"sitemap.xml", "robots.txt"} & set(names):
        return urls
    paths = {"/" + n[: -len("index.html")] for n in names if n.endswith("index.html")}
    return [u for u in urls if u[len(ORIGIN):] in paths]


def wait_for_pages(commit):
    repo = os.environ["GITHUB_REPOSITORY"]
    for _ in range(60):
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}/pages/builds/latest", "--jq", "[.commit, .status] | @tsv"],
            capture_output=True, text=True,
        ).stdout.split()
        if out and out[0] == commit and out[1] == "built":
            print(f"Pages built {commit[:7]}")
            return
        if out and out[0] == commit and out[1] == "errored":
            sys.exit("indexnow: the Pages build failed, nothing sent")
        time.sleep(10)
    sys.exit("indexnow: Pages did not build this commit within ten minutes, nothing sent")


def main():
    args = sys.argv[1:]
    commit = old = None
    if "--wait" in args:
        i = args.index("--wait"); commit = args[i + 1]; del args[i : i + 2]
    if "--changed" in args:
        i = args.index("--changed"); old = args[i + 1]; del args[i : i + 2]
    urls = changed_since(old) if old else []
    urls += [u for u in args if u in listed() and u not in urls]
    if not urls:
        print("No page in sitemap.xml changed: nothing to send.")
        return
    if commit:
        wait_for_pages(commit)
    k = key()
    body = json.dumps({"host": HOST, "key": k, "keyLocation": f"{ORIGIN}/{k}.txt", "urlList": urls}).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        # 200 and 202 both mean received; 202 is what a key not yet checked gets.
        print(f"IndexNow {r.status}: sent {len(urls)}: " + " ".join(urls))


if __name__ == "__main__":
    main()
