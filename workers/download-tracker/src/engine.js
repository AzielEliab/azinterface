/**
 * AZInterface (AIH-WP-1.0) hosted engine.
 * Same ops as Python / Worker UI / FragGate slug=azinterface.
 * Interface is CUSTODY. Never collapse into Hub.
 */

export const VERSION = "0.1.0";
export const SPEC = "AIH-WP-1.0";
export const SPEC_STRING = "azinterface-aih-wp-1.0";
export const PRODUCT = "azinterface";
export const NAME = "AZInterface";
export const IDENTITY = "Aziel Eliab";
export const RUNTIME = "https://aziel-runtime.vibelock.workers.dev";
export const FRAGGATE = "https://github.com/AzielEliab/fraggate";
export const FRAGGATE_CALL = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";
export const FRAGGATE_MCP = "https://aziel-runtime.vibelock.workers.dev/mcp";
export const HOST = "https://azinterface-download-tracker.vibelock.workers.dev";
export const SIGIL = "https://www.azielcorpuslibrary.net/sigil.png";
export const AZHUB = "https://github.com/AzielEliab/azhub";
export const GITHUB = "https://github.com/AzielEliab/azinterface";

export const LIMITATION =
  "THIS IS: AZInterface (AIH-WP-1.0) — a custodial operating environment (hold / withdraw / witness) with pre-locked page cycles, genesis one-time keying, an integrity loop, AZHome bunker surface, and Scorched Earth as a local stub/advisory only. Interface is CUSTODY. THIS IS NOT: AZHub (Blank Key / spatial container — sibling https://github.com/AzielEliab/azhub). Never collapse Interface into Hub. Hosted Worker never remotely wipes user devices, never stores a username, never serves vault contents, and never claims cloud-asleep availability. Apps do not render as living presence until the operator enables ON after integrity (OFF → [integrity check] → ON; plus FULL SHUTDOWN and MEMORIAL). Author: Aziel Eliab only.";

export const LIVE_OPS = [
  "health",
  "skill",
  "genesis_status",
  "genesis_boot",
  "site_state_get",
  "site_state_set",
  "integrity_check",
  "witness_list",
  "page_cycle_status",
  "hold",
  "withdraw",
  "scorch_local",
];

export const STUB_OPS = ["scorch_remote", "scorch", "deanonymize", "vault_read"];
export const OPS = [...LIVE_OPS, ...STUB_OPS];

export const ALIASES = {
  scorch: "scorch_remote",
  wipe_remote: "scorch_remote",
  remote_wipe: "scorch_remote",
  unmask: "deanonymize",
  identify: "deanonymize",
  vault: "vault_read",
  read_vault: "vault_read",
  genesis: "genesis_boot",
  boot: "genesis_boot",
  state_get: "site_state_get",
  state_set: "site_state_set",
  cycle: "page_cycle_status",
  integrity: "integrity_check",
};

export const SITE_STATES = ["OFF", "ON", "FULL_SHUTDOWN", "MEMORIAL"];
export const MODULES = ["azhome", "hold", "withdraw", "witness"];
const GENESIS_DOMAIN = "azinterface|genesis|AIH-WP-1.0";
const ZERO = "0".repeat(64);

