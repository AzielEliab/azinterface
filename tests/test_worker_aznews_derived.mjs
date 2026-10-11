/** AZNEWS-LIVE-DERIVED-1.0: /v1/aznews flags come from runtime news_status + the door join check, fail closed. */
import assert from "node:assert/strict";
import { handleNewsmap } from "../workers/download-tracker/src/newsmap-door.js";

const claims = { live: true, joined: true, merged: true, lattice_live: true };
function rt({ status = claims, pinOk = true, linked = true, down = false } = {}) {
  return {
    fetch: async (req) => {
      if (down) throw new Error("down");
      const { op } = await req.json();
      let result;
      if (op === "news_sources") result = { ok: true, op, outlets_live: 37 };
      else if (op === "news_status") result = { ok: true, op, outlets_live: 37, ...status };
      else if (op === "news_pin") result = pinOk ? { ok: true, item: { item_id: "i1" }, pins: [{ pin_id: "p1" }], pull_receipt_seq: 9 } : { ok: false, code: "NO-ITEM" };
      else if (op === "news_open") result = { ok: true, linked, item: { item_id: "i1" } };
      else result = { ok: true, op };
      return new Response(JSON.stringify({ ok: true, code: "FG-OK", result }), { status: 200 });
    },
  };
}
const go = (env) => handleNewsmap(new Request("https://h.example/v1/aznews"), new URL("https://h.example/v1/aznews"), env, "azinterface");
let n = 0;

// 1. Runtime verified + door round trip passes -> live/joined true (derived).
let out = await go({ AZIEL_RUNTIME: rt() });
assert.equal(out.body.live, true); assert.equal(out.body.joined, true); assert.equal(out.body.lattice_live, true);
assert.equal(out.body.door_join_check.ok, true);
assert.match(out.body.flags_from, /derived/);
assert.equal(out.body.installed, false); n++;

// 2. Runtime does not claim the join -> false.
out = await go({ AZIEL_RUNTIME: rt({ status: { live: false, joined: false, lattice_live: false } }) });
assert.equal(out.body.live, false); assert.equal(out.body.joined, false); n++;

// 3. Runtime claims, but door round trip fails -> false.
out = await go({ AZIEL_RUNTIME: rt({ pinOk: false }) });
assert.equal(out.body.live, false); assert.equal(out.body.joined, false);
assert.match(out.body.join_reason, /door round trip failed/); n++;

// 4. Pin does not link back -> false.
out = await go({ AZIEL_RUNTIME: rt({ linked: false }) });
assert.equal(out.body.joined, false); n++;

// 5. Runtime claims joined but lattice not live -> not live.
out = await go({ AZIEL_RUNTIME: rt({ status: { live: true, joined: true, lattice_live: false } }) });
assert.equal(out.body.live, false); n++;

// 6. Runtime unreachable -> never live.
out = await go({ AZIEL_RUNTIME: rt({ down: true }) });
assert.notEqual(out.body.live, true); assert.notEqual(out.body.joined, true); n++;

console.log(`test_worker_aznews_derived: ${n} passed`);
