"""Suite desk HTML. Custody stays on /custody, linked under Advanced."""

from __future__ import annotations

from html import escape

from .meta import IDENTITY, LOOPBACK, SPEC, VERSION

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZInterface</title>
<style>
:root {
  color-scheme: light dark;
  --bg: #f4f0e6;
  --card: #fffdf8;
  --ink: #1a1713;
  --muted: #5c564a;
  --line: #ddd4c2;
  --gold-ink: #1a1404;
  --link: #6b520c;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #100f0c;
    --card: #1c1b17;
    --ink: #f4efe4;
    --muted: #c8bfae;
    --line: #3d382e;
    --gold-ink: #1a1404;
    --link: #e6c56b;
  }
}
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }
button, input, summary { font: inherit; color: inherit; }
button, summary { cursor: pointer; }
a { color: var(--link); }
:focus-visible { outline: 2px solid #c9a227; outline-offset: 3px; }
.wrap { max-width: 68rem; margin: 0 auto; padding: 1.25rem 1.25rem 3rem; }
.top { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--line); }
.brand { font-weight: 650; color: var(--ink); text-decoration: none; }
.by { margin: 0; color: var(--muted); }
h1 { margin: 0 0 0.35rem; font-size: 1.75rem; letter-spacing: -0.02em; }
.lede { margin: 0 0 1rem; max-width: 40rem; }
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem; }
button.primary, button.ghost, button.open {
  min-height: 44px; border-radius: 10px; padding: 0.65rem 1rem;
}
button.primary { background: #c9a227; color: var(--gold-ink); border: 0; font-weight: 650; flex: 1 1 14rem; }
button.ghost, button.open { background: transparent; border: 1px solid var(--line); }
button:disabled { opacity: 0.6; cursor: default; }
#summary { color: var(--muted); min-height: 1.5rem; }
.layout { display: grid; gap: 1rem; }
.pane, .tile, .advanced { background: var(--card); border: 1px solid var(--line); border-radius: 14px; }
.pane { padding: 1rem; min-width: 0; }
.pane h2 { margin: 0 0 0.35rem; font-size: 1.05rem; }
#pane-note { margin: 0 0 0.75rem; color: var(--muted); white-space: pre-wrap; overflow-wrap: anywhere; }
iframe { width: 100%; max-width: 100%; border: 1px solid var(--line); border-radius: 12px; background: var(--bg); height: 16rem; }
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.7rem; min-width: 0; }
.tile { padding: 0.8rem 0.85rem 0.9rem; min-width: 0; }
.tile h3 { margin: 0; font-size: 1rem; overflow-wrap: anywhere; }
.badge { display: inline-block; margin: 0.35rem 0; font-size: 0.82rem; font-weight: 650; }
.tile p { margin: 0 0 0.6rem; color: var(--muted); font-size: 0.92rem; overflow-wrap: anywhere; }
.tile button.open { width: 100%; }
.advanced { margin-top: 1rem; padding: 0.2rem 1rem 0.8rem; }
.advanced > summary, .group > summary { min-height: 44px; display: flex; align-items: center; font-weight: 650; }
footer { margin-top: 1.25rem; color: var(--muted); font-size: 0.9rem; }
@media (max-width: 420px) {
  .wrap { padding: 1rem 1rem 2.5rem; }
  h1 { font-size: 1.45rem; }
  .top { flex-direction: column; gap: 0.15rem; }
  .tiles { grid-template-columns: 1fr; }
  iframe { height: 16rem; }
}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="/">AZInterface</a>
    <p class="by">__AUTHOR__</p>
  </header>
  <main>
    <h1>Softwares</h1>
    <p class="lede">AZInterface is the suite on this computer. Start suite opens every Software that can run here. AZVPN starts with the suite. AZCoherence stays in the background. TrajectoryLock opens a review of satellite imagery for an event place and time. ShadowLock links any Software. 4DMap shows those links.</p>
    <div class="actions">
      <button class="primary" id="start-suite" type="button">Start suite</button>
      <button class="ghost" id="refresh" type="button">Refresh</button>
    </div>
    <p id="summary" role="status" aria-live="polite">Reading the catalog…</p>
    <div class="layout">
      <section class="pane" aria-labelledby="pane-title">
        <h2 id="pane-title">No Software open yet</h2>
        <p id="pane-note">Press Start suite. A page appears here only after that Software is actually open.</p>
        <p id="pane-link"></p>
        <iframe id="pane-frame" title="Open Software" hidden></iframe>
      </section>
      <div class="tiles" id="desk"></div>
    </div>
    <details class="advanced" id="advanced">
      <summary>Advanced</summary>
      <p>Custody for this computer: integrity and the page cycle. The suite folder is <code>__VENDOR__</code>.</p>
      <iframe id="custody-frame" title="Custody" src="/custody"></iframe>
      <details class="group" id="about">
        <summary>Notes</summary>
        <p>AZInterface __VERSION__ (__SPEC__). Author: __AUTHOR__. Each other Software keeps its own ui command. This page installs a missing package from that card's download, then starts it. When a Software has no local page, the pane is a FragGate session for its slug.</p>
      </details>
    </details>
  </main>
  <footer>
    <p>AZInterface __VERSION__ · __SPEC__</p>
    <p>__AUTHOR__ · http://__LOOPBACK__:__PORT__/</p>
  </footer>
