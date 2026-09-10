"""Shared human UI HTML — black / gold / white. Pre-locked page cycles."""

from __future__ import annotations

from .meta import HOST, LIMITATION, SIGIL

ASSET = "azinterface-0.1.0.tar.gz"
INSTALL_LINE = f"curl -fsSL {HOST}/install.sh | bash"


def home_html(*, views: int = 0, downloads: int = 0, github: dict | None = None, local: bool = False) -> str:
    gh = github or {}
    v = f"{int(views or 0):,}"
    n = f"{int(downloads or 0):,}"
    local_note = "Local loopback UI (127.0.0.1). " if local else ""
    counted = HOST if local else ""
    download_href = f"{counted}/download?asset={ASSET}" if local else f"/download?asset={ASSET}"
    count_href = f"{counted}/count" if local else "/count"
    stats_href = f"{counted}/stats" if local else "/stats"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZInterface — Aziel Eliab</title>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"AZInterface","author":{{"@type":"Person","name":"Aziel Eliab"}},"codeRepository":"https://github.com/AzielEliab/azinterface","downloadUrl":"{HOST}/download","license":"https://www.apache.org/licenses/LICENSE-2.0","url":"{HOST}/","description":"AZInterface (AIH-WP-1.0) custodial operating environment by Aziel Eliab. Not AZHub."}}
