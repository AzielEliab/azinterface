/**
 * Worker LOCKED pipeline cite + homepage strip.
 * Runtime owns fabric hops. 4DMap is Domain Door inspection. No LambGate.
 */
import assert from "node:assert/strict";
import { dispatch, LIVE_OPS, resetEngine } from "../workers/download-tracker/src/engine.js";
import { PIPELINE_PATH, pipelineArch, pipelineStripHtml } from "../workers/download-tracker/src/pipeline.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { classifyV1Path } from "../workers/download-tracker/src/door.js";

resetEngine();

assert.ok(LIVE_OPS.includes("pipeline_arch"));
const pipe = pipelineArch();
assert.equal(pipe.locked, true);
assert.equal(pipe.lambgate, false);
assert.equal(pipe.owner, "aziel-runtime");
assert.equal(pipe.identity, "Aziel Eliab");
assert.equal(pipe.path, PIPELINE_PATH);
assert.equal(pipe.domain_doors.slug, "4dmap");
assert.equal(pipe.domain_doors.sequential_gate, false);
assert.equal(pipe.hops.some((h) => String(h.label || "").includes("LambGate")), false);
assert.match(pipe.note, /LambGate is not on this list/);

const cycle = await dispatch("page_cycle_status", {});
assert.equal(cycle.pipeline_path, PIPELINE_PATH);
assert.equal(cycle.pipeline.domain_doors.slug, "4dmap");
assert.equal(cycle.pipeline.lambgate, false);

const arch = await dispatch("pipeline_arch", {});
assert.equal(arch.ok, true);
assert.equal(arch.owner, "aziel-runtime");
assert.equal(arch.display.title, "LOCKED pipeline");

const html = homeHtml({ views: 1, downloads: 2, github: { stars: 0 } });
assert.match(html, /id="pipeline"/);
assert.match(html, /LOCKED pipeline/);
assert.match(html, /data-hop="domain_doors"/);
assert.match(html, /4DMap inspection/);
assert.match(html, /No LambGate/);
assert.match(html, /pipeline-btn/);
assert.match(html, /pipeline_arch/);
assert.equal(html.includes("LambGate →"), false);
assert.match(pipelineStripHtml(), /hop door/);

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

const specReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/openapi.json", { method: "GET" });
const specRes = await handleRuntimeApi(specReq, new URL(specReq.url), {});
const spec = await specRes.json();
assert.ok(spec.paths["/v1/pipeline_arch"]);
assert.ok(spec.paths["/v1/azpipe/arch"]);
assert.match(spec.info.description, /LOCKED suite pipeline/);
assert.match(spec.info.description, /4DMap/);
assert.match(spec.info.description, /no LambGate/i);
assert.equal(spec.info.description.includes("LambGate →"), false);

const mcpReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/mcp", { method: "GET" });
const mcpRes = await handleRuntimeApi(mcpReq, new URL(mcpReq.url), {});
const mcp = await mcpRes.json();
assert.equal(mcp.pipeline.owner, "aziel-runtime");
assert.equal(mcp.pipeline.lambgate, false);
assert.equal(mcp.pipeline.domain_doors.slug, "4dmap");
assert.match(mcp.note, /pipeline_arch/);

const getReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/pipeline_arch", {
  method: "GET",
  headers: { "user-agent": "Mozilla/5.0" },
});
const getRes = await handleRuntimeApi(getReq, new URL(getReq.url), {});
const getBody = await getRes.json();
assert.equal(getBody.ok, true);
assert.equal(getBody.cited_from, "embedded");
assert.equal(getBody.lambgate, false);

console.log("worker pipeline cite ok");
