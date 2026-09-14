/**
 * Live Nodes strip — QNM-BUILD-1.0 rollup + QNS-CD-1.0 cite.
 * Read-only Mesh ON / Live Nodes. GET never enables. Not a Node Gate.
 * QNS1 vias run in local qnsd (127.0.0.1). Interface holds pair memorial.
 *
 * Locked fabric law (this Worker encodes; local qnm-node executes):
 *   SPLIT THE WIRES — two planes, never one socket.
 *   COLD-COPY SURVIVAL — multiply cold copies; live body sync refused.
 *   REHEAL refuse — isolate + local phoenix; no neighbor vote-to-fix.
 *
 * Author: Aziel Eliab only.
 */

export const QNS_CD = "QNS-CD-1.0";
export const QNM_BUILD = "QNM-BUILD-1.0";
export const QNSD_BIND = "127.0.0.1";

export const SPLIT_THE_WIRES = "SPLIT THE WIRES";
export const SPLIT_THE_WIRES_SPEC = "STW-1.0";
export const COLD_COPY_SURVIVAL = "COLD-COPY SURVIVAL";
export const COLD_COPY_SPEC = "CCS-1.0";
export const REHEAL = "REHEAL";
export const REHEAL_SPEC = "REHEAL-REFUSE";
export const MESH_LAW_AUTHOR = "Aziel Eliab only";
export const STW_DOC = "https://github.com/AzielEliab/azinterface/blob/main/docs/SPLIT-THE-WIRES.md";

export const TIP_TICK_MS_MIN = 500;
export const TIP_TICK_MS_MAX = 1000;
export const GATE_DWELL_S = 777;
export const TIP_SOCKET = "tip-tick-1s";
export const GATE_SOCKET = "gate-777";
export const TIP_FIELDS = Object.freeze(["presence", "tip_hash"]);
export const TIP_PRESENCE = Object.freeze(["live", "locked", "isolated"]);
export const REHEAL_ALLOWED = Object.freeze(["live", "locked", "isolated", "tip-hash"]);
export const TIP_HASH_HEX_LEN = 64;
export const TIP_PRESENCE_PAD = 8;
export const TIP_TICK_FIXED_CHARS = TIP_PRESENCE_PAD + TIP_HASH_HEX_LEN;
export const HEX64 = /^[0-9a-f]{64}$/i;

export const SPLIT_THE_WIRES_LAW = Object.freeze({
  law: SPLIT_THE_WIRES,
  spec: SPLIT_THE_WIRES_SPEC,
  author: MESH_LAW_AUTHOR,
  tip: Object.freeze({
    plane: "tip",
    socket: TIP_SOCKET,
    interval_ms_min: TIP_TICK_MS_MIN,
    interval_ms_max: TIP_TICK_MS_MAX,
    fields: TIP_FIELDS,
    fixed_size: true,
    fixed_chars: TIP_TICK_FIXED_CHARS,
    payload: false,
  }),
  payload: Object.freeze({
    plane: "payload",
    socket: GATE_SOCKET,
    mode: "pull-only",
    push: false,
  }),
  update: Object.freeze({
    kind: "proof",
    not: "timer",
    cite_prev: true,
    lockset: true,
    fail_closed: true,
    dwell_s: GATE_DWELL_S,
    clock_desync_is_yes: false,
    ambiguous: "isolate",
  }),
  equivocation: "ends-peer",
  emit_last: "locally",
  phoenix: "local-only",
  partition: "no-auto-splice",
  heartbeat_loss: Object.freeze({
    poison: false,
    apply_last_packet: false,
  }),
  sockets_shared: false,
});

export const COLD_COPY_LAW = Object.freeze({
  law: COLD_COPY_SURVIVAL,
  spec: COLD_COPY_SPEC,
  author: MESH_LAW_AUTHOR,
  multiply_cold_copies: true,
  live_body_sync: false,
  tip_expensive_to_erase: true,
  server_pull_wipes_cold: false,
  hash_absolute_poison_refuse: true,
  data_outlives_creators: true,
});

export const REHEAL_LAW = Object.freeze({
  law: REHEAL,
  spec: REHEAL_SPEC,
  author: MESH_LAW_AUTHOR,
  refuse: true,
  isolate: true,
  phoenix: "local-only",
  neighbor_vote_to_fix: false,
  allowed: REHEAL_ALLOWED,
});

