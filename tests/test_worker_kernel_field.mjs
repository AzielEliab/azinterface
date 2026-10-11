/** KERNEL-FIELD-1.0: no URL-valued `kernel` on the hosted Worker; URL lives in kernel_repo_url. */
import assert from "node:assert/strict";
import worker from "../workers/download-tracker/src/entry.js";
const env = { DOWNLOADS: { get: async () => null, put: async () => {}, list: async () => ({ keys: [] }) }, AZIEL_RUNTIME: { fetch: async () => new Response(JSON.stringify({ ok: false }), { status: 503 }) } };
let n = 0;
function urlKernels(o, p = "", out = []) {
  if (!o || typeof o !== "object") return out;
  // KERNEL-FIELD-1.0: any `kernel` key anywhere must be exactly boolean false.
  if (Object.prototype.hasOwnProperty.call(o, "kernel") && o.kernel !== false) out.push(p + ".kernel=" + JSON.stringify(o.kernel));
  for (const [k, v] of Object.entries(o)) urlKernels(v, p + "." + k, out);
  return out;
}
for (const path of ["/v1/health", "/v1/skill", "/v1/pipeline_arch"]) {
  const res = await worker.fetch(new Request("https://h.example" + path), env, { waitUntil() {} });
  if (!String(res.headers.get("content-type") || "").includes("json")) continue;
  const body = await res.json();
  assert.deepEqual(urlKernels(body), [], path);
  n++;
}
const h = await (await worker.fetch(new Request("https://h.example/v1/health"), env, { waitUntil() {} })).json();
assert.equal(h.kernel, false);
assert.equal(h.kernel_repo_url, "https://github.com/AzielEliab/fraggate");
n += 2;
import { standingFacts } from "../workers/download-tracker/src/honesty.js";
const sf = standingFacts({ kernel: true });
assert.deepEqual(urlKernels(sf), []);
assert.match(sf.lines.kernel_note, /kernel/i);
n++;
console.log(`test_worker_kernel_field: ${n} passed`);
