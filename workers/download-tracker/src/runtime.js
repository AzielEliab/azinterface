/**
 * AZInterface hosted runtime: /v1 ops, OpenAPI, MCP pointer, FragGate door proxy.
 * /v1 never touches DOWNLOADS KV. Dual surface — not UI-only.
 *
 * Door paths (`/v1/fraggate/*`, `/v1/runtime/*`, `/v1/mesh/*`) PROXY to
 * aziel-runtime via AZIEL_RUNTIME or HTTPS fallback. Leftover
 * `/v1/azpipe/arch` is a local `pipeline_arch` alias (embedded MASTER-33).
 * Optional runtime cite is GET `/v1/fraggate`. Local ops are
 * single-segment `/v1/{op}` only.
 */
import {
  ALIASES,
  AZCLCE,
  AZCOHERENCE,
  AZCOHERENCE_WORKER,
  AZHUB,
  FRAGGATE,
  FRAGGATE_CALL,
  FRAGGATE_MCP,
  HOST,
  IDENTITY,
  LIMITATION,
  LIVE_OPS,
  OPS,
  PRODUCT,
  RUNTIME,
  SKILL_MD,
  STUB_OPS,
  VERSION,
  dispatch,
} from "./engine.js";
import { classifyV1Path, doorTargetUrl, runtimeArchUrl, RUNTIME_ARCH_PATH } from "./door.js";
import { pipelineArch } from "./pipeline.js";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function toolDefs() {
  const desc = {
    health: "Liveness. Does not increment downloads.",
    skill: "Return AZInterface skill markdown.",
    genesis_status: "Whether one-time genesis keying ran. Hash only.",
    genesis_boot: "One-time username seed → Genesis Hash Key. Never stores username.",
    site_state_get: "Read OFF / integrity / ON / FULL SHUTDOWN / MEMORIAL.",
    site_state_set: "Advance one sealed cycle step. ON requires integrity.",
    integrity_check: "Integrity loop. Required before ON.",
    witness_list: "Witness metadata. Never vault contents.",
    page_cycle_status: "Pre-locked cycle. Living presence only after ON. Includes LOCKED pipeline cite.",
    pipeline_arch: "Cite MASTER-33 hop order on aziel-runtime. FragGate is THE SINGLE DOOR. 33/11 domain layer. 4DMap is an inspection frame, not an extra door (domains_are_doors:false). No LambGate.",
    hold: "Custody hold. Living presence only. May cite pair_id + photon_id.",
    withdraw: "Custody withdraw. Living presence only.",
    scorch_local: "Local Scorched Earth advisory. Not a remote wipe.",
    pair_offer: "QNS-CD §19 OFFER. Living presence only. Via cite; qnsd runs the hop.",
    pair_accept: "QNS-CD §19 ACCEPT. Living presence only. AIH-WP-1.3 handshake.",
    pair_seal: "QNS-CD §19 SEAL. Living presence only. Pair memorial cite.",
    pair_cut: "QNS-CD §19 CUT. Living dissolve — not a remote wipe.",
    pair_status: "Read pair memorial cites. Never vault contents.",
  };
  return LIVE_OPS.map((name) => ({
    name: "azinterface_" + name,
    description: desc[name] || name,
    inputSchema: {
      type: "object",
      properties: {
        username: { type: "string" },
        seed: { type: "string" },
        state: { type: "string" },
        site_state: { type: "string" },
        label: { type: "string" },
        hold_id: { type: "string" },
        pair_id: { type: "string" },
        photon_id: { type: "string" },
        via: { type: "string" },
        payload: { type: "object" },
      },
    },
  }));
}

function opSummary(op) {
  if (STUB_OPS.includes(op)) {
    const alias = ALIASES[op] ? " Alias of " + ALIASES[op] + "." : "";
    return "STUB refuse / not hosted." + alias + " Worker /v1 documents the name so importers see the refuse. Not a live destructive action. Not a catalog LIVE op.";
  }
  return (ALIASES[op] ? "Alias of " + ALIASES[op] + ". " : "") + "UI action + FragGate op.";
}

