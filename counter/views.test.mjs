// guzh.uk's page counter (views.js): which beacons count, that the page list matches the pages carrying the
// counter script, and the shape of /views.json, which Pavel's daily report of page visits reads.
// No network, no Worker: node --test counter/views.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { HOME, PAGES, VIEWS_DAYS, countedHit, countedPage, firstKept, firstShown, isNotAReader, viewsFile } from "./views.js";

const ROOT = fileURLToPath(new URL("..", import.meta.url));
// A browser's user agent, only ever sent here to the functions under test: nothing is counted for real.
const BROWSER = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1";
const beacon = (headers = {}, method = "POST") =>
  new Request("https://guzh-uk-views.xternal.workers.dev/hit", { method, headers: { origin: HOME, "user-agent": BROWSER, ...headers } });

test("each page counts under one name, however the address bar shows it", () => {
  for (const page of PAGES) assert.equal(countedPage(page), page);
  assert.equal(countedPage("/index.html"), "/");
  assert.equal(countedPage("/goat-rodeo"), "/goat-rodeo/");
  assert.equal(countedPage("/goat-rodeo/index.html"), "/goat-rodeo/");
  assert.equal(countedPage("/weather/privacy"), "/weather/privacy/");
});

test("nothing else counts: forwarding pages, the race page, files, made-up addresses", () => {
  for (const path of [
    "/weather/", "/today/", "/goat-rodeo/race/", "/goat-rodeo/race/#zABC", "/404.html", "/404/", "/views.json",
    "/llms.txt", "/robots.txt", "/favicon.svg", "/assets/og.png", "/wp-login.php", "/WEATHER/PRIVACY/", "//", "",
    `/${"a".repeat(80)}/`, null, undefined, 404,
  ]) assert.equal(countedPage(path), null, String(path));
});

test("crawlers, AI fetchers, scripts and requests with no user agent are not readers", () => {
  for (const ua of [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ChatGPT-User/1.0; +https://openai.com/bot)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36 Chrome-Lighthouse",
    "curl/8.4.0",
    "site-visits-report/1.0",
    "",
    null,
  ]) assert.equal(isNotAReader(ua), true, String(ua));
  assert.equal(isNotAReader(BROWSER), false);
  assert.equal(isNotAReader("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"), false);
});

test("a beacon counts only as a POST from a guzh.uk page, sent by a browser", () => {
  assert.equal(countedHit(beacon(), "/"), "/");
  assert.equal(countedHit(beacon(), "/404"), "/404");
  assert.equal(countedHit(beacon(), "/goat-rodeo/index.html"), "/goat-rodeo/");
  assert.equal(countedHit(beacon({}, "GET"), "/"), null, "a GET is not a beacon");
  assert.equal(countedHit(beacon({ origin: "https://example.com" }), "/"), null, "another site");
  assert.equal(countedHit(beacon({ origin: "http://guzh.uk" }), "/"), null, "not https");
  assert.equal(countedHit(beacon({ origin: "http://localhost:8788" }), "/"), null, "a local preview");
  assert.equal(countedHit(new Request("https://x/hit", { method: "POST", headers: { "user-agent": BROWSER } }), "/"), null, "no origin");
  assert.equal(countedHit(beacon({ "user-agent": "curl/8.4.0" }), "/"), null, "a script");
  assert.equal(countedHit(beacon(), "/goat-rodeo/race/"), null, "the race page counts no visits");
  assert.equal(countedHit(beacon(), "<script>alert(1)</script>"), null);
});

// The pages under the repository root, as paths: "index.html" is "/", "goat-rodeo/index.html" is "/goat-rodeo/".
function pages(dir = ROOT) {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...pages(full));
    else if (entry.name.endsWith(".html")) out.push(full);
  }
  return out;
}
const pathOf = (file) => {
  const rel = relative(ROOT, file).split("\\").join("/");
  return rel === "404.html" ? "/404" : `/${rel.replace(/index\.html$/, "")}`;
};

test("the page list is exactly the pages that carry the counter script", () => {
  const carrying = [];
  for (const file of pages()) {
    const html = readFileSync(file, "utf8");
    if (!html.includes("guzh-uk-views.xternal.workers.dev/hit")) continue;
    const path = pathOf(file);
    carrying.push(path);
    const sends = path === "/404" ? '"/404"' : "location.pathname";
    assert.ok(html.includes(`navigator.sendBeacon("https://guzh-uk-views.xternal.workers.dev/hit", ${sends})`), `${path} sends ${sends}`);
    assert.ok(html.includes('location.hostname === "guzh.uk"'), `${path} counts only on guzh.uk itself`);
    assert.ok(html.includes("a simple page counter"), `${path} says in its footer that visits are counted`);
  }
  assert.deepEqual(carrying.sort(), [...PAGES].sort(), "add a new page to PAGES in views.js, or take the script off it");
});

test("/views.json is newest first, one number per page per day, and days with no views are left out", () => {
  const now = new Date("2026-10-21T10:00:00Z");
  const file = viewsFile([
    { day: "2026-10-20", path: "/", n: 3 },
    { day: "2026-10-21", path: "/", n: 1 },
    { day: "2026-10-20", path: "/goat-rodeo/", n: 2n },
    { day: "2026-10-18", path: "/404", n: 1 },
  ], now);
  assert.deepEqual(file, {
    generated_at: "2026-10-21T10:00:00.000Z",
    days: [
      { date: "2026-10-21", pages: { "/": 1 } },
      { date: "2026-10-20", pages: { "/": 3, "/goat-rodeo/": 2 } },
      { date: "2026-10-18", pages: { "/404": 1 } },
    ],
  });
  assert.deepEqual(viewsFile([], now), { generated_at: now.toISOString(), days: [] });
});

test("the counter shows 30 days, today included, and keeps a few more", () => {
  const now = new Date("2026-10-21T23:59:59Z");
  assert.equal(VIEWS_DAYS, 30);
  assert.equal(firstShown(now), "2026-09-22");
  assert.equal(firstKept(now), "2026-09-12");
});
