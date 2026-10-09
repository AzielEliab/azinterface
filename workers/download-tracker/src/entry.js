/**
 * Worker entry for azinterface-download-tracker. Wraps src/index.js (unchanged) to add,
 * at serve time and in new files only:
 *   GET /aznews, /newsmap   the AZNews + 4DMap human page (src/newsmap-page.js)
 *   GET /openapi.json       the spec from index.js plus the newsmap routes fragment
 *   GET /                   one link to /aznews added to the human page
 *   GET/POST /v1/tether/aznews, /v1/tether/4dmap, GET /v1/aznews/copy, /v1/4dmap/copy
 *                           AZInterface's own verified local copies (src/news-copy.js,
 *                           Durable Object LocalNewsCopy, SQLite; no KV or D1 writes)
 * The newsmap door (used by index.js) gets this host's copy reader, so AZNews reads answer
 * from the copy when the runtime is unreachable (standalone:true only when it re-verifies),
 * and GET /v1/map serves 4DMap from the 4DMap copy with no AZNews.
 * Everything else goes to index.js as before. Author: Aziel Eliab.
 */
import worker from "./index.js";
import { NEWSMAP_PAGE_PATHS, newsmapPageHtml } from "./newsmap-page.js";
import { LOOK_RULE, MAP_RULE, registerLocalCopy } from "./newsmap-door.js";
import { LocalNewsCopy, handleNewsCopyRoute, newsCopyCall, localMapRead, COPY_RULE } from "./news-copy.js";

export { LocalNewsCopy };
registerLocalCopy(async (env, op, payload) => (op === "map" ? localMapRead(env, payload) : (await newsCopyCall(env, { op, payload })).body));

const q = (name, description, schema = { type: "string" }) => ({ name, in: "query", required: false, description, schema });
const LOOK_PARAMS = [
  q("view", "1 = a real look by a page that shows the items (mints the view receipts). Otherwise the read is forwarded with dry_run and mints nothing."),
  q("dry_run", "1 = never mint, even with view=1."),
  q("limit", "Row cap.", { type: "integer" }),
];
const get = (operationId, summary, extra = []) => ({ get: { operationId, summary, parameters: [...extra, ...LOOK_PARAMS], responses: { "200": { description: "door answer: live/joined/merged from this door's own join check, runtime_claims apart" } } } });