function openapiSpec(origin) {
  const paths = {
    "/v1/health": { get: { operationId: "azinterface_health", summary: "Liveness. Does not increment downloads.", responses: { "200": { description: "ok" } } } },
    "/v1/skill": { get: { operationId: "azinterface_skill", summary: "Skill markdown.", responses: { "200": { description: "markdown" } } } },
    "/openapi.json": { get: { operationId: "azinterface_openapi", summary: "OpenAPI 3.1 — first-class backend.", responses: { "200": { description: "spec" } } } },
    "/mcp": {
      get: { operationId: "azinterface_mcp_docs", summary: "Pointer only. Agents use aziel-runtime FragGate/MCP; this host is custody UI only. Not a product MCP.", responses: { "200": { description: "docs" } } },
      post: { operationId: "azinterface_mcp", summary: "Pointer only. Agents use aziel-runtime FragGate/MCP; this host is custody UI only. Not a product MCP.", responses: { "200": { description: "rpc" } } },
    },
  };
  for (const op of OPS) {
    if (op === "health" || op === "skill") continue;
    paths["/v1/" + op] = {
      post: {
        operationId: "azinterface_" + op,
        summary: opSummary(op),
        requestBody: { content: { "application/json": { schema: { type: "object" } } } },
        responses: { "200": { description: STUB_OPS.includes(op) ? "STUB refuse / not hosted" : "display + result" } },
      },
    };
  }
  for (const op of ["genesis_status", "site_state_get", "page_cycle_status", "pipeline_arch", "witness_list", "pair_status"]) {
    paths["/v1/" + op].get = {
      operationId: "azinterface_" + op + "_get",
      summary: "Read " + op + ".",
      responses: { "200": { description: "ok" } },
    };
  }
  paths["/v1/fraggate/call"] = {
    post: {
      operationId: "azinterface_fraggate_call_proxy",
      summary: "PROXY to aziel-runtime POST /v1/fraggate/call. Not a local op.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "FragGate ResultEnvelope" } },
    },
  };
  paths["/v1/fraggate/list"] = {
    get: {
      operationId: "azinterface_fraggate_list_proxy",
      summary: "PROXY to aziel-runtime GET /v1/fraggate/list. Not a local op.",
      responses: { "200": { description: "hashed registry" } },
    },
  };
  paths["/v1/runtime/call"] = {
    post: {
      operationId: "azinterface_runtime_call_proxy",
      summary: "Alias PROXY → origin /v1/fraggate/call. Not a local op.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "FragGate ResultEnvelope" } },
    },
  };
  paths["/v1/runtime/list"] = {
    get: {
      operationId: "azinterface_runtime_list_proxy",
      summary: "Alias PROXY → origin /v1/fraggate/list. Not a local op.",
      responses: { "200": { description: "hashed registry" } },
    },
  };
  paths["/v1/fraggate"] = {
    get: {
      operationId: "azinterface_fraggate_arch_proxy",
      summary: "PROXY to aziel-runtime GET /v1/fraggate. MASTER-33 pipeline / pipeline_strip live cite. FragGate is THE SINGLE DOOR. Local frozen cite is GET /v1/pipeline_arch.",
      responses: { "200": { description: "FragGate door summary + MASTER-33 pipeline strip" } },
    },
  };
  paths["/v1/azpipe/arch"] = {
    get: {
      operationId: "azinterface_azpipe_arch_local",
      summary: "Local alias of GET /v1/pipeline_arch. Embedded MASTER-33 strip. Not a Softwares door. Does not proxy a runtime path. Optional runtime cite is GET /v1/fraggate.",
      responses: { "200": { description: "embedded MASTER-33 pipeline cite" } },
    },
    post: {
      operationId: "azinterface_azpipe_arch_local_post",
      summary: "Local alias of POST /v1/pipeline_arch. Embedded MASTER-33 strip.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "embedded MASTER-33 pipeline cite" } },
    },
  };
  paths["/v1/mesh"] = {
    get: {
      operationId: "azinterface_mesh_status_proxy",
      summary: "PROXY to aziel-runtime GET /v1/mesh. QNM-BUILD-1.0 suite rollup. Default OFF. Never enables. Not a local op. Not a Node Gate. Not AnonBroadcast.",
      responses: { "200": { description: "enabled + rollup live|locked|isolated" } },
    },
  };
  paths["/v1/mesh/status"] = {
    get: {
      operationId: "azinterface_mesh_status_alias_proxy",
      summary: "PROXY alias of GET /v1/mesh. Default OFF until runtime enable.",
      responses: { "200": { description: "enabled + rollup live|locked|isolated" } },
    },
  };
  paths["/v1/mesh/nodes"] = {
    get: {
      operationId: "azinterface_mesh_nodes_proxy",
      summary: "PROXY to aziel-runtime GET /v1/mesh/nodes. Presence roster. No scores. Not a Node Gate. AIH-WP-1.3 spiderweb is local qnm-node.",
      responses: { "200": { description: "nodes[]" } },
    },
  };
  paths["/v1/mesh/join"] = {
    post: {
      operationId: "azinterface_mesh_join_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/join. Refused while radios are OFF. Body {product, node_id?, label?, presence?}.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "session + node" } },
    },
  };
  paths["/v1/mesh/heartbeat"] = {
    post: {
      operationId: "azinterface_mesh_heartbeat_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/heartbeat. Presence refresh. No auto-heal.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "node last_seen" } },
    },
  };
  paths["/v1/mesh/leave"] = {
    post: {
      operationId: "azinterface_mesh_leave_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/leave. Idempotent. No implicit heal.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "left" } },
    },
  };
  paths["/v1/mesh/enable"] = {
    post: {
      operationId: "azinterface_mesh_enable_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/enable. Operator bearer required. Interface does not enable on its own.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "enabled" } },
    },
  };
  paths["/v1/mesh/disable"] = {
    post: {
      operationId: "azinterface_mesh_disable_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/disable. Always allowed. Tethers drop clean. No wipe.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "disabled" } },
    },
  };
  paths["/v1/mesh/broadcast"] = {
    post: {
      operationId: "azinterface_mesh_broadcast_proxy",
      summary: "PROXY to aziel-runtime POST /v1/mesh/broadcast. SHA-256 hash receipt only. Not a publish path. Not AnonBroadcast. No video bytes.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "hash receipt" } },
    },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "AZInterface runtime",
      version: VERSION,
      summary: "Dual surface. This host is custody UI only. Agents use aziel-runtime FragGate/MCP (slug=azinterface). /mcp is a pointer, not a product MCP.",
      description: LIMITATION + " LOCKED suite pipeline (MASTER-33 on aziel-runtime; FragGate is THE SINGLE DOOR; AZInterface is not a second door; no LambGate): Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer (33/11 isolation labels; 4DMap inspection frame, not an extra door (domains_are_doors:false)) → optional ASE → RoseClock (forward-only) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return. Local GET|POST /v1/pipeline_arch and leftover /v1/azpipe/arch return the same frozen MASTER-33 cite; optional runtime cite is GET /v1/fraggate (pipeline / pipeline_strip). Cite never depends on a missing runtime path. Agent door is FragGate only: POST " + FRAGGATE_CALL + " {slug:azinterface,op,payload}. Catalog MCP: POST " + FRAGGATE_MCP + ". This host /mcp is a pointer (ok:false), not a product MCP. Agents use aziel-runtime FragGate/MCP; this host is custody UI only. Human chrome uses same-origin /v1. Suite mesh /v1/mesh/* PROXIES to aziel-runtime (AZIEL_RUNTIME or HTTPS fallback). QNM-BUILD-1.0 rollup live|locked|isolated. Default OFF until runtime enable. GET never enables. QNS-CD-1.0 photon vias run in local qnm-node qnsd (127.0.0.1). Interface holds pair memorial (pair_offer/accept/seal/cut/status). Not a Softwares-tab QNS product. AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. No auto-heal. Not anonymity. Anon-broadcast is not a publish path. No untraceable-origin claim. AZCoherence is separate Plain Softwares on the same door (slug=azcoherence; peer of AZ-CLCE; not AKM-TRIAD). Agents: fraggate_describe then fraggate_call via aziel-runtime. Humans: " + AZCOHERENCE_WORKER + "/ + /download. Softwares tabs: GET " + RUNTIME + "/v1/software (plain A–Z).",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: IDENTITY, url: "https://github.com/AzielEliab/azinterface" },
    },
    servers: [{ url: origin }, { url: RUNTIME, description: "aziel-runtime" }],
    paths,
  };
}

