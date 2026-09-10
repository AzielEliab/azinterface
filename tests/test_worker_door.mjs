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
assert.deepEqual(classifyV1Path("/v1/mesh"), {
  kind: "door",
  path: "/v1/mesh",
  originPath: "/v1/mesh",
});
assert.deepEqual(classifyV1Path("/v1/azpipe/arch"), {
  kind: "door",
  path: "/v1/azpipe/arch",
  originPath: "/v1/azpipe/arch",
});
assert.deepEqual(classifyV1Path("/v1/pipeline_arch"), {
  kind: "local",
  path: "/v1/pipeline_arch",
  op: "pipeline_arch",
});
assert.deepEqual(classifyV1Path("/v1/mesh/status"), {
  kind: "door",
  path: "/v1/mesh/status",
  originPath: "/v1/mesh/status",
});
assert.equal(localOpFromPath("/v1/mesh"), null);
assert.equal(
  doorTargetUrl("/v1/mesh/nodes", "https://azinterface-download-tracker.vibelock.workers.dev/v1/mesh/nodes"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/mesh/nodes",
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

  fetches.length = 0;
  const meshReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/mesh/status", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const meshRes = await handleRuntimeApi(meshReq, new URL(meshReq.url), {});
  const meshBody = await meshRes.json();
  assert.equal(meshBody.ok, true);
  assert.equal(meshRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/mesh/status" && f.method === "GET"));

  fetches.length = 0;
  const boundCalls = [];
  const meshBoundReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/mesh/nodes", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const meshBoundRes = await handleRuntimeApi(meshBoundReq, new URL(meshBoundReq.url), {
    AZIEL_RUNTIME: {
      fetch: async (input, init) => {
        const url = typeof input === "string" ? input : input.url;
        boundCalls.push({ url, method: (init && init.method) || "GET" });
        return new Response(JSON.stringify({ ok: true, enabled: false, live_nodes: 0, via: "binding" }), {
          status: 200,
          headers: { "content-type": "application/json; charset=utf-8" },
        });
      },
    },
  });
  const meshBoundBody = await meshBoundRes.json();
  assert.equal(meshBoundBody.via, "binding");
  assert.equal(fetches.length, 0, "AZIEL_RUNTIME binding must win over HTTPS fallback");
  assert.ok(boundCalls.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/mesh/nodes"));

  fetches.length = 0;
  const azpipeReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/azpipe/arch", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const azpipeRes = await handleRuntimeApi(azpipeReq, new URL(azpipeReq.url), {});
  const azpipeBody = await azpipeRes.json();
  assert.equal(azpipeBody.ok, true);
  assert.equal(azpipeRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/azpipe/arch" && f.method === "GET"));

  const specReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/openapi.json", { method: "GET" });
  const specRes = await handleRuntimeApi(specReq, new URL(specReq.url), {});
  const spec = await specRes.json();
  assert.ok(spec.paths["/v1/mesh"]);
  assert.ok(spec.paths["/v1/mesh/nodes"]);
  assert.ok(spec.paths["/v1/mesh/broadcast"]);
  assert.match(spec.info.description, /\/v1\/mesh/);
  assert.match(spec.info.description, /QNM-BUILD-1.0/);
  assert.match(spec.info.description, /QNS-CD-1.0/);
  assert.match(spec.info.description, /qnm-node/);
  assert.ok(spec.paths["/v1/pair_offer"]);
  assert.ok(spec.paths["/v1/pair_status"]);
  assert.ok(spec.paths["/v1/pipeline_arch"]);
  assert.ok(spec.paths["/v1/azpipe/arch"]);
  assert.match(spec.info.description, /LOCKED suite pipeline/);
  assert.match(spec.info.description, /4DMap/);

  const mcpReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/mcp", { method: "GET" });
  const mcpRes = await handleRuntimeApi(mcpReq, new URL(mcpReq.url), {});
  const mcp = await mcpRes.json();
  assert.equal(mcp.mesh.path, "/v1/mesh");
  assert.equal(mcp.mesh.enabled_default, false);
  assert.equal(mcp.mesh.node_gate, false);
  assert.equal(mcp.mesh.auto_heal, false);
  assert.equal(mcp.mesh.anonymity, false);
  assert.equal(mcp.mesh.spec, "QNM-BUILD-1.0");
  assert.equal(mcp.mesh.qns_cd, "QNS-CD-1.0");
  assert.equal(mcp.mesh.get_enables, false);
  assert.equal(mcp.qns.softwares_tab_qns, false);
  assert.equal(mcp.qns.via_runs_in, "qnsd");
  assert.equal(mcp.pipeline.owner, "aziel-runtime");
  assert.equal(mcp.pipeline.lambgate, false);
  assert.equal(mcp.pipeline.domain_doors.slug, "4dmap");
  assert.match(mcp.mesh.spiderweb, /qnm-node/);
  assert.match(mcp.mesh.anon_broadcast, /not a publish path/);
  assert.match(mcp.note, /mesh/);
  assert.match(mcp.note, /pipeline_arch/);

  const llmsReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/llms.txt", { method: "GET" });
  const llmsRes = await handleRuntimeApi(llmsReq, new URL(llmsReq.url), {});
  const llms = await llmsRes.text();
  assert.match(llms, /\/v1\/mesh/);
  assert.match(llms, /not a public Node Gate/);

  for (const path of ["/count", "/stats", "/download", "/"]) {
    const req = new Request("https://azinterface-download-tracker.vibelock.workers.dev" + path, { method: "GET" });
    const res = await handleRuntimeApi(req, new URL(req.url), {});
    assert.equal(res, null, path + " must stay on the download tracker, not the runtime router");
  }
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker door proxy smoke ok");
