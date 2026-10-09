/**
 * AZInterface AZNews + 4DMap page (/aznews, /newsmap), served by src/entry.js in new
 * files only; openapi gains the newsmap routes at serve time; "/" gets one link.
 * The page reads only through the newsmap door: one look (?view=1) and one dry read.
 */
import assert from "node:assert/strict";
import entry, { NEWSMAP_OPENAPI } from "../workers/download-tracker/src/entry.js";
import { newsmapPageHtml } from "../workers/download-tracker/src/newsmap-page.js";

const env = { AZIEL_RUNTIME: { fetch: async () => new Response(JSON.stringify({ ok: true, result: { ok: true } })) } };
for (const p of ["/aznews", "/newsmap", "/aznews/"]) {
  const res = await entry.fetch(new Request("https://h.example" + p), env, {});
  assert.equal(res.status, 200, p);
  assert.match(res.headers.get("content-type"), /text\/html/);
  const html = await res.text();
  for (const needle of ['id="map"', 'class="land"', 'id="key"', 'id="last"', 'id="news"', 'id="sky"', 'id="weather"', "?pin=", "/v1/newsmap/globe?view=1", '"/v1/newsmap"', "Natural Earth"]) {
    assert.ok(html.includes(needle), p + " has " + needle);
  }
  assert.ok(!html.includes("__LAND__") && !html.includes("__RTORIGIN__") && !html.includes("__GLOBE__"));
  // The page script parses.
  const js = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
  new Function(js);
}
assert.ok(newsmapPageHtml("https://rt.example").includes("https://rt.example/aznews"));

const spec = await (await entry.fetch(new Request("https://h.example/openapi.json"), env, {})).json();
for (const p of Object.keys(NEWSMAP_OPENAPI)) assert.ok(spec.paths[p], "openapi has " + p);
assert.ok(spec.paths["/v1/health"] || Object.keys(spec.paths).length > Object.keys(NEWSMAP_OPENAPI).length, "index.js paths kept");
assert.match(spec["x-newsmap-look-rule"], /view=1/);
const enumOps = spec.paths["/v1/newsmap/{op}"].post.parameters[0].schema.enum;
for (const op of ["feed", "pins", "globe", "pin_open", "item", "weather"]) assert.ok(enumOps.includes(op));

const other = await entry.fetch(new Request("https://h.example/v1/health"), env, {});
assert.equal(other.status, 200, "other routes still served by index.js");
console.log("NEWSMAP-PAGE-OK");
