#!/usr/bin/env python3
"""Render the Always Weather store documents into /weather/privacy/ and /weather/support/.

The copy is NOT written here. It lives in the app repo, where it is kept in step with the Play
Data safety form and the Apple privacy label:

    store/privacy-policy.md  -> weather/privacy/index.html
    store/support-page.md    -> weather/support/index.html

Each page file is an ordinary hand-written shell — head, masthead, footer, all the CSS — with one
generated region:

    <!-- BEGIN generated from store/<file>.md ... -->
    <!-- END generated -->

Only that region is rewritten, so the pages can be restyled by hand and re-synced at any time:

    ./tools/make-weather-pages.py [path-to-always_weather-repo] [--ref=origin/main]

The source files carry bracketed items waiting on Pavel. Each one needs an entry in SUBSTITUTIONS
below or this script refuses to render the file, so nothing bracketed can reach the live site by
accident.
"""

import html
import pathlib
import re
import subprocess
import sys

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
APP = pathlib.Path(ARGS[0] if ARGS else "~/dev/always_weather").expanduser()
SITE = pathlib.Path(__file__).resolve().parent.parent

# The documents are read from what is merged — not from whatever the app repo happens to have
# checked out (it usually sits on a feature branch), and not from a local main that may be behind.
# Fetch that repo first. Pass --ref=<branch> to preview copy that has not merged yet, or
# --ref=worktree to take the files as they are on disk.
REF = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "origin/main")


def read_source(path: str) -> str:
    """The document at REF, or the working tree when REF is 'worktree'."""
    if REF == "worktree":
        return (APP / path).read_text(encoding="utf-8")
    try:
        return subprocess.run(["git", "-C", str(APP), "show", f"{REF}:{path}"],
                              check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        detail = getattr(e, "stderr", "") or e
        raise SystemExit(f"cannot read {path} at {REF} in {APP}: {detail}")

# Exact source text -> what the published page says instead. Every one of these is a placeholder
# waiting on a decision of Pavel's; delete the entry once the source file carries the real thing.
SUBSTITUTIONS = {
    # The date the pages first went live.
    "[date of publication]": "17 September 2026",
    # The documents assume flat files sitting next to each other; the site serves directories.
    "](./privacy)": "](/weather/privacy/)",
}

PAGES = [
    ("store/privacy-policy.md", "weather/privacy/index.html"),
    ("store/support-page.md", "weather/support/index.html"),
]


def smarten(text: str) -> str:
    """Straight quotes to typographic ones. Presentation only — no word is changed."""
    text = re.sub(r'"([^"]*)"', "“\\1”", text)
    return text.replace("'", "’")


def inline(text: str) -> str:
    """The inline markdown the two documents actually use: **bold** and [links](url)."""
    out, last = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        out.append(escape_and_emphasise(text[last:m.start()]))
        href = m.group(2)
        rel = "" if href.startswith(("./", "/", "#")) else ' rel="noopener"'
        out.append(f'<a href="{html.escape(href, quote=True)}"{rel}>'
                   f"{escape_and_emphasise(m.group(1))}</a>")
        last = m.end()
    out.append(escape_and_emphasise(text[last:]))
    return "".join(out)


def escape_and_emphasise(text: str) -> str:
    # Smarten first: html.escape would hide the straight quotes behind entities. quote=False
    # keeps the typographic quotes as characters; hrefs are escaped separately.
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>",
                  html.escape(smarten(text), quote=False))


def strip_notes(markdown: str) -> str:
    """Drop the publishing notes at the top of each source file: they are for us, not readers."""
    return re.sub(r"^<!--.*?-->\s*", "", markdown, flags=re.S)


def render(markdown: str) -> str:
    """The small subset of markdown these two documents use."""
    lines, blocks, buf, mode = markdown.splitlines(), [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        if mode == "ul":
            items = "\n".join(f"      <li>{inline(i)}</li>" for i in buf)
            blocks.append(f"    <ul>\n{items}\n    </ul>")
        else:
            # Both documents hard-wrap prose at ~95 characters, so a short line that is not the
            # last one is a break the author meant — the address block on the support page.
            text = buf[0]
            for prev, line in zip(buf, buf[1:]):
                text += ("<br>" if len(prev) < 70 else " ") + line
            # "Last updated: …" under the title, and the legal basis under each thing the app
            # sends, are the two paragraphs that get their own voice on the page.
            cls = ""
            if text.startswith("Last updated:"):
                cls = ' class="updated"'
            elif text.startswith("**Legal basis:**"):
                cls = ' class="basis"'
            html_text = "<br>\n      ".join(inline(part) for part in text.split("<br>"))
            blocks.append(f"    <p{cls}>{html_text}</p>")
        buf, mode = [], None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith("### "):
            flush()
            blocks.append(f"    <h3>{inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            flush()
            blocks.append(f"    <h2>{inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush()
            blocks.append(f"    <h1>{inline(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if mode != "ul":
                flush()
                mode = "ul"
            buf.append(stripped[2:])
        else:
            if mode == "ul":
                buf[-1] += " " + stripped          # a wrapped bullet
            else:
                mode = "p"
                buf.append(stripped)
    flush()
    return "\n".join(blocks)


def main() -> int:
    for source, target in PAGES:
        dst = SITE / target
        text = strip_notes(read_source(source))
        for placeholder, replacement in SUBSTITUTIONS.items():
            # The source files are hard-wrapped, so a phrase may straddle a line break.
            pattern = r"\s+".join(re.escape(w) for w in placeholder.split())
            text = re.sub(pattern, replacement.replace("\\", "\\\\"), text)
        left = re.findall(r"\[[^\]]+\]\s*(?!\()", text)
        if left:
            print(f"{source}: unresolved placeholder {left[0].strip()} — add it to "
                  f"SUBSTITUTIONS in {pathlib.Path(__file__).name}, or wait for the real text",
                  file=sys.stderr)
            return 1

        page = dst.read_text(encoding="utf-8")
        begin = f"<!-- BEGIN generated from {source} — edit that file, then re-run tools/make-weather-pages.py -->"
        end = "<!-- END generated -->"
        i, j = page.find(begin), page.find(end)
        if i == -1 or j == -1:
            print(f"{target}: no generated region — expected {begin}", file=sys.stderr)
            return 1

        page = page[:i] + begin + "\n" + render(text) + "\n    " + page[j:]
        dst.write_text(page, encoding="utf-8")
        print(f"{source}@{REF} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
