/**
 * Worker MASTER-ARCHITECTURE-2.0 pipeline cite + homepage strip.
 */
import assert from "node:assert/strict";
import { dispatch, LIVE_OPS, resetEngine } from "../workers/download-tracker/src/engine.js";
import { DOMAIN_MAP, PIPELINE_PATH, domainSlugs, pipelineArch, pipelineStripHtml, domainMapHtml } from "../workers/download-tracker/src/pipeline.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { classifyV1Path, DEFAULT_RUNTIME_ORIGIN, RUNTIME_ARCH_PATH } from "../workers/download-tracker/src/door.js";

resetEngine();

assert.ok(LIVE_OPS.includes("pipeline_arch"));
const pipe = pipelineArch();
assert.equal(pipe.locked, true);
assert.equal(pipe.lambgate, false);
assert.equal(pipe.second_door, false);
assert.equal(pipe.owner, "aziel-runtime");
assert.equal(pipe.identity, "Aziel Eliab");
assert.equal(pipe.path, PIPELINE_PATH);
assert.equal(pipe.single_door, "fraggate");
assert.equal(pipe.domain_count, 11);
assert.equal(pipe.software_count, 33);
assert.equal(pipe.azchat.status, "stub / not hosted yet");
assert.equal(pipe.domain_doors.slug, "4dmap");
assert.equal(DOMAIN_MAP.length, 11);
assert.equal(domainSlugs().length, 33);
assert.equal(pipe.hops.some((h) => String(h.label || "").includes("LambGate")), false);
assert.match(pipe.note, /LambGate is not a hop/);
assert.equal(pipe.controlling_design, "MASTER-33");
assert.equal(pipe.runtime_lock, "1.7.0");
assert.equal(pipe.suite_pipe_status, "historical");
assert.ok(!pipe.softwares.includes("azinterface"));
assert.ok(pipe.softwares.includes("4dmap"));
assert.match(pipe.note, /MASTER-33/);
assert.match(pipe.note, /aziel-runtime/);
assert.equal(pipe.owner.includes("fraggate"), false);

const cycle = await dispatch("page_cycle_status", {});
assert.equal(cycle.pipeline_path, PIPELINE_PATH);
assert.equal(cycle.pipeline.software_count, 33);

const html = homeHtml({ views: 1, downloads: 2, github: { stars: 0 } });
assert.match(html, /id="pipeline"/);
assert.match(html, /THE SINGLE DOOR/);
assert.match(html, /Internal Domain Layer/);
assert.match(html, /id="domains"/);
assert.match(html, /data-slug="azchat"/);
assert.match(html, /stub \/ not hosted yet/);
assert.match(html, /No LambGate/);
assert.match(html, /pipeline-btn/);
assert.match(html, /id="cycle-toast"/);
assert.match(html, /toastMemorial/);
assert.match(html, /AIH-CYCLE-TERMINAL/);
assert.match(html, /MEMORIAL is terminal/);
assert.equal(html.includes("LambGate →"), false);
assert.match(pipelineStripHtml() + domainMapHtml(), /hop door/);

assert.deepEqual(classifyV1Path("/v1/pipeline_arch"), {
  kind: "local",
  path: "/v1/pipeline_arch",
  op: "pipeline_arch",
});
assert.deepEqual(classifyV1Path("/v1/azpipe/arch"), {
  kind: "local",
  path: "/v1/azpipe/arch",
  op: "pipeline_arch",
});

const specReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/openapi.json", { method: "GET" });
const specRes = await handleRuntimeApi(specReq, new URL(specReq.url), {});
const spec = await specRes.json();
assert.ok(spec.paths["/v1/pipeline_arch"]);
assert.match(spec.info.description, /MASTER-33/);
assert.match(spec.info.description, /THE SINGLE DOOR/);
assert.match(spec.info.description, /no LambGate/i);

const mcpReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/mcp", { method: "GET" });
const mcpRes = await handleRuntimeApi(mcpReq, new URL(mcpReq.url), {});
const mcp = await mcpRes.json();
assert.equal(mcp.pipeline.owner, "aziel-runtime");
assert.equal(mcp.pipeline.software_count, 33);
assert.equal(mcp.pipeline.second_door, false);
assert.equal(mcp.pipeline.path_local_alias, "/v1/azpipe/arch");
assert.equal(mcp.pipeline.path_runtime_cite, RUNTIME_ARCH_PATH);
assert.equal(mcp.pipeline.proxy, false);

const RUNTIME_STRIP =
  "Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer → optional ASE → RoseClock (forward-only; StaticClock/VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return";