function mcpDocs(origin) {
  return {
    ok: false,
    error: "not a product MCP",
    message: "Agents use aziel-runtime FragGate/MCP. This host is custody UI only — not a product MCP and not a second Interface door.",
    product: PRODUCT,
    door: "fraggate",
    slug: "azinterface",
    identity: IDENTITY,
    agent_path: FRAGGATE_CALL,
    catalog_mcp: FRAGGATE_MCP,
    body: { slug: "azinterface", op: "page_cycle_status", payload: {} },
    openapi: origin + "/openapi.json",
    note: "Agents use aziel-runtime FragGate/MCP. This host is custody UI only. AI / MCP path is the one FragGate door. This host /v1/fraggate/* , /v1/runtime/* , and /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME or HTTPS fallback to " + RUNTIME + "). Leftover /v1/azpipe/arch is a local pipeline_arch alias (embedded MASTER-33). Local ops are /v1/{op} only. LOCKED pipeline cite is GET|POST /v1/pipeline_arch (frozen hop list) plus optional runtime GET /v1/fraggate pipeline / pipeline_strip (runtime owns fabric hops; no LambGate; 4DMap is an inspection frame after AZPIPE, not an extra door (domains_are_doors:false)). Cite never depends on a missing runtime path. Catalog MCP: POST " + FRAGGATE_MCP + ". Suite mesh is slug=mesh on that catalog (QNM-BUILD-1.0; default OFF; GET never enables). QNS-CD-1.0 vias run in local qnsd (127.0.0.1); Interface holds pair memorial. Not a Softwares-tab QNS product. AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. Anon-broadcast is not a publish path. AZHub is separate software, not this product. AZCoherence is separate Plain Softwares (slug=azcoherence; peer of AZ-CLCE; not AKM-TRIAD). Agents fraggate_describe/call via aziel-runtime; humans " + AZCOHERENCE_WORKER + "/ + /download.",
    ops: OPS,
    live_ops: LIVE_OPS,
    stub_ops: STUB_OPS,
    mesh: {
      path: "/v1/mesh",
      enabled_default: false,
      proxy: true,
      spec: "QNM-BUILD-1.0",
      companion: "AIH-WP-1.1",
      qns_cd: "QNS-CD-1.0",
      qnsd: "127.0.0.1",
      via_runs_in: "qnsd",
      pair_memorial: "azinterface custody",
      spiderweb: "local qnm-node (AIH-WP-1.3)",
      node_gate: false,
      auto_heal: false,
      anonymity: false,
      qnm_s: false,
      rollup_only: true,
      get_enables: false,
      anon_broadcast: "not a publish path",
    },
    pipeline: {
      ...pipelineArch(),
      path_local: "/v1/pipeline_arch",
      path_local_alias: "/v1/azpipe/arch",
      path_runtime_cite: RUNTIME_ARCH_PATH,
      proxy: false,
      owner: "aziel-runtime",
      lambgate: false,
    },
    qns: {
      spec: "QNS-CD-1.0",
      handshake: "AIH-WP-1.3",
      ops: ["pair_offer", "pair_accept", "pair_seal", "pair_cut", "pair_status"],
      via_runs_in: "qnsd",
      qnsd: "127.0.0.1",
      canonical: "https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node",
      catalog: "azinterface",
      softwares_tab_qns: false,
      untraceable_origin: false,
      remote_wipe: false,
    },
    tools: toolDefs().map((t) => t.name),
    limitation: LIMITATION,
    kernel: FRAGGATE,
    sibling_hub: AZHUB,
    sibling_azcoherence: AZCOHERENCE,
    peer_azclce: AZCLCE,
  };
}

