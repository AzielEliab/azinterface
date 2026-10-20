/**
 * AZ-LOCKSTEP-1.0 feature union, AZInterface side. Features AZ-OS or the runtime had and this leg
 * lacked, added with real wiring. Each one fails closed and stands alone when the runtime is absent:
 *   GET  /v1/tether         this leg's stored, verified signed lattice tips (AZRT-AZOS-TETHER-1.0 rules)
 *   POST /v1/tether/tip     receive a signed tip: pinned key, Ed25519, both lattice links (src/lattice-tether.js,
 *                           the AZ-OS receiver byte for byte). Until the runtime pushes here, nothing is stored.
 *   GET  /v1/lattice        read-only snapshot of this leg's TemporalLock/StaticClock lattice (KV lattice|azinterface)
 *   POST /v1/lattice        refused here (LATTICE-WRITE-NOT-ON-THIS-LEG): no unauthenticated write is added
 *   GET  /v1/prefab         the same prefab hook records as AZ-OS (installed:false on every row)
 *   /v1/session|exec|halt|close|invite|revoke|status   ARC session shell: refused here with ARC-SHELL-AZOS-LEG
 *                           (needs AZ-OS's session-vfs sandbox; never mocked)
 *   GET  /sigil.svg, /brand/sigil.svg   the sigil
 *   GET  /workspace, /v1/anchor/heads, receipts tip, memory, qns, uses, update manifest, catalog, about,
 *        4DMap globe, MCP install cards   read through the runtime over AZIEL_RUNTIME; absent -> 503 LEG-RUNTIME-ABSENT
 * Proxy reads time out after LEG_RUNTIME_TIMEOUT_MS (default 4000) with 503 LEG-RUNTIME-TIMEOUT and abort the upstream
 * request; the caller IP rides as X-Azrt-Client-IP (LEG-CLIENT-IP-1.0; the runtime trusts it over the binding only).
 * Known limit (follow-up): the tether tip write is a KV read-modify-write, not compare-and-set. Concurrent valid
 * packets or a stale KV read can store an older tip; the next push re-links from the runtime tip (TETHER-LINK on a
 * fork). Same as AZ-OS src/tether.js, kept byte for byte.
 * Nothing here flips a live flag. Author: Aziel Eliab. SPDX-License-Identifier: Apache-2.0
 */
import { receiveTether, tetherState } from "./lattice-tether.js";
import { sigilSvg } from "./sigil.js";
import { runtimeBinding } from "./lockstep.js";

const LEG = "azinterface";
const H = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" };
const j = (body, status = 200) => new Response(JSON.stringify(body, null, 2), { status, headers: body && (body.code === "LEG-RUNTIME-ABSENT" || body.code === "LEG-RUNTIME-TIMEOUT") ? { ...H, "X-Leg-Runtime": "down" } : H });
const honest = { live: false, alt_internet_live: false, packet_path_live: false, mesh_node_live: false, kernel_live: false, booted: false, installed: false, kernel_base: false, second_device: false };

export const PREFAB_SLUGS = Object.freeze(["azos", "temporallock", "staticclock", "shadowlock", "foldlock", "azai", "godlock", "vibelock", "veillock", "spectrallock", "miragegrid", "codelock", "decisiongate", "chronolock", "azclce", "ark"]);
export const ARC_PATHS = Object.freeze(["/v1/session", "/v1/exec", "/v1/halt", "/v1/close", "/v1/invite", "/v1/revoke", "/v1/status"]);
export const RUNTIME_READ_PATHS = Object.freeze(["/workspace", "/v1/anchor/heads", "/v1/receipts/tip", "/v1/memory", "/v1/qns", "/v1/uses", "/v1/update/manifest", "/v1/catalog.json", "/about", "/4dmap/globe", "/install/cursor.json"]);

export function prefabCatalog() {
  return {
    ok: true,
    prefab: true,
    leg: LEG,
    hook_count: PREFAB_SLUGS.length,
    apps: PREFAB_SLUGS.map((slug) => ({ slug, installed: false, hooked: true, hook_record: true, author: "Aziel Eliab", catalog: "https://aziel-runtime.vibelock.workers.dev/p/" + slug })),
    note: "AZInterface lists the same catalog products as hook records as AZ-OS. Nothing is installed.",
    ...honest,
  };
}

/** Proxy timeout (ms). LEG_RUNTIME_TIMEOUT_MS clamps to 250..10000; default 4000. */
export function runtimeTimeoutMs(env) {
  const n = Number(env && env.LEG_RUNTIME_TIMEOUT_MS);
  return Number.isFinite(n) && n > 0 ? Math.min(10000, Math.max(250, Math.floor(n))) : 4000;
}

