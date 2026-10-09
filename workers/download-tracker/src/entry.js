/**
 * Worker entry for azinterface-download-tracker. Wraps src/index.js (unchanged) to add,
 * at serve time and in new files only:
 *   GET /aznews, /newsmap   the AZNews + 4DMap human page (src/newsmap-page.js)
 *   GET /openapi.json       the spec from index.js plus the newsmap routes fragment
 *   GET /                   one link to /aznews added to the human page
 * Everything else goes to index.js as before. Author: Aziel Eliab.
 */
import worker from "./index.js";
import { NEWSMAP_PAGE_PATHS, newsmapPageHtml } from "./newsmap-page.js";
import { LOOK_RULE } from "./newsmap-door.js";

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
  "/v1/map": get("azinterface_map", "4DMap standalone (plot) through FragGate."),
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
  "/aznews": { get: { operationId: "azinterface_aznews_page", summary: "AZNews + 4DMap human page: map with colored pins, headlines, weather, sky, last 10, color key, permalinks (?pin=). Reads through the newsmap door.", responses: { "200": { description: "text/html" } } } },
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
      return new Response(request.method === "HEAD" ? null : newsmapPageHtml(runtimeOrigin(env)), { status: 200, headers });
    }
    const res = await worker.fetch(request, env, ctx);
    if (path === "/openapi.json" && request.method === "GET" && res.status === 200) {
      try {
        const spec = await res.clone().json();
        spec.paths = { ...(spec.paths || {}), ...NEWSMAP_OPENAPI };
        spec["x-newsmap-look-rule"] = LOOK_RULE;
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