function runtimeFetcher(env) {
  if (env && env.AZIEL_RUNTIME && typeof env.AZIEL_RUNTIME.fetch === "function") return env.AZIEL_RUNTIME;
  return null;
}

function extractRuntimeArch(remote) {
  if (!remote || typeof remote !== "object") return null;
  const pipeline = remote.pipeline && typeof remote.pipeline === "object" ? remote.pipeline : null;
  const strip =
    typeof remote.pipeline_strip === "string"
      ? remote.pipeline_strip
      : pipeline && typeof pipeline.strip === "string"
        ? pipeline.strip
        : typeof remote.strip === "string"
          ? remote.strip
          : null;
  const master = (pipeline && pipeline.master) || remote.master || null;
  if (!strip && !pipeline && master !== "MASTER-33") return null;
  return {
    master: master || "MASTER-33",
    locked: pipeline ? pipeline.locked !== false : true,
    lambgate: pipeline ? pipeline.lambgate === true : false,
    fraggate_single_door: pipeline ? pipeline.fraggate_single_door !== false : true,
    software_tab: pipeline ? pipeline.software_tab === true : false,
    pipeline,
    pipeline_strip: strip,
  };
}

async function maybeCiteRuntimeArch(env, local) {
  const dest = runtimeArchUrl(env);
  const headers = { "User-Agent": "Mozilla/5.0 AZInterface/0.1.0", Accept: "application/json" };
  try {
    const fetcher = runtimeFetcher(env);
    const res = fetcher
      ? await fetcher.fetch(dest, { method: "GET", headers })
      : await fetch(dest, { method: "GET", headers });
    if (!res.ok) {
      return { ...local, cited_from: "embedded", runtime_cite: null, runtime_arch: dest, runtime_status: res.status };
    }
    const remote = await res.json();
    const cite = extractRuntimeArch(remote);
    if (!cite) {
      return { ...local, cited_from: "embedded", runtime_cite: null, runtime_arch: dest, runtime_status: res.status };
    }
    return { ...local, cited_from: dest, runtime_cite: cite, runtime_arch: dest, runtime_status: res.status };
  } catch {
    return { ...local, cited_from: "embedded", runtime_cite: null, runtime_arch: dest };
  }
}