async function viaRuntime(request, env, path) {
  const bind = runtimeBinding(env);
  const absent = { ok: false, code: "LEG-RUNTIME-ABSENT", leg: LEG, path, standalone: true, plain: "The runtime is not reachable from this leg right now. Nothing was shown as live.", ...honest };
  if (!bind) return j(absent, 503);
  const ms = runtimeTimeoutMs(env);
  const ctl = new AbortController();
  let timer;
  let timedOut = false;
  // R5: one deadline covers headers AND body. A runtime that sends headers then stalls the body is a timeout too.
  const late = new Promise((r) => { timer = setTimeout(() => { timedOut = true; ctl.abort(); r(null); }, ms); });
  const timeoutResponse = () => j({ ...absent, code: "LEG-RUNTIME-TIMEOUT", timeout_ms: ms, plain: `The runtime did not answer within ${ms} ms. Nothing was shown as live.` }, 503);
  try {
    const u = new URL(request.url);
    const headers = { accept: request.headers.get("accept") || "*/*" };
    // LEG-CLIENT-IP-1.0: name the caller so the runtime keys its rate limits per client (trusted over the binding only).
    const ip = request.headers.get("CF-Connecting-IP");
    if (ip && ip.trim()) headers["X-Azrt-Client-IP"] = ip.trim();
    const call = bind.fetch(new Request("https://aziel-runtime.internal" + path + u.search, { method: "GET", headers, signal: ctl.signal }));
    const r = await Promise.race([call, late]);
    if (!r) {
      call.catch(() => null);
      return timeoutResponse();
    }
    let body = null;
    if (request.method !== "HEAD") {
      const read = r.arrayBuffer().then((b) => ({ b }), () => null);
      const got = await Promise.race([read, late]);
      if (!got) return timedOut ? timeoutResponse() : j(absent, 503);
      body = got.b;
    }
    const out = new Headers(r.headers);
    out.set("X-Served-Through", "AZIEL_RUNTIME");
    out.delete("content-length");
    return new Response(body, { status: r.status, headers: out });
  } catch {
    return timedOut ? timeoutResponse() : j(absent, 503);
  } finally {
    clearTimeout(timer);
  }
}

/** Returns a Response for a union route, or null. */
export async function handleUnionRoute(request, env) {
  const path = new URL(request.url).pathname.replace(/\/+$/, "") || "/";
  const m = request.method;
  const get = m === "GET" || m === "HEAD";
  if (path === "/v1/tether" && get) {
    const st = await tetherState(env);
    return j({
      ...st,
      ...honest,
      leg: LEG,
      direction: "runtime-sends, azinterface-verifies-and-stores",
      plain: st.chains && st.chains.length
        ? "AZInterface stored and verified signed lattice tips from aziel-runtime. The runtime did not run anything inside AZInterface."
        : "AZInterface has not stored a verified tip yet. Nothing is marked updated.",
    });
  }
  if (path === "/v1/tether/tip" && m === "POST") {
    const out = await receiveTether(request, env);
    return j({ ...out.body, ...honest, leg: LEG }, out.status);
  }
  if (path === "/v1/lattice" && get) {
    let stored = null;
    try { const raw = env && env.DOWNLOADS ? await env.DOWNLOADS.get("lattice|" + LEG) : null; stored = raw ? JSON.parse(raw) : null; } catch { stored = null; }
    const gears = (stored && stored.gears) || [];
    return j({ ok: true, leg: LEG, kind: "temporallock_staticclock_lattice", rollback: false, gear_ticks: gears.length, timeslates: ((stored && stored.slates) || []).length, tip: gears.length ? gears[gears.length - 1] : null, writes_here: false, note: "Read-only on AZInterface. AZ-OS takes lattice appends." });
  }
  if (path === "/v1/lattice" && m === "POST") {
    return j({ ok: false, code: "LATTICE-WRITE-NOT-ON-THIS-LEG", leg: LEG, written: false, plain: "AZInterface does not take lattice writes. Nothing was written.", ...honest }, 403);
  }
  if (path === "/v1/prefab" && get) return j(prefabCatalog());
  if (ARC_PATHS.includes(path)) {
    return j({ ok: false, code: "ARC-SHELL-AZOS-LEG", leg: LEG, path, written: false, plain: "The ARC session shell runs on AZ-OS (session-vfs sandbox). It is not on AZInterface. Nothing ran.", see: "https://azos-download-tracker.vibelock.workers.dev" + path, ...honest }, 501);
  }
  if ((path === "/sigil.svg" || path === "/brand/sigil.svg") && get) {
    return new Response(m === "HEAD" ? null : sigilSvg(), { status: 200, headers: { "Content-Type": "image/svg+xml; charset=utf-8", "Cache-Control": "public, max-age=86400" } });
  }
  if (RUNTIME_READ_PATHS.includes(path) && get) return viaRuntime(request, env, path);
  return null;
}
