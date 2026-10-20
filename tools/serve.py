#!/usr/bin/env python3
"""Serve the site locally the way GitHub Pages does, 404 page included.

    ./tools/serve.py [port]

Like `python3 -m http.server`, but an address with no page gets /404.html with a 404 status, as
on guzh.uk, so the not-found page can be tried on real broken links (say /goat-rodeo/ or
/Weather/Privacy/). It serves the repo root worked out from this file, never the current directory
(see "Local preview" in the README for why), and only on 127.0.0.1.
"""

import functools
import http.server
import os
import pathlib
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent


class Pages(http.server.SimpleHTTPRequestHandler):
    # A folder without an index.html is a 404 on GitHub Pages, not a file listing.
    def list_directory(self, path):
        self.send_error(404)

    def send_error(self, code, message=None, explain=None):
        page = SITE / "404.html"
        if code != 404 or not page.is_file():
            return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main():
    port = int(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PORT", 8788))
    handler = functools.partial(Pages, directory=str(SITE))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Serving {SITE} on http://127.0.0.1:{port}/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