async function proxyDoor(request, url, env) {
  const dest = doorTargetUrl(url.pathname, request.url, env);
  if (!dest) {
    return json({ ok: false, error: "not a door path", path: url.pathname, limitation: LIMITATION }, 404);
  }
  const headers = new Headers();
  const pass = ["content-type", "accept", "authorization", "user-agent", "mcp-protocol-version", "mcp-session-id", "x-aziel-runtime-token"];
  for (const name of pass) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }
  if (!headers.has("User-Agent")) headers.set("User-Agent", "Mozilla/5.0 AZInterface/0.1.0");
  const init = { method: request.method, headers, redirect: "follow" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }
  try {
    const fetcher = runtimeFetcher(env);
    const res = fetcher ? await fetcher.fetch(dest, init) : await fetch(dest, init);
    const outHeaders = new Headers(res.headers);
    for (const [k, v] of Object.entries(corsHeaders())) outHeaders.set(k, v);
    outHeaders.set("X-Aziel-Door", "proxy");
    outHeaders.set("X-Aziel-Door-Origin", dest);
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers: outHeaders });
  } catch (exc) {
    return json({
      ok: false,
      error: "fraggate_proxy_failed",
      detail: String(exc).slice(0, 240),
      origin: dest,
      agent_path: FRAGGATE_CALL,
      limitation: LIMITATION,
    }, 502);
  }
}