export const SKILL_MD = `---
name: AZInterface
description: >-
  Use when operating AZInterface (AIH-WP-1.0) custody — hold / withdraw /
  witness, pre-locked page cycles, genesis keying, integrity, AZHome.
  Interface is CUSTODY. Never collapse into Hub. Author Aziel Eliab.
---

# AZInterface

Custodial operating environment (AIH-WP-1.0). Hold / withdraw / witness.
AZHome bunker browser surface. Genesis one-time keying. Integrity loop.
Witness list (no vault contents). Scorched Earth is a **local stub/advisory
only** on the hosted Worker — never a remote wipe of user devices.

Author: **Aziel Eliab** only.

**THIS IS:** Interface custody. Pre-locked page cycles
(\`OFF → [integrity check] → ON\`, plus FULL SHUTDOWN and MEMORIAL).

**THIS IS NOT:** AZHub (Blank Key / spatial container — sibling
https://github.com/AzielEliab/azhub). Never collapse Interface into Hub.
Not a vault dump. Not a remote wipe service.

Always send \`User-Agent: Mozilla/5.0\`.

**Agent path is FragGate only.** MCP / agents call aziel-runtime — not a
separate Interface MCP brand.

\`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call\`
body \`{"slug":"azinterface","op":"<op>","payload":{}}\`

Same door as MCP \`fraggate_call\` (\`slug=azinterface\`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog listing lands in a
sibling aziel-runtime PR. Human chrome uses this Worker \`/v1/{op}\`
(single-segment local ops only). \`/v1/fraggate/*\` and \`/v1/runtime/*\`
PROXY to aziel-runtime. \`GET|POST /mcp\` here is a pointer, not a second MCP.

**Human UI stays on this Worker.** AI path is FragGate + this OpenAPI.

## Safe LIVE ops

| op | What |
|----|------|
| \`health\` | Liveness. Does not increment downloads. |
| \`skill\` | This markdown. |
| \`genesis_status\` | Whether one-time keying ran. Hash only. |
| \`genesis_boot\` | One-time username seed → Genesis Hash Key. Never stores username. |
| \`site_state_get\` | OFF / ON / FULL_SHUTDOWN / MEMORIAL. |
| \`site_state_set\` | Set site state. ON requires integrity. |
| \`integrity_check\` | Integrity loop. Required before ON. |
| \`witness_list\` | Witness metadata. Never vault contents. |
| \`page_cycle_status\` | Pre-locked cycle. Living presence only after ON. |
| \`hold\` / \`withdraw\` | Custody acts. Living presence only. |
| \`scorch_local\` | Local advisory. Not a remote wipe. |

## Stub (refuse)

\`scorch_remote\` / \`scorch\` / \`deanonymize\` / \`vault_read\`

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants — **through FragGate only**.

Agents display \`display.title\`, \`display.summary\`, and
\`display.fields\` in chat, then take the next input.

## How to call

\`\`\`bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \\
  -H 'content-type: application/json' \\
  -d '{"slug":"azinterface","op":"page_cycle_status","payload":{}}'
curl -s -A 'Mozilla/5.0' -X POST https://azinterface-download-tracker.vibelock.workers.dev/v1/integrity_check \\
  -H 'content-type: application/json' -d '{}'
curl -s -A 'Mozilla/5.0' https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list
\`\`\`

Apache-2.0. Forks are welcome and always allowed.
`;

function displayOf(title, summary, fields) {
  return {
    title,
    summary,
    fields: (fields || []).map(([label, value]) => ({ label, value: String(value) })),
    next: "Show this output to the user, then take the next input.",
  };
}

async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(text)));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function genesisHashKey(username) {
  return sha256Hex(`${GENESIS_DOMAIN}|${username}`);
}

function normalizeState(raw) {
  if (raw == null) return null;
  let text = String(raw).trim().toUpperCase().replace(/[ -]/g, "_");
  const aliases = {
    FULLSHUTDOWN: "FULL_SHUTDOWN",
    FULL_STOP: "FULL_SHUTDOWN",
    SHUTDOWN: "FULL_SHUTDOWN",
    MEM: "MEMORIAL",
    OFFLINE: "OFF",
    ONLINE: "ON",
  };
  text = aliases[text] || text;
  return SITE_STATES.includes(text) ? text : null;
}

function createState() {
  return {
    site_state: "OFF",
    integrity_ok: false,
    integrity_ts: null,
    integrity_digest: null,
    genesis_hash: null,
    genesis_keyed: false,
    holds: [],
    witnesses: [],
    receipts: [],
  };
}

const STATE = createState();

export function resetEngine() {
  const next = createState();
  for (const key of Object.keys(STATE)) delete STATE[key];
  Object.assign(STATE, next);
}

function livingPresence(s) {
  return s.site_state === "ON" && s.integrity_ok === true;
}

