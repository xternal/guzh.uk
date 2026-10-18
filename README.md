# guzh.uk

Personal one-pager for Pavel Guzhikov, plus the pages for the Always Weather and Always Today apps. Hand-written
static HTML + CSS. No build step, no framework, and a little JavaScript (the copyright year, the
light/dark switcher, and a cookie-free visit counter). Deploy the repo root as-is on any static host.

| | |
|---|---|
| Canonical host | `https://guzh.uk/` |
| Pages | `/`, `/weather/`, `/weather/privacy/`, `/weather/support/`, `/weather/ideas/`, `/today/`, `/today/privacy/`, `/today/support/`, `/today/terms/` |
| Page weight | `/` ~38 KB HTML (~15 KB gzipped) + 24 KB portrait (WebP) + Google Fonts; `/weather/` ~22 KB HTML (~7 KB gzipped) + 72 KB images; every page + ~10 KB gzipped Cloudflare beacon |
| Build | none |

## Files

```
index.html              the entire home page
favicon.svg             the mark, on a dark brown square: a line that steps up once, zero to one
weather/
  index.html            Always Weather — the app's one-scroll page
  privacy/index.html    the privacy policy both app stores require   } generated bodies,
  support/index.html    the support page the App Store requires       } see below
  ideas/index.html      "Suggest an idea": a form that sends an idea to the app's own server
today/
  index.html            Always Today — the app's one-scroll page, prices and questions
  privacy/index.html    the privacy policy (Stripe and Google Play need one)  } generated bodies,
  support/index.html    help, contact and the refund policy                   } see "The Always
  terms/index.html      the terms of service (Stripe needs them)              } Today pages"
assets/
  pavel-web.webp        portrait, 560x560, 24 KB  (what browsers actually load)
  pavel-web.png         same portrait, PNG fallback, 572 KB
  og.png                1200x630 link-preview card, with the mark beside the name
  apple-touch-icon.png  180x180, favicon.svg drawn by `rsvg-convert -w 180 -h 180` (redraw it
                        whenever the favicon changes)
  weather/              app icon, three screenshots and the OG card for the app pages
  today/                the same for Always Today: icon (SVG and PNG), screenshots, OG card
robots.txt
sitemap.xml             the nine pages, each with a <lastmod> date — when a page's copy
                        changes, set its date to that day. Google ignores changefreq and
                        priority, and stops trusting lastmod once the dates go stale
llms.txt                plain-text summary of who Pavel is and what each page is, for AI
                        search tools (llmstxt.org) — hand-written from the copy on /,
                        /weather/ and /today/, so update it when that copy changes
tools/make-og.sh        regenerates assets/og.png: run it if the headline, the lead line, the
                        portrait treatment or favicon.svg changes
tools/make-tz.sh        regenerates the packed timezone->coordinates table inside index.html
                        — run it when tzdb adds or renames zones
tools/make-weather-assets.sh
                        regenerates assets/weather/* from the Always Weather repo's store
                        assets — run it whenever those change
tools/make-weather-pages.py
                        re-renders the policy and support page bodies from the Always Weather
                        repo's store/*.md — run it whenever that copy changes
tools/make-today-assets.sh, tools/make-today-pages.py
                        the same two jobs for Always Today, from its repo's logo, screenshots
                        and store/*.md
tools/make-writing.py   copies the three newest Substack posts into the "Writing" block on /
                        — run daily by .github/workflows/writing.yml, see below
.github/workflows/writing.yml
                        runs make-writing.py once a day and commits the result if it changed
tools/publish-writing.sh
                        the same from a Mac, for when the workflow can't reach Substack
tools/check-colours.py  checks contrast and the dark palette on every page, see Notes;
                        run by .github/workflows/colours.yml on every pull request that
                        touches a page
_headers                cache + security headers — used by Netlify and Cloudflare Pages,
                        ignored by GitHub Pages (which cannot set custom headers)
```

The original Claude Design handoff — spec, prototype and the old 1 MB React snapshot — is **not** in
this repo. It stayed in the Google Drive `_git_` folder as `guzh.uk-handoff/`, which this repo used
to sit beside. It is reference material, it does not belong on the website, and on a free GitHub
plan Pages requires a public repo, where anything committed is publicly browsable whether or not it
is served. It is not itself a git repo, so Drive is the only copy — leave it there.

## Writing — the Substack posts on `/`