export const NEWSMAP_OPENAPI = Object.freeze({
  "/v1/newsmap": get("azinterface_newsmap", "Joined AZNews + 4DMap status through FragGate (news_status). Flags are this door's own round-trip result (NEWSMAP-DOOR-JOIN-1.0); runtime_claims shows the runtime's."),
  "/v1/aznews": get("azinterface_aznews", "AZNews standalone (news_sources) through FragGate."),
  "/v1/map": { get: { operationId: "azinterface_map", summary: "4DMap on its own: map pins (corpus + reference layers) from AZInterface's own verified 4DMap copy. Needs no AZNews. ?layers=news adds AZNews pins; ?source=runtime|local. Mints nothing.", parameters: [q("layers", "corpus,reference,news"), q("source", "local or runtime"), q("limit", "Pin cap.", { type: "integer" })], responses: { "200": { description: "pins, last10, colors, layer_report, standalone, map_copy" } } } },
  "/v1/tether/aznews": {
    get: { operationId: "azinterface_news_copy_state", summary: "AZInterface's own AZNews copy: tip seq, signed tips, rows, from_genesis.", responses: { "200": { description: "copy state" } } },
    post: { operationId: "azinterface_news_copy_ingest", summary: "Signed AZRT-AZOS-NEWS-1.0 packet from aziel-runtime; checked (pinned Ed25519 key, every document hash, both lattice links from the stored tip) before anything is kept. Durable Object SQLite only.", responses: { "200": { description: "stored" }, "403": { description: "key or signature refused" }, "409": { description: "link, hash, chain or double refused" } } },
  },
  "/v1/tether/4dmap": {
    get: { operationId: "azinterface_map_copy_state", summary: "AZInterface's own 4DMap copy: tip seq, signed tips, rows, from_genesis.", responses: { "200": { description: "copy state" } } },
    post: { operationId: "azinterface_map_copy_ingest", summary: "Signed AZRT-MAP-COPY-1.0 packet from the runtime 4DMap store; same checks.", responses: { "200": { description: "stored" }, "403": { description: "key or signature refused" }, "409": { description: "link, hash or chain refused" } } },
  },
  "/v1/aznews/copy": { get: { operationId: "azinterface_news_copy_export", summary: "Verified AZNews copy rows after a seq.", parameters: [q("after", "seq", { type: "integer" }), q("limit", "max 500", { type: "integer" })], responses: { "200": { description: "rows" } } } },
  "/v1/4dmap/copy": { get: { operationId: "azinterface_map_copy_export", summary: "Verified 4DMap copy rows after a seq.", parameters: [q("after", "seq", { type: "integer" }), q("limit", "max 500", { type: "integer" })], responses: { "200": { description: "rows" } } } },
  "/v1/newsmap/feed": get("azinterface_newsmap_feed", "Newest stored real headlines (news_feed).", [q("outlet", "Outlet id.")]),
  "/v1/newsmap/sky": get("azinterface_newsmap_sky", "Computed sky (news_sky)."),
  "/v1/newsmap/weather": get("azinterface_newsmap_weather", "Open-Meteo weather (news_weather)."),
  "/v1/newsmap/pins": get("azinterface_newsmap_pins", "Colored pins, last 10, color key (news_pins).", [q("type", "pin_type"), q("era", "year", { type: "integer" })]),
  "/v1/newsmap/globe": get("azinterface_newsmap_globe", "One read for the globe (news_globe)."),
  "/v1/newsmap/verify": get("azinterface_newsmap_verify", "Runtime full lattice walk and join check (news_verify)."),
  "/v1/newsmap/receipts": get("azinterface_newsmap_receipts", "Newest pull and view receipts (news_receipts)."),
  "/v1/newsmap/{op}": {
    post: {
      operationId: "azinterface_newsmap_op",
      summary: "One AZNews or 4DMap op through FragGate. Body is the op payload; {\"view\": true} marks a real look, otherwise reads are dry_run.",
      parameters: [{ name: "op", in: "path", required: true, schema: { type: "string", enum: ["status", "pin", "open", "sources", "ingest", "weather", "plot", "library_pin", "lattice_tip", "feed", "item", "sky", "pins", "pin_open", "globe", "verify", "receipts"] } }],
      responses: { "200": { description: "door answer" }, "404": { description: "unknown op" } },
    },
  },
  "/aznews": { get: { operationId: "azinterface_aznews_page", summary: "AZNews + 4DMap human page, three views (?mode=combined|news|map): map with colored pins, headlines, weather, sky, last 10, color key, permalinks (?mode=&pin=). Reads through the newsmap door and this host's own verified copies.", responses: { "200": { description: "text/html" } } } },
  "/newsmap": { get: { operationId: "azinterface_newsmap_page", summary: "Alias of /aznews.", responses: { "200": { description: "text/html" } } } },
});

function runtimeOrigin(env) {
  const raw = env && (env.AZIEL_RUNTIME_ORIGIN || env.RUNTIME_ORIGIN);
  return raw ? String(raw).replace(/\/+$/, "") : "https://aziel-runtime.vibelock.workers.dev";
}

class AddNewsLink {
  element(e) {
    e.prepend('<p style="margin:6px 0;font:14px system-ui"><a href="/aznews">AZNews + 4DMap</a>: headlines, weather, sky and colored map pins, read through the newsmap door.</p>', { html: true });
  }
}

export default {
  ...worker,
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    if (NEWSMAP_PAGE_PATHS.includes(path) && (request.method === "GET" || request.method === "HEAD")) {
      const headers = { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "public, max-age=60", "X-Look-Rule": "page JS reads /v1/newsmap/globe?view=1 once" };
      return new Response(request.method === "HEAD" ? null : newsmapPageHtml(runtimeOrigin(env), url.searchParams.get("mode") || "combined"), { status: 200, headers });
    }
    const copy = await handleNewsCopyRoute(request, url, env);
    if (copy) return new Response(JSON.stringify(copy.body), { status: copy.status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" } });
    const res = await worker.fetch(request, env, ctx);
    if (path === "/openapi.json" && request.method === "GET" && res.status === 200) {
      try {
        const spec = await res.clone().json();
        spec.paths = { ...(spec.paths || {}), ...NEWSMAP_OPENAPI };
        spec["x-newsmap-look-rule"] = LOOK_RULE;
        spec["x-newsmap-map-rule"] = MAP_RULE;
        spec["x-local-copy-rule"] = COPY_RULE.replace(/AZ-OS/g, "AZInterface");
        const headers = new Headers(res.headers);
        headers.delete("content-length");
        return new Response(JSON.stringify(spec, null, 2), { status: 200, headers });
      } catch {
        return res;
      }
    }
    if (path === "/" && request.method === "GET" && res.status === 200 && typeof HTMLRewriter === "function" && String(res.headers.get("content-type") || "").includes("text/html")) {
      return new HTMLRewriter().on("body", new AddNewsLink()).transform(res);
    }
    return res;
  },
};
