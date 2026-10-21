// guzh.uk's page counter: how many times each page was opened on each UTC day, and nothing about who
// opened it. /views.json gives the last 30 days in the same format as Pavel's other sites' counters
// (alwaysweather.uk, RussiaLedger.com and the rest), which his daily report of page visits reads (the
// site-visits repository).
//
// guzh.uk is static on GitHub Pages, so it cannot count by itself: each page sends its own path, once, to
// this Worker (worker.js) when it opens in a browser (the counter script on each page, see "Visitor
// numbers" in ../README.md). Only the pages listed below count, so nothing a visitor types can become a
// row. The user agent is read only to skip crawlers, AI fetchers and scripts that run pages, and is not
// stored: not the IP address, country, device, browser, referrer or time of day. No cookies, nothing
// kept on the reader's device.
//
// No Cloudflare imports here, so the tests run in plain Node (views.test.mjs).

export const HOME = "https://guzh.uk";
export const HIT_PATH = "/hit";
export const VIEWS_PATH = "/views.json";
// How many days /views.json returns, today included.
export const VIEWS_DAYS = 30;
// How long /views.json keeps an answer before asking the counter again.
export const VIEWS_CACHE_SECONDS = 600;
// How long the counter keeps a day: a little over the 30 days it shows.
export const KEEP_DAYS = 40;

// Every page that carries the counter script, as the browser's address bar shows it; 404.html sends
// "/404" whatever the missing address was. Not /weather/ and /today/, which forward to the apps' own
// sites before anything could load, and not /goat-rodeo/race/, whose footer promises it counts no
// visits. A new page needs adding here and the Worker deploying again (views.test.mjs checks the list
// against the pages).
export const PAGES = [
  "/",
  "/404",
  "/weather/privacy/",
  "/weather/support/",
  "/weather/ideas/",
  "/today/privacy/",
  "/today/support/",
  "/today/terms/",
  "/goat-rodeo/",
  "/goat-rodeo/privacy/",
];

/** The page a path counts as, or null. "/goat-rodeo", "/goat-rodeo/" and "/goat-rodeo/index.html" are
 * the same page. */
export function countedPage(path) {
  if (typeof path !== "string" || !path.startsWith("/") || path.length > 64) return null;
  let p = path.replace(/index\.html$/, "");
  if (p !== "/404" && !p.endsWith("/")) p += "/";
  return PAGES.includes(p) ? p : null;
}

const NOT_A_READER =
  /bot|crawl|spider|slurp|preview|facebookexternalhit|facebookcatalog|meta-external|embedly|whatsapp|telegram|skype|discord|slack|curl|wget|python|httpx|go-http|java\/|okhttp|axios|node-fetch|undici|^node|deno|ruby|php|libwww|postman|insomnia|headless|lighthouse|pagespeed|inspectiontool|pingdom|uptime|monitor|feed|rss|scan|archive|chatgpt|claude|perplexity|anthropic|openai|site-visits|https?:\/\//i;
/** A crawler, an AI fetcher or a script that runs pages (browsers never put a web address in their
 * name); a request with no user agent is not counted either. */
export const isNotAReader = (userAgent) => !userAgent || NOT_A_READER.test(userAgent);

/** The page a beacon adds one to today, or null: a POST from a guzh.uk page, sent by a browser, naming
 * one of the pages above. `body` is the beacon's text, read by the Worker. */
export function countedHit(request, body) {
  if (request.method !== "POST" || request.headers.get("origin") !== HOME) return null;
  if (isNotAReader(request.headers.get("user-agent"))) return null;
  return countedPage(body);
}

const DAY_MS = 86_400_000;
export const utcDay = (date) => date.toISOString().slice(0, 10);
/** The first day /views.json shows, and the first day the counter keeps. */
export const firstShown = (now) => utcDay(new Date(now.getTime() - (VIEWS_DAYS - 1) * DAY_MS));
export const firstKept = (now) => utcDay(new Date(now.getTime() - (KEEP_DAYS - 1) * DAY_MS));

/** The counter's rows ({ day, path, n }) as /views.json: { generated_at, days: [{ date, pages }] },
 * newest first; days with no views are left out. */
export function viewsFile(rows, now) {
  const days = new Map();
  for (const { day, path, n } of rows) {
    if (!days.has(day)) days.set(day, {});
    days.get(day)[path] = Number(n);
  }
  return {
    generated_at: now.toISOString(),
    days: [...days.keys()].sort().reverse().map((date) => ({ date, pages: days.get(date) })),
  };
}