function cyclePosture(s) {
  if (s.site_state === "FULL_SHUTDOWN") return "FULL_SHUTDOWN";
  if (s.site_state === "MEMORIAL") return "MEMORIAL";
  if (s.site_state === "ON" && s.integrity_ok) return "ON";
  if (s.site_state === "OFF" && s.integrity_ok) return "INTEGRITY";
  return "OFF";
}

function moduleSurface(s, name) {
  const living = livingPresence(s);
  if (name === "witness") {
    return {
      module: name,
      served: true,
      living_presence: living,
      posture: living ? "living" : "locked_list_only",
      vault_contents: false,
      note: "Witness list is metadata only. Vault contents are never served.",
    };
  }
  return {
    module: name,
    served: living,
    living_presence: living,
    posture: living ? "living" : "pre_locked",
    note: living
      ? "Living presence."
      : "Pre-locked. Content does not serve as living presence until ON after integrity.",
  };
}

function pageCycleSnapshot(s) {
  const living = livingPresence(s);
  return {
    site_state: s.site_state,
    cycle: cyclePosture(s),
    cycle_path: "OFF → [integrity check] → ON",
    also: ["FULL_SHUTDOWN", "MEMORIAL"],
    locked: !living,
    pre_locked: !living,
    living_presence: living,
    integrity_ok: s.integrity_ok,
    integrity_ts: s.integrity_ts,
    genesis_keyed: s.genesis_keyed,
    genesis_hash: s.genesis_hash,
    cloud_asleep: false,
    modules: Object.fromEntries(MODULES.map((name) => [name, moduleSurface(s, name)])),
    note: living
      ? "Living presence enabled."
      : "Pre-locked page cycle. Apps do not render as living presence until the operator enables ON after integrity. No cloud-asleep availability.",
  };
}

async function appendReceipt(s, action, payload) {
  const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const seq = s.receipts.length + 1;
  const prev = s.receipts.length ? s.receipts[s.receipts.length - 1].hash : ZERO;
  const payloadHash = await sha256Hex(JSON.stringify(payload || {}));
  const hash = await sha256Hex(`${seq}|${prev}|${action}|${payloadHash}|${ts}`);
  const row = {
    kind: "azinterface.receipt",
    seq,
    ts,
    action,
    prev,
    payload_hash: payloadHash,
    hash,
  };
  s.receipts.push(row);
  if (s.receipts.length > 64) s.receipts.shift();
  return row;
}

function base(extra) {
  return {
    product: PRODUCT,
    name: NAME,
    version: VERSION,
    spec: SPEC,
    spec_string: SPEC_STRING,
    identity: IDENTITY,
    author: IDENTITY,
    slug: PRODUCT,
    door: "fraggate",
    role: "custody",
    hub_collapse: false,
    sibling_hub: AZHUB,
    kv_increment: false,
    stored: false,
    vault_contents: false,
    cloud_asleep: false,
    remote_wipe: false,
    username_stored: false,
    limitation: LIMITATION,
    agent_path: FRAGGATE_CALL,
    runtime: RUNTIME,
    kernel: FRAGGATE,
    host: HOST,
    sigil: SIGIL,
    azhome: "AZHome",
    ...extra,
  };
}

function stubRefuse(op, rec) {
  const reasons = {
    scorch_remote: "Hosted Scorched Earth never remotely wipes user devices. Local stub/advisory only (scorch_local).",
    deanonymize: "AZInterface does not deanonymize. Identity is Aziel Eliab only.",
    vault_read: "Hosted Worker never serves vault contents. Witness list is metadata only.",
  };
  return base({
    ok: false,
    code: "STUB",
    stub: true,
    op,
    error: reasons[op] || "stub",
    note: reasons[op] || "stub",
    receipt: rec,
    display: displayOf("Stub refused", reasons[op] || "stub", [["op", op], ["code", "STUB"]]),
  });
}