function aiHtml(origin) {
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>AZInterface — AI / MCP</title>
<style>body{font:16px/1.45 system-ui;max-width:46rem;margin:3rem auto;padding:0 1.25rem;background:#0b0b0b;color:#e8e0d0}a{color:#c9a227}.banner{border:1px solid #5c4a1a;background:#241c0d;color:#f0d78c;padding:.85rem 1rem;border-radius:8px}pre{background:#141414;padding:.85rem 1rem;overflow:auto;border-radius:8px}</style>
<h1>AZInterface dual surface</h1>
<p class="banner">${LIMITATION}</p>
<p>Agents use aziel-runtime FragGate/MCP. This host is custody UI only — not a product MCP and not a second Interface door.</p>
<p>Human UI is the Worker homepage (pre-locked custody cycle). Agent path is FragGate:</p>
<pre>POST ${FRAGGATE_CALL}
{"slug":"azinterface","op":"page_cycle_status","payload":{}}</pre>
<p>Catalog MCP: <code>POST ${FRAGGATE_MCP}</code>. This Worker <code>/mcp</code> is a pointer (<code>ok: false</code>), not a product MCP.</p>
<p>LOCKED suite pipeline (MASTER-33 on aziel-runtime): FragGate is THE SINGLE DOOR. Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer (33/11; 4DMap inspection frame) → optional ASE → RoseClock → TemporalLock → ChainLock-OUT → ForgeReceipts → Return. 4DMap is an inspection frame after AZPIPE, not an extra door (domains_are_doors:false). aziel-runtime owns fabric hops. SUITE-PIPE-1.6.15 is historical. No LambGate. Local <code>/v1/pipeline_arch</code>.</p>
<p>Suite mesh <code>/v1/mesh/*</code> PROXIES to aziel-runtime (QNM-BUILD-1.0 rollup; default OFF; GET never enables). QNS-CD-1.0 vias run in local <code>qnsd</code> (127.0.0.1). Interface holds pair memorial — not a Softwares-tab QNS product. AIH-WP-1.3 spiderweb is local <code>qnm-node/</code> — not a public Node Gate. Anon-broadcast is not a publish path.</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a> · mesh: <a href="${origin}/v1/mesh">${origin}/v1/mesh</a></p>
<p>Kernel: <a href="${FRAGGATE}">${FRAGGATE}</a> · Plain peers A–Z (same FragGate door): AZ-CLCE <a href="${AZCLCE}">${AZCLCE}</a> · AZCoherence <a href="${AZCOHERENCE}">${AZCOHERENCE}</a> (slug=azcoherence; humans <a href="${AZCOHERENCE_WORKER}/">${AZCOHERENCE_WORKER}/</a> + <a href="${AZCOHERENCE_WORKER}/download">/download</a>; agents <a href="${RUNTIME}/v1/fraggate/describe?slug=azcoherence">describe</a> then <code>fraggate_call</code>) · AZHub <a href="${AZHUB}">${AZHUB}</a>. Not AKM-TRIAD.</p>
<p>Clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama, Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence, Amazon Q, DuckAssist, You.com, Cohere.</p>
<p><a href="/">Downloads + custody UI</a></p>
</html>`;
}

export { SKILL_MD };

const READ_OPS = new Set(["health", "skill", "genesis_status", "site_state_get", "page_cycle_status", "pipeline_arch", "witness_list", "pair_status"]);

export async function handleRuntimeApi(request, url, env) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/mcp" && request.method === "GET") return json(mcpDocs(originOf(request)));
  if (path === "/mcp" && request.method === "POST") return json(mcpDocs(originOf(request)));

  if (path === "/v1/health" && request.method === "GET") return json(await dispatch("health", {}));
  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MD, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() },
    });
  }
  if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec(originOf(request)));
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return new Response(aiHtml(originOf(request)), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
  }
  if (path === "/llms.txt" || path === "/ai.txt") {
    return new Response(
      `AZInterface ${VERSION} by ${IDENTITY}. Apache-2.0. ${LIMITATION}\nAgent path is FragGate only: POST ${FRAGGATE_CALL} {"slug":"azinterface","op":"…","payload":{}}\nThis Worker /v1/fraggate/* , /v1/runtime/* , and /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME or HTTPS fallback). Leftover /v1/azpipe/arch is a local pipeline_arch alias.\nLOCKED pipeline cite: GET ${originOf(request)}/v1/pipeline_arch (local) · alias GET ${originOf(request)}/v1/azpipe/arch · optional runtime GET ${RUNTIME}/v1/fraggate (pipeline / pipeline_strip)\nMASTER-33 on aziel-runtime. FragGate is THE SINGLE DOOR. AZInterface is not a second door.\nHuman → AZInterface → PUBLIC/UI/AGENT/API → FragGate → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer (33/11; 4DMap inspection frame) → optional ASE → RoseClock → TemporalLock → ChainLock-OUT → ForgeReceipts → Return\n4DMap is an inspection frame after AZPIPE, not an extra door (domains_are_doors:false). SUITE-PIPE-1.6.15 is historical. aziel-runtime owns fabric hops. No LambGate.\nSuite mesh default OFF. GET never enables. QNM-BUILD-1.0 rollup live|locked|isolated. QNS-CD-1.0 vias run in local qnsd (127.0.0.1). Interface holds pair memorial. Not a Softwares-tab QNS product. AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. No auto-heal. Not anonymity. Anon-broadcast is not a publish path.\nLocal ops are /v1/{op} only.\nCatalog MCP: POST ${FRAGGATE_MCP}\nThis Worker /mcp is a pointer (ok:false), not a product MCP. Agents use aziel-runtime FragGate/MCP. This host is custody UI only.\nHuman UI: ${originOf(request)}/\nSkill: ${originOf(request)}/v1/skill\nOpenAPI: ${originOf(request)}/openapi.json\nMesh: ${originOf(request)}/v1/mesh\nQNS: ${originOf(request)} — pair_offer/accept/seal/cut/status\nPlain peers A–Z (same FragGate door; not extra doors): AZ-CLCE ${AZCLCE} · AZCoherence ${AZCOHERENCE} (slug=azcoherence; AZC-WP-0.1; scoring-review; peer of AZ-CLCE; not AKM-TRIAD; humans ${AZCOHERENCE_WORKER}/ + /download; agents GET ${RUNTIME}/v1/fraggate/describe?slug=azcoherence then POST ${FRAGGATE_CALL} {"slug":"azcoherence","op":"…"})\nAZHub sibling: ${AZHUB}\nSoftwares tabs: GET ${RUNTIME}/v1/software (plain A–Z → gate A–Z → lock A–Z). Interface does not host that catalog.\n`,
      { headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() } },
    );
  }

  const classified = classifyV1Path(url.pathname);
  if (classified.kind === "door") {
    return proxyDoor(request, url, env);
  }
  if (classified.kind === "multi") {
    return json({
      ok: false,
      error: "not a local op",
      code: "NOT_LOCAL_OP",
      path: classified.path,
      hint: "Local ops are POST|GET /v1/{op} only (single segment). FragGate door is /v1/fraggate/* (proxied to aziel-runtime). /v1/runtime/list and /v1/runtime/call alias that door. Suite mesh is /v1/mesh/* (proxied; QNM-BUILD-1.0; default OFF).",
      agent_path: FRAGGATE_CALL,
      ops: OPS,
      limitation: LIMITATION,
    }, 404);
  }
  if (classified.kind === "local" && (request.method === "POST" || (request.method === "GET" && READ_OPS.has(classified.op)))) {
    let body = {};
    if (request.method === "POST") {
      try {
        const n = request.headers.get("content-length");
        if (n !== "0") body = await request.json();
      } catch {
        body = {};
      }
    }
    const out = await dispatch(classified.op, body || {}, body && body.session_id);
    if (classified.op === "pipeline_arch" && out && out.ok) {
      const cited = await maybeCiteRuntimeArch(env, out);
      return json(cited, 200);
    }
    return json(out, out.ok === false && out.code === "FG-HALLUC-TOOL" ? 404 : 200);
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health GET /v1/skill POST /v1/{op} GET /v1/fraggate/list POST /v1/fraggate/call GET /v1/mesh GET /openapi.json POST /mcp", ops: OPS, limitation: LIMITATION }, 404);
  }
  return null;
}
