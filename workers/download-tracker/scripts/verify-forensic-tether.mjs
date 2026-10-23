/**
 * AZBot Node Collaborative Forensic Design 1.0 — public cite stays off the door.
 */
import assert from "node:assert/strict";
import { classifyV1Path } from "../src/door.js";
import { custodyCycle, resetEngine } from "../src/engine.js";
import { handleForensicRoute, nameOnly } from "../src/forensic-tether.js";

let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; };
const TOKEN = "operator-token-9f3a";

ok(nameOnly("cap-7") && nameOnly("ICANN") && nameOnly("a.aziel") && !nameOnly("127.0.0.1"), "Cap-7 names only");
ok(classifyV1Path("/v1/forensic/tip").kind === "multi", "forensic tip is not a FragGate door prefix");
ok(classifyV1Path("/v1/azieltether").kind === "local" && classifyV1Path("/v1/fraggate/call").kind === "door", "azieltether cite is not the door");

resetEngine();
const before = custodyCycle();
ok(before.current === "OFF" && before.living_presence === false && before.cloud_asleep === false, "public cycle stays OFF");

const call = (path, init = {}) => handleForensicRoute(new Request("https://leg.example" + path, init));
let res = await call("/v1/forensic/tip");
let body = await res.json();
ok(res.status === 200 && body.stored_here === false && body.sessions.length === 0 && body.share_tips_only === true && body.rewrite === false, "public tip read stores nothing");
ok(body.second_door === false && body.door === "fraggate" && body.mesh_enabled === false && body.remain_off.mesh_auto_enable === false, "remain-off and single door");

res = await call("/v1/forensic/session", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ session_id: "node-a", tip: "a".repeat(64) }) });
body = await res.json();
ok(res.status === 403 && body.code === "LOCAL-DESK-ONLY" && body.written === false && body.stored_here === false, "public append refused");

res = await call("/v1/forensic/handoff");
body = await res.json();
ok(body.code === "LOCAL-DESK-ONLY" && body.executed === false && body.package === null && body.bind === "127.0.0.1" && body.skip_forbidden === true, "public handoff is a cite");
ok(body.cycles.join("|") === "OFF|integrity|ON|FULL SHUTDOWN|MEMORIAL", "sealed cycles");

res = await call("/v1/forensic/handoff", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ host: "cap-7", slug: "azinterface", op: "health" }) });
body = await res.json();
ok(body.code === "MG-NO-IP-EXIT" && body.icann === false && body.executed === false, "Cap-7 is not an exit");

res = await call("/v1/azieltether");
body = await res.json();
ok(res.status === 401 && body.code === "MESH-NEED-BEARER" && body.exposed === false && body.radios_enabled === false, "bearer required");

res = await call("/v1/azieltether", { headers: { authorization: `Bearer ${TOKEN}` } });
body = await res.json();
ok(res.status === 200 && body.exposed === true && body.bearer === "present" && body.tether.slug === "azieltether" && body.tether.door === "fraggate" && body.tether.second_door === false, "AzielTether cite under bearer");
ok(!JSON.stringify(body).includes(TOKEN) && body.mesh_enabled === false, "bearer is not returned and radios stay off");

res = await call("/v1/azieltether", { method: "POST", headers: { authorization: "Bearer cap-7", "content-type": "application/json" }, body: "{}" });
body = await res.json();
ok(body.code === "MG-NO-IP-EXIT" && body.exposed === false, "Cap-7 bearer is a name");

const after = custodyCycle();
ok(after.current === "OFF" && after.living_presence === false, "cite did not advance the page cycle");

globalThis.fetch = async () => { throw new Error("network off"); };
const worker = (await import("../src/entry.js")).default;
const live = await worker.fetch(new Request("https://leg.example/v1/forensic/tip"), {}, { waitUntil() {} });
const liveBody = await live.json();
ok(live.status === 200 && liveBody.code === "FORENSIC-TIP" && liveBody.stored_here === false, "entry serves the cite before the door proxy");
const denied = await worker.fetch(new Request("https://leg.example/v1/forensic/session", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }), {}, { waitUntil() {} });
const deniedBody = await denied.json();
ok(denied.status === 403 && deniedBody.code === "LOCAL-DESK-ONLY", "entry refuses public append without a runtime call");
const tether = await worker.fetch(new Request("https://leg.example/v1/azieltether", { headers: { authorization: `Bearer ${TOKEN}` } }), {}, { waitUntil() {} });
const tetherBody = await tether.json();
ok(tether.status === 200 && tetherBody.code === "AZIELTETHER-CITE" && tetherBody.second_door === false && !JSON.stringify(tetherBody).includes(TOKEN), "entry exposes AzielTether under bearer");

console.log(`verify-forensic-tether: ${n} checks ok`);