export function isTipTickInterval(ms) {
  const n = Number(ms);
  return Number.isFinite(n) && n >= TIP_TICK_MS_MIN && n <= TIP_TICK_MS_MAX;
}

export function socketsMustSplit(tipSocket, gateSocket) {
  if (!tipSocket || !gateSocket) {
    return { ok: false, code: "STW-SOCKET-MISSING", shared: false };
  }
  if (tipSocket === gateSocket) {
    return { ok: false, code: "STW-SOCKET-SHARED", shared: true };
  }
  return { ok: true, shared: false, tip: tipSocket, gate: gateSocket };
}

export function encodeTipTick(input) {
  const src = input && typeof input === "object" ? input : {};
  const extras = Object.keys(src).filter((k) => !TIP_FIELDS.includes(k));
  if (extras.length) {
    return { ok: false, code: "STW-TIP-PAYLOAD", extras };
  }
  if (src.payload != null || src.body != null || src.bytes != null) {
    return { ok: false, code: "STW-TIP-PAYLOAD" };
  }
  const presence = String(src.presence || "");
  const tipHash = String(src.tip_hash || "");
  if (!TIP_PRESENCE.includes(presence)) {
    return { ok: false, code: "STW-TIP-PRESENCE" };
  }
  if (!HEX64.test(tipHash)) {
    return { ok: false, code: "STW-TIP-HASH" };
  }
  const wire = presence.padEnd(TIP_PRESENCE_PAD, " ") + tipHash.toLowerCase();
  if (wire.length !== TIP_TICK_FIXED_CHARS) {
    return { ok: false, code: "STW-TIP-SIZE" };
  }
  return {
    ok: true,
    plane: "tip",
    socket: TIP_SOCKET,
    presence,
    tip_hash: tipHash.toLowerCase(),
    wire,
    bytes: TIP_TICK_FIXED_CHARS,
    fixed_size: true,
  };
}

export function payloadPlane() {
  return {
    ok: true,
    plane: "payload",
    socket: GATE_SOCKET,
    mode: "pull-only",
    push: false,
    live_body_sync: false,
  };
}

export function mayPushPayload() {
  return false;
}

export function judgeUpdate(input) {
  const src = input && typeof input === "object" ? input : {};
  if (src.ambiguous === true) {
    return { ok: false, action: "isolate", code: "STW-AMBIGUOUS-ISOLATE" };
  }
  if (src.clock_desync === true) {
    return { ok: false, action: "no", code: "STW-CLOCK-DESYNC", yes: false };
  }
  const citePrev = typeof src.cite_prev === "string" && HEX64.test(src.cite_prev);
  const lockset = src.lockset === true || (typeof src.lockset === "string" && src.lockset.length > 0);
  if (src.timer_only === true || !citePrev || !lockset) {
    return { ok: false, action: "fail-closed", code: "STW-UPDATE-FAIL-CLOSED", kind: "proof", not: "timer" };
  }
  if (Number.isFinite(Number(src.now_s)) && Number.isFinite(Number(src.last_valid_cite_s))) {
    const elapsed = Number(src.now_s) - Number(src.last_valid_cite_s);
    if (elapsed < GATE_DWELL_S) {
      return {
        ok: false,
        action: "dwell",
        code: "STW-GATE-DWELL",
        dwell_s: GATE_DWELL_S,
        remain_s: GATE_DWELL_S - elapsed,
      };
    }
  }
  return { ok: true, action: "apply-proof", kind: "proof", not: "timer", cite_prev: true, lockset: true };
}

export function judgeHeartbeatLoss() {
  return {
    ok: true,
    loss: true,
    poison: false,
    apply_last_packet: false,
    action: "loss-only",
    code: "STW-HEARTBEAT-LOSS",
  };
}

export function judgeEquivocation(tips) {
  const rows = Array.isArray(tips) ? tips : [];
  const seen = new Map();
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const height = String(row.height ?? row.seq ?? "");
    const hash = String(row.tip_hash || row.hash || "").toLowerCase();
    if (!height || !hash) continue;
    if (seen.has(height) && seen.get(height) !== hash) {
      return { ok: false, action: "end-peer", code: "STW-EQUIVOCATION" };
    }
    seen.set(height, hash);
  }
  return { ok: true, action: "hold", code: "STW-OK" };
}

