/**
 * Prove FragGate / runtime door paths are proxied — never local ops.
 */
import assert from "node:assert/strict";
import {
  classifyV1Path,
  DEFAULT_RUNTIME_ORIGIN,
  doorTargetUrl,
  localOpFromPath,
  mapDoorPath,
} from "../workers/download-tracker/src/door.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { dispatch, resetEngine } from "../workers/download-tracker/src/engine.js";

assert.deepEqual(classifyV1Path("/v1/fraggate/call"), {
  kind: "door",
  path: "/v1/fraggate/call",
  originPath: "/v1/fraggate/call",
});
assert.deepEqual(classifyV1Path("/v1/runtime/list"), {
  kind: "door",
  path: "/v1/runtime/list",
  originPath: "/v1/fraggate/list",
});
assert.deepEqual(classifyV1Path("/v1/page_cycle_status"), {
  kind: "local",
  path: "/v1/page_cycle_status",
  op: "page_cycle_status",
});
assert.equal(localOpFromPath("/v1/fraggate/call"), null);
assert.equal(localOpFromPath("/v1/integrity_check"), "integrity_check");
assert.equal(mapDoorPath("/v1/runtime/call"), "/v1/fraggate/call");
assert.equal(
  doorTargetUrl("/v1/fraggate/call", "https://azinterface-download-tracker.vibelock.workers.dev/v1/fraggate/call"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call",
);

const engineRefuse = await dispatch("fraggate/call", {});
assert.equal(engineRefuse.code, "FG-HALLUC-TOOL");

const fetches = [];
const previousFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input.url;
  fetches.push({ url, method: (init && init.method) || (input && input.method) || "GET" });
  return new Response(JSON.stringify({ ok: true, door: "fraggate", proxied: true, origin: url }), {
    status: 200,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
};

try {
  resetEngine();
  const callReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/fraggate/call", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "azinterface", op: "health", payload: {} }),
  });
  const callRes = await handleRuntimeApi(callReq, new URL(callReq.url), {});
  const callBody = await callRes.json();
  assert.notEqual(callBody.code, "FG-HALLUC-TOOL");
  assert.equal(callBody.ok, true);
  assert.equal(callRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call" && f.method === "POST"));

  const localReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/page_cycle_status", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: "{}",
  });
  const localRes = await handleRuntimeApi(localReq, new URL(localReq.url), {});
  const localBody = await localRes.json();
  assert.equal(localBody.ok, true);
  assert.equal(localBody.living_presence, false);
  assert.equal(localBody.product, "azinterface");

  const healthReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/health", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const healthRes = await handleRuntimeApi(healthReq, new URL(healthReq.url), {});
  const healthBody = await healthRes.json();
  assert.equal(healthBody.ok, true);
  assert.equal(healthBody.product, "azinterface");
  assert.equal(healthBody.hub_collapse, false);

  for (const path of ["/count", "/stats", "/download", "/"]) {
    const req = new Request("https://azinterface-download-tracker.vibelock.workers.dev" + path, { method: "GET" });
    const res = await handleRuntimeApi(req, new URL(req.url), {});
    assert.equal(res, null, path + " must stay on the download tracker, not the runtime router");
  }
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker door proxy smoke ok");
