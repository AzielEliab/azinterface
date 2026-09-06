/** Hosted AZInterface homepage: counted download + pre-locked custody UI. */
import { LIMITATION } from "./engine.js";

const HOST = "https://azinterface-download-tracker.vibelock.workers.dev";
const INSTALL_LINE = `curl -fsSL ${HOST}/install.sh | bash`;
const SIGIL = "https://www.azielcorpuslibrary.net/sigil.png";
const ASSET = "azinterface-0.1.0.tar.gz";

export function homeHtml({ views, downloads, github }) {
  const v = Number(views || 0).toLocaleString("en-US");
  const n = Number(downloads || 0).toLocaleString("en-US");
  const gh = github || {};
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZInterface — Aziel Eliab</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"AZInterface","author":{"@type":"Person","name":"Aziel Eliab"},"codeRepository":"https://github.com/AzielEliab/azinterface","downloadUrl":"${HOST}/download","license":"https://www.apache.org/licenses/LICENSE-2.0","url":"${HOST}/","description":"AZInterface (AIH-WP-1.0) custodial operating environment by Aziel Eliab. Not AZHub."}
</script>
<style>
:root { color-scheme: dark; --bg:#0b0b0b; --card:#141414; --gold:#c9a227; --gold-dim:#8a7219; --ivory:#e8e0d0; --muted:#9a927e; --line:#2a2414; --ok:#7dcf9a; --alert:#ffb4b4; }
* { box-sizing: border-box; }
body { margin:0; font:15px/1.45 system-ui,sans-serif; background:var(--bg); color:var(--ivory); }
header { display:flex; align-items:center; gap:12px; padding:14px 18px; border-bottom:1px solid var(--gold); }
header img { width:40px; height:40px; }
h1 { margin:0; font-size:1.4rem; color:var(--gold); }
.motto { color:var(--muted); font-size:.9rem; }
.banner { margin:12px 18px 0; border:1px solid #5c4a1a; background:#241c0d; color:#f0d78c; padding:.75rem 1rem; border-radius:8px; font-size:.88rem; }
.nums { display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin:12px 18px; }
.count { background:var(--card); border:1px solid var(--gold-dim); border-radius:12px; padding:12px; font-size:2rem; font-weight:700; }
.count span { display:block; font-size:.9rem; font-weight:500; color:var(--muted); }
.btns { display:grid; grid-template-columns:1fr 1fr; gap:.75rem; margin:0 18px 1rem; }
@media (max-width:720px){ .btns,.nums,.grid{grid-template-columns:1fr;} }
a.btn, button.btn { display:block; text-align:center; font:inherit; font-weight:750; padding:1rem; border-radius:10px; border:0; cursor:pointer; text-decoration:none; }
a.btn.primary { background:var(--ivory); color:#0b0b0b; }
button.btn.install { background:var(--gold); color:#14110a; }
.iso { margin:0 18px 1rem; color:#7d8696; font-size:.85rem; }
.iso a { color:#c9d4ff; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 18px 1rem; }
.card { background:var(--card); border:1px solid var(--gold-dim); border-radius:12px; padding:12px; }
h2 { margin:0 0 .5rem; font-size:1.05rem; color:var(--gold); }
.row { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
button.act { background:var(--gold); color:#14110a; border:0; border-radius:8px; padding:.5rem .85rem; font-weight:700; cursor:pointer; }
button.ghost { background:transparent; color:var(--gold); border:1px solid var(--gold-dim); border-radius:8px; padding:.5rem .85rem; cursor:pointer; }
button.danger { background:transparent; color:var(--alert); border:1px solid #b54a4a; border-radius:8px; padding:.5rem .85rem; cursor:pointer; }
label { display:block; font-size:.8rem; color:var(--muted); margin:.4rem 0 .2rem; }
input { width:100%; background:#1a1a1a; color:var(--ivory); border:1px solid var(--line); border-radius:8px; padding:.5rem .6rem; font:inherit; }
pre { white-space:pre-wrap; word-break:break-word; font-size:.78rem; color:#cfc6ad; min-height:2.4rem; }
.lock { border:1px dashed var(--gold-dim); color:var(--muted); padding:1rem; border-radius:10px; text-align:center; }
.lock.on { border-style:solid; color:var(--ivory); }
.badge { display:inline-block; font-size:.75rem; font-weight:700; padding:.15rem .5rem; border-radius:999px; border:1px solid var(--gold-dim); color:var(--gold); }
#nodes { display:flex; align-items:center; gap:10px; padding:6px 18px; border-bottom:1px solid var(--gold); background:#0f0f0f; flex-wrap:wrap; color:var(--muted); font-size:12px; }
#nodes strong { color:var(--gold); font-weight:700; }
#nodes .off, #nodes .on { color:var(--gold); }
#nodesList { flex:1; min-width:12rem; }
footer { padding:12px 18px 28px; color:var(--muted); font-size:.82rem; }
footer a { color:var(--gold); }
</style>
</head>
<body>
<header>
  <img src="${SIGIL}" alt="Aziel Eliab sigil">
  <div>
    <h1>AZInterface</h1>
    <div class="motto">AIH-WP-1.0 custodial operating environment. Interface is CUSTODY — never Hub. Author: Aziel Eliab only.</div>
  </div>
</header>
<div id="nodes">
  <strong>Live Nodes</strong>
  <span id="nodesState" class="off">Mesh OFF</span>
  <span id="nodesRollup"></span>
  <div id="nodesList">Default off until runtime enable. QNM-BUILD-1.0 rollup live|locked|isolated. AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. Presence only — not anonymity. Anon-broadcast is not a publish path.</div>
</div>
<p class="banner">${LIMITATION}</p>
<div class="nums">
  <div class="count">${v}<span>Views</span></div>
  <div class="count">${n}<span>Downloads</span></div>
</div>
<div class="btns">
  <a class="btn primary" href="/download?asset=${ASSET}">Download ${ASSET}</a>
  <button class="btn install" id="install-btn" type="button">One-click install</button>
</div>
<pre class="iso" id="install-cmd">${INSTALL_LINE}
Then run: azinterface ui  →  http://127.0.0.1:8880 (this computer only).</pre>
<p class="iso">Isolated counter: Worker <code>azinterface-download-tracker</code>, KV AZINTERFACE_DOWNLOADS. /v1 does not increment.
<strong>Human UI is this page.</strong> AI / MCP path is FragGate only:
<code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code> body <code>{"slug":"azinterface","op":"…","payload":{}}</code>.
GitHub stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0}.
<a href="/count">/count</a> · <a href="/stats">/stats</a> · <a href="/v1/skill">Skill</a> · <a href="/ai">AI / FragGate</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="https://github.com/AzielEliab/azinterface">GitHub</a> · <a href="https://github.com/AzielEliab/azhub">AZHub (separate software)</a></p>

<div class="grid">
  <div class="card">
    <h2>Site state</h2>
    <p>Sealed cycle: <strong>OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL</strong>. One step only. No skip. Living presence only at ON after integrity. No cloud-asleep availability.</p>
    <p>State <span class="badge" id="state-badge">OFF</span> · living <span class="badge" id="live-badge">false</span></p>
    <div class="row">
      <button class="act" data-state="ON" type="button">ON</button>
      <button class="ghost" data-state="OFF" type="button">OFF</button>
      <button class="danger" data-state="FULL_SHUTDOWN" type="button">FULL SHUTDOWN</button>
      <button class="ghost" data-state="MEMORIAL" type="button">MEMORIAL</button>
    </div>
    <pre id="state-out"></pre>
  </div>
  <div class="card">
    <h2>Integrity loop</h2>
    <p>Integrity must pass before ON. Apps stay locked through the check.</p>
    <div class="row"><button class="act" id="integrity-btn" type="button">Integrity status / check</button></div>
    <pre id="integrity-out"></pre>
  </div>
  <div class="card">
    <h2>Genesis boot</h2>
    <p>One-time username seed → Genesis Hash Key (hash only). Username is never stored.</p>
    <label for="seed">Username seed (discarded)</label>
    <input id="seed" autocomplete="off" placeholder="one-time seed">
    <div class="row">
      <button class="act" id="genesis-btn" type="button">Genesis boot</button>
      <button class="ghost" id="genesis-status-btn" type="button">Genesis status</button>
    </div>
    <pre id="genesis-out"></pre>
  </div>
  <div class="card">
    <h2>Witness / withdraw</h2>
    <p>Witness list is metadata only. Vault contents are never shown.</p>
    <label for="hold-label">Hold label (hashed, not stored as contents)</label>
    <input id="hold-label" placeholder="label">
    <div class="row">
      <button class="act" id="hold-btn" type="button">Hold</button>
      <button class="ghost" id="withdraw-btn" type="button">Withdraw</button>
      <button class="ghost" id="witness-btn" type="button">Witness list</button>
    </div>
    <pre id="custody-out"></pre>
  </div>
</div>

<div class="card" style="margin:0 18px 1rem;">
  <h2>AZHome bunker</h2>
  <p>Bunker browser surface. Entered only through the locked page cycle. Not a living serve until ON after integrity.</p>
  <div id="azhome" class="lock">PRE-LOCKED — AZHome does not render as living presence.</div>
</div>

<div class="card" style="margin:0 18px 1rem;">
  <h2>Scorched Earth</h2>
  <p>Local stub / advisory only on this hosted Worker. Never a remote wipe of user devices.</p>
  <div class="row">
    <button class="ghost" id="scorch-local-btn" type="button">Local advisory</button>
    <button class="danger" id="scorch-remote-btn" type="button">Remote wipe (stub refuse)</button>
  </div>
  <pre id="scorch-out"></pre>
</div>

<div class="card" style="margin:0 18px 1rem;">
  <h2>Page cycle status</h2>
  <div class="row"><button class="ghost" id="cycle-btn" type="button">Refresh cycle</button></div>
  <pre id="cycle-out"></pre>
</div>

<footer>
  Interface is CUSTODY. AZHub is separate software (Blank Key) under the one FragGate door — do not collapse them.
  Agents use FragGate only:
  <code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code>
  <code>{"slug":"azinterface",…}</code>
  — not a second MCP on this Worker
  (<a href="https://github.com/AzielEliab/fraggate">kernel</a>).
  Suite mesh <code>/v1/mesh/*</code> PROXIES (AZIEL_RUNTIME or HTTPS). Default OFF. QNM-BUILD-1.0 rollup. Not a Node Gate. Not a publish path.
  Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama, Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence, Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.
  <a href="https://www.azielcorpuslibrary.net/">library</a> ·
  <a href="https://godlock.uk">godlock.uk</a> ·
  <a href="https://www.azieleliab.com">azieleliab.com</a>.
  Apache-2.0. Forks always allowed.
  Cite: Eliab, Aziel. (2026). AZInterface 0.1.0 [Software].
</footer>
<script>
(function () {
  var cmd = ${JSON.stringify(INSTALL_LINE)};
  var btn = document.getElementById("install-btn");
  if (btn) btn.addEventListener("click", function () {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(cmd).then(function () { btn.textContent = "Copied — paste in Terminal, then azinterface ui"; });
    }
  });
  function show(id, obj) {
    var el = document.getElementById(id);
    if (el) el.textContent = JSON.stringify(obj, null, 2);
  }
  async function call(op, payload) {
    var res = await fetch("/v1/" + op, {
      method: "POST",
      headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
      body: JSON.stringify(payload || {})
    });
    return res.json();
  }
  async function refresh() {
    var cycle = await call("page_cycle_status", {});
    document.getElementById("state-badge").textContent = cycle.site_state || "?";
    document.getElementById("live-badge").textContent = String(!!cycle.living_presence);
    var home = document.getElementById("azhome");
    if (cycle.living_presence) {
      home.className = "lock on";
      home.textContent = "AZHome bunker living. Hold / withdraw / witness are on this cycle. Not Hub. Not a vault dump.";
    } else {
      home.className = "lock";
      home.textContent = "PRE-LOCKED — AZHome does not render as living presence. Cycle: " + (cycle.cycle || "OFF") + ". No cloud-asleep availability.";
    }
    show("cycle-out", cycle);
    return cycle;
  }
  document.querySelectorAll("[data-state]").forEach(function (b) {
    b.addEventListener("click", async function () {
      var out = await call("site_state_set", { state: b.getAttribute("data-state") });
      show("state-out", out);
      await refresh();
    });
  });
  document.getElementById("integrity-btn").addEventListener("click", async function () {
    var out = await call("integrity_check", {});
    show("integrity-out", out);
    await refresh();
  });
  document.getElementById("genesis-btn").addEventListener("click", async function () {
    var seed = document.getElementById("seed").value;
    var out = await call("genesis_boot", { username: seed });
    document.getElementById("seed").value = "";
    show("genesis-out", out);
  });
  document.getElementById("genesis-status-btn").addEventListener("click", async function () {
    show("genesis-out", await call("genesis_status", {}));
  });
  document.getElementById("hold-btn").addEventListener("click", async function () {
    show("custody-out", await call("hold", { label: document.getElementById("hold-label").value }));
    await refresh();
  });
  document.getElementById("withdraw-btn").addEventListener("click", async function () {
    show("custody-out", await call("withdraw", {}));
    await refresh();
  });
  document.getElementById("witness-btn").addEventListener("click", async function () {
    show("custody-out", await call("witness_list", {}));
  });
  document.getElementById("scorch-local-btn").addEventListener("click", async function () {
    show("scorch-out", await call("scorch_local", {}));
  });
  document.getElementById("scorch-remote-btn").addEventListener("click", async function () {
    show("scorch-out", await call("scorch_remote", {}));
  });
  document.getElementById("cycle-btn").addEventListener("click", refresh);
  refresh();
  meshBoot();

  var MESH_PRODUCT = "azinterface";
  var MESH_LABEL = "AZInterface";
  var MESH_OFF = "Default off until runtime enable. QNM-BUILD-1.0 rollup live|locked|isolated. AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. Presence only — not anonymity. Anon-broadcast is not a publish path.";
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
    var enabled = !!(j && j.enabled);
    var stateEl = document.getElementById("nodesState");
    var rollEl = document.getElementById("nodesRollup");
    var listEl = document.getElementById("nodesList");
    if (!stateEl || !rollEl || !listEl) return;
    if (!enabled) {
      stateEl.textContent = "Mesh OFF";
      stateEl.className = "off";
      rollEl.textContent = "";
      listEl.textContent = MESH_OFF;
      meshNodeId = "";
      return;
    }
    stateEl.textContent = "Mesh ON";
    stateEl.className = "on";
    var roll = meshRollup(j);
    rollEl.textContent = roll
      ? ("live " + roll.live + " · locked " + roll.locked + " · isolated " + roll.isolated)
      : ((j.live_nodes || 0) + " live");
    var products = j.products_present || j.products || [];
    var roster = j.nodes || [];
    var labels = roster.length
      ? roster.map(function (n) { return (n && (n.label || n.product || n.node_id)) || ""; }).filter(Boolean)
      : products;
    listEl.textContent = labels.length ? labels.join(" · ") : "No live nodes.";
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
})();
</script>
</body>
</html>`;
}