</script>
<style>
:root {{ color-scheme: dark; --bg:#0b0b0b; --card:#141414; --gold:#c9a227; --gold-dim:#8a7219; --ivory:#e8e0d0; --muted:#9a927e; --line:#2a2414; --ok:#7dcf9a; --alert:#ffb4b4; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font:15px/1.45 system-ui,sans-serif; background:var(--bg); color:var(--ivory); }}
header {{ display:flex; align-items:center; gap:12px; padding:14px 18px; border-bottom:1px solid var(--gold); }}
header img {{ width:40px; height:40px; }}
h1 {{ margin:0; font-size:1.4rem; color:var(--gold); }}
.motto {{ color:var(--muted); font-size:.9rem; }}
.banner {{ margin:12px 18px 0; border:1px solid #5c4a1a; background:#241c0d; color:#f0d78c; padding:.75rem 1rem; border-radius:8px; font-size:.88rem; }}
.nums {{ display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin:12px 18px; }}
.count {{ background:var(--card); border:1px solid var(--gold-dim); border-radius:12px; padding:12px; font-size:2rem; font-weight:700; }}
.count span {{ display:block; font-size:.9rem; font-weight:500; color:var(--muted); }}
.btns {{ display:grid; grid-template-columns:1fr 1fr; gap:.75rem; margin:0 18px 1rem; }}
@media (max-width:720px){{ .btns,.nums,.grid{{grid-template-columns:1fr;}} }}
a.btn, button.btn {{ display:block; text-align:center; font:inherit; font-weight:750; padding:1rem; border-radius:10px; border:0; cursor:pointer; text-decoration:none; }}
a.btn.primary {{ background:var(--ivory); color:#0b0b0b; }}
button.btn.install {{ background:var(--gold); color:#14110a; }}
.iso {{ margin:0 18px 1rem; color:#7d8696; font-size:.85rem; }}
.iso a {{ color:#c9d4ff; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 18px 1rem; }}
.card {{ background:var(--card); border:1px solid var(--gold-dim); border-radius:12px; padding:12px; }}
h2 {{ margin:0 0 .5rem; font-size:1.05rem; color:var(--gold); }}
.row {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }}
button.act {{ background:var(--gold); color:#14110a; border:0; border-radius:8px; padding:.5rem .85rem; font-weight:700; cursor:pointer; }}
button.ghost {{ background:transparent; color:var(--gold); border:1px solid var(--gold-dim); border-radius:8px; padding:.5rem .85rem; cursor:pointer; }}
button.danger {{ background:transparent; color:var(--alert); border:1px solid #b54a4a; border-radius:8px; padding:.5rem .85rem; cursor:pointer; }}
label {{ display:block; font-size:.8rem; color:var(--muted); margin:.4rem 0 .2rem; }}
input {{ width:100%; background:#1a1a1a; color:var(--ivory); border:1px solid var(--line); border-radius:8px; padding:.5rem .6rem; font:inherit; }}
pre {{ white-space:pre-wrap; word-break:break-word; font-size:.78rem; color:#cfc6ad; min-height:2.4rem; }}
.lock {{ border:1px dashed var(--gold-dim); color:var(--muted); padding:1rem; border-radius:10px; text-align:center; }}
.lock.on {{ border-style:solid; color:var(--ivory); }}
.badge {{ display:inline-block; font-size:.75rem; font-weight:700; padding:.15rem .5rem; border-radius:999px; border:1px solid var(--gold-dim); color:var(--gold); }}
#nodes {{ display:flex; align-items:center; gap:10px; padding:6px 18px; border-bottom:1px solid var(--gold); background:#0f0f0f; flex-wrap:wrap; color:var(--muted); font-size:12px; }}
#nodes strong {{ color:var(--gold); font-weight:700; }}
footer {{ padding:12px 18px 28px; color:var(--muted); font-size:.82rem; }}
footer a {{ color:var(--gold); }}
</style>
</head>
<body>
<header>
  <img src="{SIGIL}" alt="Aziel Eliab sigil">
  <div>
    <h1>AZInterface</h1>
    <div class="motto">AIH-WP-1.0 custodial operating environment. Interface is CUSTODY — never Hub. Author: Aziel Eliab only.</div>
  </div>
</header>
<div id="nodes">
  <strong>Live Nodes</strong>
  <span class="off">Mesh OFF</span>
  <div>Default off. QNM-BUILD-1.0 rollup. QNS-CD-1.0 vias run in local qnsd (127.0.0.1). AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. GET never enables.</div>
</div>
<p class="banner">{LIMITATION}</p>
<div class="nums">
  <div class="count">{v}<span>Views</span></div>
  <div class="count">{n}<span>Downloads</span></div>
</div>
<div class="btns">
  <a class="btn primary" href="{download_href}">Download {ASSET}</a>
  <button class="btn install" id="install-btn" type="button">One-click install</button>
</div>
<pre class="iso" id="install-cmd">{INSTALL_LINE}
Then run: azinterface ui  →  http://127.0.0.1:8880 (this computer only).</pre>
<p class="iso">{local_note}Isolated counter: Worker <code>azinterface-download-tracker</code>, KV AZINTERFACE_DOWNLOADS. /v1 does not increment.
<strong>Human UI is this page.</strong> AI / MCP path is FragGate only:
<code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code> body <code>{{"slug":"azinterface","op":"…","payload":{{}}}}</code>.
GitHub stars {gh.get("stars") or 0} · forks {gh.get("forks") or 0} · watchers {gh.get("watchers") or 0}.
<a href="{count_href}">/count</a> · <a href="{stats_href}">/stats</a> · <a href="/v1/skill">Skill</a> · <a href="https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list">FragGate list</a> · <a href="https://github.com/AzielEliab/azinterface">GitHub</a> · <a href="https://github.com/AzielEliab/azhub">AZHub (separate software)</a></p>

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
  <div class="card">
    <h2>QNS pair custody</h2>
    <p>QNS-CD-1.0 / AIH-WP-1.3: OFFER → ACCEPT → SEAL. Vias run in local qnsd (127.0.0.1). Interface holds pair_id + photon_id cites — never vault contents. Living presence only.</p>
    <label for="pair-via">Via (lan/plc/bt/rf/light/qns/operator/local)</label>
    <input id="pair-via" placeholder="local" value="local">
    <label for="pair-id">pair_id (optional cite)</label>
    <input id="pair-id" placeholder="pair-…">
    <label for="photon-id">photon_id (optional cite)</label>
    <input id="photon-id" placeholder="qns1-…">
    <div class="row">
      <button class="act" id="pair-offer-btn" type="button">Offer</button>
      <button class="ghost" id="pair-accept-btn" type="button">Accept</button>
      <button class="ghost" id="pair-seal-btn" type="button">Seal</button>
      <button class="danger" id="pair-cut-btn" type="button">Cut</button>
      <button class="ghost" id="pair-status-btn" type="button">Pair status</button>
    </div>
    <pre id="pair-out"></pre>
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
  {local_note}Interface is CUSTODY. AZHub is separate software (Blank Key) under the one FragGate door — do not collapse them.
  Agents use FragGate only:
  <code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code>
  <code>{{"slug":"azinterface",…}}</code>
  — not a second MCP on this Worker
  (<a href="https://github.com/AzielEliab/fraggate">kernel</a>).
  QNS-CD-1.0 pair memorial. Vias in local qnsd. QNM-BUILD-1.0 mesh default OFF. Not a Node Gate.
  Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama, Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence, Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.
  <a href="https://www.azielcorpuslibrary.net/">library</a> ·
  <a href="https://godlock.uk">godlock.uk</a> ·
  <a href="https://www.azieleliab.com">azieleliab.com</a>.
  Apache-2.0. Forks always allowed.
  Cite: Eliab, Aziel. (2026). AZInterface 0.1.0 [Software].
</footer>
<script>
(function () {{
  var cmd = {INSTALL_LINE!r};
  var btn = document.getElementById("install-btn");
  if (btn) btn.addEventListener("click", function () {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(cmd).then(function () {{ btn.textContent = "Copied — paste in Terminal, then azinterface ui"; }});
    }}
  }});
  function show(id, obj) {{
    var el = document.getElementById(id);
    if (el) el.textContent = JSON.stringify(obj, null, 2);
  }}
  async function call(op, payload) {{
    var res = await fetch("/v1/" + op, {{
      method: "POST",
      headers: {{ "content-type": "application/json", "user-agent": "Mozilla/5.0" }},
      body: JSON.stringify(payload || {{}})
    }});
    return res.json();
  }}
  async function refresh() {{
    var cycle = await call("page_cycle_status", {{}});
    document.getElementById("state-badge").textContent = cycle.site_state || "?";
    document.getElementById("live-badge").textContent = String(!!cycle.living_presence);
    var home = document.getElementById("azhome");
    if (cycle.living_presence) {{
      home.className = "lock on";
      home.textContent = "AZHome bunker living. Hold / withdraw / witness are on this cycle. Not Hub. Not a vault dump.";
    }} else {{
      home.className = "lock";
      home.textContent = "PRE-LOCKED — AZHome does not render as living presence. Cycle: " + (cycle.cycle || "OFF") + ". No cloud-asleep availability.";
    }}
    show("cycle-out", cycle);
    return cycle;
  }}
  document.querySelectorAll("[data-state]").forEach(function (b) {{
    b.addEventListener("click", async function () {{
      var out = await call("site_state_set", {{ state: b.getAttribute("data-state") }});
      show("state-out", out);
      await refresh();
    }});
  }});
  document.getElementById("integrity-btn").addEventListener("click", async function () {{
    var out = await call("integrity_check", {{}});
    show("integrity-out", out);
    await refresh();
  }});
  document.getElementById("genesis-btn").addEventListener("click", async function () {{
    var seed = document.getElementById("seed").value;
    var out = await call("genesis_boot", {{ username: seed }});
    document.getElementById("seed").value = "";
    show("genesis-out", out);
  }});
  document.getElementById("genesis-status-btn").addEventListener("click", async function () {{
    show("genesis-out", await call("genesis_status", {{}}));
  }});
  document.getElementById("hold-btn").addEventListener("click", async function () {{
    show("custody-out", await call("hold", {{ label: document.getElementById("hold-label").value }}));
    await refresh();
  }});
  document.getElementById("withdraw-btn").addEventListener("click", async function () {{
    show("custody-out", await call("withdraw", {{}}));
    await refresh();
  }});
  document.getElementById("witness-btn").addEventListener("click", async function () {{
    show("custody-out", await call("witness_list", {{}}));
  }});
  document.getElementById("scorch-local-btn").addEventListener("click", async function () {{
    show("scorch-out", await call("scorch_local", {{}}));
  }});
  document.getElementById("scorch-remote-btn").addEventListener("click", async function () {{
    show("scorch-out", await call("scorch_remote", {{}}));
  }});
  document.getElementById("cycle-btn").addEventListener("click", refresh);
  function pairPayload() {{
    return {{
      via: document.getElementById("pair-via").value,
      pair_id: document.getElementById("pair-id").value,
      photon_id: document.getElementById("photon-id").value
    }};
  }}
  document.getElementById("pair-offer-btn").addEventListener("click", async function () {{
    var out = await call("pair_offer", pairPayload());
    if (out && out.pair && out.pair.pair_id) document.getElementById("pair-id").value = out.pair.pair_id;
    if (out && out.pair && out.pair.photon_id) document.getElementById("photon-id").value = out.pair.photon_id;
    show("pair-out", out);
  }});
  document.getElementById("pair-accept-btn").addEventListener("click", async function () {{
    show("pair-out", await call("pair_accept", pairPayload()));
  }});
  document.getElementById("pair-seal-btn").addEventListener("click", async function () {{
    show("pair-out", await call("pair_seal", pairPayload()));
  }});
  document.getElementById("pair-cut-btn").addEventListener("click", async function () {{
    show("pair-out", await call("pair_cut", pairPayload()));
  }});
  document.getElementById("pair-status-btn").addEventListener("click", async function () {{
    show("pair-out", await call("pair_status", {{}}));
  }});
  refresh();
}})();
</script>
</body>
</html>
"""
