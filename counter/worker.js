// guzh.uk's page counter (views.js), at https://guzh-uk-views.xternal.workers.dev:
//   POST /hit         a guzh.uk page, once as it opens: its own path as text, nothing else
//   GET  /views.json  public: one number per page per UTC day, last 30 days (the Site visits report)
//   cd counter && wrangler deploy      # publish
//   node --test counter/views.test.mjs  # the tests, no network
import { DurableObject } from "cloudflare:workers";
import { HIT_PATH, VIEWS_CACHE_SECONDS, VIEWS_PATH, countedHit, firstKept, firstShown, utcDay, viewsFile } from "./views.js";

/**
 * The counter: one table, a row per page per UTC day, kept 40 days (views.js KEEP_DAYS). A Durable Object, so two
 * views in the same second both count, and it lives with this Worker: nothing to set up by hand.
 */
export class Views extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS views (day TEXT NOT NULL, path TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY (day, path)) WITHOUT ROWID");
  }

  /** One more view of a page today; older days than the counter keeps go. */
  count(path) {
    const at = new Date();
    this.sql.exec("INSERT INTO views (day, path, n) VALUES (?, ?, 1) ON CONFLICT (day, path) DO UPDATE SET n = n + 1", utcDay(at), path);
    this.sql.exec("DELETE FROM views WHERE day < ?", firstKept(at));
  }

  /** Every row from `since` (a UTC day) on. */
  read(since) {
    return this.sql.exec("SELECT day, path, n FROM views WHERE day >= ?", since).toArray();
  }
}

const counter = (env) => env.VIEWS.get(env.VIEWS.idFromName("guzh.uk"));

/**
 * A beacon: answered at once with nothing, and counted after, if it is a browser on a guzh.uk page naming one of
 * its pages. The address is used only by the rate limiter, in memory, so one address can't run a count up.
 */
async function hit(request, env, ctx) {
  if (Number(request.headers.get("content-length") ?? 0) <= 128) {
    const page = countedHit(request, await request.text());
    if (page) {
      ctx.waitUntil((async () => {
        const { success } = await env.LIMIT.limit({ key: request.headers.get("cf-connecting-ip") ?? "" });
        if (success) await counter(env).count(page);
      })().catch((e) => console.error(`views: ${e?.message ?? e}`)));
    }
  }
  return new Response(null, { status: 204 });
}

const VIEWS_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Access-Control-Allow-Origin": "*",
  "X-Content-Type-Options": "nosniff",
  "X-Robots-Tag": "noindex",
};

/**
 * /views.json: how many times each page was opened on each of the last 30 days (UTC), newest first.
 * Open to anyone, like the other sites' counters, and kept ten minutes at the edge so asking often
 * never reaches the counter. A counter that can't be read answers 503.
 */
async function views(request, env, ctx) {
  const cache = caches.default;
  const key = new Request(new URL(VIEWS_PATH, request.url).toString());
  const cached = await cache.match(key);
  if (cached) return request.method === "HEAD" ? new Response(null, cached) : cached;
  try {
    const now = new Date();
    const body = JSON.stringify(viewsFile(await counter(env).read(firstShown(now)), now));
    const response = new Response(body, { headers: { ...VIEWS_HEADERS, "Cache-Control": `public, max-age=${VIEWS_CACHE_SECONDS}` } });
    ctx.waitUntil(cache.put(key, response.clone()));
    return request.method === "HEAD" ? new Response(null, response) : response;
  } catch (e) {
    console.error(`views.json: ${e?.message ?? e}`);
    return new Response(JSON.stringify({ error: "the counter cannot be read now" }), {
      status: 503,
      headers: { ...VIEWS_HEADERS, "Cache-Control": "no-store" },
    });
  }
}

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    if (pathname === HIT_PATH && request.method === "POST") return hit(request, env, ctx);
    if (pathname === VIEWS_PATH && (request.method === "GET" || request.method === "HEAD")) return views(request, env, ctx);
    if (pathname === "/" && request.method === "GET") {
      return new Response("guzh.uk's page counter: one number per page per day, nothing about readers. See /views.json.\n", {
        headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" },
      });
    }
    return new Response("Not found\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  },
};