function runtimeArchPayload() {
  return {
    ok: true,
    door: "fraggate",
    pipeline: {
      v: "AZPIPE-0.2",
      locked: true,
      master: "MASTER-33",
      lambgate: false,
      lamb_lens: true,
      fraggate_single_door: true,
      software_tab: false,
      strip: RUNTIME_STRIP,
    },
    pipeline_strip: RUNTIME_STRIP,
  };
}

function mockRuntime(status, body) {
  return {
    AZIEL_RUNTIME: {
      fetch: async (input) => {
        const url = typeof input === "string" ? input : input.url;
        assert.equal(url, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
        return new Response(JSON.stringify(body), {
          status,
          headers: { "content-type": "application/json; charset=utf-8" },
        });
      },
    },
  };
}

async function getPipelineArch(env, path = "/v1/pipeline_arch") {
  const req = new Request("https://azinterface-download-tracker.vibelock.workers.dev" + path, {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const res = await handleRuntimeApi(req, new URL(req.url), env);
  return { res, body: await res.json() };
}

const previousFetch = globalThis.fetch;
globalThis.fetch = async () => {
  throw new Error("pipeline cite tests must not use live HTTPS");
};

try {
  const getBody = (await getPipelineArch({})).body;
  assert.equal(getBody.ok, true);
  assert.equal(getBody.software_count, 33);
  assert.equal(getBody.cited_from, "embedded");
  assert.equal(getBody.runtime_arch, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
  assert.equal(getBody.controlling_design, "MASTER-33");
  assert.match(getBody.path, /FragGate \(THE SINGLE DOOR\)/);
  assert.equal(getBody.hops.some((h) => String(h.label || "").includes("LambGate")), false);

  const live = await getPipelineArch(mockRuntime(200, runtimeArchPayload()));
  assert.equal(live.res.status, 200);
  assert.equal(live.body.ok, true);
  assert.equal(live.body.cited_from, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
  assert.equal(live.body.runtime_status, 200);
  assert.equal(live.body.runtime_cite.master, "MASTER-33");
  assert.equal(live.body.runtime_cite.lambgate, false);
  assert.equal(live.body.runtime_cite.pipeline_strip, RUNTIME_STRIP);
  assert.equal(live.body.software_count, 33);
  assert.equal(live.body.path, PIPELINE_PATH);
  assert.equal(live.body.hops.some((h) => String(h.label || "").includes("LambGate")), false);

  const missing = await getPipelineArch(mockRuntime(404, { error: "not found" }));
  assert.equal(missing.body.ok, true);
  assert.equal(missing.body.cited_from, "embedded");
  assert.equal(missing.body.runtime_status, 404);
  assert.equal(missing.body.runtime_arch, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
  assert.equal(missing.body.software_count, 33);
  assert.equal(missing.body.path, PIPELINE_PATH);

  const empty = await getPipelineArch(mockRuntime(200, { ok: true }));
  assert.equal(empty.body.cited_from, "embedded");
  assert.equal(empty.body.software_count, 33);

  globalThis.fetch = async (input) => {
    const url = typeof input === "string" ? input : input.url;
    assert.equal(url, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
    return new Response(JSON.stringify(runtimeArchPayload()), {
      status: 200,
      headers: { "content-type": "application/json; charset=utf-8" },
    });
  };
  const httpsCite = await getPipelineArch({});
  assert.equal(httpsCite.body.cited_from, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
  assert.equal(httpsCite.body.runtime_status, 200);
  assert.equal(httpsCite.body.runtime_cite.pipeline_strip, RUNTIME_STRIP);
  assert.equal(httpsCite.body.path, PIPELINE_PATH);

  const aliasMissing = await getPipelineArch(mockRuntime(404, { error: "not found" }), "/v1/azpipe/arch");
  assert.equal(aliasMissing.res.status, 200);
  assert.equal(aliasMissing.body.ok, true);
  assert.equal(aliasMissing.body.cited_from, "embedded");
  assert.equal(aliasMissing.body.runtime_status, 404);
  assert.equal(aliasMissing.body.software_count, 33);
  assert.equal(aliasMissing.body.path, PIPELINE_PATH);
  assert.equal(aliasMissing.body.controlling_design, "MASTER-33");
  assert.equal(aliasMissing.body.hops.some((h) => String(h.label || "").includes("LambGate")), false);

  const aliasLive = await getPipelineArch(mockRuntime(200, runtimeArchPayload()), "/v1/azpipe/arch");
  assert.equal(aliasLive.res.status, 200);
  assert.equal(aliasLive.body.path, PIPELINE_PATH);
  assert.equal(aliasLive.body.software_count, 33);
  assert.equal(aliasLive.body.cited_from, DEFAULT_RUNTIME_ORIGIN + RUNTIME_ARCH_PATH);
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker pipeline cite ok");
