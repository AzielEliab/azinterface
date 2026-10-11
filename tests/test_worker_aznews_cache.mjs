/** AZNEWS-JOIN-CACHE-1.0: derived join flags reused briefly (labelled), failing closed. */
import assert from "node:assert/strict";
import { deriveJoinFlagsCached, clearJoinCache, JOIN_CACHE_LIVE_MS, JOIN_CACHE_FAIL_MS, handleNewsmap } from "../workers/download-tracker/src/newsmap-door.js";
const claims = { live: true, joined: true, merged: true, lattice_live: true };
let calls = 0;
const binding = (state) => ({
  fetch: async (req) => {
    calls++;
    if (state.down) throw new Error("down");
    const { op } = await req.json();
    let result;
    if (op === "news_status") result = { ok: true, op, outlets_live: 37, ...claims };
    else if (op === "news_pin") result = { ok: true, item: { item_id: "i1" }, pins: [{ pin_id: "p1" }], pull_receipt_seq: 9 };
    else if (op === "news_open") result = { ok: true, linked: true, item: { item_id: "i1" } };
    else result = { ok: true, op };
    return new Response(JSON.stringify({ ok: true, code: "FG-OK", result }), { status: 200 });
  },
});
const view = () => ({ path: "/v1/aznews", live: false, joined: false, merged: false, lattice_live: false });
let n = 0;
const st = { down: false };
const env = { AZIEL_RUNTIME: binding(st) };
const call = undefined;
clearJoinCache();
const t0 = 1_000_000;
let v = await deriveJoinFlagsCached(view(), env, "azinterface", call, t0);
const first = calls;
assert.equal(v.live, true); assert.equal(v.join_cached, false); assert.ok(first > 0); n++;
// Within TTL: no runtime calls, labelled cached.
v = await deriveJoinFlagsCached(view(), env, "azinterface", call, t0 + 5_000);
assert.equal(calls, first); assert.equal(v.live, true); assert.equal(v.join_cached, true); assert.equal(v.join_cache_age_s, 5); n++;
// After TTL with runtime down: re-derives and fails closed.
st.down = true;
v = await deriveJoinFlagsCached(view(), env, "azinterface", call, t0 + JOIN_CACHE_LIVE_MS + 1);
assert.equal(v.live, false); assert.equal(v.joined, false); assert.equal(v.join_cached, false); n++;
// Failure is reused only briefly, then re-checked.
const c1 = calls;
v = await deriveJoinFlagsCached(view(), env, "azinterface", call, t0 + JOIN_CACHE_LIVE_MS + 2_000);
assert.equal(calls, c1); assert.equal(v.live, false); assert.equal(v.join_cached, true); n++;
st.down = false;
v = await deriveJoinFlagsCached(view(), env, "azinterface", call, t0 + JOIN_CACHE_LIVE_MS + JOIN_CACHE_FAIL_MS + 2);
assert.ok(calls > c1); assert.equal(v.live, true); n++;
// Different runtime binding never shares an entry.
const st2 = { down: true };
const other = { AZIEL_RUNTIME: binding(st2) };
v = await deriveJoinFlagsCached(view(), other, "azinterface", undefined, t0 + JOIN_CACHE_LIVE_MS + JOIN_CACHE_FAIL_MS + 3);
assert.equal(v.live, false); n++;
console.log(`ok aznews join cache: ${n} checks`);
// Plain text carries the cache age when the flags come from the cache.
{
  clearJoinCache();
  const st3 = { down: false };
  const env3 = { AZIEL_RUNTIME: binding(st3) };
  const fresh = await deriveJoinFlagsCached(view(), env3, "azinterface", undefined, 5_000_000);
  assert.doesNotMatch(fresh.plain, /reused from this door's short cache/);
  const cached = await deriveJoinFlagsCached(view(), env3, "azinterface", undefined, 5_000_000 + 12_000);
  assert.equal(cached.join_cached, true);
  assert.match(cached.plain, /derived 12 s ago and reused from this door's short cache/);
  console.log("ok aznews plain text carries cache age");
}
