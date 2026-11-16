# Three variants of guzh.uk/defence/ (spec for the builders, 16 Nov 2026)

Pavel Guzhikov's page for UK defence and dual-use tech startups (drones, counter-drone, autonomy, defence AI,
space, advanced manufacturing; 15 to a few hundred people, just after a raise or a first contract). Cold emails link
to it; three variants are A/B/C-tested, so they must be **strongly different** in form, typography and the "live"
element, while saying the same true things.

## What Pavel said about the current page (https://guzh.uk/defence/)

- "The top is too narrow; make the typography better." (The hero is squeezed into a ~800px column. Use the width.)
- "Not impressive. It doesn't show how deeply hands-on I am: a leader in the trenches, T-shaped, deep both
  technically and in business."
- "Show LedgerGov and Ruminator as projects I do: they're a bit to the side, for society and the state."
- "Make them live" (motion, interaction, something that moves or responds; respect reduced motion).
- Fonts: pick interesting ones from https://www.typedump.com/ , but only fonts whose licence allows free web use
  (SIL OFL or similar) and that you can serve from Google Fonts or self-host as woff2 under assets/defence/fonts/
  with the licence file next to them. Say which fonts and licences in your report.

## The message (keep all of it, any order, any form)

1. **Value line first** (bold, true): after a raise or a first contract, the hard part stops being the technology;
   it's everything around it: hiring fast, suppliers, paperwork, and getting feedback from trials back into the
   product before the next round. Pavel takes that on, hands-on, so the engineers stay on the product.
   Current headline, keep or beat: "You build the thing that flies. I'll build the company that delivers it."
2. **Who he is, as proof of hands-on and T-shape** (facts below only).
3. **What he takes on**: delivery (production tracking, supplier onboarding, quality and test paperwork); product
   (trial and operator feedback into the next release); scale (first ops team, hiring at speed, internal software
   that keeps 40 people working like 400); paperwork (bid packs, contract reporting, customer documentation).
4. **What stays theirs**: the technology, the defence know-how, the clearances, the customer relationships. The work
   sits on the unclassified side; where anything needs vetting, it is said plainly at the start.
5. **How we start**: a 30-minute call; two weeks on one bottleneck (mapped, a working fix for the worst of it, a
   plain plan); then build it together as a project, a part-time role inside the team, or something closer.
6. **CTA**: "Book 30 minutes" -> https://calendar.app.google/RG3g5WzxB3y9tXu39 (new tab), and mailto:pavel@guzh.uk.
   No prices anywhere.

## Facts you may use (all true; use nothing else about Pavel, invent no numbers or clients)

- Twenty years of building, from a multi-channel mobile messenger in 2005 to national payment infrastructure in 2022.
- Zero to one, four times. Two exits. One unicorn.
- Uzum (Uzbekistan's first unicorn): founding team. Fintech, lending, marketplace, payments, cards, and the data
  culture underneath them. Millions of users and 1,000+ employees in two years, in a market with no digital
  infrastructure.
- Founded and sold Worki, a fast-growing jobs marketplace (acquired by Mail.Ru Group, 2019). Co-founded an
  earned-wage-access company backed by Target Global (sold). Fintech products with 100+ banks.
  (Prefer leading with Uzum and the scale facts; Worki and Mail.Ru only lower down, plainly, if at all.)
- Now most interested in problems where the technology is genuinely hard, the deployment is political and the blast
  radius is national: sovereign infrastructure, public systems, defence and dual-use, AI in the public interest.
- Writes and ships the code himself: his public GitHub is https://github.com/xternal (you may fetch public
  activity live from https://api.github.com/users/xternal/events/public in the browser, with a graceful fallback if
  it fails or is rate-limited; never show raw commit messages, only counts / repo names / dates).
