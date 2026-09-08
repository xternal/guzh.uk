# guzh.uk

Personal one-pager for Pavel Guzhikov. Hand-written static HTML + CSS. No build step, no framework,
and one line of JavaScript (the copyright year). Deploy the repo root as-is on any static host.

| | |
|---|---|
| Canonical host | `https://guzh.uk/` |
| Page weight | ~15 KB HTML + 24 KB portrait (WebP) + Google Fonts |
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
_headers                cache + security headers — used by Netlify and Cloudflare Pages,
                        ignored by GitHub Pages (which cannot set custom headers)
```

The original Claude Design handoff — spec, prototype and the old 1 MB React snapshot — is **not** in
this repo. It lives beside it at `../guzh.uk-handoff/`. It is reference material, it does not belong
on the website, and on a free GitHub plan Pages requires a public repo, where anything committed is
publicly browsable whether or not it is served.

## Local preview

```bash
python3 -m http.server 8788
```

Then open <http://127.0.0.1:8788/>.

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
- **Light and dark** both ship. The palette is one set of custom properties on `:root`, redefined
  under `prefers-color-scheme: dark`; `theme-color` is declared twice with a media attribute to match.
  There is no toggle — the page follows the reader's OS.
- **Texture** is two fixed, pointer-events-none layers on `body`: warm radial lifts in the top
  corners, and a `feTurbulence` grain as an inline SVG data URI (multiply in light, screen in dark).
  Both are dropped in print.
- **The entrance animation** is staggered CSS only, wrapped in `prefers-reduced-motion: no-preference`
  so the default when the query does not match is plain visible content, never a blank page.
- **OG image** is generated, not photographed — `assets/og.png`, 1200x630. Re-check link previews
  (Slack, WhatsApp, LinkedIn) after the first deploy; scrapers cache aggressively.
