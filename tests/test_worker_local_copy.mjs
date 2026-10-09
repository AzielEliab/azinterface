/**
 * AZInterface's own verified local copies (same files as AZ-OS: news-copy.js, newsmap-door.js):
 * signed packets in through /v1/tether/{aznews,4dmap}, checked from genesis; with the runtime
 * unreachable, AZNews reads answer from the copy with standalone:true and GET /v1/map serves
 * 4DMap with no AZNews. Tamper tests. Driven through the Worker entry. No network.
 */
import assert from "node:assert/strict";
import entry, { LocalNewsCopy } from "../workers/download-tracker/src/entry.js";
import { canonicalize, sha256Hex, primaryOf, onlineSecondaryOf, GENESIS } from "../workers/download-tracker/src/tether.js";
import { memCopyRepo, MAP_TETHER_SPEC, MAP_TETHER_KIND, NEWS_TETHER_SPEC, NEWS_TETHER_KIND } from "../workers/download-tracker/src/news-copy.js";

const b64u = (bytes) => Buffer.from(bytes).toString("base64url");
const pair = await crypto.subtle.generateKey({ name: "Ed25519" }, true, ["sign", "verify"]);
const pub = b64u(new Uint8Array(await crypto.subtle.exportKey("raw", pair.publicKey)));
const other = await crypto.subtle.generateKey({ name: "Ed25519" }, true, ["sign", "verify"]);
async function sign(packet, priv = pair.privateKey) {
  const { sig: _s, ...unsigned } = packet;
  return { ...packet, sig: b64u(new Uint8Array(await crypto.subtle.sign("Ed25519", priv, new TextEncoder().encode(canonicalize(unsigned))))) };
}
function ledger() {
  const rows = [];
  let tip = { primary: GENESIS, secondary: GENESIS };
  return { rows, async add(kind, doc) {
    const document_hash = await sha256Hex(canonicalize(doc));
    const primary = await primaryOf(document_hash, tip.primary);
    const secondary = await onlineSecondaryOf(primary, tip.secondary);
    rows.push({ seq: rows.length + 1, kind, at: new Date(Date.UTC(2026, 9, 9, 8, rows.length)).toISOString(), doc, lattice: { document_hash, primary, primary_prev: tip.primary, secondary, secondary_prev: tip.secondary, offline: false, username: null } });
    tip = { primary, secondary };
  } };
}
const news = ledger();
for (let i = 0; i < 3; i++) {
  await news.add("news", { item_id: "n-" + i, title: "Storm in Manila " + i, outlet: { id: "x", name: "X" }, link: "https://example.org/" + i });
  const item = news.rows.length;
  const h = news.rows[item - 1].lattice.document_hash;
  await news.add("pin", { pin_type: "news-report", color: "blue", color_hex: "#1e88e5", role: "report", event: "Storm " + i, geo: { name: "Manila", lat: 14.6, lon: 121 }, report_seq: item, report_document_hash: h, pull_receipt_seq: item + 2 });
  await news.add("pull_receipt", { report_seq: item, document_hash: h });
}
await news.add("sky", { moon: { phase_name: "waning crescent", illuminated_percent: 2.2 } });
await news.add("weather", { anchor: { id: "manila", name: "Manila" }, reading: { temperature_c: 30 } });
const map = ledger();
await map.add("map_pin", { kind: "4dmap-pin", layer: "reference", pin_type: "reference-capital", color: "grey", color_hex: "#9e9e9e", event: "Manila, capital of Philippines", geo: { name: "Manila", lat: 14.6, lon: 121 }, source_id: "ref:capital:PH" });
await map.add("map_pin", { kind: "4dmap-pin", layer: "corpus", pin_type: "library-aziel-event", color: "purple", color_hex: "#8e24aa", event: "1101 event", date: "1101", geo: { name: "coord", lat: 1, lon: 2 }, source_id: "corpus:AZEVT-1", source: { event_id: "AZEVT-1" } });
const packet = (l, chain, from, to) => {
  const rows = l.rows.slice(from, to);
  const last = rows[rows.length - 1];
  const sk = chain === "4dmap" ? { spec: MAP_TETHER_SPEC, kind: MAP_TETHER_KIND } : { spec: NEWS_TETHER_SPEC, kind: NEWS_TETHER_KIND };
  return sign({ ...sk, chain, after_seq: from, rows, tips: { primary: last.lattice.primary, secondary: last.lattice.secondary, seq: last.seq }, public_key: pub });
};

// Fake Durable Object namespace running the real LocalNewsCopy class over in-memory repos.
const objects = {};
const baseEnv = { COPY_HOST: "azinterface", RUNTIME_TETHER_PUBKEY: pub };
const LOCAL_NEWS_COPY = { getByName(name) { if (!objects[name]) { const o = new LocalNewsCopy({}, baseEnv); o.repo = memCopyRepo(); objects[name] = o; } return objects[name]; } };
let rtCalls = 0;
const down = { ...baseEnv, LOCAL_NEWS_COPY, AZIEL_RUNTIME: { fetch: async () => { rtCalls += 1; throw new Error("runtime unreachable"); } } };
const call = async (path, init, env = down) => { const r = await entry.fetch(new Request("https://azi.example" + path, init), env, { waitUntil() {} }); return { status: r.status, body: await r.json() }; };
const post = (body) => ({ method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });

// Empty copies: NEWSMAP-NO-LOCAL-COPY is gone; the copy says it is empty, standalone false.
let o = await call("/v1/newsmap/feed?source=local");
assert.notEqual(o.body.code, "NEWSMAP-NO-LOCAL-COPY");
assert.equal(o.body.standalone, false);
o = await call("/v1/map");
assert.equal(o.status, 503, "empty 4DMap copy and runtime down: refused, nothing invented");