export function judgeEmitLast() {
  return { ok: true, scope: "locally", rebroadcast: false, apply_remote: false, code: "STW-EMIT-LAST-LOCAL" };
}

export function judgePhoenix(input) {
  const src = input && typeof input === "object" ? input : {};
  if (src.reheal === true || src.vote_to_fix === true || src.neighbor_vote === true) {
    return { ok: false, scope: "local-only", isolate: true, hunt: false, code: "REHEAL-REFUSE" };
  }
  if (src.hunt === true || src.controller === true || src.scope === "remote") {
    return { ok: false, scope: "local-only", hunt: false, code: "STW-PHOENIX-HUNT-REFUSE" };
  }
  return { ok: true, scope: "local-only", hunt: false, code: "STW-PHOENIX-LOCAL" };
}

export function rehealSurfaceAllows(token) {
  const raw = String(token || "").toLowerCase();
  const mapped = raw === "tip_hash" || raw === "tiphash" ? "tip-hash" : raw;
  return REHEAL_ALLOWED.includes(mapped);
}

export function judgeRehealSurface(fields) {
  const list = Array.isArray(fields) ? fields : [];
  const bad = list.filter((field) => !rehealSurfaceAllows(field));
  if (bad.length) {
    return { ok: false, refuse: true, allowed: REHEAL_ALLOWED.slice(), extras: bad, code: "REHEAL-SURFACE-REFUSE" };
  }
  return { ok: true, allowed: REHEAL_ALLOWED.slice(), extras: [], code: "REHEAL-SURFACE-OK" };
}

export function judgeReheal(input) {
  const src = input && typeof input === "object" ? input : {};
  const vote = src.neighbor_vote === true || src.vote_to_fix === true || src.neighbors_fix === true;
  return {
    ok: false,
    refuse: true,
    isolate: true,
    phoenix: "local-only",
    neighbor_vote_to_fix: false,
    allowed: REHEAL_ALLOWED.slice(),
    code: vote ? "REHEAL-VOTE-REFUSE" : "REHEAL-REFUSE",
  };
}

export function judgePartition() {
  return { ok: true, auto_splice: false, action: "no-auto-splice", code: "STW-NO-AUTO-SPLICE" };
}

export function multiplyColdCopies(copies) {
  const list = Array.isArray(copies) ? copies.slice() : [];
  return {
    ok: true,
    multiply: true,
    count: list.length,
    may_grow: true,
    live_body_only: false,
    code: "CCS-MULTIPLY",
    copies: list,
  };
}

export function judgeLiveBodySync() {
  return { ok: false, refuse: true, live_body_sync: false, code: "CCS-LIVE-BODY-SYNC-REFUSE" };
}

export function tipEraseCost() {
  return { expensive: true, cheap_erase: false, timer_erase: false, code: "CCS-TIP-EXPENSIVE" };
}

export function serverPullCannotWipeCold(replicas, pull) {
  const cold = Array.isArray(replicas) ? replicas.slice() : [];
  const wipe = !!(pull && (pull.wipe === true || pull.delete === true || pull.scorch === true));
  if (wipe) {
    return {
      ok: false,
      wipe: false,
      remain: cold,
      code: "CCS-COLD-WIPE-REFUSE",
    };
  }
  return { ok: true, wipe: false, remain: cold, code: "CCS-COLD-HOLD" };
}

export function judgePoison(input) {
  const src = input && typeof input === "object" ? input : {};
  const got = String(src.hash || "").toLowerCase();
  const expected = String(src.expected || "").toLowerCase();
  if (!HEX64.test(got) || !HEX64.test(expected) || got !== expected) {
    return { ok: false, refuse: true, interpret: false, code: "CCS-POISON-REFUSE" };
  }
  return { ok: true, refuse: false, interpret: false, code: "CCS-HASH-ABSOLUTE" };
}

export function dataOutlivesCreators(input) {
  const src = input && typeof input === "object" ? input : {};
  return {
    ok: true,
    outlives: true,
    creator_absent: src.creator_absent === true,
    creator_death_deletes: false,
    code: "CCS-OUTLIVES",
  };
}

