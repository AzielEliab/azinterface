/**
 * AZInterface public cite for AZBot Node Collaborative Forensic Design 1.0.
 *
 * The node desk is http://127.0.0.1:8880. This host stores no session, does not
 * package a FragGate call, and does not enable mesh radios. AzielTether is a
 * cite under an operator bearer. Cap-7 and .aziel stay names.
 * FragGate stays the one door (this path is not a door prefix).
 *
 * Author: Aziel Eliab. Apache-2.0.
 */
import { FRAGGATE_CALL, PAGE_CYCLES, custodyCycle } from "./engine.js";

export const SPEC = "AZBOT-NODE-COLLABORATIVE-FORENSIC-1.0";
export const CAP7_SENTENCE = "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP.";
const NAME_ONLY = new Set(["cap7", "cap-7", "icann", "cap7-egress"]);
const USERNAME_KEYS = new Set(["username", "user_name", "user"]);
const REMAIN_KEYS = new Set([
  "deanonymize", "invent_mark", "backdate", "rollback", "public_rollback",
  "scorch", "scorch_remote", "wipe", "unlock", "shell", "exec",
  "vault", "vault_read", "mesh_enable", "auto_enable",
]);
const PATHS = new Set(["/v1/forensic/tip", "/v1/forensic/session", "/v1/forensic/handoff", "/v1/azieltether"]);

const H = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store",
  "Access-Control-Allow-Origin": "*",
};

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), { status, headers: H });
}

export function nameOnly(value) {
  const raw = String(value || "").trim().toLowerCase();
  if (!raw) return false;
  if (nameOnlyText(raw)) return true;
  let host = raw;
  if (raw.includes("://")) host = raw.split("://", 1)[1].split("/", 1)[0].split("@").pop().split(":")[0];
  return nameOnlyText(host.replace(/^\[|\]$/g, ""));
}

function nameOnlyText(raw) {
  return NAME_ONLY.has(raw.replace(/_/g, "-")) || raw.endsWith(".aziel");
}

function* walk(value, depth = 0) {
  if (depth > 4 || value == null) return;
  if (Array.isArray(value)) {
    for (const item of value.slice(0, 32)) yield* walk(item, depth + 1);
    return;
  }
  if (typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      yield [String(key), item];
      yield* walk(item, depth + 1);
    }
  }
}

function usernamePresent(payload) {
  for (const [key, item] of walk(payload)) {
    if (USERNAME_KEYS.has(key.toLowerCase().replace(/-/g, "_")) && item != null && item !== "" && item !== false) return true;
  }
  return false;
}

function remainKey(payload) {
  for (const [key, item] of walk(payload)) {
    const folded = key.toLowerCase().replace(/-/g, "_");
    if (REMAIN_KEYS.has(folded) && item != null && item !== "" && item !== false) return folded;
  }
  return null;
}

function payloadNameOnly(payload) {
  for (const [key, item] of walk(payload)) {
    if (nameOnly(key) || (typeof item === "string" && nameOnly(item))) return true;
  }
  return false;
}

function bearerToken(authorization, payload) {
  const header = String(authorization || "");
  const matched = /^Bearer\s+(\S+)\s*$/i.exec(header);
  if (matched) return matched[1];
  for (const key of ["bearer", "token"]) {
    const raw = payload && payload[key];
    if (typeof raw === "string" && raw.trim()) return raw.trim();
  }
  return "";
}

function frame() {
  const cycle = custodyCycle();
  return {
    spec: SPEC,
    author: "Aziel Eliab",
    bind: "127.0.0.1",
    desk: "http://127.0.0.1:8880",
    public_port: false,
    stored_here: false,
    door: "fraggate",
    second_door: false,
    agent_path: FRAGGATE_CALL,
    executed: false,
    stored_payload: false,
    username_stored: false,
    share_tips_only: true,
    rewrite: false,
    mesh_enabled: false,
    radios_enabled: false,
    cap7_names_only: true,
    icann: false,
    cap7_sentence: CAP7_SENTENCE,
    remain_off: {
      mesh_auto_enable: false,
      get_v1_mesh_enables: false,
      azos_public_exec: false,
      vault_destructive_public: false,
      deanonymize: false,
      invent_mark: false,
      backdate: false,
      public_rollback: false,
      second_public_door: false,
      radios_enabled: false,
      cap7_is_icann: false,
    },
    cycles: PAGE_CYCLES.slice(),
    skip_forbidden: true,
    cloud_asleep: false,
    public_cycle: cycle,
    page_cycle: cycle.current,
    living_presence: cycle.living_presence,
  };
}

