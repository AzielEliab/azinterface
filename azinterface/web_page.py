"""Shared human UI HTML — black / gold / white. Pre-locked page cycles."""

from __future__ import annotations

from .meta import HOST, LIMITATION, SIGIL
from .pipeline import domain_map_html, pipeline_strip_html

ASSET = "azinterface-0.1.0.tar.gz"
INSTALL_LINE = f"curl -fsSL {HOST}/install.sh -o install-azinterface.sh"
INSTALL_STEPS = "\n".join(
    [
        f"Download the counted tarball: {HOST}/download?asset={ASSET}",
        f"tar -xzf {ASSET}",
        "python3 -m venv .venv && source .venv/bin/activate && pip install -e .",
        "azinterface ui  →  http://127.0.0.1:8880 (this computer only)",
    ]
)


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
<meta name="description" content="AZInterface is a custodial operating environment by Aziel Eliab. Download the package or use the hosted custody page.">
<meta name="author" content="Aziel Eliab">
<title>AZInterface — Aziel Eliab</title>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"AZInterface","author":{{"@type":"Person","name":"Aziel Eliab"}},"codeRepository":"https://github.com/AzielEliab/azinterface","downloadUrl":"{HOST}/download","license":"https://www.apache.org/licenses/LICENSE-2.0","url":"{HOST}/","description":"AZInterface (AIH-WP-1.0) custodial operating environment by Aziel Eliab. Not AZHub."}}
</script>
<style>
:root {{
  color-scheme: dark;
  --bg:#0b0b0b;
  --card:#141414;
  --gold:#c9a227;
  --gold-dim:#8a7219;
  --ivory:#e8e0d0;
  --muted:#9a927e;
  --line:#2a2414;
  --ok:#7dcf9a;
  --alert:#ffb4b4;
  --ink:#14110a;
  --focus:#f3e6b8;
  --btn:#c9a227;
  --btn-ink:#14110a;
  --banner-bg:#241c0d;
  --banner-fg:#f0d78c;
  --banner-line:#5c4a1a;
  --input:#1a1a1a;
  --pre-bg:#0f0f0f;
  --pre-fg:#cfc6ad;
  --code:#c9d4ff;
  --door-bg:#241c0d;
  --danger-line:#b54a4a;
  --toast-bg:#2a1212;
  --link:#e6d19a;
}}
@media (prefers-color-scheme: light) {{
  :root {{
    color-scheme: light;
    --bg:#f6f3ec;
    --card:#ffffff;
    --gold:#5c4a12;
    --gold-dim:#6e5608;
    --ivory:#1c1812;
    --muted:#4e4638;
    --line:#6e6252;
    --ok:#0f6b3a;
    --alert:#8f1d1d;
    --ink:#f6f3ec;
    --focus:#5c4a12;
    --btn:#5c4a12;
    --btn-ink:#f6f3ec;
    --banner-bg:#fff6dc;
    --banner-fg:#3d3208;
    --banner-line:#8a7219;
    --input:#ffffff;
    --pre-bg:#f3efe6;
    --pre-fg:#1c1812;
    --code:#1e3a8a;
    --door-bg:#fff6dc;
    --danger-line:#8f1d1d;
    --toast-bg:#fde8e8;
    --link:#5c4a12;
  }}
}}
* {{ box-sizing: border-box; }}
html {{ overflow-x: clip; }}
body {{ margin:0; overflow-x:clip; font:16px/1.5 system-ui,"Segoe UI",sans-serif; background:var(--bg); color:var(--ivory); }}
img {{ max-width:100%; height:auto; }}
a {{ color:var(--link); }}
a:focus-visible, button:focus-visible, input:focus-visible, summary:focus-visible, a.skip:focus {{ outline:2px solid var(--focus); outline-offset:2px; }}
a.skip {{ position:absolute; left:-999px; top:0; }}
a.skip:focus {{ left:1rem; top:1rem; z-index:5; background:var(--btn); color:var(--btn-ink); padding:.45rem .75rem; text-decoration:none; border-radius:8px; }}
.page {{ max-width:58rem; margin:0 auto; padding:0 1rem 2.5rem; }}
.hero {{ padding:1.25rem 0 .2rem; }}
.brandrow {{ display:flex; align-items:center; gap:12px; margin:0 0 12px; }}
.brandmark {{ width:40px; height:40px; border-radius:10px; object-fit:cover; display:block; box-shadow:0 0 0 1px var(--line); }}
h1 {{ margin:0 0 .2rem; font-size:2rem; font-weight:650; letter-spacing:.02em; line-height:1.15; color:var(--ivory); }}
.motto {{ color:var(--gold); font-style:italic; margin:0 0 .7rem; font-size:1.08rem; }}
.lede {{ color:var(--muted); margin:0 0 1rem; max-width:46rem; }}
.kicker {{ display:block; margin:1.15rem 0 .75rem; font:.68rem/1.2 ui-monospace,Menlo,Consolas,monospace; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }}
a.btn, button.btn {{ display:block; text-align:center; font:inherit; font-weight:700; padding:1rem; border-radius:10px; border:0; cursor:pointer; text-decoration:none; }}
a.btn.block.primary {{ width:100%; max-width:40rem; margin:0 0 .75rem; padding:1.05rem 1.2rem; border:1px solid transparent; border-radius:9px; background:var(--btn); color:var(--btn-ink); font:700 1.25rem/1.1 ui-monospace,Menlo,Consolas,monospace; letter-spacing:.03em; }}
a.btn.block.primary:hover {{ filter:brightness(1.06); }}
button.btn.install {{ width:100%; max-width:40rem; margin:.25rem 0 1rem; background:transparent; color:var(--gold); border:1px solid var(--line); font:700 .95rem/1.1 ui-monospace,Menlo,Consolas,monospace; }}
.asset-note {{ color:var(--muted); font-size:.95rem; margin:0 0 .85rem; max-width:46rem; }}
.features {{ display:grid; grid-template-columns:1fr; gap:.65rem 1.2rem; margin:0 0 1.1rem; padding:0; list-style:none; max-width:46rem; }}
.features li {{ margin:0; }}
.nums {{ display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin:0 0 1rem; max-width:40rem; }}
.count {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:.7rem .9rem; margin:0; font-size:1.35rem; font-weight:700; font-variant-numeric:tabular-nums; }}
.count span {{ display:block; font-size:.85rem; font-weight:500; color:var(--muted); }}
.iso {{ margin:0 0 1rem; color:var(--muted); font-size:.9rem; }}
.iso a {{ color:var(--link); }}
.install-steps {{ margin:0 0 .6rem; padding-left:1.25rem; color:var(--muted); font-size:.95rem; max-width:46rem; }}
.install-steps code, .features code, .iso code, .checksum-note code {{ color:var(--code); }}
.advanced {{ margin:0 0 1rem; color:var(--muted); font-size:.9rem; max-width:46rem; }}
.advanced summary, .notes summary {{ cursor:pointer; color:var(--gold); }}
.advanced pre {{ max-height:8rem; overflow:auto; }}
.checksum-note {{ margin:.4rem 0 0; }}
.banner {{ margin:0 0 1rem; border:1px solid var(--banner-line); background:var(--banner-bg); color:var(--banner-fg); padding:.75rem 1rem; border-radius:8px; font-size:.92rem; }}
.out-panel {{ margin-top:.5rem; }}
.out-summary {{ margin:0; color:var(--ivory); font-size:.85rem; }}
.out-json {{ margin-top:.35rem; color:var(--muted); font-size:.78rem; }}
.out-json summary {{ cursor:pointer; color:var(--gold); }}
.out-pre {{ max-height:12rem; overflow:auto; margin:.4rem 0 0; white-space:pre-wrap; word-break:break-word; font-size:.78rem; color:var(--pre-fg); background:var(--pre-bg); border:1px solid var(--line); border-radius:8px; padding:.6rem; }}
.grid {{ display:grid; grid-template-columns:1fr; gap:12px; margin:0 0 1rem; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px; min-width:0; }}
.card.stack {{ margin:0 0 1rem; }}
h2 {{ margin:0 0 .5rem; font-size:1.05rem; color:var(--gold); }}
.row {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }}
button.act {{ background:var(--btn); color:var(--btn-ink); border:0; border-radius:8px; padding:.55rem .85rem; font-weight:700; cursor:pointer; }}
button.ghost {{ background:transparent; color:var(--gold); border:1px solid var(--gold-dim); border-radius:8px; padding:.55rem .85rem; cursor:pointer; }}
button.danger {{ background:transparent; color:var(--alert); border:1px solid var(--danger-line); border-radius:8px; padding:.55rem .85rem; cursor:pointer; }}
label {{ display:block; font-size:.85rem; color:var(--muted); margin:.4rem 0 .2rem; }}
input {{ width:100%; max-width:100%; background:var(--input); color:var(--ivory); border:1px solid var(--line); border-radius:8px; padding:.5rem .6rem; font:inherit; }}
pre {{ white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere; font-size:.78rem; color:var(--pre-fg); max-height:12rem; overflow:auto; max-width:100%; }}
.lock {{ border:1px dashed var(--gold-dim); color:var(--muted); padding:1rem; border-radius:10px; text-align:center; }}
.lock.on {{ border-style:solid; color:var(--ivory); }}
.badge {{ display:inline-block; font-size:.75rem; font-weight:700; padding:.15rem .5rem; border-radius:999px; border:1px solid var(--gold-dim); color:var(--gold); }}
.reference {{ margin-top:.4rem; }}
#nodes, #pipeline, #domains {{ padding:12px 14px; margin:0 0 12px; border:1px solid var(--line); border-radius:12px; background:var(--card); max-width:100%; }}
#nodes {{ display:flex; flex-direction:column; align-items:flex-start; gap:6px; color:var(--muted); font-size:.82rem; }}
#nodes strong {{ color:var(--gold); font-weight:700; }}
#nodes .off, #nodes .on {{ color:var(--gold); }}
#nodesList {{ width:100%; min-width:0; overflow-wrap:anywhere; }}
#pipeline strong {{ color:var(--gold); font-size:.82rem; letter-spacing:.02em; }}
#pipeline .pipe-path {{ margin:.35rem 0 .45rem; color:var(--ivory); font-size:.82rem; overflow-wrap:anywhere; }}
#pipeline .hops {{ list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:6px; align-items:center; }}
#pipeline .hop {{ display:flex; flex-direction:column; gap:1px; max-width:100%; padding:.28rem .55rem; border:1px solid var(--line); border-radius:8px; font-size:.72rem; color:var(--muted); background:var(--bg); }}
#pipeline .hop.door {{ border-color:var(--gold); color:var(--gold); background:var(--door-bg); box-shadow:0 0 0 1px var(--banner-line) inset; }}
#pipeline .hop.single {{ font-weight:700; }}
#pipeline .hop.optional {{ opacity:.85; border-style:dashed; }}
#pipeline .hop .inspect {{ font-style:normal; font-size:.65rem; color:var(--gold); }}
#pipeline .pipe-note, #domains .pipe-note {{ margin:.45rem 0 0; color:var(--muted); font-size:.75rem; overflow-wrap:anywhere; }}
#domains strong {{ color:var(--gold); font-size:.82rem; }}
#domains .domain-grid {{ display:grid; grid-template-columns:1fr; gap:8px; margin-top:8px; }}
#domains .domain {{ background:var(--bg); border:1px solid var(--line); border-radius:10px; padding:8px 10px; min-width:0; }}
#domains .domain h3 {{ margin:0 0 .4rem; font-size:.78rem; color:var(--gold); }}
#domains .domain ul {{ list-style:none; margin:0; padding:0; }}
#domains .sw {{ display:flex; gap:6px; flex-wrap:wrap; align-items:baseline; font-size:.75rem; color:var(--ivory); padding:.12rem 0; }}
#domains .sw code {{ color:var(--gold); }}
#domains .sw .st {{ color:var(--muted); }}
#domains .sw.stub {{ color:var(--muted); }}
footer.quiet {{ padding:1.15rem 0 2.8rem; color:var(--muted); font-size:.9rem; }}
footer.quiet p {{ margin:.35rem 0; }}
footer.quiet a {{ color:var(--ivory); text-decoration:underline; text-underline-offset:.15em; }}
.notes {{ margin-top:.8rem; }}
.iso, footer, .banner, .motto, .lede, .asset-note {{ overflow-wrap:anywhere; }}
#cycle-toast {{ display:none; margin:.6rem 0 0; border:1px solid var(--danger-line); background:var(--toast-bg); color:var(--alert); padding:.65rem .75rem; border-radius:8px; font-size:.82rem; font-weight:650; }}
#cycle-toast.show {{ display:block; }}
@media (min-width:721px) {{
  .page {{ padding:0 1.2rem 2.8rem; }}
  .features {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
  .grid {{ grid-template-columns:1fr 1fr; }}
  #domains .domain-grid {{ grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr)); }}
}}
</style>
</head>
<body>
<a class="skip" href="#custody">Skip to custody tools</a>
<div class="page">
<header class="hero">
  <div class="brandrow">
    <img class="brandmark" src="{SIGIL}" alt="" width="40" height="40">
  </div>
  <h1>AZInterface</h1>
  <p class="motto">Custodial page cycles, one step at a time.</p>
  <p class="lede">AIH-WP-1.0 software by Aziel Eliab. Download the package, or hold, witness, and withdraw on this page.</p>
  <a class="btn block primary" id="downloadBtn" href="{download_href}" aria-describedby="downloadNote">Download</a>
  <p class="asset-note" id="downloadNote">{n} downloads · {v} views · {ASSET} · counted on this Worker for every branch and fork</p>
  <div class="nums" aria-label="Counts">
    <p class="count">{n}<span>Downloads</span></p>
    <p class="count">{v}<span>Views</span></p>
  </div>
  <ul class="features">
    <li>Five sealed steps: OFF, integrity, ON, FULL SHUTDOWN, MEMORIAL</li>
    <li>Hold, witness, and withdraw stay on this page</li>
    <li>After install, <code>azinterface ui</code> opens on this computer only</li>
  </ul>
</header>
<ol class="install-steps" id="install-steps">
  <li>Download the counted tarball (button above).</li>
  <li><code>tar -xzf {ASSET}</code></li>
  <li><code>python3 -m venv .venv &amp;&amp; source .venv/bin/activate &amp;&amp; pip install -e .</code></li>
  <li>Run <code>azinterface ui</code> → http://127.0.0.1:8880 (this computer only).</li>
</ol>
<button class="btn install" id="install-btn" type="button">Copy install steps</button>
<details class="advanced" id="install-advanced">
  <summary>Advanced / optional: scripted installer (review first)</summary>
  <p>Prefer the tarball steps. This host is custody UI only. Agents use aziel-runtime FragGate/MCP — not a second Interface MCP.</p>
  <pre id="install-cmd">{INSTALL_LINE}
# review install-azinterface.sh, then: bash install-azinterface.sh</pre>
  <p class="checksum-note">Checksum note: after download, run <code>sha256sum {ASSET}</code> (or <code>shasum -a 256</code>) and compare with a hash you trust. Pipe-to-bash (<code>curl … | bash</code>) is optional and not the recommended path.</p>
</details>
<main id="custody">
  <p class="kicker">Custody tools</p>
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
    <div id="cycle-toast" role="status" aria-live="polite"></div>
    <div class="out-panel" id="state-out"></div>
  </div>
  <div class="card">
    <h2>Integrity loop</h2>
    <p>Integrity must pass before ON. Apps stay locked through the check.</p>
    <div class="row"><button class="act" id="integrity-btn" type="button">Integrity status / check</button></div>
    <div class="out-panel" id="integrity-out"></div>
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
    <div class="out-panel" id="genesis-out"></div>
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
    <div class="out-panel" id="custody-out"></div>
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
    <div class="out-panel" id="pair-out"></div>
  </div>
</div>

<div class="card stack">
  <h2>AZHome bunker</h2>
  <p>Bunker browser surface. Entered only through the locked page cycle. Not a living serve until ON after integrity.</p>
  <div id="azhome" class="lock">PRE-LOCKED — AZHome does not render as living presence.</div>
</div>

<div class="card stack">
  <h2>Scorched Earth</h2>
  <p>Local stub / advisory only on this hosted Worker. Never a remote wipe of user devices.</p>
  <div class="row">
    <button class="ghost" id="scorch-local-btn" type="button">Local advisory</button>
    <button class="danger" id="scorch-remote-btn" type="button">Remote wipe (stub refuse)</button>
  </div>
  <div class="out-panel" id="scorch-out"></div>
</div>

<div class="card stack">
  <h2>Page cycle status</h2>
  <p>Sealed custody cycle plus the MASTER-33 hop order on aziel-runtime. FragGate is THE SINGLE DOOR. Internal Domain Layer is 33/11 isolation labels with 4DMap inspection frame — not an extra door (domains_are_doors:false). No LambGate.</p>
  <div class="row">
    <button class="ghost" id="cycle-btn" type="button">Refresh cycle</button>
    <button class="ghost" id="pipeline-btn" type="button">Pipeline cite</button>
  </div>
  <div class="out-panel" id="cycle-out"></div>
</div>
</main>
<section class="reference" aria-label="Live nodes and pipeline">
<div id="nodes">
  <strong>Live Nodes</strong>
  <span id="nodesState" class="on">Mesh ON</span>
  <span id="nodesRollup"></span>
  <div id="nodesList">Live Nodes. QNM-BUILD-1.0 rollup live|locked|isolated. SPLIT THE WIRES: 0.5–1s tip tick presence+tip hash only fixed-size; payload pull-only second plane; update=proof not timer (cite prev+lockset fail-closed; 777s dwell after valid cite; clock desync≠yes; ambiguous=isolate); equivocation ends peer; emit last locally; Phoenix local only; partition no auto-splice; heartbeat loss≠poison≠apply last packet; 1s loop and 777s gate never share a socket. COLD-COPY SURVIVAL: multiply cold copies; refuse live body sync; tip expensive to erase; server pull cannot wipe cold replicas; hash-absolute poison refuse; data outlives creators. REHEAL refuse: isolate+local phoenix; no neighbor vote-to-fix; allowed live/locked/isolated/tip-hash only. QNS-CD-1.0 photon vias run in local qnsd (127.0.0.1). AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate. Presence only — not anonymity. Anon-broadcast is not a publish path. GET never enables.</div>
</div>
{pipeline_strip_html()}
{domain_map_html()}
</section>
<footer class="quiet">
  <p>Apache-2.0 · Aziel Eliab · AZInterface 0.1.0</p>
  <p><a href="https://github.com/AzielEliab/azinterface">GitHub</a> · <a href="/cite.json">cite.json</a> · <a href="/v1/skill">Skill</a> · <a href="https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list">FragGate list</a> · <a href="{count_href}">/count</a> · <a href="{stats_href}">/stats</a></p>
  <details class="notes">
    <summary>Custody notes</summary>
    <p class="banner">{LIMITATION}</p>
    <p class="iso">{local_note}Isolated counter: Worker <code>azinterface-download-tracker</code>, KV AZINTERFACE_DOWNLOADS. /v1 does not increment.
<strong>Human UI is this page (custody UI only).</strong> Agents use aziel-runtime FragGate/MCP:
<code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code> body <code>{{"slug":"azinterface","op":"…","payload":{{}}}}</code>.
This host <code>/mcp</code> is a pointer, not a product MCP.
GitHub stars {gh.get("stars") or 0} · forks {gh.get("forks") or 0} · watchers {gh.get("watchers") or 0}.
<a href="{count_href}">/count</a> · <a href="{stats_href}">/stats</a> · <a href="/v1/skill">Skill</a> · <a href="/cite.json">cite.json</a> · <a href="https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list">FragGate list</a> · <a href="https://github.com/AzielEliab/azinterface">GitHub</a> · <a href="https://github.com/AzielEliab/az-clce">AZ-CLCE</a> · <a href="https://github.com/AzielEliab/AZCoherence">AZCoherence</a> · <a href="https://azcoherence-download-tracker.vibelock.workers.dev/">AZCoherence Worker</a> · <a href="https://github.com/AzielEliab/azhub">AZHub</a></p>
    {local_note}Interface is CUSTODY. AZHub is separate software (Blank Key) under the one FragGate door — do not collapse them.
  AZCoherence (AZC-WP-0.1) is separate Softwares on that same door — second-pass triad coherence (PASS/FLAG/NEUTRALIZE/REFUSE), peer of AZ-CLCE, not AKM-TRIAD. Agents: <code>fraggate_describe</code> then <code>fraggate_call</code> <code>slug=azcoherence</code>. Humans: <a href="https://azcoherence-download-tracker.vibelock.workers.dev/">AZCoherence Worker</a> + <a href="https://azcoherence-download-tracker.vibelock.workers.dev/download">/download</a>. Softwares tabs pull from runtime <code>GET /v1/software</code> (plain A–Z); Interface does not host that catalog.
  Agents use aziel-runtime FragGate/MCP:
  <code>POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call</code>
  <code>{{"slug":"azinterface",…}}</code>
  — this host is custody UI only, not a product MCP
  (<a href="https://github.com/AzielEliab/fraggate">kernel</a>).
  LOCKED pipeline cite: FragGate is THE SINGLE DOOR. MASTER-33 on aziel-runtime. SUITE-PIPE-1.6.15 is historical. AZInterface is not a second door. No LambGate.
  QNS-CD-1.0 pair memorial. Vias in local qnsd. QNM-BUILD-1.0 Live Nodes read-only. SPLIT THE WIRES + COLD-COPY SURVIVAL. REHEAL refuse. Not a Node Gate.
  Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama, Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence, Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.
  <a href="https://www.azielcorpuslibrary.net/">library</a> ·
  <a href="https://godlock.uk">godlock.uk</a> ·
  <a href="https://www.azieleliab.com">azieleliab.com</a>.
  Apache-2.0. Forks always allowed.
  Cite: Eliab, Aziel. (2026). AZInterface 0.1.0 [Software].
  </details>
</footer>
</div>
<script>
(function () {{
  var cmd = {INSTALL_STEPS!r};
  var btn = document.getElementById("install-btn");
  if (btn) btn.addEventListener("click", function () {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(cmd).then(function () {{ btn.textContent = "Copied tarball install steps — then azinterface ui"; }});
    }}
  }});
  function show(id, obj) {{
    var host = document.getElementById(id);
    if (!host) return;
    var raw = JSON.stringify(obj, null, 2);
    var title = obj && obj.display && obj.display.title;
    var summary = obj && obj.display && obj.display.summary;
    var line = title && summary
      ? String(title).replace(/\\.$/, "") + ". " + summary
      : (summary || title || (obj && (obj.error || obj.code || obj.note)) || "Response");
    var code = obj && obj.code ? " [" + obj.code + "]" : "";
    host.replaceChildren();
    var compact = document.createElement("p");
    compact.className = "out-summary";
    compact.textContent = String(line) + code;
    var det = document.createElement("details");
    det.className = "out-json";
    var sum = document.createElement("summary");
    sum.textContent = "Full JSON (" + raw.length.toLocaleString() + " chars) — collapsed by default";
    var pre = document.createElement("pre");
    pre.className = "out-pre";
    pre.textContent = raw;
    det.appendChild(sum);
    det.appendChild(pre);
    host.appendChild(compact);
    host.appendChild(det);
  }}
  function toastMemorial(out) {{
    var el = document.getElementById("cycle-toast");
    if (!el) return;
    var terminal = out && (out.code === "AIH-CYCLE-TERMINAL" || (out.refused && (out.site_state === "MEMORIAL" || out.current === "MEMORIAL")));
    if (!terminal) {{
      el.className = "";
      el.textContent = "";
      return;
    }}
    var title = out.display && out.display.title;
    var summary = out.display && out.display.summary;
    var human = title && summary
      ? String(title).replace(/\\.$/, "") + ". " + summary
      : (summary || title || out.error || "");
    el.textContent = /terminal/i.test(human)
      ? human
      : "MEMORIAL is terminal. Cannot leave MEMORIAL. Cycles stay pre-locked.";
    el.className = "show";
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
      toastMemorial(out);
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
  document.getElementById("pipeline-btn").addEventListener("click", async function () {{
    show("cycle-out", await call("pipeline_arch", {{}}));
  }});
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
  var MESH_STATUS = "{HOST}/v1/mesh/status";
  var MESH_NODES = "{HOST}/v1/mesh/nodes";
  var TIP_SOCKET = "tip-tick-1s";
  var GATE_SOCKET = "gate-777";
  if (TIP_SOCKET === GATE_SOCKET) throw new Error("STW-SOCKET-SHARED");
  function meshRollup(j) {{
    if (j && j.rollup && typeof j.rollup === "object") {{
      var live = Number(j.rollup.live);
      var locked = Number(j.rollup.locked);
      var isolated = Number(j.rollup.isolated);
      if ([live, locked, isolated].some(Number.isFinite)) {{
        return {{ live: Number.isFinite(live) ? live : 0, locked: Number.isFinite(locked) ? locked : 0, isolated: Number.isFinite(isolated) ? isolated : 0 }};
      }}
    }}
    return null;
  }}
  function paintMesh(j) {{
    var stateEl = document.getElementById("nodesState");
    var rollEl = document.getElementById("nodesRollup");
    var listEl = document.getElementById("nodesList");
    if (!stateEl || !rollEl || !listEl) return;
    stateEl.textContent = "Mesh ON";
    stateEl.className = "on";
    if (!j) return;
    var roll = meshRollup(j);
    rollEl.textContent = roll
      ? ("live " + roll.live + " · locked " + roll.locked + " · isolated " + roll.isolated)
      : ((j.live_nodes || 0) + " live");
    var products = j.products_present || j.products || [];
    var roster = j.nodes || [];
    var labels = roster.length
      ? roster.map(function (n) {{ return (n && (n.label || n.product || n.node_id)) || ""; }}).filter(Boolean)
      : products;
    if (labels.length) listEl.textContent = labels.join(" · ");
  }}
  async function meshJson(path) {{
    var r = await fetch(path, {{ headers: {{ "user-agent": "Mozilla/5.0" }} }});
    return r.json();
  }}
  async function meshTick() {{
    var status;
    try {{ status = await meshJson(MESH_STATUS); }} catch (e) {{ return; }}
    var view = status;
    try {{
      var extra = await meshJson(MESH_NODES);
      if (extra && extra.nodes) view = Object.assign({{}}, status, extra);
    }} catch (e) {{ /* status is enough */ }}
    paintMesh(view);
  }}
  refresh();
  meshTick();
  setInterval(meshTick, 20000);
}})();
</script>
</body>
</html>
"""
