# guzh.uk

Personal one-pager for Pavel Guzhikov. Hand-written static HTML + CSS. No build step, no framework,
and a little JavaScript (the copyright year, and the light/dark switcher). Deploy the repo root as-is on any static host.

| | |
|---|---|
| Canonical host | `https://guzh.uk/` |
| Page weight | ~38 KB HTML (~15 KB gzipped) + 24 KB portrait (WebP) + Google Fonts |
| Build | none |

## Files

```
index.html              the entire page
favicon.svg             dark square, PG wordmark
assets/
  pavel-web.webp        portrait, 560x560, 24 KB  (what browsers actually load)
  pavel-web.png         same portrait, PNG fallback, 572 KB
  og.png                1200x630 link-preview card
  apple-touch-icon.png  180x180
robots.txt
sitemap.xml
tools/make-og.sh        regenerates assets/og.png — run it if the headline, the lead line
                        or the portrait treatment changes
tools/make-tz.sh        regenerates the packed timezone->coordinates table inside index.html
                        — run it when tzdb adds or renames zones
_headers                cache + security headers — used by Netlify and Cloudflare Pages,
                        ignored by GitHub Pages (which cannot set custom headers)
```

The original Claude Design handoff — spec, prototype and the old 1 MB React snapshot — is **not** in
this repo. It lives beside it at `../guzh.uk-handoff/`. It is reference material, it does not belong
on the website, and on a free GitHub plan Pages requires a public repo, where anything committed is
publicly browsable whether or not it is served.

## Local preview

```bash
python3 -m http.server 8788 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8788/>. The `--bind` matters: without it the server answers on every
interface, so an unfinished draft is readable by anything on the same wifi.

### The in-editor preview does not work from here, and cannot be made to

`.claude/launch.json` is correct and works on a normal path. It fails in *this* checkout because the
repo lives on a Google Drive `CloudStorage` mount, and the sandbox the editor spawns dev servers
under has no read access to it. The symptom is `PermissionError: [Errno 1] Operation not permitted`
somewhere that looks unrelated — `os.getcwd()`, or the import machinery scanning `sys.path`.

It is not a configuration problem, and the obvious workarounds make it worse rather than better:

- Passing `--directory "$PWD"` looks right and is dangerous. The launcher does not set `PWD` to the
  repo, so it expands to `/` and the server cheerfully publishes the whole filesystem on localhost.
- `python3 -I -c` with an explicit `directory=` gets past the import scan and the server starts, but
  every request 404s, because `SimpleHTTPRequestHandler` catches the `PermissionError` from reading
  the directory and reports it as a missing file.

The real fix is to move the repo off Google Drive to an ordinary local path. Until then, use the
terminal command above — it works, because a normal shell can read the mount.

## Deploy — GitHub Pages (simplest)

Best choice if `guzh.uk` is the only domain that needs to serve the page.

1. Push this repo to GitHub. On a free plan the repo must be **public** — GitHub Pages only works on
   private repos with Pro or above.
2. **Settings → Pages → Source: Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
   You get `<username>.github.io/<repo>` within a minute.
3. **Settings → Pages → Custom domain**: enter `guzh.uk`, Save. This commits a `CNAME` file.
4. At your registrar's DNS, for `guzh.uk`:

   | Type | Name | Value |
   |---|---|---|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | CNAME | `www` | `<username>.github.io` |

   IPv6 is optional: AAAA `@` → `2606:50c0:8000::153`, `…8001::153`, `…8002::153`, `…8003::153`.
5. Wait for the certificate, then tick **Enforce HTTPS**.

GitHub creates the redirect between `guzh.uk` and `www.guzh.uk` automatically once both are
configured — you do not need to do anything else for the `www` variant.

Limits are irrelevant here: 1 GB site, 100 GB/month soft bandwidth, 10 builds/hour soft.

### The one catch: one custom domain per repo

A repo's `CNAME` file holds a single domain. If you own other domains that should land on this page,
pick one of these — no second host required for the first option:

- **Registrar URL forwarding (easiest).** Most registrars (Porkbun, Namecheap, Gandi, GoDaddy) offer
  free forwarding. Point each spare domain at `https://guzh.uk` with a 301. Nothing to deploy.