- Building now, alongside (show as live proof, with links):
  - **Ruminator** (https://ruminator.xyz/): for anyone who needs to know what is really happening inside Russia, and
    what Russians are told about it, beyond Moscow's national channels: journalists, analysts, researchers,
    diplomats, investors. Every day it reads Russia's regional and local press across dozens of regions, from state
    television to independent and exiled outlets and residents' Telegram channels, and shows what each kind of
    outlet reports and how it frames it. Every claim is checked word for word against the source. Invite-only.
  - **LedgerGov.UK** (https://ledgergov.uk/): an open P&L of the UK state: where public money comes from, where it
    goes and what every political promise would cost, each number linked to its official source. Independent
    public alpha, built as a citizen.
  - **BoroughBook.UK** (https://boroughbook.uk/): the same for one London borough (Hammersmith & Fulham).
  - **Agent Hands** (https://agenthands.cc/): lets any AI hire a person nearby for a real-world task; the money is
    locked before anyone sees the task and paid once the proof is accepted.
- Based in London. Email pavel@guzh.uk. LinkedIn https://www.linkedin.com/in/pavelguzhikov/

## Hard rules (the site's; a page that breaks one is rejected)

- Single static HTML file per variant, everything inline except fonts (Google Fonts link, or self-hosted woff2) and
  images you create. No frameworks, no build step, no external JS except the Cloudflare beacon snippet below.
- **No em dash (U+2014) and no middle dot (U+00B7) anywhere**, in text, code comments or CSS content.
- `lang="en-GB"`. Title, meta description, canonical, Open Graph (`og:title`, `og:description`, `og:url`,
  `og:image` 1200x630 with `og:image:alt`, width, height) and Twitter card tags, JSON-LD (`Service` with provider
  `Person` Pavel Guzhikov, url https://guzh.uk/), favicon `/favicon.svg`, apple-touch-icon
  `/assets/apple-touch-icon.png`.
- **Palette**: copy the `:root` light tokens and the two identical dark blocks (`@media (prefers-color-scheme:dark)
  { :root:not([data-theme="light"]) {...} }` and `:root[data-theme="dark"] {...}`) exactly from
  `tools/rebuild/rebuild.css` (names and values: --paper, --paper-lift, --ink, --ink-2, --ink-3, --accent, --rule,
  --rule-soft, --card, --red, --amber, --green and the -bg ones, --on-accent). You may add your own extra tokens
  for decoration, but text must use --ink/--ink-2/--ink-3/--accent on --paper/--paper-lift/--card. Dark mode is the
  dark brown (#241F1A), never black or navy. `theme-color` metas for both modes, as in the existing pages.
  `python3 tools/check-colours.py` must pass with your page added to its PAGES list (already added for you; do not edit that file).
- Light/dark switcher button like the rebuild pages (copy the small inline script from tools/rebuild/rebuild.js and
  the early theme script in the head), and it must work.
- **Header nav** with three links: "Defence tech" (this page, `aria-current="page"`, highlighted), "Back-office
  rebuild" (/rebuild/), and "Pavel Guzhikov" home link (/). On mobile the current item stays visible.
- **Footer** on every variant: "Made by Pavel Guzhikov" linking to https://guzh.uk and "Buy me a matcha 🍵" linking
  to https://ko-fi.com/pavelg, plain links; plus the line "Visits are counted by Cloudflare Web Analytics, without
  cookies or tracking you."
- Cloudflare beacon just before `</body>`, exactly as on index.html (the `if (location.hostname === "guzh.uk")`
  snippet with token bb18b698dcf74edab4f19890c1fb5005). Do **not** add the sendBeacon page counter.
- Buttons that open the booking page: no spinner needed (a plain link to a new tab), but give them
  `rel="noopener noreferrer"`.
- Motion: everything that moves stops or simplifies under `prefers-reduced-motion: reduce`. No layout shift. Works
  at 375px wide with no horizontal scroll and a 16px side gutter; hero typography large and confident on desktop
  (use the full width, roughly 1100 to 1280px container).
- Real crawlable text (not text baked into images or canvas). A short FAQ is welcome.
- WCAG AA for all text; keyboard focus visible; images have alt text.
- No fake data presented as real, no invented clients, no "classified" or official government markings
  (no "OFFICIAL", "SECRET", crests or MoD styling that imitates the state).

## Share image

Each variant gets its own 1200x630 PNG at `assets/defence/<slug>-og.png` that shows the substance (the headline and
the variant's idea), in the dark brown palette. Make it by writing an HTML card in `tools/defence/<slug>-og.html`
and screenshotting it with headless Chrome:
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,630 --screenshot=assets/defence/<slug>-og.png file://$PWD/tools/defence/<slug>-og.html`

## Checking your work

Serve the repo root (`python3 -m http.server <your port>` from the worktree root, kill it when done) and screenshot
with headless Chrome at 1440x2400 and 1280x900 (desktop) and look at the images; check light and dark
(`--force-dark-mode --blink-settings=preferredColorScheme=0` for dark). Headless Chrome cannot make a window
narrower than about 500px, so check mobile layout by reading your CSS carefully (and with a 500px screenshot).
Run `python3 tools/check-colours.py`. Grep your files for U+2014 and U+00B7.

Do not commit, push or touch files outside your own variant's paths
and `assets/defence/`. Another builder is working on each of the other variants in the same folder at the same time.
