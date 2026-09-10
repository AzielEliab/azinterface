/**
 * AZInterface (AIH-WP-1.0) hosted engine.
 * Same ops as Python / Worker UI / FragGate slug=azinterface.
 * Interface is CUSTODY. Never collapse into Hub.
 * Pre-locked cycles: OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL.
 * AZHub is separate software under the one FragGate door.
 * LOCKED suite pipeline is a cite — runtime owns fabric hops. No LambGate.
 */
import { pipelineArch } from "./pipeline.js";

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
export const QNS_CD = "QNS-CD-1.0";
export const QNM_BUILD = "QNM-BUILD-1.0";
export const AIH_PAIR = "AIH-WP-1.3";
export const QNSD_BIND = "127.0.0.1";
export const QNM_NODE = "https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node";
export const QNS_DOC = "https://github.com/AzielEliab/azinterface/blob/main/docs/QNS-CD-1.0.md";
export const QNS_VIAS = Object.freeze(["lan", "plc", "bt", "rf", "light", "qns", "operator", "local"]);
export const PAIR_STEPS = Object.freeze(["OFFER", "ACCEPT", "SEAL"]);

export const LIMITATION =
  "THIS IS: AZInterface (AIH-WP-1.0) — a custodial operating environment (hold / withdraw / witness) with five pre-locked page cycles (OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL). Cycles cannot be invented, reordered, or skipped. Genesis one-time keying, integrity loop, AZHome bunker surface, and Scorched Earth as a local stub/advisory only. Interface is CUSTODY. Agent path is the one FragGate door (slug=azinterface). THIS IS NOT: AZHub (separate software — Blank Key / spatial container — https://github.com/AzielEliab/azhub). Never collapse Interface into Hub. Never a combined hub+interface product. Hosted Worker never remotely wipes user devices, never stores a username, never serves vault contents, and never claims cloud-asleep availability. Living presence only at ON after integrity. Author: Aziel Eliab only.";

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
  "pipeline_arch",
  "hold",
  "withdraw",
  "scorch_local",
  "pair_offer",
  "pair_accept",
  "pair_seal",
  "pair_cut",
  "pair_status",
];

export const STUB_OPS = [
  "scorch_remote",
  "scorch",
  "pair_wipe",
  "deanonymize",
  "vault_read",
  "auto_unlock",
  "ranking",
  "completeness_detect",
  "unlock",
  "complete",
  "completeness",
  "rank",
  "skip_cycle",
  "invent_cycle",
];
export const OPS = [...LIVE_OPS, ...STUB_OPS];
export const PAGE_CYCLES = Object.freeze(["OFF", "integrity", "ON", "FULL SHUTDOWN", "MEMORIAL"]);
export const FORBIDDEN_EVENT_KEYS = Object.freeze([
  "auto_unlock",
  "autounlock",
  "autoUnlock",
  "unlock_auto",
  "completeness",
  "completeness_detect",
  "completeness_event",
  "complete_event",
  "ranking",
  "rank",
  "scorch_remote",
  "scorch",
  "skip_cycle",
  "invent_cycle",
]);
const FORBIDDEN_TEXT =
  /\b(auto[-_ ]?unlock|completeness([-_ ]detect|[-_ ]?event)?|rank(ing)?|scorch([-_ ]remote)?|skip[-_ ]cycle|invent[-_ ]cycle)\b/i;

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
  pipeline: "pipeline_arch",
  arch: "pipeline_arch",
  integrity: "integrity_check",
  offer: "pair_offer",
  accept: "pair_accept",
  seal: "pair_seal",
  cut: "pair_cut",
  pair: "pair_status",
  wipe_pair: "pair_wipe",
  pair_remote_wipe: "pair_wipe",
};

export const SITE_STATES = PAGE_CYCLES;
export const MODULES = ["azhome", "hold", "withdraw", "witness"];
const WITNESS_CAP = 64;
const PAIR_CAP = 64;
const LABEL_CAP = 160;
const ID_CAP = 80;
const QNS_VIA_ALIASES = Object.freeze({ bluetooth: "bt", loopback: "local", localhost: "local" });

export function normalizeVia(raw) {
  if (raw == null || raw === "") return "local";
  const text = String(raw).trim().toLowerCase().replace(/_/g, "-");
  const via = QNS_VIA_ALIASES[text] || text;
  return QNS_VIAS.includes(via) ? via : null;
}

export function qnsCrossMap() {
  return {
    spec: QNS_CD,
    handshake: AIH_PAIR,
    handshake_steps: PAIR_STEPS.slice(),
    ops: ["pair_offer", "pair_accept", "pair_seal", "pair_cut", "pair_status"],
    vias: QNS_VIAS.slice(),
    walker_restricted: true,
    packet: "QNS1",
    via_runs_in: "qnsd",
    qnsd: QNSD_BIND,
    canonical: QNM_NODE,
    doc: QNS_DOC,
    catalog: "azinterface",
    softwares_tab_qns: false,
    mesh: QNM_BUILD,
    mesh_default: "OFF",
    get_enables_mesh: false,
    node_gate: false,
    untraceable_origin: false,
    remote_wipe: false,
    vault_contents: false,
    pair_memorial: "azinterface custody",
    note: "Vias run in local qnsd (127.0.0.1). Interface holds pair memorial cites only.",
  };
}
const GENESIS_DOMAIN = "azinterface|genesis|AIH-WP-1.0";
const ZERO = "0".repeat(64);