- **A second repo per domain** containing only a redirect stub. Works, but it is a hop through HTML
  and it is not a real 301 — only worth it if forwarding is unavailable.
- **Move to Netlify** (below), which handles many domains on one site.

## Alternative — Netlify

Worth it if you have several domains and want them all on one site, or if you want the repo private.

1. Add site from Git (or drag this folder onto <https://app.netlify.com/drop>). No build command,
   publish directory `/`. Free tier deploys private repos.
2. **Domain management** → add `guzh.uk` and set it as the **primary domain**; add the others as
   **domain aliases**. Netlify redirects apex ↔ `www` automatically.
3. For the other domains, do not rely on the automatic behaviour — make the 301 explicit by adding a
   `_redirects` file at the root, one line per domain:

   ```
   https://olddomain.com/*  https://guzh.uk/:splat  301!
   ```

   Netlify's `_redirects` **does** match hostnames, so this works there. (This is the syntax the
   original `DEPLOY.md` gave — it is Netlify's, not Cloudflare's. See below.)

## Alternative — Cloudflare Pages

Fine, but the most setup of the three. Workers & Pages → Create → Pages → Connect to Git; framework
preset None, build command empty, output directory `/`. Add each domain under Custom domains.

**Do not use a `_redirects` file here.** Cloudflare Pages matches paths only and lists domain-level
redirects as explicitly unsupported, so `https://www.guzh.uk/* … 301!` silently never fires. Use
**Rules → Redirect Rules** instead, per domain:

- Request URL `http*://olddomain.com/*` → Target `https://guzh.uk/${2}`, status 301, preserve query
  string on.
- The domain also needs a *proxied* DNS record or the rule never runs: A `@` → `192.0.2.1`, orange
  cloud on.

Free plan: 10 redirect rules per zone.

## Where this differs from the design handoff

The handoff README and the design prototype disagreed in two places. Both have since been settled by
Pavel directly, so the live page is now the authority — not either source document. Recorded here
because both disagreements will otherwise look like mistakes to anyone reading the handoff later.

1. **Portrait treatment — warm, not greyscale.** The handoff README specified
   `grayscale(1) contrast(1.04)`; the prototype's default was `warm`. The page uses **warm**
   (`saturate(1.02) contrast(1.02) brightness(1.03)`), and `assets/og.png` is generated in colour to
   match. If you change the filter, change it in both places — `.portrait img` in `index.html` and
   the `-modulate` line in `tools/make-og.sh`, which carries the equivalent for each treatment.

2. **The body copy has moved past both sources.** It now reads: "Margin, growth and retention are
   the only scoreboard I care about. Public value is now on the same line." That keeps the "only"
   the prototype had dropped, and adds a second beat that sets up the "Now" block rather than
   diluting the first three into a longer list. Neither source document has this wording.

## Notes

- **Copyright year updates itself.** The markup ships `© <span id="year">2026</span>`, and one line
  of script below it overwrites the span with the current year. If scripting is off the 2026 in the
  HTML still renders, so it degrades to exactly what it was before — worth bumping that fallback if
  you happen to edit the file in a later year.

  A scheduled GitHub Action was the obvious alternative and does not work here: GitHub disables
  scheduled workflows after 60 days without repository activity in a public repo, so a once-a-year
  cron on a quiet site repo would be switched off long before it ever fired.
- **Fonts** load from Google Fonts (Geist 400/500) — one family, everything. A display serif was
  tried across the headline, stat figures, block headings and the closing line, and taken back out:
  it read as someone else's page. Geist also renders the OG card, so page and link preview agree.
  Self-host the two weights if you want to remove the third-party request.
- **Light and dark** both ship, with an Auto / Light / Dark switcher in the masthead. The
  resolution order is: an explicit choice, else the sun where the reader is, else
  `prefers-color-scheme`. A choice pins `data-theme` on `<html>`; Auto clears it and recomputes.

  The dark palette is therefore declared twice — once under the media query as
  `:root:not([data-theme="light"])`, once as `:root[data-theme="dark"]`. **The two blocks must stay
  identical**; edit one and the switcher and the OS start to disagree.

  Everything resolves in an inline script in `<head>`, *before* first paint — anything later is a
  flash of the wrong theme on every load. Every `localStorage` access is wrapped in try/catch,
  because a private window can throw on the accessor itself. With JavaScript off nothing is pinned
  and the media query alone governs.

  `theme-color` stays as two media-scoped tags for the unpinned case; once something is pinned the
  script overwrites both with the same value, so whichever one the browser matches is correct.