</div>
<script>
(function () {
  var picked = null;
  var summary = document.getElementById("summary");
  var desk = document.getElementById("desk");
  var frame = document.getElementById("pane-frame");
  var title = document.getElementById("pane-title");
  var note = document.getElementById("pane-note");
  var link = document.getElementById("pane-link");
  var startBtn = document.getElementById("start-suite");

  function countsText(data) {
    var counts = data.counts || {};
    var order = ["ready", "running", "quiet", "review", "link", "map", "installing", "needs-install", "local-only", "fraggate-only", "repair", "failed"];
    var labels = {
      ready: "Ready",
      running: "Running",
      quiet: "Quiet",
      review: "Review",
      link: "Link",
      map: "Map",
      installing: "Installing",
      "needs-install": "Needs install",
      "local-only": "Local only",
      "fraggate-only": "FragGate only",
      repair: "Repair",
      failed: "Could not open"
    };
    var parts = [];
    order.forEach(function (key) {
      if (counts[key]) parts.push(labels[key] + " " + counts[key]);
    });
    var line = (data.count || 0) + " Softwares";
    if (data.source) line += " · " + data.source;
    if (parts.length) line += " · " + parts.join(" · ");
    if (data.running) line += " · Starting";
    return line;
  }

  function show(row) {
    if (!row) return;
    title.textContent = row.name;
    var bits = [];
    if (row.reason) bits.push(row.reason);
    if (row.next) bits.push("Next: " + row.next);
    note.textContent = bits.join(" ");
    link.textContent = "";
    if (row.url) {
      frame.hidden = false;
      if (frame.getAttribute("src") !== row.url) frame.setAttribute("src", row.url);
      if (/^https?:/.test(row.url)) {
        var a = document.createElement("a");
        a.href = row.url;
        a.textContent = row.url;
        a.target = "_blank";
        a.rel = "noopener";
        link.appendChild(a);
      }
    } else {
      frame.hidden = true;
      frame.removeAttribute("src");
    }
  }

  function paint(data) {
    summary.textContent = countsText(data);
    desk.replaceChildren();
    var rows = data.software || [];
    rows.forEach(function (row) {
      var tile = document.createElement("article");
      tile.className = "tile";
      var h = document.createElement("h3");
      h.textContent = row.name;
      var badge = document.createElement("div");
      badge.className = "badge";
      badge.textContent = row.label || row.posture || "";
      var p = document.createElement("p");
      p.textContent = row.reason || "";
      tile.appendChild(h);
      tile.appendChild(badge);
      tile.appendChild(p);
      if (!row.background) {
        var button = document.createElement("button");
        button.className = "open";
        button.type = "button";
        var action = "Open";
        if (row.always_on) action = "Rotate IP";
        else if (row.review) action = "Review";
        else if (row.link) action = "Link";
        else if (row.map) action = "Map";
        button.textContent = action;
        button.addEventListener("click", function () {
          picked = row.slug;
          if (row.always_on || row.review || row.link || row.map) show(row);
          else openOne(row.slug);
        });
        tile.appendChild(button);
      }
      desk.appendChild(tile);
    });
    var chosen = null;
    if (picked) {
      rows.forEach(function (row) { if (row.slug === picked) chosen = row; });
    }
    if (!chosen) {
      rows.forEach(function (row) {
        if (!chosen && row.url && row.mode === "local" && (row.outcome === "booted" || row.outcome === "install-then-boot")) chosen = row;
      });
    }
    if (!chosen) {
      rows.forEach(function (row) {
        if (!chosen && row.url && row.mode === "suite" && row.outcome === "booted") chosen = row;
      });
    }
    if (!chosen) {
      rows.forEach(function (row) {
        if (!chosen && row.url && row.outcome) chosen = row;
      });
    }
    if (chosen) show(chosen);
    startBtn.disabled = !!data.running;
    startBtn.textContent = data.running ? "Starting…" : "Start suite";
    if (data.running) setTimeout(load, 800);
  }

  async function load() {
    try {
      var res = await fetch("/suite/software", { headers: { accept: "application/json" } });
      paint(await res.json());
    } catch (e) {
      summary.textContent = "The suite list could not be read. Stay on this computer and press Refresh.";
    }
  }

  async function openOne(slug) {
    summary.textContent = "Opening " + slug + "…";
    try {
      await fetch("/suite/boot", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ slug: slug })
      });
    } catch (e) {
      summary.textContent = "That Software could not be opened. Press Refresh and read the tile.";
    }
    load();
  }

  startBtn.addEventListener("click", async function () {
    picked = null;
    startBtn.disabled = true;
    startBtn.textContent = "Starting…";
    try {
      await fetch("/suite/start", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
    } catch (e) {
      summary.textContent = "Start suite could not begin. Stay on this computer and try again.";
      startBtn.disabled = false;
      startBtn.textContent = "Start suite";
      return;
    }
    load();
  });
  document.getElementById("refresh").addEventListener("click", load);
  load();
})();
</script>
</body>
</html>
"""


def suite_html(*, port: int, vendor: str) -> str:
    return (
        _PAGE.replace("__AUTHOR__", IDENTITY)
        .replace("__VERSION__", VERSION)
        .replace("__SPEC__", SPEC)
        .replace("__LOOPBACK__", LOOPBACK)
        .replace("__PORT__", str(port))
        .replace("__VENDOR__", escape(vendor))
    )