export const SKILL_MD = `---
name: AZInterface
description: >-
  Use when operating AZInterface (AIH-WP-1.0) custody — hold / withdraw /
  witness, pre-locked page cycles, genesis keying, integrity, AZHome,
  QNS-CD-1.0 pair memorial (offer/accept/seal/cut). Interface is CUSTODY.
  Never collapse into Hub. Author Aziel Eliab.
---

# AZInterface

Custodial operating environment (AIH-WP-1.0). Hold / withdraw / witness.
AZHome bunker browser surface. Genesis one-time keying. Integrity loop.
Witness list (no vault contents). Scorched Earth is a **local stub/advisory
only** on the hosted Worker — never a remote wipe of user devices.

Author: **Aziel Eliab** only.

**THIS IS:** Interface custody. Five pre-locked page cycles
(\`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL\`). One step only.
No skip. No invented cycle. No auto-unlock.

**THIS IS NOT:** AZHub (separate software — Blank Key / spatial container —
https://github.com/AzielEliab/azhub). Never collapse Interface into Hub.
Never a combined hub+interface product. Not a vault dump. Not a remote wipe
service. Not a separate FragGate door.

Always send \`User-Agent: Mozilla/5.0\`.

**Agent path is the one FragGate door.** MCP / agents call aziel-runtime —
not a second Interface MCP brand. AZHub and AZInterface are separate
software under that door.

\`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call\`
body \`{"slug":"azinterface","op":"<op>","payload":{}}\`

Same door as MCP \`fraggate_call\` (\`slug=azinterface\`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog is live. Human chrome uses
this Worker \`/v1/{op}\` (single-segment local ops only). \`/v1/fraggate/*\`,
\`/v1/runtime/*\`, and \`/v1/mesh/*\` PROXY to aziel-runtime (\`AZIEL_RUNTIME\`
or HTTPS). Suite mesh is QNM-BUILD-1.0 rollup (live|locked|isolated);
default OFF until runtime enable. \`GET /v1/mesh\` never enables.
QNS-CD-1.0 photon vias run in local \`qnm-node/\` **qnsd** (127.0.0.1).
Interface holds pair memorial cites only — not a Softwares-tab QNS
product. AIH-WP-1.3 spiderweb is local \`qnm-node/\` — not a public
Node Gate. No auto-heal. Not anonymity. Anon-broadcast is not a
publish path. \`GET|POST /mcp\` here is a pointer, not a second MCP.

**Human UI stays on this Worker.** AI path is FragGate + this OpenAPI.

## Catalog LIVE ops (FragGate)

| op | What |
|----|------|
| \`health\` | Liveness. Does not increment downloads. |
| \`skill\` | This markdown. |
| \`genesis_status\` | Cycle seal + optional one-time hash. Username never stored. |
| \`site_state_get\` | Current cycle: OFF / integrity / ON / FULL SHUTDOWN / MEMORIAL. |
| \`site_state_set\` | Advance one sealed step only. ON requires integrity. |
| \`integrity_check\` | Records integrity. Advances OFF → integrity. Does not auto-unlock ON. |
| \`witness_list\` | Witness metadata. Never vault contents. Never a ranking. |
| \`page_cycle_status\` | Pre-locked cycle. Living presence only at ON. Includes LOCKED pipeline cite. |

## LOCKED suite pipeline (cite)

Controlling design: MASTER-33 on aziel-runtime (lock introduced 1.7.0).
The product name is aziel-runtime — not a version+FragGate mash.
FragGate is THE SINGLE DOOR. AZInterface is the human UI before that door,
not a second door. SUITE-PIPE-1.6.15 is historical. No LambGate.

\`Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; 4DMap inspection) → optional ASE → RoseClock (forward-only; StaticClock / VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return\`

Internal Domain Layer: 33 softwares / 11 domains after AZPIPE — isolation
labels, not extra doors. 4DMap inspects Research. AZChat (Comms) is stub /
not hosted yet. Lamb Lens is fabric ethics after FragGate. RoseClock is
forward-only.
Local op \`pipeline_arch\` returns the same cite. Hosted
\`GET|POST /v1/pipeline_arch\` and leftover \`/v1/azpipe/arch\` serve that
embedded strip. Optional runtime cite is \`GET /v1/fraggate\`
(\`pipeline\` / \`pipeline_strip\`). Cite never depends on a missing
runtime path.

## Local Worker extras (human UI \`/v1\`)

\`genesis_boot\` · \`hold\` · \`withdraw\` · \`scorch_local\` · \`pipeline_arch\` ·
\`pair_offer\` · \`pair_accept\` · \`pair_seal\` · \`pair_cut\` · \`pair_status\`

## QNS-CD-1.0 cross-map

Canonical qnsd: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
(bind \`127.0.0.1\`). Design summary: \`docs/QNS-CD-1.0.md\`.

| Plane | Who | What |
|-------|-----|------|
| CUSTODY | AZInterface | Pair memorial (\`pair_id\` + \`photon_id\` cites) |
| VIA | local qnsd | QNS1 packet on lan/plc/bt/rf/light/qns/operator/local |
| CATALOG | aziel-runtime | \`slug=azinterface\` + QNM-BUILD-1.0 mesh rollup |

Handshake is AIH-WP-1.3: \`OFFER → ACCEPT → SEAL\`. Walker restriction
applies. Pair mutate only at ON after integrity. \`pair_status\` reads
memorial in any cycle. \`pair_cut\` is a dissolve — not a remote wipe.
Do not invent a Softwares-tab QNS product. Do not claim untraceable
origin. \`GET /v1/mesh\` never enables. No Node Gate.

\`hold\` / \`witness_list\` may record \`pair_id\` + \`photon_id\` cites.
Vault contents are never stored.

## Stub (refuse)

\`scorch_remote\` / \`scorch\` / \`pair_wipe\` / \`auto_unlock\` / \`unlock\` /
\`ranking\` / \`rank\` / \`completeness_detect\` / \`complete\` / \`completeness\` /
\`skip_cycle\` / \`invent_cycle\` / \`deanonymize\` / \`vault_read\`

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

export function normalizeCycle(raw) {
  if (raw == null) return null;
  const text = String(raw).trim();
  if (!text) return null;
  if (PAGE_CYCLES.includes(text)) return text;
  const folded = text.toLowerCase().replace(/[_-]+/g, " ").replace(/\s+/g, " ");
  const aliases = {
    off: "OFF",
    offline: "OFF",
    integrity: "integrity",
    on: "ON",
    online: "ON",
    "full shutdown": "FULL SHUTDOWN",
    fullshutdown: "FULL SHUTDOWN",
    "full stop": "FULL SHUTDOWN",
    shutdown: "FULL SHUTDOWN",
    memorial: "MEMORIAL",
    mem: "MEMORIAL",
  };
  return aliases[folded] || null;
}

function normalizeState(raw) {
  return normalizeCycle(raw);
}

export function cycleIndexOf(name) {
  return PAGE_CYCLES.indexOf(name);
}

export function detectForbiddenEvent(payload) {
  const src = payload && typeof payload === "object" ? payload : {};
  for (const key of FORBIDDEN_EVENT_KEYS) {
    if (!Object.prototype.hasOwnProperty.call(src, key)) continue;
    const val = src[key];
    if (val === false || val == null || val === "") continue;
    if (key === "ranking" || key === "rank") return { kind: "ranking", key, code: "AIH-RANKING-REFUSE" };
    if (key === "scorch_remote" || key === "scorch") return { kind: "scorch_remote", key, code: "AIH-SCORCH-REFUSE" };
    if (key.includes("complete")) return { kind: "completeness", key, code: "AIH-COMPLETENESS-REFUSE" };
    if (key === "skip_cycle" || key === "invent_cycle") return { kind: "cycle_skip", key, code: "AIH-CYCLE-LOCKED" };
    return { kind: "auto_unlock", key, code: "AIH-AUTO-UNLOCK-REFUSE" };
  }
  for (const val of Object.values(src)) {
    if (typeof val !== "string" || !FORBIDDEN_TEXT.test(val)) continue;
    const text = val.toLowerCase();
    if (text.includes("complete")) return { kind: "completeness", key: "text", code: "AIH-COMPLETENESS-REFUSE" };
    if (text.includes("rank")) return { kind: "ranking", key: "text", code: "AIH-RANKING-REFUSE" };
    if (text.includes("scorch")) return { kind: "scorch_remote", key: "text", code: "AIH-SCORCH-REFUSE" };
    if (text.includes("skip") || text.includes("invent")) return { kind: "cycle_skip", key, code: "AIH-CYCLE-LOCKED" };
    return { kind: "auto_unlock", key: "text", code: "AIH-AUTO-UNLOCK-REFUSE" };
  }
  return null;
}

function createState() {
  return {
    cycle_index: 0,
    integrity_ok: false,
    integrity_ts: null,
    integrity_digest: null,
    genesis_hash: null,
    genesis_keyed: false,
    holds: [],
    witnesses: [],
    pairs: [],
    receipts: [],
  };
}

const STATE = createState();

export function resetEngine() {
  const next = createState();
  for (const key of Object.keys(STATE)) delete STATE[key];
  Object.assign(STATE, next);
}

function currentCycle(s) {
  return PAGE_CYCLES[s.cycle_index] || "OFF";
}

function livingPresence(s) {
  return currentCycle(s) === "ON" && s.integrity_ok === true;
}

function cyclePosture(s) {
  return currentCycle(s);
}

function cycleView(s) {
  const current = currentCycle(s);
  return {
    pre_locked: true,
    locked_order: true,
    skip_forbidden: true,
    invent_forbidden: true,
    auto_unlock: false,
    cycles: PAGE_CYCLES.slice(),
    current,
    index: s.cycle_index,
    next: s.cycle_index < PAGE_CYCLES.length - 1 ? PAGE_CYCLES[s.cycle_index + 1] : null,
    terminal: current === "MEMORIAL",
  };
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
  const view = cycleView(s);
  return {
    site_state: currentCycle(s),
    cycle: view.current,
    current: view.current,
    cycle_index: s.cycle_index,
    cycles: PAGE_CYCLES.slice(),
    cycle_path: "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL",
    page_cycle: view,
    OFF: view.current === "OFF",
    integrity: view.current === "integrity",
    ON: view.current === "ON",
    "FULL SHUTDOWN": view.current === "FULL SHUTDOWN",
    MEMORIAL: view.current === "MEMORIAL",
    locked: !living,
    pre_locked: true,
    living_presence: living,
    integrity_ok: s.integrity_ok,
    integrity_ts: s.integrity_ts,
    genesis_keyed: s.genesis_keyed,
    genesis_hash: s.genesis_hash,
    genesis_sealed: true,
    cloud_asleep: false,
    auto_unlock: false,
    completeness: false,
    ranking: false,
    separate_from: "azhub",
    modules: Object.fromEntries(MODULES.map((name) => [name, moduleSurface(s, name)])),
    pipeline: pipelineArch(),
    pipeline_path: pipelineArch().path,
    note: living
      ? "Living presence enabled."
      : "AIH-WP-1.0 pre-locked page cycles: OFF / integrity / ON / FULL SHUTDOWN / MEMORIAL. One step only. No skip. No cloud-asleep availability.",
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
    qns: qnsCrossMap(),
    pipeline: pipelineArch(),
    ...extra,
  };
}

function stubRefuse(op, rec) {
  const reasons = {
    scorch_remote: "Hosted Scorched Earth never remotely wipes user devices. Local stub/advisory only (scorch_local).",
    pair_wipe: "Pair cut is a local dissolve of memorial cites. Hosted Worker never remotely wipes user devices.",
    deanonymize: "AZInterface does not deanonymize. Identity is Aziel Eliab only.",
    vault_read: "Hosted Worker never serves vault contents. Witness list is metadata only.",
    auto_unlock: "Auto-unlock is refused. Cycles advance one explicit step only.",
    unlock: "Unlock is refused. ON requires integrity, then an explicit site_state_set.",
    ranking: "AZInterface does not rank. Witness list is metadata only.",
    rank: "AZInterface does not rank. Witness list is metadata only.",
    completeness_detect: "Completeness detection is refused. Hub/Interface stay separate software.",
    complete: "Completeness is refused.",
    completeness: "Completeness is refused.",
    skip_cycle: "Skip is refused. Cycles are sealed: OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL.",
    invent_cycle: "Invented cycles are refused. Only the five sealed AIH-WP-1.0 cycles exist.",
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

function citeIds(payload) {
  const src = payload && typeof payload === "object" ? payload : {};
  const pairId = String(src.pair_id || src.pair || "").trim().slice(0, ID_CAP);
  const photonId = String(src.photon_id || src.photon || "").trim().slice(0, ID_CAP);
  return { pairId, photonId };
}

function pairPublic(row) {
  return {
    pair_id: row.pair_id,
    photon_id: row.photon_id,
    via: row.via,
    handshake: row.handshake,
    walker_restricted: true,
    packet: "QNS1",
    via_runs_in: "qnsd",
    qnsd: QNSD_BIND,
    spec: QNS_CD,
    handshake_spec: AIH_PAIR,
    vault_contents: false,
    remote_wipe: false,
    untraceable_origin: false,
    transferred: false,
  };
}

function findPair(s, pairId) {
  if (!pairId) return null;
  return s.pairs.find((p) => p.pair_id === pairId) || null;
}

function latestPair(s, handshake) {
  for (let i = s.pairs.length - 1; i >= 0; i--) {
    if (handshake == null || s.pairs[i].handshake === handshake) return s.pairs[i];
  }
  return null;
}

async function pairCycleRefuse(s, op) {
  if (livingPresence(s)) return null;
  const current = currentCycle(s);
  if (current === "MEMORIAL") {
    const rec = await appendReceipt(s, op + "_refused", { reason: "memorial" });
    return base({
      ok: false,
      code: "AIH-CYCLE-TERMINAL",
      refused: true,
      error: "MEMORIAL is terminal. Pair memorial cites remain readable; pair mutate is refused.",
      living_presence: false,
      site_state: current,
      current: current,
      qns_cd: QNS_CD,
      receipt: rec,
      display: displayOf("Memorial is terminal", "QNS pair mutate does not run in MEMORIAL. pair_status still reads cites."),
    });
  }
  if (current === "FULL SHUTDOWN") {
    const rec = await appendReceipt(s, op + "_refused", { reason: "full_shutdown" });
    return base({
      ok: false,
      code: "QNS-CYCLE-REFUSE",
      refused: true,
      error: "QNS pair ops require living presence (ON after integrity). FULL SHUTDOWN refuses pair mutate.",
      living_presence: false,
      site_state: current,
      current: current,
      qns_cd: QNS_CD,
      receipt: rec,
      display: displayOf("Cycle refuses pair", "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL. Pair mutate only at ON."),
    });
  }
  const rec = await appendReceipt(s, op + "_refused", { reason: "pre_locked" });
  return base({
    ok: false,
    code: "PRE_LOCKED",
    error: "QNS pair ops are living-presence acts. Enable ON after integrity.",
    living_presence: false,
    site_state: current,
    receipt: rec,
    display: displayOf("Pre-locked", "pair_offer / pair_accept / pair_seal / pair_cut do not run until ON after integrity."),
  });
}

function viaOrRefuse(payload, existing) {
  const src = payload && typeof payload === "object" ? payload : {};
  const raw = Object.prototype.hasOwnProperty.call(src, "via") ? src.via : src.bearer;
  if (raw == null || raw === "") return { via: existing || "local", error: null };
  const via = normalizeVia(raw);
  if (!via) {
    return {
      via: null,
      error: base({
        ok: false,
        code: "QNS-VIA-UNKNOWN",
        refused: true,
        error: "Walker restriction: only lan/plc/bt/rf/light/qns/operator/local. Vias run in local qnsd.",
        allowed: QNS_VIAS.slice(),
        walker_restricted: true,
        via_runs_in: "qnsd",
        qnsd: QNSD_BIND,
        display: displayOf("Via refused", "Unknown via. Walker cannot invent a hop.", [["allowed", QNS_VIAS.join(",")]]),
      }),
    };
  }
  if (existing && via !== existing) {
    return {
      via: null,
      error: base({
        ok: false,
        code: "QNS-WALKER-RESTRICT",
        refused: true,
        error: "Walker restriction: via cannot change mid-handshake. qnsd owns the hop; Interface cites one via.",
        via: existing,
        requested: via,
        walker_restricted: true,
        via_runs_in: "qnsd",
        qnsd: QNSD_BIND,
        display: displayOf("Walker restricted", "Via is sealed on offer. Packet hops stay in local qnsd.", [["via", existing], ["requested", via]]),
      }),
    };
  }
  return { via, error: null };
}

function pushPairWitness(s, rec, kind, pairId, photonId) {
  const witness = {
    kind,
    hold_id: null,
    hash: rec.hash,
    ts: rec.ts,
    seq: rec.seq,
    vault_contents: false,
  };
  if (pairId) witness.pair_id = pairId;
  if (photonId) witness.photon_id = photonId;
  s.witnesses.push(witness);
  return witness;
}

export async function dispatch(op, payload, _sessionId) {
  payload = payload || {};
  const hit = detectForbiddenEvent(payload);
  if (hit) {
    const rec = await appendReceipt(STATE, "forbidden_refuse", { op, event: hit.kind });
    return base({
      ok: false,
      code: hit.code,
      refused: true,
      event: hit.kind,
      op,
      site_state: currentCycle(STATE),
      current: currentCycle(STATE),
      cycles: PAGE_CYCLES.slice(),
      page_cycle: cycleView(STATE),
      receipt: rec,
      display: displayOf("Refused", hit.code, [["op", op], ["event", hit.kind]]),
    });
  }
  const name = ALIASES[String(op || "").trim().toLowerCase().replace(/-/g, "_")] || String(op || "").trim().toLowerCase().replace(/-/g, "_");
  if (STUB_OPS.includes(name)) {
    const rec = await appendReceipt(STATE, "stub_refuse", { op: name });
    return stubRefuse(name, rec);
  }
  if (!LIVE_OPS.includes(name)) {
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

  if (name === "health") {
    const rec = await appendReceipt(s, "health", { site_state: currentCycle(s) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      runtime_true: true,
      live_ops: LIVE_OPS,
      stub_ops: STUB_OPS,
      ops: OPS,
      site_state: currentCycle(s),
      current: currentCycle(s),
      living_presence: cycle.living_presence,
      catalog_mcp: FRAGGATE_MCP,
      github: GITHUB,
      receipt: rec,
      display: displayOf("AZInterface health", "Custodial operating environment. Interface is CUSTODY — not Hub.", [
        ["version", VERSION],
        ["spec", SPEC],
        ["site_state", currentCycle(s)],
        ["living_presence", cycle.living_presence],
        ["hub_collapse", false],
        ["qns_cd", QNS_CD],
        ["qnsd", QNSD_BIND],
        ["pipeline_owner", "aziel-runtime"],
        ["lambgate", false],
      ]),
    });
  }

  if (name === "skill") {
    return base({ ok: true, markdown: SKILL_MD });
  }

  if (name === "genesis_status") {
    const rec = await appendReceipt(s, "genesis_status", { keyed: s.genesis_keyed });
    const view = cycleView(s);
    return base({
      ok: true,
      keyed: s.genesis_keyed,
      genesis_keyed: s.genesis_keyed,
      genesis_hash: s.genesis_hash,
      genesis_sealed: true,
      cycles_sealed: true,
      cycles: PAGE_CYCLES.slice(),
      page_cycle: view,
      username_stored: false,
      one_time: true,
      receipt: rec,
      display: displayOf("Genesis status", "Five page cycles sealed at genesis. Username hash is one-time and never stored.", [
        ["keyed", s.genesis_keyed],
        ["genesis_hash", s.genesis_hash || ""],
        ["genesis_sealed", true],
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
    const rec = await appendReceipt(s, "site_state_get", { site_state: currentCycle(s) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      site_state: currentCycle(s),
      current: currentCycle(s),
      allowed: SITE_STATES.slice(),
      living_presence: cycle.living_presence,
      cycle,
      page_cycle: cycle.page_cycle,
      receipt: rec,
      display: displayOf("Site state", `Current posture ${currentCycle(s)}. Living presence only at ON after integrity.`, [
        ["site_state", currentCycle(s)],
        ["living_presence", cycle.living_presence],
      ]),
    });
  }

  if (name === "site_state_set") {
    const wanted = normalizeCycle(payload.cycle || payload.state || payload.site_state || payload.page_cycle || payload.to);
    if (!wanted) {
      return base({
        ok: false,
        code: "AIH-CYCLE-UNKNOWN",
        refused: true,
        error: "Only the five pre-locked cycles are accepted: OFF, integrity, ON, FULL SHUTDOWN, MEMORIAL.",
        allowed: PAGE_CYCLES.slice(),
        site_state: currentCycle(s),
        current: currentCycle(s),
        page_cycle: cycleView(s),
      });
    }
    const target = cycleIndexOf(wanted);
    const current = s.cycle_index;
    if (target === current) {
      const rec = await appendReceipt(s, "site_state_set", { unchanged: wanted });
      const cycle = pageCycleSnapshot(s);
      return base({
        ok: true,
        unchanged: true,
        site_state: currentCycle(s),
        current: currentCycle(s),
        living_presence: cycle.living_presence,
        cycle,
        page_cycle: cycle.page_cycle,
        receipt: rec,
        display: displayOf("Site state unchanged", `Already ${wanted}.`, [["current", wanted]]),
      });
    }
    if (PAGE_CYCLES[current] === "MEMORIAL") {
      const rec = await appendReceipt(s, "site_state_set_refused", { wanted, reason: "terminal" });
      return base({
        ok: false,
        code: "AIH-CYCLE-TERMINAL",
        refused: true,
        error: "MEMORIAL is terminal. Page cycles stay pre-locked.",
        site_state: currentCycle(s),
        current: currentCycle(s),
        living_presence: false,
        page_cycle: cycleView(s),
        receipt: rec,
        display: displayOf("Memorial is terminal", "Cannot leave MEMORIAL. Cycles stay pre-locked."),
      });
    }
    if (target !== current + 1) {
      const rec = await appendReceipt(s, "site_state_set_refused", { wanted, reason: "locked_order" });
      const view = cycleView(s);
      return base({
        ok: false,
        code: "AIH-CYCLE-LOCKED",
        refused: true,
        error: "Pre-locked cycles advance one step only. Auto-unlock / skip / invent stay refused.",
        requested: wanted,
        site_state: currentCycle(s),
        current: currentCycle(s),
        living_presence: false,
        need_integrity: wanted === "ON" && !s.integrity_ok,
        page_cycle: view,
        receipt: rec,
        display: displayOf("Cycle locked", "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL. One step only.", [
          ["current", currentCycle(s)],
          ["requested", wanted],
          ["next", view.next || ""],
        ]),
      });
    }
    if (wanted === "ON" && !s.integrity_ok) {
      const rec = await appendReceipt(s, "site_state_set_refused", { wanted: "ON", reason: "need_integrity" });
      return base({
        ok: false,
        code: "AIH-INTEGRITY-REQUIRED",
        refused: true,
        error: "ON requires a passing integrity_check. Auto-unlock is refused.",
        site_state: currentCycle(s),
        current: currentCycle(s),
        living_presence: false,
        need_integrity: true,
        page_cycle: cycleView(s),
        receipt: rec,
        display: displayOf("Integrity required", "ON requires a passing integrity check. Integrity does not auto-unlock to ON.", [
          ["site_state", currentCycle(s)],
          ["integrity_ok", false],
        ]),
      });
    }
    const prev = currentCycle(s);
    s.cycle_index = target;
    const rec = await appendReceipt(s, "site_state_set", { from: prev, to: wanted, living: livingPresence(s) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      advanced: true,
      site_state: currentCycle(s),
      current: currentCycle(s),
      previous: prev,
      living_presence: cycle.living_presence,
      cycle,
      page_cycle: cycle.page_cycle,
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
      const rec = await appendReceipt(s, "integrity_fail", { ok: false });
      return base({
        ok: false,
        code: "INTEGRITY_FAIL",
        integrity_ok: false,
        living_presence: false,
        site_state: currentCycle(s),
        current: currentCycle(s),
        page_cycle: cycleView(s),
        receipt: rec,
        display: displayOf("Integrity failed", "Cycle remains pre-locked. ON is refused."),
      });
    }
    const digest = await sha256Hex(`azinterface|integrity|${SPEC}|${s.genesis_hash || "ungekeyed"}|${s.receipts.length ? s.receipts[s.receipts.length - 1].hash : ZERO}`);
    s.integrity_ok = true;
    s.integrity_ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    s.integrity_digest = digest;
    const witnessId = String(payload.witness || payload.witness_id || payload.id || "").trim().slice(0, ID_CAP);
    const label = String(payload.label || payload.note || "").trim().slice(0, LABEL_CAP);
    if (witnessId && s.witnesses.length < WITNESS_CAP && !s.witnesses.some((w) => w.id === witnessId)) {
      s.witnesses.push({
        id: witnessId,
        kind: "integrity",
        label: label || witnessId,
        hold_id: null,
        hash: digest,
        ts: s.integrity_ts,
        vault_contents: false,
      });
    }
    if (currentCycle(s) === "OFF") s.cycle_index = cycleIndexOf("integrity");
    const rec = await appendReceipt(s, "integrity_check", { ok: true, digest_prefix: digest.slice(0, 16) });
    const cycle = pageCycleSnapshot(s);
    return base({
      ok: true,
      integrity_ok: true,
      integrity_digest: digest,
      integrity_ts: s.integrity_ts,
      site_state: currentCycle(s),
      current: currentCycle(s),
      living_presence: cycle.living_presence,
      cycle,
      page_cycle: cycle.page_cycle,
      witnesses: s.witnesses.length,
      receipt: rec,
      display: displayOf("Integrity passed", "Integrity recorded. Does not auto-unlock to ON.", [
        ["integrity_ok", true],
        ["current", currentCycle(s)],
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
        ["pipeline", cycle.pipeline_path || ""],
        ["4dmap", "Domain Door inspection — not a sequential gate"],
      ]),
    });
  }

  if (name === "pipeline_arch") {
    const rec = await appendReceipt(s, "pipeline_arch", { locked: true });
    const pipe = pipelineArch();
    return base({
      ok: true,
      ...pipe,
      receipt: rec,
      display: displayOf("LOCKED pipeline", pipe.note, [
        ["path", pipe.path],
        ["owner", pipe.owner],
        ["lambgate", false],
        ["4dmap", "Domain Door inspection"],
        ["software_tab", false],
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
        site_state: currentCycle(s),
        receipt: rec,
        display: displayOf("Pre-locked", "Hold does not run until ON after integrity."),
      });
    }
    const label = String(payload.label || payload.name || "hold").trim().slice(0, 80);
    const labelHash = await sha256Hex(`azinterface|hold|${label}`);
    const holdId = "hold-" + labelHash.slice(0, 12);
    const cites = citeIds(payload);
    const row = { hold_id: holdId, label_hash: labelHash, status: "held", vault_contents: false };
    if (cites.pairId) row.pair_id = cites.pairId;
    if (cites.photonId) row.photon_id = cites.photonId;
    s.holds.push(row);
    const rec = await appendReceipt(s, "hold", { hold_id: holdId, label_hash: labelHash, pair_id: cites.pairId || null, photon_id: cites.photonId || null });
    const witness = { kind: "hold", hold_id: holdId, hash: rec.hash, ts: rec.ts, seq: rec.seq, vault_contents: false };
    if (cites.pairId) witness.pair_id = cites.pairId;
    if (cites.photonId) witness.photon_id = cites.photonId;
    s.witnesses.push(witness);
    const fields = [
      ["hold_id", holdId],
      ["status", "held"],
      ["vault_contents", false],
    ];
    if (cites.pairId) fields.push(["pair_id", cites.pairId]);
    if (cites.photonId) fields.push(["photon_id", cites.photonId]);
    return base({
      ok: true,
      hold: row,
      witness,
      vault_contents: false,
      display: displayOf("Hold", "Custody hold recorded. Label hashed. Pair/photon cites only — vault contents not stored.", fields),
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
        site_state: currentCycle(s),
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

  if (name === "pair_offer") {
    const gated = await pairCycleRefuse(s, "pair_offer");
    if (gated) return gated;
    const viaHit = viaOrRefuse(payload);
    if (viaHit.error) return viaHit.error;
    if (s.pairs.length >= PAIR_CAP) {
      return base({ ok: false, code: "PAIR_CAP", error: "Pair memorial cap reached. Witness list is metadata only." });
    }
    const cites = citeIds(payload);
    let pairId = cites.pairId;
    if (!pairId) {
      const seed = await sha256Hex(`azinterface|qns|${QNS_CD}|${viaHit.via}|${s.receipts.length ? s.receipts[s.receipts.length - 1].hash : ZERO}|${s.pairs.length}`);
      pairId = "pair-" + seed.slice(0, 12);
    }
    if (findPair(s, pairId)) {
      return base({
        ok: false,
        code: "PAIR_EXISTS",
        error: "pair_id already memorialized. Use pair_accept / pair_seal / pair_cut.",
        pair_id: pairId,
      });
    }
    let photonId = cites.photonId;
    if (!photonId) {
      photonId = "qns1-" + (await sha256Hex(`azinterface|photon|${pairId}|${viaHit.via}`)).slice(0, 12);
    }
    const row = { pair_id: pairId, photon_id: photonId, via: viaHit.via, handshake: "OFFER", vault_contents: false };
    s.pairs.push(row);
    const rec = await appendReceipt(s, "pair_offer", { pair_id: pairId, photon_id: photonId, via: viaHit.via });
    const witness = pushPairWitness(s, rec, "pair_offer", pairId, photonId);
    return base({
      ok: true,
      pair: pairPublic(row),
      handshake: "OFFER",
      witness,
      vault_contents: false,
      remote_wipe: false,
      display: displayOf("Pair OFFER", "AIH-WP-1.3 offer recorded. QNS1 via cite only — qnsd on 127.0.0.1 runs the hop.", [
        ["pair_id", pairId],
        ["photon_id", photonId],
        ["via", viaHit.via],
        ["handshake", "OFFER"],
      ]),
    });
  }

  if (name === "pair_accept") {
    const gated = await pairCycleRefuse(s, "pair_accept");
    if (gated) return gated;
    const cites = citeIds(payload);
    const target = cites.pairId ? findPair(s, cites.pairId) : latestPair(s, "OFFER");
    if (!target) {
      return base({
        ok: false,
        code: "PAIR_NOT_FOUND",
        error: "No matching OFFER. pair_status lists pair_id cites only — never vault contents.",
        vault_contents: false,
      });
    }
    if (target.handshake !== "OFFER") {
      return base({
        ok: false,
        code: "QNS-HANDSHAKE-LOCKED",
        refused: true,
        error: "AIH-WP-1.3 handshake is OFFER → ACCEPT → SEAL. Accept only from OFFER.",
        pair: pairPublic(target),
        display: displayOf("Handshake locked", "Accept only from OFFER.", [["handshake", target.handshake || ""]]),
      });
    }
    const viaHit = viaOrRefuse(payload, target.via);
    if (viaHit.error) return viaHit.error;
    if (cites.photonId) target.photon_id = cites.photonId;
    target.handshake = "ACCEPT";
    const rec = await appendReceipt(s, "pair_accept", { pair_id: target.pair_id, photon_id: target.photon_id, via: target.via });
    const witness = pushPairWitness(s, rec, "pair_accept", target.pair_id, target.photon_id);
    return base({
      ok: true,
      pair: pairPublic(target),
      handshake: "ACCEPT",
      witness,
      vault_contents: false,
      remote_wipe: false,
      display: displayOf("Pair ACCEPT", "AIH-WP-1.3 accept recorded. Via still cited; qnsd runs the packet.", [
        ["pair_id", target.pair_id],
        ["photon_id", target.photon_id || ""],
        ["handshake", "ACCEPT"],
      ]),
    });
  }

  if (name === "pair_seal") {
    const gated = await pairCycleRefuse(s, "pair_seal");
    if (gated) return gated;
    const cites = citeIds(payload);
    const target = cites.pairId ? findPair(s, cites.pairId) : latestPair(s, "ACCEPT");
    if (!target) {
      return base({
        ok: false,
        code: "PAIR_NOT_FOUND",
        error: "No matching ACCEPT. Seal only after accept. Witness list is metadata only.",
        vault_contents: false,
      });
    }
    if (target.handshake !== "ACCEPT") {
      return base({
        ok: false,
        code: "QNS-HANDSHAKE-LOCKED",
        refused: true,
        error: "AIH-WP-1.3 handshake is OFFER → ACCEPT → SEAL. Seal only from ACCEPT.",
        pair: pairPublic(target),
        display: displayOf("Handshake locked", "Seal only from ACCEPT.", [["handshake", target.handshake || ""]]),
      });
    }
    const viaHit = viaOrRefuse(payload, target.via);
    if (viaHit.error) return viaHit.error;
    target.handshake = "SEAL";
    const rec = await appendReceipt(s, "pair_seal", { pair_id: target.pair_id, photon_id: target.photon_id, via: target.via });
    const witness = pushPairWitness(s, rec, "pair_seal", target.pair_id, target.photon_id);
    return base({
      ok: true,
      pair: pairPublic(target),
      handshake: "SEAL",
      witness,
      memorial: true,
      vault_contents: false,
      remote_wipe: false,
      display: displayOf("Pair SEAL", "Pair memorial sealed. Interface holds cites only. qnsd on 127.0.0.1 owns the via.", [
        ["pair_id", target.pair_id],
        ["photon_id", target.photon_id || ""],
        ["handshake", "SEAL"],
      ]),
    });
  }

  if (name === "pair_cut") {
    const gated = await pairCycleRefuse(s, "pair_cut");
    if (gated) return gated;
    const cites = citeIds(payload);
    let target = cites.pairId ? findPair(s, cites.pairId) : null;
    if (!target) {
      for (let i = s.pairs.length - 1; i >= 0; i--) {
        if (s.pairs[i].handshake !== "CUT") {
          target = s.pairs[i];
          break;
        }
      }
    }
    if (!target) {
      return base({
        ok: false,
        code: "PAIR_NOT_FOUND",
        error: "No living pair to cut. Cut is a dissolve — not a remote wipe.",
        vault_contents: false,
        remote_wipe: false,
      });
    }
    if (target.handshake === "CUT") {
      const rec = await appendReceipt(s, "pair_cut", { unchanged: target.pair_id });
      return base({
        ok: true,
        unchanged: true,
        pair: pairPublic(target),
        handshake: "CUT",
        remote_wipe: false,
        receipt: rec,
        display: displayOf("Pair already cut", "Memorial cite remains. No remote wipe.", [["pair_id", target.pair_id]]),
      });
    }
    const prev = target.handshake;
    target.handshake = "CUT";
    const rec = await appendReceipt(s, "pair_cut", { pair_id: target.pair_id, photon_id: target.photon_id, from: prev });
    const witness = pushPairWitness(s, rec, "pair_cut", target.pair_id, target.photon_id);
    return base({
      ok: true,
      pair: pairPublic(target),
      handshake: "CUT",
      previous: prev,
      witness,
      vault_contents: false,
      remote_wipe: false,
      local_only: true,
      display: displayOf("Pair CUT", "Pair dissolved. Memorial cite kept. Hosted Worker never remotely wipes devices.", [
        ["pair_id", target.pair_id],
        ["from", prev || ""],
        ["remote_wipe", false],
      ]),
    });
  }

  if (name === "pair_status") {
    const rec = await appendReceipt(s, "pair_status", { count: s.pairs.length });
    const rows = s.pairs.map((p) => pairPublic(p));
    return base({
      ok: true,
      pairs: rows,
      count: rows.length,
      vault_contents: false,
      remote_wipe: false,
      living_presence: livingPresence(s),
      site_state: currentCycle(s),
      receipt: rec,
      display: displayOf("Pair memorial", "QNS-CD pair cites only. Vias run in local qnsd. Vault contents are never listed.", [
        ["count", rows.length],
        ["qnsd", QNSD_BIND],
        ["vault_contents", false],
        ["softwares_tab_qns", false],
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