- **Following the sun** needs a latitude and longitude. They come from the IANA timezone
  (`Intl.DateTimeFormat().resolvedOptions().timeZone`) against a packed table built by
  `tools/make-tz.sh` — *not* from the geolocation API. No permission prompt, no network call,
  nothing about the reader leaves the page. The price is city-level precision, which is well inside
  what sunrise timing needs. An unknown zone returns no coordinates and the page falls back to
  `prefers-color-scheme`, so the feature degrades instead of guessing.

  Sunrise and sunset use the NOAA sunrise equation, good to about a minute. Polar day and polar
  night are real cases and are handled explicitly: `cos(hour angle)` leaves [-1, 1] and the page
  returns light or dark outright rather than producing a NaN. After each transition it re-arms a
  timer for the next one, capped at six hours so a sleeping laptop, a clock change, or a polar
  stretch with no transition at all still gets picked up; it also re-syncs on `visibilitychange`,
  since a timer that fired while the machine was asleep cannot be trusted.

  This is the bulk of the page weight — the zone table alone is ~7 KB raw, ~4 KB gzipped. Trimming
  the table to the most-populated zones would roughly halve it, at the cost of everyone else falling
  back to the OS setting.
- **Contrast** is set by measurement, not by eye, and every text token clears WCAG AA at the size
  it is actually used. The tertiary grey was the problem in both palettes and was fixed in both:

  | | light on #F1EFE9 | dark on #141311 |
  |---|---|---|
  | `--ink` headline, lead | 15.7:1 AAA | 15.7:1 AAA |
  | `--ink-2` body copy | 7.1:1 AAA | 7.7:1 AAA |
  | `--ink-3` place, eyebrows, colophon | 4.9:1 AA | 5.4:1 AA |
  | `--accent` links | 7.4:1 AAA | 8.3:1 AAA |

  `--ink-3` was #8B857A (3.2:1) in light and #78736A (3.9:1) in dark — both below AA, and both
  setting the 11.5px block eyebrows, which is where it hurt most. They are now #6C675F and #8F8A80,
  picked along the original hue line so the warmth survives.

  The tertiary text is necessarily closer to the body copy than it was. The hierarchy now leans on
  type rather than colour alone — 11.5px, uppercase, letter-spaced — which is the more robust place
  for it anyway.
- **Texture** is two fixed, pointer-events-none layers on `body`: warm radial lifts in the top
  corners, and a `feTurbulence` grain as an inline SVG data URI (multiply in light, screen in dark).
  Both are dropped in print.
- **The entrance animation** is staggered CSS only, wrapped in `prefers-reduced-motion: no-preference`
  so the default when the query does not match is plain visible content, never a blank page.
- **The like button** under the portrait is a clicker, not a counter. There is nowhere to put a
  shared number on a static page, so this one is honestly per-visitor in `localStorage` and the
  zero state says so. Rather than tick +1 forever it runs the ladder the page is already about:
  pre-seed, seed, Series A, unicorn on paper, down round, exit and the earn-out, a second company,
  a regulator in every room, sovereign infrastructure, and out the other side at ten thousand.

  Clicking fast compounds, and the cap rises with the company — 8 early, 40 once it is large. That
  ramp is what keeps ten thousand a ninety-second session instead of a three-minute grind; the
  multiplier decays 1.1s after you stop. Past ten thousand there is nothing left to be promoted to,
  so every 2,500 draws a line at random from a pool of two dozen. The draw is remembered per step
  in `localStorage`, so reloading mid-step does not reshuffle the line under the reader.

  If a real shared count is ever wanted it needs a backend — a Cloudflare Worker with KV is about
  twenty-five lines and a free tier, at the cost of a cross-origin call the page does not make
  today, and rate limiting, because people are people.
- **OG image** is generated, not photographed — `assets/og.png`, 1200x630. Re-check link previews
  (Slack, WhatsApp, LinkedIn) after the first deploy; scrapers cache aggressively.