export async function dispatch(op, payload, _sessionId) {
  const name = ALIASES[String(op || "").trim().toLowerCase().replace(/-/g, "_")] || String(op || "").trim().toLowerCase().replace(/-/g, "_");
  if (!OPS.includes(name)) {
    return {
      ok: false,
      code: "FG-HALLUC-TOOL",
      error: "unknown op",
      op,
      ops: LIVE_OPS,
      stub_ops: STUB_OPS,
      limitation: LIMITATION,
      agent_path: FRAGGATE_CALL,
    };
  }
  const s = STATE;
  payload = payload || {};

  if (name === "health") {
    const rec = await appendReceipt(s, "health", { site_state: s.site_state });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      runtime_true: true,
      live_ops: LIVE_OPS,
      stub_ops: STUB_OPS,
      ops: OPS,
      site_state: s.site_state,
      living_presence: cycle.living_presence,
      catalog_mcp: FRAGGATE_MCP,
      github: GITHUB,
      receipt: rec,
      display: displayOf("AZInterface health", "Custodial operating environment. Interface is CUSTODY — not Hub.", [
        ["version", VERSION],
        ["spec", SPEC],
        ["site_state", s.site_state],
        ["living_presence", cycle.living_presence],
        ["hub_collapse", false],
      ]),
    });
  }

  if (name === "skill") {
    return base({ ok: true, markdown: SKILL_MD });
  }

  if (name === "genesis_status") {
    const rec = await appendReceipt(s, "genesis_status", { keyed: s.genesis_keyed });
    return base({
      ok: true,
      keyed: s.genesis_keyed,
      genesis_keyed: s.genesis_keyed,
      genesis_hash: s.genesis_hash,
      username_stored: false,
      one_time: true,
      receipt: rec,
      display: displayOf("Genesis status", "One-time keying. Hash only. Username is never stored.", [
        ["keyed", s.genesis_keyed],
        ["genesis_hash", s.genesis_hash || ""],
        ["username_stored", false],
      ]),
    });
  }

  if (name === "genesis_boot") {
    let username = String(payload.username || payload.seed || payload.name || "").trim();
    if (s.genesis_keyed) {
      const rec = await appendReceipt(s, "genesis_boot_refused", { reason: "already_keyed" });
      return base({
        ok: false,
        code: "GENESIS_ALREADY_KEYED",
        keyed: true,
        genesis_keyed: true,
        genesis_hash: s.genesis_hash,
        username_stored: false,
        receipt: rec,
        display: displayOf("Genesis already keyed", "One-time only. Existing Genesis Hash Key is shown. Username was never stored.", [
          ["genesis_hash", s.genesis_hash || ""],
          ["username_stored", false],
        ]),
      });
    }
    if (!username) {
      return base({
        ok: false,
        code: "GENESIS_SEED_REQUIRED",
        keyed: false,
        error: "username seed required (used once, never stored)",
        display: displayOf("Genesis seed required", "Provide a one-time username seed. It is hashed and discarded."),
      });
    }
    const digest = await genesisHashKey(username);
    username = "";
    s.genesis_hash = digest;
    s.genesis_keyed = true;
    const rec = await appendReceipt(s, "genesis_boot", { keyed: true, hash_prefix: digest.slice(0, 16) });
    return base({
      ok: true,
      keyed: true,
      genesis_keyed: true,
      genesis_hash: digest,
      genesis_hash_key: digest,
      username_stored: false,
      one_time: true,
      receipt: rec,
      display: displayOf("Genesis Hash Key", "One-time keying complete. Display is the hash only. Username discarded.", [
        ["genesis_hash", digest],
        ["username_stored", false],
      ]),
    });
  }

  if (name === "site_state_get") {
    const rec = await appendReceipt(s, "site_state_get", { site_state: s.site_state });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      site_state: s.site_state,
      allowed: SITE_STATES,
      living_presence: cycle.living_presence,
      cycle,
      receipt: rec,
      display: displayOf("Site state", `Current posture ${s.site_state}. Living presence only after ON following integrity.`, [
        ["site_state", s.site_state],
        ["living_presence", cycle.living_presence],
      ]),
    });
  }

  if (name === "site_state_set") {
    const wanted = normalizeState(payload.state || payload.site_state || payload.to);
    if (!wanted) {
      return base({
        ok: false,
        code: "SITE_STATE_UNKNOWN",
        error: "state must be ON, OFF, FULL_SHUTDOWN, or MEMORIAL",
        allowed: SITE_STATES,
        site_state: s.site_state,
      });
    }
    if (wanted === "ON" && !s.integrity_ok) {
      const rec = await appendReceipt(s, "site_state_set_refused", { wanted: "ON", reason: "need_integrity" });
      return base({
        ok: false,
        code: "NEED_INTEGRITY",
        error: "ON requires a passing integrity check in this cycle. Pre-locked. No cloud-asleep availability.",
        site_state: s.site_state,
        living_presence: false,
        need_integrity: true,
        receipt: rec,
        display: displayOf("Integrity required", "OFF → [integrity check] → ON. Living presence is not served until the operator enables ON after integrity.", [
          ["site_state", s.site_state],
          ["integrity_ok", false],
        ]),
      });
    }
    const prev = s.site_state;
    s.site_state = wanted;
    if (prev === "ON" && wanted !== "ON") {
      s.integrity_ok = false;
      s.integrity_ts = null;
      s.integrity_digest = null;
    }
    if (wanted === "FULL_SHUTDOWN" || wanted === "MEMORIAL") {
      s.integrity_ok = false;
      s.integrity_ts = null;
      s.integrity_digest = null;
    }
    const rec = await appendReceipt(s, "site_state_set", { from: prev, to: wanted, living: livingPresence(s) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      site_state: s.site_state,
      previous: prev,
      living_presence: cycle.living_presence,
      cycle,
      receipt: rec,
      display: displayOf(`Site state ${wanted}`, cycle.living_presence ? "Living presence." : "Locked posture. No living app serve.", [
        ["from", prev],
        ["to", wanted],
        ["living_presence", cycle.living_presence],
      ]),
    });
  }

  if (name === "integrity_check") {
    if (payload.fail || payload.force_fail) {
      s.integrity_ok = false;
      s.integrity_ts = null;
      s.integrity_digest = null;
      if (s.site_state === "ON") s.site_state = "OFF";
      const rec = await appendReceipt(s, "integrity_fail", { ok: false });
      return base({
        ok: false,
        code: "INTEGRITY_FAIL",
        integrity_ok: false,
        living_presence: false,
        site_state: s.site_state,
        receipt: rec,
        display: displayOf("Integrity failed", "Cycle remains pre-locked. ON is refused."),
      });
    }
    const digest = await sha256Hex(`azinterface|integrity|${SPEC}|${s.genesis_hash || "ungekeyed"}|${s.receipts.length ? s.receipts[s.receipts.length - 1].hash : ZERO}`);
    s.integrity_ok = true;
    s.integrity_ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    s.integrity_digest = digest;
    const rec = await appendReceipt(s, "integrity_check", { ok: true, digest_prefix: digest.slice(0, 16) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      integrity_ok: true,
      integrity_digest: digest,
      integrity_ts: s.integrity_ts,
      site_state: s.site_state,
      living_presence: cycle.living_presence,
      cycle,
      receipt: rec,
      display: displayOf("Integrity passed", "Operator may now enable ON. Living presence is still locked until ON.", [
        ["integrity_ok", true],
        ["site_state", s.site_state],
        ["digest", digest],
      ]),
    });
  }

  if (name === "page_cycle_status") {
    const rec = await appendReceipt(s, "page_cycle_status", { cycle: cyclePosture(s) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      ...cycle,
      receipt: rec,
      display: displayOf("Page cycle", cycle.note, [
        ["site_state", cycle.site_state],
        ["cycle", cycle.cycle],
        ["living_presence", cycle.living_presence],
        ["cloud_asleep", false],
      ]),
    });
  }

  if (name === "witness_list") {
    const rec = await appendReceipt(s, "witness_list", { count: s.witnesses.length });
    return base({
      ok: true,
      witnesses: s.witnesses.map((w) => ({ ...w })),
      count: s.witnesses.length,
      vault_contents: false,
      receipt: rec,
      display: displayOf("Witness list", "Custody witnesses only. Vault contents are never listed.", [
        ["count", s.witnesses.length],
        ["vault_contents", false],
      ]),
    });
  }

  if (name === "hold") {
    if (!livingPresence(s)) {
      const rec = await appendReceipt(s, "hold_refused", { reason: "pre_locked" });
      return base({
        ok: false,
        code: "PRE_LOCKED",
        error: "Hold is a living-presence act. Enable ON after integrity.",
        living_presence: false,
        site_state: s.site_state,
        receipt: rec,
        display: displayOf("Pre-locked", "Hold does not run until ON after integrity."),
      });
    }
    const label = String(payload.label || payload.name || "hold").trim().slice(0, 80);
    const labelHash = await sha256Hex(`azinterface|hold|${label}`);
    const holdId = "hold-" + labelHash.slice(0, 12);
    const row = { hold_id: holdId, label_hash: labelHash, status: "held", vault_contents: false };
    s.holds.push(row);
    const rec = await appendReceipt(s, "hold", { hold_id: holdId, label_hash: labelHash });
    const witness = { kind: "hold", hold_id: holdId, hash: rec.hash, ts: rec.ts, seq: rec.seq, vault_contents: false };
    s.witnesses.push(witness);
    return base({
      ok: true,
      hold: row,
      witness,
      vault_contents: false,
      display: displayOf("Hold", "Custody hold recorded. Label hashed. Vault contents not stored.", [
        ["hold_id", holdId],
        ["status", "held"],
        ["vault_contents", false],
      ]),
    });
  }

  if (name === "withdraw") {
    if (!livingPresence(s)) {
      const rec = await appendReceipt(s, "withdraw_refused", { reason: "pre_locked" });
      return base({
        ok: false,
        code: "PRE_LOCKED",
        error: "Withdraw is a living-presence act. Enable ON after integrity.",
        living_presence: false,
        site_state: s.site_state,
        receipt: rec,
        display: displayOf("Pre-locked", "Withdraw does not run until ON after integrity."),
      });
    }
    const holdId = String(payload.hold_id || payload.id || "").trim();
    let target = null;
    if (holdId) target = s.holds.find((h) => h.hold_id === holdId) || null;
    else {
      for (let i = s.holds.length - 1; i >= 0; i--) {
        if (s.holds[i].status === "held") {
          target = s.holds[i];
          break;
        }
      }
    }
    if (!target) {
      return base({
        ok: false,
        code: "HOLD_NOT_FOUND",
        error: "No matching hold. Witness list shows ids only — never vault contents.",
        vault_contents: false,
      });
    }
    target.status = "withdrawn";
    const rec = await appendReceipt(s, "withdraw", { hold_id: target.hold_id });
    const witness = { kind: "withdraw", hold_id: target.hold_id, hash: rec.hash, ts: rec.ts, seq: rec.seq, vault_contents: false };
    s.witnesses.push(witness);
    return base({
      ok: true,
      hold: target,
      witness,
      vault_contents: false,
      display: displayOf("Withdraw", "Custody withdraw recorded. Vault contents were never stored on this Worker.", [
        ["hold_id", target.hold_id],
        ["status", "withdrawn"],
      ]),
    });
  }

  if (name === "scorch_local") {
    const rec = await appendReceipt(s, "scorch_local_advisory", { remote_wipe: false });
    return base({
      ok: true,
      advisory: true,
      local_only: true,
      remote_wipe: false,
      code: "SCORCH_LOCAL_ADVISORY",
      note: "Scorched Earth on the hosted Worker is a local stub/advisory only. It never remotely wipes user devices.",
      receipt: rec,
      display: displayOf("Scorched Earth (local advisory)", "Hosted Worker will not remotely wipe devices. Local operator machines stay under local control.", [
        ["remote_wipe", false],
        ["local_only", true],
      ]),
    });
  }

  if (name === "scorch_remote" || name === "deanonymize" || name === "vault_read") {
    const rec = await appendReceipt(s, "stub_refuse", { op: name });
    return stubRefuse(name, rec);
  }

  return {
    ok: false,
    code: "FG-HALLUC-TOOL",
    error: "unknown op",
    op,
    limitation: LIMITATION,
  };
}
