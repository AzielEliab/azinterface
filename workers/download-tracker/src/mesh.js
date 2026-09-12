/**
 * Live Nodes strip — QNM-BUILD-1.0 rollup + QNS-CD-1.0 cite.
 * Read-only Mesh ON / Live Nodes. GET never enables. Not a Node Gate.
 * QNS1 vias run in local qnsd (127.0.0.1). Interface holds pair memorial.
 * Author: Aziel Eliab only.
 */

export const QNS_CD = "QNS-CD-1.0";
export const QNM_BUILD = "QNM-BUILD-1.0";
export const QNSD_BIND = "127.0.0.1";

export const LIVE_NODES_COPY =
  "Live Nodes. QNM-BUILD-1.0 rollup live|locked|isolated. " +
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
  var meshNodeId = "";
  var meshBeatAt = 0;
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
  async function meshJson(path, init) {
    var headers = { "user-agent": "Mozilla/5.0" };
    if (init && init.method && init.method !== "GET") headers["content-type"] = "application/json";
    var r = await fetch(path, Object.assign({ headers: headers }, init || {}));
    return r.json();
  }
  async function meshTick() {
    var status;
    try { status = await meshJson("/v1/mesh/status"); } catch (e) { return; }
    var view = status;
    try {
      var extra = await meshJson("/v1/mesh/nodes");
      if (extra && extra.nodes) view = Object.assign({}, status, extra);
    } catch (e) { /* status is enough */ }
    paintMesh(view);
    if (!view || !view.enabled) return;
    var now = Date.now();
    if (!meshNodeId) {
      try {
        var joined = await meshJson("/v1/mesh/join", { method: "POST", body: JSON.stringify({ product: MESH_PRODUCT, label: MESH_LABEL, presence: "live" }) });
        meshNodeId = (joined.node_id) || (joined.session && joined.session.node_id) || (joined.node && joined.node.node_id) || "";
        meshBeatAt = now;
        if (joined && (joined.nodes || joined.live_nodes != null || joined.rollup)) paintMesh(joined);
      } catch (e) { /* no auto-heal */ }
      return;
    }
    if (now - meshBeatAt >= 60000) {
      try {
        var hb = await meshJson("/v1/mesh/heartbeat", { method: "POST", body: JSON.stringify({ node_id: meshNodeId }) });
        meshBeatAt = now;
        if (hb && hb.ok === false && hb.code === "MESH-UNKNOWN-NODE") meshNodeId = "";
        else if (hb && (hb.nodes || hb.live_nodes != null || hb.rollup)) paintMesh(hb);
      } catch (e) { /* no auto-heal */ }
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
