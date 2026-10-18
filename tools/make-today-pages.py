#!/usr/bin/env python3
"""Render the Always Today documents into /today/privacy/, /today/support/ and /today/terms/.

The copy is NOT written here. It lives in the Always Today repo, next to the code it describes:

    store/privacy.md  -> today/privacy/index.html
    store/support.md  -> today/support/index.html   (help, contact and the refund policy)
    store/terms.md    -> today/terms/index.html

Exactly as tools/make-weather-pages.py does for Always Weather, and with its renderer: each page is a
hand-written shell with one generated region,

    <!-- BEGIN generated from store/<file>.md ... -->
    <!-- END generated -->

and only that region is rewritten:

    ./tools/make-today-pages.py [path-to-always-today-repo] [--ref=origin/main]

--ref takes any branch (for example --ref=website, before the copy is merged) or --ref=worktree for
the files as they are on disk. Anything still [bracketed] in a source needs an entry in SUBSTITUTIONS
below, or the script refuses to publish it.
"""

import importlib.util
import pathlib
import re
import subprocess
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
APP = pathlib.Path(ARGS[0] if ARGS else "~/dev/always-today").expanduser()
REF = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "origin/main")

# The same small markdown renderer as the weather pages, so the two apps' documents read alike.
# (No __pycache__ left in tools/ from importing it.)
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("weather_pages", SITE / "tools" / "make-weather-pages.py")
weather = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(weather)

# Exact source text -> what the published page says instead. Each one waits on a decision of Pavel's;
# delete the entry once the source carries the real thing.
SUBSTITUTIONS = {
    # The documents link to each other as flat files; the site serves directories.
    "](./privacy)": "](/today/privacy/)",
    "](./support)": "](/today/support/)",
    "](./terms)": "](/today/terms/)",
}

PAGES = [
    ("store/privacy.md", "today/privacy/index.html"),
    ("store/support.md", "today/support/index.html"),
    ("store/terms.md", "today/terms/index.html"),
]


def read_source(path: str) -> str:
    if REF == "worktree":
        return (APP / path).read_text(encoding="utf-8")
    try:
        return subprocess.run(["git", "-C", str(APP), "show", f"{REF}:{path}"],
                              check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        detail = getattr(e, "stderr", "") or e
        raise SystemExit(f"cannot read {path} at {REF} in {APP}: {detail}")


def main() -> int:
    for source, target in PAGES:
        dst = SITE / target
        text = weather.strip_notes(read_source(source))
        for placeholder, replacement in SUBSTITUTIONS.items():
            pattern = r"\s+".join(re.escape(w) for w in placeholder.split())
            text = re.sub(pattern, replacement.replace("\\", "\\\\"), text)
        left = re.findall(r"\[[^\]]+\]\s*(?!\()", text)
        if left:
            print(f"{source}: unresolved placeholder {left[0].strip()} — add it to "
                  f"SUBSTITUTIONS in {pathlib.Path(__file__).name}, or wait for the real text",
                  file=sys.stderr)
            return 1

        page = dst.read_text(encoding="utf-8")
        begin = f"<!-- BEGIN generated from {source} — edit that file, then re-run tools/make-today-pages.py -->"
        end = "<!-- END generated -->"
        i, j = page.find(begin), page.find(end)
        if i == -1 or j == -1:
            print(f"{target}: no generated region — expected {begin}", file=sys.stderr)
            return 1

        page = page[:i] + begin + "\n" + weather.render(text) + "\n    " + page[j:]
        dst.write_text(page, encoding="utf-8")
        print(f"{source}@{REF} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