// Ingest refusals and good packets through the public routes.
o = await call("/v1/tether/aznews", post(await sign({ ...(await packet(news, "aznews", 0, 5)), sig: undefined }, other.privateKey)));
assert.equal(o.status, 403);
assert.equal(o.body.code, "NEWS-COPY-SIG");
o = await call("/v1/tether/4dmap", post(await packet(news, "aznews", 0, 5)));
assert.equal(o.body.code, "NEWS-COPY-SPEC", "an AZNews packet is refused on the 4DMap route");
o = await call("/v1/tether/aznews", post(await packet(news, "aznews", 0, 5)));
assert.equal(o.body.stored, true);
o = await call("/v1/tether/aznews", post(await packet(news, "aznews", 5, news.rows.length)));
assert.equal(o.body.tip_seq, news.rows.length);
o = await call("/v1/tether/4dmap", post(await packet(map, "4dmap", 0, 2)));
assert.equal(o.body.stored, true);
o = await call("/v1/tether/aznews");
assert.equal(o.body.host, "azinterface");
assert.equal(o.body.tip_seq, news.rows.length);
assert.equal(o.body.from_genesis, true);
assert.equal(o.body.kv_writes, false);
assert.equal((await call("/v1/tether/4dmap")).body.chain, "4dmap");

// Runtime unreachable: served from AZInterface's own copy, standalone:true.
rtCalls = 0;
for (const p of ["/v1/newsmap", "/v1/newsmap/globe?view=1", "/v1/newsmap/feed", "/v1/newsmap/pins", "/v1/aznews"]) {
  o = await call(p);
  assert.equal(o.status, 200, p);
  assert.equal(o.body.standalone, true, p);
  assert.equal(o.body.source, "azinterface-local-copy", p);
  assert.equal(o.body.served_because, "the runtime was unreachable", p);
  assert.equal(o.body.live, false, p);
  assert.match(o.body.door, /AZInterface own verified copy/);
}
assert.ok(rtCalls > 0, "the runtime was tried first");
o = await call("/v1/newsmap/globe?view=1");
assert.equal(o.body.items.length, 3);
assert.equal(o.body.joined, true, "the copy's own join check");
// 4DMap alone, and with the news layer.
rtCalls = 0;
o = await call("/v1/map");
assert.equal(o.body.standalone, true);
assert.equal(o.body.source, "azinterface-local-copy");
assert.equal(o.body.pins.length, 2);
assert.equal(o.body.needs_aznews, false);
assert.equal(rtCalls, 0);
o = await call("/v1/map?layers=corpus,reference,news");
assert.equal(o.body.pins.filter((p) => p.layer === "news").length, 3);
// Tamper in storage: AZNews read is not standalone; 4DMap copy is not served.
const nrow = await objects["azos-news-copy-v1"].repo.get(2);
nrow.doc.event = "edited";
o = await call("/v1/newsmap/globe?view=1");
assert.equal(o.body.standalone, false);
assert.match(o.body.copy_verify.reason, /document hash/);
nrow.doc.event = "Storm 0";
const mrow = await objects["azos-4dmap-copy-v1"].repo.get(2);
mrow.doc.geo.lat = 50;
o = await call("/v1/map");
assert.equal(o.status, 503);
assert.equal(o.body.local_copy.code, "NEWS-COPY-VERIFY-FAILED");
mrow.doc.geo.lat = 1;
assert.equal((await call("/v1/map")).body.standalone, true);

// Page: three views.
const html = await (await entry.fetch(new Request("https://azi.example/aznews?mode=map"), down, {})).text();
for (const n of ['data-mode="combined"', 'data-mode="news"', 'data-mode="map"', "/v1/map?layers=corpus,reference", "standalone"]) assert.ok(html.includes(n), n);
assert.ok(html.includes('id="news" class="panel muted">Headlines hidden in map-only view.'), "map-only view says the headlines are hidden, in the served HTML");
assert.ok(!html.includes('id="news" class="panel muted">Loading'), "map-only view never shows Loading for headlines");
const combined = await (await entry.fetch(new Request("https://azi.example/aznews"), down, {})).text();
assert.ok(combined.includes('id="news" class="panel muted">Loading'));
// Retracted 4DMap pins are hidden by default through the door, listed with ?include_retracted=1.
await map.add("map_pin", { kind: "4dmap-pin", layer: "corpus", pin_type: "library-aziel-event", color: "purple", color_hex: "#8e24aa", event: "1101 event", date: "1101", geo: { name: "coord", lat: 1, lon: 2 }, source_id: "corpus:AZEVT-1", source: { event_id: "AZEVT-1" }, supersedes_seq: 2, retracted: "geoparser_junk", retract_reason: "bare coordinate pair" });
assert.equal((await call("/v1/tether/4dmap", post(await packet(map, "4dmap", 2, 3)))).body.stored, true);
o = await call("/v1/map");
assert.equal(o.body.pins.length, 1);
assert.equal(o.body.retracted.count, 1);
assert.equal(o.body.standalone, true);
o = await call("/v1/map?include_retracted=1");
assert.equal(o.body.pins.find((p) => p.source_id === "corpus:AZEVT-1").retracted, "geoparser_junk");
const spec = await (await entry.fetch(new Request("https://azi.example/openapi.json"), down, {})).json();
for (const p of ["/v1/map", "/v1/tether/aznews", "/v1/tether/4dmap", "/v1/aznews/copy", "/v1/4dmap/copy"]) assert.ok(spec.paths[p], p);
assert.match(spec["x-local-copy-rule"], /AZInterface/);
console.log("AZINTERFACE-LOCAL-COPY-OK");
