/**
 * Worker MASTER-ARCHITECTURE-2.0 pipeline cite + homepage strip.
 */
import assert from "node:assert/strict";
import { dispatch, LIVE_OPS, resetEngine } from "../workers/download-tracker/src/engine.js";
import { DOMAIN_MAP, PIPELINE_PATH, domainSlugs, pipelineArch, pipelineStripHtml, domainMapHtml } from "../workers/download-tracker/src/pipeline.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { classifyV1Path } from "../workers/download-tracker/src/door.js";

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
assert.match(pipe.note, /MASTER-ARCHITECTURE-2.0/);

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
assert.equal(html.includes("LambGate →"), false);
assert.match(pipelineStripHtml() + domainMapHtml(), /hop door/);

assert.deepEqual(classifyV1Path("/v1/pipeline_arch"), {
  kind: "local",
  path: "/v1/pipeline_arch",
  op: "pipeline_arch",
});

const specReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/openapi.json", { method: "GET" });
const specRes = await handleRuntimeApi(specReq, new URL(specReq.url), {});
const spec = await specRes.json();
assert.ok(spec.paths["/v1/pipeline_arch"]);
assert.match(spec.info.description, /MASTER-ARCHITECTURE-2.0/);
assert.match(spec.info.description, /THE SINGLE DOOR/);
assert.match(spec.info.description, /no LambGate/i);

const mcpReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/mcp", { method: "GET" });
const mcpRes = await handleRuntimeApi(mcpReq, new URL(mcpReq.url), {});
const mcp = await mcpRes.json();
assert.equal(mcp.pipeline.owner, "aziel-runtime");
assert.equal(mcp.pipeline.software_count, 33);
assert.equal(mcp.pipeline.second_door, false);

const getReq = new Request("https://azinterface-download-tracker.vibelock.workers.dev/v1/pipeline_arch", {
  method: "GET",
  headers: { "user-agent": "Mozilla/5.0" },
});
const getRes = await handleRuntimeApi(getReq, new URL(getReq.url), {});
const getBody = await getRes.json();
assert.equal(getBody.ok, true);
assert.equal(getBody.software_count, 33);
assert.equal(getBody.cited_from, "embedded");

console.log("worker pipeline cite ok");