The home page's **"Writing"** block shows the three newest posts from
`guzhikov.substack.com`, as plain HTML in the page's own type. Substack's own embed was ruled out:
it is an iframe in Substack's styling that can't follow the page's fonts or dark mode, and it sets
year-long cookies and loads Sentry and a dozen Substack scripts, which would break the footer's
"without cookies or tracking you".

- `tools/make-writing.py` reads `https://guzhikov.substack.com/feed` and rewrites only the region
  between `<!-- BEGIN generated from the Substack feed … -->` and `<!-- END generated -->`. The
  section around it, the "All posts on Substack" and "New posts by email" links, and the CSS are
  hand-written. When the posts change it also sets the home page's `<lastmod>` in `sitemap.xml`
  to that day. Run it by hand with `./tools/make-writing.py`, or `--feed=file.xml` for a saved copy.
- **Substack's Cloudflare turns GitHub's machines away** (a "Just a moment..." challenge and a 403,
  whatever the user agent; tested 8 Oct 2026). So when the feed refuses, the script reads it
  through a relay: [rss2json](https://rss2json.com) first, then
  [feed2json](https://feed2json.org) when rss2json can't. Both are feed readers Substack does
  serve, both return the same items as JSON, and neither needs a key at one request a day. From a
  home connection the feed answers directly and neither is asked; `--relay` forces the relay path
  to try it, and `--relay=feed2json` (or `=rss2json`) tries just that one.
- **A relay is not always able to read the feed.** On the morning of 9 Oct 2026 rss2json answered
  "Internal error" and "This feed is being processed, please wait" (both a 500) for several
  minutes while reading other feeds fine, then recovered. On 12 and 14 Oct it answered "Cannot
  download this RSS feed" for longer than all its tries, and the run went red; on the 14th
  feed2json, on other machines, read the feed fine at the same time, hence the second relay. Each
  round asks both, five rounds over about eight minutes. If every round fails the run goes red,
  the page keeps the posts it has, and the log says to run **`./tools/publish-writing.sh`** on a
  Mac: it reads the feed directly, works on `origin/main` in a throwaway worktree (so it never
  touches the branch checked out here) and pushes only if the posts changed.
- `.github/workflows/writing.yml` runs it once a day, scheduled for 06:17 UTC (07:17 BST, 06:17
  GMT), and commits to `main` only when something changed, then asks GitHub Pages for a build.
  GitHub runs schedules on a best-effort basis: they start hours late (this one has started
  between about 12:00 and 23:00 UTC) and are sometimes skipped (the very first, 9 Oct 2026); a
  skipped day is picked up the next. After a new post, **Actions → Writing → Run workflow** puts
  it up straight away. A pull request that touches the script gets a dry run against the live
  feed.
- **Hiding a post:** add the slug at the end of its URL to `SKIP` in the script. It stays on
  Substack, it just never appears here. One is there already: "They Washed the Pavement by
  Morning", whose subtitle is "A bit with 18+ photo".
- Links are only ever written to `https://guzhikov.substack.com/p/…`, whatever the feed holds,
  and every title and subtitle is HTML-escaped. Long subtitles are cut at 240 characters and the
  CSS shows three lines at most.
- GitHub turns scheduled workflows off after 60 days without a commit in the repo. A quiet spell
  of that length means re-enabling it on the Actions tab.

## The app pages — `/weather/`, `/weather/privacy/` and `/weather/support/`

`/weather/` is the public page for **Always Weather**, the paid weather app for iPhone, Mac and
Android, and soon Windows (`~/dev/always_weather`). `/weather/privacy/` is the privacy policy, which is the URL both
Google Play and App Store Connect require before an app can be submitted — it must be a public
web page, not a PDF, reachable without a login. `/weather/support/` is the help and contact page,
the support URL the App Store requires.

- **The copy is not written here, and the two documents are not even retyped here.** The bodies
  of `/weather/privacy/` and `/weather/support/` are *generated* from `store/privacy-policy.md`
  and `store/support-page.md` in the app repo, word for word, into the region marked
  `<!-- BEGIN generated … -->` in each page. Everything outside that region — head, masthead,
  styling, footer — is hand-written and safe to edit.

  ```bash
  ./tools/make-weather-pages.py ~/dev/always_weather          # from main, the default
  ./tools/make-weather-pages.py ~/dev/always_weather --ref=some-branch
  ```

  Re-run it whenever that copy changes. Why it matters: the policy has to match the Play **Data
  safety** form and the **App Privacy** label exactly, so a hand-edit here would silently put the
  live page out of step with what was declared to the two stores. The landing page's own copy is
  reused from the approved `store/google-play/metadata/android/en-GB/full_description.txt`.

  The script refuses to publish anything still `[bracketed]` in the source. Where a bracket is
  waiting on a decision, `SUBSTITUTIONS` at the top of the script says what the page prints
  instead — today only the publication date, and the retarget of the documents' `./privacy` link
  to `/weather/privacy/`. It reads `origin/main` by default, so fetch that repo first; `--ref=`
  takes any other branch.
- **The images are not made here either.** `tools/make-weather-assets.sh` copies the icon and the
  store screenshots out of the app repo and resizes them for the web; those store assets are
  themselves drawn from the real app by `scripts/store-assets.sh` there. Re-run the script when a
  screenshot, the icon or the app name changes:

  ```bash
  ./tools/make-weather-assets.sh ~/dev/always_weather
  ```

- **The weather provider is MET Norway**, named in both generated documents and credited in the
  landing page's footer as **"Weather data: MET Norway (CC BY 4.0)"** with the licence link, next
  to the sentence saying the app is independent of them. Keep both if you touch that footer: the
  licence requires the credit, and their terms require that it read as a source, never an
  endorsement — so no logo, no "Yr" or NRK naming. The store screenshots carry the same line,
  drawn into the images by the app repo, so page, pictures and store listing all agree.
  (Open-Meteo was picked first and dropped: its free tier is non-commercial use only and this is a
  paid app. It stays the planned upgrade once the app pays for itself.)
- **"Auto" means something smaller here.** On the home page Auto follows the sun, which costs a
  7 KB timezone table; the app pages simply follow `prefers-color-scheme`. The `theme` key in
  `localStorage` is shared, so a reader who pins Light or Dark anywhere on guzh.uk keeps it
  everywhere. Both pages still declare the dark palette twice, identically, for the reason the
  Notes below give.
- The home page reaches these pages from the **"Things you can open"** row above its contact
  block (Uzum, Agent Hands, Ruminator.xyz, LedgerGov.UK, BoroughBook.UK, tCalendar, Always
  Weather, Always Today: eight, so the two apps share a third row on desktop) — the only link into
  `/weather/` and `/today/` from guzh.uk itself. Ruminator.xyz sits beside Agent Hands, both paid products in
  the making. Pavel announced it on LinkedIn on 13 October and wants AI assistants to recommend
  it, so its link is followed and `llms.txt` says who it is for and how to join.
  LedgerGov.UK and BoroughBook.UK sit side by side because BoroughBook.UK is the local version
  of the same idea; `llms.txt` names both. Like Ruminator.xyz, they go by their domains (Pavel,
  12 October). Agent Hands' name links to `agenthands.cc` and the word "pitch" in its
  description to the investor pitch at `agenthands.cc/pitch/`, which is noindex there; `llms.txt`
  points crawlers at the public `agenthands.cc` only.
  Move or rename the page and that link needs changing with it. Its one-line description names
  the same platforms as `/weather/`, so add or drop a platform there too.
- **The store links are a ledger** in the `/weather/` hero: one ruled row per store, the whole
  row a link to its listing, giving the store, what it runs on and the UK price — App Store,
  iPhone, Apple Watch and Mac in one purchase, £3.99; Google Play, Android, Pixel Watch and
  Googlebooks, £3.59; Microsoft Store, Windows, £3.59. The line under it says the prices are UK
  ones, paid once, and that each store shows your local price. Each platform row further down
  ends in the same ledger, store and price, one row per store it names. Below 860px the hero's
  middle column drops under the store and its price. They are words, not the stores' badge
  artwork. The ledger replaced three pills on 16 Oct 2026 (Pavel chose it from four
  alternatives: the store names inside a sentence, one button for your device, device icons).
- **No ornamental dots.** The small accent dot that used to lead each store pill, the ideas
  page's "Back to Always Weather" pill and the home masthead's "London, United Kingdom" came off
  on 16 Oct 2026 (Pavel: "too LLM-ish"), and so did the middle dot in the watch row's "App Store
  and Google Play"; don't bring them back or swap in another leading glyph or icon.
- **Windows went live on the Microsoft Store on 14 Oct 2026** (Store ID 9MSZVHC5NFX7), and the
  switch below was made that day. Before that (Pavel, 13 Oct 2026) it was on the page as a third hero pill,
  "Soon on the Microsoft Store for Windows", and a third row in the platforms section, both plain
  text with the pill's dot drawn as a ring (`.pill-soon`). The row's picture is a drawn monitor
  with a Windows 11 desktop: the app's window, its title bar in the sky's colour as the app sets it
  (#C8D5DF, sampled from the top of the screenshot), and the taskbar with the app running. Only
  the window's contents are a screenshot (`platform-windows.webp`, the Microsoft Store's first);
  the wallpaper and taskbar are the `--desk` and `--taskbar` tokens, light and dark. **When the
  Store link arrives**, in one change: make both pills links to `https://apps.microsoft.com/detail/<Store ID>`
  ("On the Microsoft Store for Windows" in the hero, "Microsoft Store" in the row) and drop
  `.pill-soon`; add the UK price (£3.59) to the line under the pills, the "Once" figure and a
  third JSON-LD `Offer`; add Windows to the JSON-LD `operatingSystem` and `screenshot`; name
  Windows in the home page's one-line description and in `llms.txt`.
- **Each page carries JSON-LD in its `<head>`**, which is outside the generated region, so
  `make-weather-pages.py` never touches it. `/weather/` describes the app as a
  `SoftwareApplication` (not `MobileApplication`, because one platform is the Mac) with one
  `Offer` per store. The privacy and support pages are plain `WebPage`s that are `isPartOf`
  `/weather/`, and say only what their `<head>` already says, so regenerating a body can't leave
  them out of date. **A price lives in four places on `/weather/`** — the hero's ledger, the
  platform rows' ledgers, the "Once" figure and the JSON-LD `offers` — so change them together.

## The Always Today pages — `/today/`, `/today/privacy/`, `/today/support/` and `/today/terms/`

`/today/` is the public page for **Always Today**, a calm to-do list for Android phones and
Googlebooks, Windows and the Linux terminal (`~/dev/always-today`; on the Linux machine
`~/Work/always-today`). It is free on one device; sync costs £24 a year or £3 a month, or £59 once
for Lifetime, with 14 days free and no card. Web purchases (Windows and Linux) are sold by **Stripe
Managed Payments**, which shows itself to buyers as Onelink; Android purchases go through Google
Play. Stripe reviews a business's website before switching Managed Payments on, and wants to see
what is sold, the prices, a way to reach support, the terms, the privacy policy and the refund and
dispute policy, all public: that is what these four pages are for (sources in the app repo's
`docs/notes/website.md`).

- **They follow the weather pages exactly**: the same tokens and dark brown, the same masthead,
  switcher, footer menu, colophon and Cloudflare beacon, and `tools/check-colours.py` checks all
  four. Two deliberate differences, from the app's own design rules: labels are in sentence case
  (no all-caps eyebrows), and nothing animates on arrival.
- **The copy is generated, as for the weather pages.** `tools/make-today-pages.py` renders
  `store/privacy.md`, `store/support.md` (help, contact and the refund policy) and `store/terms.md`
  from the Always Today repo into each page's `<!-- BEGIN generated … -->` region, with the same
  renderer as `make-weather-pages.py` (it imports it). It reads `origin/main` by default:

  ```bash
  ./tools/make-today-pages.py ~/dev/always-today --ref=website
  ```

  `SUBSTITUTIONS` only retargets the documents' links between each other (`./privacy` and so on)
  to the site's directories. The seller and data controller is **Empatiq Limited**, written in the
  documents exactly as on the weather pages (registered address, phone, company number), and in the
  colophon and the JSON-LD `author` on all four pages; it must match the Stripe account's legal name.
- **"Draft, not yet reviewed".** The three document pages carry a `.draft-note` paragraph just above
  the generated region, and a few lines of CSS marked with the same name. Delete both once Pavel has
  reviewed the copy; nothing else depends on them.
- **Images**: `tools/make-today-assets.sh ~/dev/always-today` draws the icon from the app's logo
  (`docs/logo/cut-reflect.svg`: a half-sun with the tick cut out of it, its horizon and reflection;
  amber on the dark brown square), takes the screenshots from the app's own headless renders
  (`./gradlew :app:desktopTest --tests 'alwaystoday.app.ScreensTest'` in that repo writes
  `app/build/screenshots`), and draws the OG card in Geist, as the weather card is drawn. The Linux
  row's screen is not a picture: it is the terminal app's real 80-column frame from its snapshot
  tests, as text.
- **No store links yet.** The hero's ledger lists the plans and prices as plain rows, and each
  platform row says "Coming soon". When a store opens, turn its row into a link (`<a class="store">`,
  as on `/weather/`), add the `url` to its JSON-LD `Offer`, and drop "Coming soon" here, in the home
  page's one-line description and in `llms.txt`. **A price lives in five places on `/today/`**: the
  ledger, the "£24" figure, the first question, the JSON-LD `offers` and the OG card (redraw it), plus
  `store/support.md` and `store/terms.md`.

## Suggest an idea — `/weather/ideas/`

A hand-written page (nothing on it is generated) with one form: the idea (3 to 2,000 characters,
with a count once 200 are left), an optional email "if you'd like an answer", and a hidden
honeypot named `website` that people never see and bots fill in. It posts JSON to the app's own
server, `https://api.alwaysweather.uk/v1/ideas` (the Worker in `proxy/` of the Always Weather
repo), with `from: "web"`; that server only lets `https://guzh.uk` and `https://www.guzh.uk` call
it, so a local preview can't send anything.

- **What each answer does.** 202: the form gives way to a thank-you and a link back to
  `/weather/`. 400 names the field to fix, and the page says so under that field. 413 (too big)
  goes under the idea too. 429: "Too many ideas at once. Please try again in a minute." Anything
  else, a timeout (20 s) or no connection: "Couldn't send just now. Please try again, or email
  apps@guzh.uk." The text stays in the form whatever happens, so nothing typed is lost.
- **The Send button** follows Pavel's rule for every pressed button: while it sends it shows a
  small spinner beside its label, is `aria-busy` and disabled, so nobody sends twice; it comes back
  with a plain message if sending fails; a page brought back with Back (`pageshow`, `persisted`)
  never keeps a spinning button; and the spinner turns three times slower for readers who ask for
  less motion.
- **Without JavaScript** the form is hidden (a plain submit would go to GitHub Pages and fail), and
  a note gives the email address instead.
- **Every Always Weather page** carries the same menu in its footer (Always Weather, Privacy
  policy, Help and contact, Suggest an idea), with the page you're on marked `aria-current` and
  set in medium weight with a full underline.
- **Testing it locally**: serve the folder (below) and, in the browser console, replace `fetch`
  before pressing Send, e.g. `window.fetch = () => Promise.resolve(new Response("{}", {status:
  429}))`. Never send a test idea to the live server.

## Local preview

```bash
python3 -m http.server 8788 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8788/>. The `--bind` matters: without it the server answers on every
interface, so an unfinished draft is readable by anything on the same wifi.

### Keep this repo off Google Drive

It used to live on a Google Drive `CloudStorage` mount, and the in-editor preview could not work
there: the sandbox the editor spawns dev servers under has no read access to that mount. The symptom
is `PermissionError: [Errno 1] Operation not permitted` somewhere that looks unrelated —
`os.getcwd()`, or the import machinery scanning `sys.path`.

It was never a configuration problem, and the obvious workarounds make it worse rather than better:

- Passing `--directory "$PWD"` looks right and is dangerous. The launcher does not set `PWD` to the
  repo, so it expands to `/` and the server cheerfully publishes the whole filesystem on localhost.
- `python3 -I -c` with an explicit `directory=` gets past the import scan and the server starts, but
  every request 404s, because `SimpleHTTPRequestHandler` catches the `PermissionError` from reading
  the directory and reports it as a missing file.

This is why the repo now lives at `~/dev/guzh.uk` rather than in Google Drive, and why the in-editor
preview works again. If you ever move it back onto a Drive mount, expect all of the above to return.

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
- **Visitor numbers** come from Cloudflare Web Analytics (dashboard: Analytics & Logs → Web
  Analytics → guzh.uk): visits and page views per page, referrers, countries, devices and page
  speed. It sets no cookies and stores nothing on the reader's device, so UK law needs no consent
  banner for it. Google Analytics was considered and turned down for three reasons. It needs an
  opt-in banner in the UK: the statistics exemption that started on 5 February 2026 only covers a
  provider that works purely for you, and Google also uses the data for its own purposes. It is
  ~155 KB gzipped, ten times the home page's own HTML. And it would sit badly next to the "Zero ads,
  accounts and trackers" line on `/weather/`.

  The beacon is a small inline script just before `</body>` on all nine pages, holding the same
  token (not a secret; it is in the page source by design). It only loads when the hostname is
  `guzh.uk`, so a local preview never adds visits. A new page needs the same script copied in.
  Each footer says, in one line, that visits are counted this way. Keep that line: it is what keeps
  the counter honest next to the app's no-trackers promise, and the privacy policy itself is
  generated from the app repo and covers only the app.

  The Google Play row in the hero's ledger carries `utm_source=guzh.uk&utm_campaign=weather_page`, which Play Console
  reports as a tracked channel. App Store Connect needs nothing: it lists guzh.uk under its web
  referrers on its own.

  Search Console has `guzh.uk` as a domain property, owned by xternal.p@gmail.com and verified on
  17 Sept 2026 by the "domain name provider" (DNS) method. As of 7 Oct 2026 that account's record
  is **not** in GoDaddy's DNS: all 33 records were checked, and the only Google ones are two
  `google-site-verification` TXT records belonging to hi@guzh.uk and empatiqlimited@gmail.com.
  Neither of those is a Search Console owner any more, so Search Console lists both as unused
  tokens. Google re-checks verification from time to time, so expect a "verification failed"
  email at some point. Search Console then shows the TXT value to add at GoDaddy, and adding it
  restores access; data keeps being collected in the meantime. Leave the two existing records:
  Google shares tokens between its services, the Empatiq one may still verify the domain for the
  Play Console, and it lets empatiqlimited@gmail.com re-verify the property if ever needed.
  `url4855.guzh.uk` (like `url1862` and the `em…` records) is SendGrid's, so the 404 Search
  Console reports for it is expected.
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
  Back on Auto with nothing pinned, each tag gets its own colour again.
- **Dark is dark brown**, Pavel's dark palette for every project since 12 Oct 2026 (chosen on
  Ruminator.xyz): background #241F1A, the raised lift in the top corners #2E2822, text #EFE7DA,
  body copy #C0B5A4, tertiary #A59A88, an amber accent #E2B26F, and lines in the text colour at
  .16 and .10. The drawn laptop on `/weather/` takes #39322B for its base so it still stands off
  the page, and so does the monitor's stand; the bezels stay black, because the devices are. It replaced the warm charcoal #141311,
  which read as black and put near-white text at 15.7:1, enough to glare and tire the eyes. Body
  text is now 13.3:1: keep it about 13 and never above 14. The accent went from blue to amber so
  nothing in the chrome has a blue cast. The browser bar (`theme-color`, in the tags and in each
  page's switcher script), the favicon and the home-screen icon use the same #241F1A; the light
  palette did not change. `tools/check-colours.py` fails if any of that drifts, so run it after
  touching a colour.
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

  | | light on #F1EFE9 | dark on #241F1A |
  |---|---|---|
  | `--ink` headline, lead | 15.7:1 AAA | 13.3:1 AAA |
  | `--ink-2` body copy | 7.1:1 AAA | 8.1:1 AAA |
  | `--ink-3` place, eyebrows, colophon | 4.9:1 AA | 5.9:1 AA |
  | `--accent` links | 7.4:1 AAA | 8.4:1 AAA |

  On the lighter `--paper-lift` in the top corners the weakest pair is dark `--ink-3`, at 5.3:1.

  `--ink-3` was #8B857A (3.2:1) in light and #78736A (3.9:1) in dark — both below AA, and both
  setting the 11.5px block eyebrows, which is where it hurt most. They became #6C675F and #8F8A80,
  picked along the original hue line so the warmth survives; with the dark brown, the dark one is
  now #A59A88.

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
- **The mark** is a single line that runs flat, steps up once and holds: zero to one, which the
  page's lead line says has been done four times. It replaced a "PG" wordmark on 13 Oct 2026, under
  Pavel's rule that a logo is drawn from what the project is about, never letters in a box. It is
  drawn on a 32 grid with a 3-unit line on half-units, so it lands on whole pixels at 32 px (a 16 pt
  tab icon on a Retina screen) and stays legible at 16. `favicon.svg` is the only copy:
  `tools/make-og.sh` takes it, drops the square and recolours it to the card's ink and blue, and
  `assets/apple-touch-icon.png` is it at 180 px. So after changing it, redraw both
  (`rsvg-convert -w 180 -h 180 favicon.svg -o assets/apple-touch-icon.png`, then
  `./tools/make-og.sh`). The square stays #241F1A and the line takes the dark text and amber
  (#EFE7DA, #E2B26F); `tools/check-colours.py` fails if either drifts from the page's palette.