export function meshLaw() {
  return Object.freeze({
    split_the_wires: SPLIT_THE_WIRES_LAW,
    cold_copy_survival: COLD_COPY_LAW,
    reheal: REHEAL_LAW,
    sockets: socketsMustSplit(TIP_SOCKET, GATE_SOCKET),
    doc: STW_DOC,
    author: MESH_LAW_AUTHOR,
  });
}

export const LIVE_NODES_COPY =
  "Live Nodes. QNM-BUILD-1.0 rollup live|locked|isolated. " +
  "SPLIT THE WIRES: 0.5–1s tip tick presence+tip hash only fixed-size; " +
  "payload pull-only second plane; update=proof not timer " +
  "(cite prev+lockset fail-closed; 777s dwell after valid cite; clock desync≠yes; ambiguous=isolate); " +
  "equivocation ends peer; emit last locally; Phoenix local only; partition no auto-splice; " +
  "heartbeat loss≠poison≠apply last packet; 1s loop and 777s gate never share a socket. " +
  "COLD-COPY SURVIVAL: multiply cold copies; refuse live body sync; tip expensive to erase; " +
  "server pull cannot wipe cold replicas; hash-absolute poison refuse; data outlives creators. " +
  "REHEAL refuse: isolate+local phoenix; no neighbor vote-to-fix; allowed live/locked/isolated/tip-hash only. " +
  "QNS-CD-1.0 photon vias run in local qnsd (127.0.0.1). " +
  "AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. " +
  "Presence only — not anonymity. Anon-broadcast is not a publish path. " +
  "GET never enables.";

export function meshStripHtml() {
  return `<div id="nodes">
  <strong>Live Nodes</strong>
  <span id="nodesState" class="on">Mesh ON</span>
  <span id="nodesRollup"></span>
  <div id="nodesList">${LIVE_NODES_COPY}</div>
</div>`;
}