function refuse(code, status, summary, extra = {}) {
  return {
    status,
    body: {
      ...frame(),
      ok: false,
      code,
      written: false,
      admitted: false,
      ...extra,
      display: { title: "AZInterface forensic tether", summary, fields: [{ label: "code", value: code }, { label: "door", value: "fraggate" }] },
    },
  };
}

function guard(payload) {
  if (payloadNameOnly(payload)) return refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE);
  if (usernamePresent(payload)) return refuse("USERNAME-NOT-STORED", 403, "A username is not stored.");
  const remain = remainKey(payload);
  if (remain) return refuse("REMAIN-OFF", 403, "Remain-OFF. This tether does not enable that verb.", { event: remain });
  return null;
}

export function publicTipRead(sessionId) {
  if (sessionId && nameOnly(sessionId)) return refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE);
  const body = {
    ...frame(),
    ok: true,
    code: "FORENSIC-TIP",
    written: false,
    tip: null,
    sessions: [],
    session_id: sessionId || null,
    note: "The public host stores no session tip. Read and append tips on the local desk. A tip cannot be rewritten.",
  };
  return { status: 200, body };
}

export function publicHandoffCite() {
  const body = {
    ...frame(),
    ok: true,
    code: "LOCAL-DESK-ONLY",
    admitted: false,
    written: false,
    package: null,
    azbot: "127.0.0.1",
    note: "Handoff is admitted on the local desk only when that desk is ON after integrity. This host does not package or send the FragGate call.",
  };
  return { status: 200, body };
}

export function publicDeskRefuse(payload) {
  const guarded = guard(payload || {});
  if (guarded) return guarded;
  return refuse("LOCAL-DESK-ONLY", 403, "Session append and AZBot handoff run on http://127.0.0.1:8880. This host stores nothing.");
}

export function publicExposeTether(authorization, payload) {
  const src = payload && typeof payload === "object" ? payload : {};
  const guarded = guard(src);
  if (guarded) {
    guarded.body.exposed = false;
    return guarded;
  }
  const token = bearerToken(authorization, src);
  if (nameOnly(token)) return refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE, { exposed: false });
  if (!token) {
    return refuse("MESH-NEED-BEARER", 401, "AzielTether is exposed under an operator bearer. Mesh radios stay off.", { exposed: false });
  }
  const body = {
    ...frame(),
    ok: true,
    code: "AZIELTETHER-CITE",
    exposed: true,
    bearer: "present",
    written: false,
    tether: {
      name: "AzielTether",
      slug: "azieltether",
      door: "fraggate",
      under_bearer: true,
      second_door: false,
      spec: "AZRT-AZOS-TETHER-1.0",
    },
    anchors: ["AZRT-AZOS-TETHER-1.0", "azieltether", "external-anchors-cite-only"],
    note: "AzielTether is cited under bearer. The bearer is not stored. Radios stay off. FragGate stays the one door.",
  };
  return { status: 200, body };
}

async function readJson(request) {
  if (request.method === "GET" || request.method === "HEAD") return { value: {} };
  const n = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(n) && n > 65536) return { error: "too-large" };
  try {
    const text = await request.text();
    if (text.length > 65536) return { error: "too-large" };
    if (!text) return { value: {} };
    const value = JSON.parse(text);
    return { value: value && typeof value === "object" && !Array.isArray(value) ? value : {} };
  } catch {
    return { value: {} };
  }
}

/** Returns a Response, or null when the path is not this tether. */
export async function handleForensicRoute(request) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (!PATHS.has(path)) return null;
  const method = request.method;
  if (method === "OPTIONS") return new Response(null, { status: 204, headers: H });
  const read = await readJson(request);
  if (read.error) return json({ ...frame(), ok: false, code: "BODY-TOO-LARGE", written: false }, 413);
  const payload = read.value;
  const sessionId = url.searchParams.get("session_id");
  let out = null;
  if (path === "/v1/azieltether" && (method === "GET" || method === "HEAD" || method === "POST")) {
    out = publicExposeTether(request.headers.get("authorization"), method === "POST" ? payload : {});
  } else if ((path === "/v1/forensic/tip" || path === "/v1/forensic/session") && (method === "GET" || method === "HEAD")) {
    out = publicTipRead(sessionId);
  } else if (path === "/v1/forensic/handoff" && (method === "GET" || method === "HEAD")) {
    out = publicHandoffCite();
  } else if (method === "POST" && (path === "/v1/forensic/session" || path === "/v1/forensic/handoff" || path === "/v1/forensic/tip")) {
    out = publicDeskRefuse(payload);
  } else {
    out = refuse("FORENSIC-INPUT", 405, "This cite accepts GET, or POST where the local desk is required.");
  }
  if (method === "HEAD") return new Response(null, { status: out.status, headers: H });
  return json(out.body, out.status);
}