export function meshClientScript() {
  return `
  var MESH_PRODUCT = "azinterface";
  var MESH_LABEL = "AZInterface";
  var LIVE_NODES = ${JSON.stringify(LIVE_NODES_COPY)};
  var SPLIT_THE_WIRES = ${JSON.stringify(SPLIT_THE_WIRES)};
  var COLD_COPY_SURVIVAL = ${JSON.stringify(COLD_COPY_SURVIVAL)};
  var REHEAL = ${JSON.stringify(REHEAL)};
  var TIP_SOCKET = ${JSON.stringify(TIP_SOCKET)};
  var GATE_SOCKET = ${JSON.stringify(GATE_SOCKET)};
  var GATE_DWELL_S = ${GATE_DWELL_S};
  var TIP_TICK_MS_MIN = ${TIP_TICK_MS_MIN};
  var TIP_TICK_MS_MAX = ${TIP_TICK_MS_MAX};
  if (TIP_SOCKET === GATE_SOCKET) throw new Error("STW-SOCKET-SHARED");
  var meshNodeId = "";
  var meshBeatAt = 0;
  var lastTipHash = "";
  var lastPacket = null;
  function meshRollup(j) {
    if (j && j.rollup && typeof j.rollup === "object") {
      var live = Number(j.rollup.live);
      var locked = Number(j.rollup.locked);
      var isolated = Number(j.rollup.isolated);
      if ([live, locked, isolated].some(Number.isFinite)) {
        return { live: Number.isFinite(live) ? live : 0, locked: Number.isFinite(locked) ? locked : 0, isolated: Number.isFinite(isolated) ? isolated : 0 };
      }
    }
    var nodes = (j && j.nodes) || [];
    if (!nodes.length) return null;
    var liveN = 0, lockedN = 0, isolatedN = 0, tagged = false;
    nodes.forEach(function (n) {
      var state = String((n && (n.state || n.status || n.mode || n.presence)) || "").toLowerCase();
      if (!n) return;
      if (n.isolated === true || state === "isolated") { isolatedN += 1; tagged = true; }
      else if (n.locked === true || state === "locked") { lockedN += 1; tagged = true; }
      else if (state === "live" || n.live === true || n.product) { liveN += 1; tagged = true; }
    });
    return tagged ? { live: liveN, locked: lockedN, isolated: isolatedN } : null;
  }
  function tipFromView(j) {
    if (!j || typeof j !== "object") return null;
    var presence = String(j.presence || (j.enabled ? "live" : "") || "").toLowerCase();
    var tip = String(j.tip_hash || j.tip || "");
    return { presence: presence, tip_hash: tip, socket: TIP_SOCKET };
  }
  function paintMesh(j) {
    var stateEl = document.getElementById("nodesState");
    var rollEl = document.getElementById("nodesRollup");
    var listEl = document.getElementById("nodesList");
    if (!stateEl || !rollEl || !listEl) return;
    stateEl.textContent = "Mesh ON";
    stateEl.className = "on";
    if (!j) {
      rollEl.textContent = "";
      listEl.textContent = LIVE_NODES;
      return;
    }
    var roll = meshRollup(j);
    var tip = tipFromView(j);
    if (tip && tip.tip_hash && lastTipHash && tip.tip_hash !== lastTipHash && j.equivocation === true) {
      meshNodeId = "";
      lastPacket = null;
      listEl.textContent = LIVE_NODES;
      return;
    }
    if (tip && tip.tip_hash) lastTipHash = tip.tip_hash;
    rollEl.textContent = roll
      ? ("live " + roll.live + " · locked " + roll.locked + " · isolated " + roll.isolated)
      : ((j.live_nodes || 0) + " live");
    var products = j.products_present || j.products || [];
    var roster = j.nodes || [];
    var labels = roster.length
      ? roster.map(function (n) { return (n && (n.label || n.product || n.node_id)) || ""; }).filter(Boolean)
      : products;
    listEl.textContent = labels.length ? labels.join(" · ") : LIVE_NODES;
  }
  async function meshJson(path, init, socket) {
    if (socket === GATE_SOCKET && path.indexOf("/v1/mesh/") === 0) {
      return { ok: false, code: "CCS-LIVE-BODY-SYNC-REFUSE" };
    }
    var headers = { "user-agent": "Mozilla/5.0" };
    if (init && init.method && init.method !== "GET") headers["content-type"] = "application/json";
    var r = await fetch(path, Object.assign({ headers: headers }, init || {}));
    return r.json();
  }
  async function meshTick() {
    var status;
    try { status = await meshJson("/v1/mesh/status", { method: "GET" }, TIP_SOCKET); } catch (e) { return; }
    var view = status;
    try {
      var extra = await meshJson("/v1/mesh/nodes", { method: "GET" }, TIP_SOCKET);
      if (extra && extra.nodes) view = Object.assign({}, status, extra);
    } catch (e) { /* status is enough */ }
    if (view && (view.reheal === true || view.vote_to_fix === true || view.neighbor_vote === true)) {
      lastPacket = null;
      /* REHEAL refuse: isolate+local phoenix; no neighbor vote-to-fix */
      return;
    }
    paintMesh(view);
    if (!view || !view.enabled) return;
    var now = Date.now();
    if (!meshNodeId) {
      try {
        var joined = await meshJson("/v1/mesh/join", { method: "POST", body: JSON.stringify({ product: MESH_PRODUCT, label: MESH_LABEL, presence: "live" }) }, TIP_SOCKET);
        meshNodeId = (joined.node_id) || (joined.session && joined.session.node_id) || (joined.node && joined.node.node_id) || "";
        meshBeatAt = now;
        if (joined && (joined.nodes || joined.live_nodes != null || joined.rollup)) paintMesh(joined);
      } catch (e) { /* no auto-heal */ }
      return;
    }
    if (now - meshBeatAt >= 60000) {
      try {
        var hb = await meshJson("/v1/mesh/heartbeat", { method: "POST", body: JSON.stringify({ node_id: meshNodeId }) }, TIP_SOCKET);
        meshBeatAt = now;
        if (hb && hb.ok === false && hb.code === "MESH-UNKNOWN-NODE") meshNodeId = "";
        else if (hb && (hb.nodes || hb.live_nodes != null || hb.rollup)) paintMesh(hb);
      } catch (e) {
        lastPacket = null;
        /* heartbeat loss≠poison≠apply last packet; REHEAL refuse isolate+local phoenix; no neighbor vote-to-fix; no auto-heal */
      }
    }
  }
  function meshBoot() {
    meshTick();
    setInterval(meshTick, 20000);
    var leave = function () {
      if (!meshNodeId) return;
      fetch("/v1/mesh/leave", { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify({ node_id: meshNodeId }), keepalive: true }).catch(function () {});
    };
    window.addEventListener("pagehide", leave);
  }
`;
}
