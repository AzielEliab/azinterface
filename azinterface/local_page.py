"""Loopback operator page for people who already installed AZInterface.

The Worker homepage stays in web_page.home_html. This page is the local console only.
"""

from __future__ import annotations

from .meta import IDENTITY, LOOPBACK, PORT, SPEC, VERSION

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
  --gold: #c9a227;
  --gold-ink: #1a1404;
  --link: #6b520c;
  --shadow: 0 1px 0 rgba(26, 23, 19, 0.04);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #100f0c;
    --card: #1c1b17;
    --ink: #f4efe4;
    --muted: #c8bfae;
    --line: #3d382e;
    --gold: #c9a227;
    --gold-ink: #1a1404;
    --link: #e6c56b;
    --shadow: none;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body {
  font: 16px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--ink);
}
button, input, summary { font: inherit; color: inherit; }
button, summary { cursor: pointer; }
a { color: var(--link); }
:focus-visible {
  outline: 2px solid #c9a227;
  outline-offset: 3px;
}
.wrap { max-width: 40rem; margin: 0 auto; padding: 1.25rem 1.25rem 3rem; }
.top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--line);
}
.brand { font-weight: 650; letter-spacing: 0.01em; text-decoration: none; color: var(--ink); }
.by { margin: 0; color: var(--muted); font-size: 0.95rem; }
h1 { margin: 0 0 0.4rem; font-size: 1.75rem; font-weight: 650; letter-spacing: -0.02em; }
h2 { margin: 0 0 0.35rem; font-size: 1rem; font-weight: 650; }
.lede { margin: 0 0 1.25rem; font-size: 1.05rem; max-width: 38rem; }
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1rem 1rem 1.1rem;
  box-shadow: var(--shadow);
}
.status { margin: 0; }
.cycle {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  list-style: none;
  margin: 0.9rem 0 0;
  padding: 0;
}
.cycle li {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.15rem 0.65rem;
  color: var(--muted);
  font-size: 0.85rem;
}
.cycle li[aria-current="step"] {
  border-color: #c9a227;
  color: var(--ink);
  font-weight: 650;
}
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; }
button.primary, button.ghost {
  min-height: 44px;
  border-radius: 10px;
  padding: 0.65rem 1rem;
}
button.primary {
  background: #c9a227;
  color: var(--gold-ink);
  border: 0;
  font-weight: 650;
  flex: 1 1 12rem;
}
button.ghost {
  background: transparent;
  border: 1px solid var(--line);
  flex: 1 1 8rem;
}
button:disabled { opacity: 0.6; cursor: default; }
#result {
  margin: 0.9rem 0 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
#result:empty { display: none; }
.advanced { margin-top: 1.25rem; }
.advanced > summary, .group > summary {
  min-height: 44px;
  display: flex;
  align-items: center;
  font-weight: 650;
}
.group {
  border-top: 1px solid var(--line);
  padding: 0.15rem 0 0.35rem;
}
.group p, .advanced > p { color: var(--muted); margin: 0.35rem 0 0.6rem; }
label { display: block; margin: 0.7rem 0 0.3rem; font-size: 0.92rem; }
input {
  width: 100%;
  max-width: 100%;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.6rem 0.7rem;
  min-height: 44px;
}
.row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
.row button { flex: 1 1 8rem; }
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-width: 100%;
  margin: 0.4rem 0 0;
  font-size: 0.82rem;
  line-height: 1.45;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.75rem;
}
footer { margin-top: 1.5rem; color: var(--muted); font-size: 0.9rem; }
footer p { margin: 0.2rem 0; }
@media (max-width: 420px) {
  .wrap { padding: 1rem 1rem 2.5rem; }
  h1 { font-size: 1.5rem; }
  .top { align-items: flex-start; flex-direction: column; gap: 0.15rem; }
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
    <h1>Custody on this computer</h1>
    <p class="lede">Hold, withdraw, and witness follow one sealed page step at a time.</p>
    <section class="card" aria-labelledby="now-title">
      <h2 id="now-title">Status</h2>
      <p class="status" id="status" aria-live="polite">Reading the page record…</p>
      <ol class="cycle" id="cycle">
        <li data-step="OFF">OFF</li>
        <li data-step="integrity">integrity</li>
        <li data-step="ON">ON</li>
        <li data-step="FULL SHUTDOWN">FULL SHUTDOWN</li>
        <li data-step="MEMORIAL">MEMORIAL</li>
      </ol>
      <div class="actions">
        <button class="primary" id="integrity-btn" type="button">Integrity check</button>
        <button class="ghost" id="health-btn" type="button">Check health</button>
      </div>
      <p id="result" role="status" aria-live="polite"></p>
    </section>
    <noscript><p>Turn on JavaScript for this page, or run <code>azinterface integrity</code> in a terminal.</p></noscript>
    <details class="advanced" id="advanced">
      <summary>Advanced</summary>
      <p>The rest of the custody controls. The page still moves one sealed step at a time.</p>
      <details class="group" id="group-genesis">
        <summary>Genesis</summary>
        <p>One-time key. The seed is hashed and discarded. It is not stored.</p>
        <label for="seed">Seed</label>
        <input id="seed" autocomplete="off" spellcheck="false">
        <div class="row">
          <button class="ghost" id="genesis-btn" type="button">Set genesis key</button>
          <button class="ghost" id="genesis-status-btn" type="button">Genesis status</button>
        </div>
      </details>
      <details class="group" id="group-cycle">
        <summary>Page cycle</summary>
        <p>Ask for one step. A skip is refused. MEMORIAL stays in place.</p>
        <div class="row">
          <button class="ghost" id="next-step-btn" type="button">Continue</button>
          <button class="ghost" data-state="integrity" type="button">integrity</button>
          <button class="ghost" data-state="ON" type="button">ON</button>
          <button class="ghost" data-state="OFF" type="button">OFF</button>
          <button class="ghost" data-state="FULL_SHUTDOWN" type="button">FULL SHUTDOWN</button>
          <button class="ghost" data-state="MEMORIAL" type="button">MEMORIAL</button>
        </div>
      </details>
      <details class="group" id="group-hold">
        <summary>Hold and witness</summary>
        <p>Hold and withdraw run when the page is ON. The witness list is metadata.</p>
        <label for="hold-label">Hold label</label>
        <input id="hold-label" autocomplete="off">
        <div class="row">
          <button class="ghost" id="hold-btn" type="button">Hold</button>
          <button class="ghost" id="withdraw-btn" type="button">Withdraw</button>
          <button class="ghost" id="witness-btn" type="button">Witness list</button>
        </div>
      </details>
      <details class="group" id="group-pair">
        <summary>Pair</summary>
        <p>Offer, accept, then seal. This page stores the cite. The via runs in local qnsd on 127.0.0.1.</p>
        <label for="pair-via">Via</label>
        <input id="pair-via" value="local" autocomplete="off">
        <label for="pair-id">Pair id</label>
        <input id="pair-id" autocomplete="off">
        <label for="photon-id">Photon id</label>
        <input id="photon-id" autocomplete="off">
        <div class="row">
          <button class="ghost" id="pair-offer-btn" type="button">Offer</button>
          <button class="ghost" id="pair-accept-btn" type="button">Accept</button>
          <button class="ghost" id="pair-seal-btn" type="button">Seal</button>
          <button class="ghost" id="pair-cut-btn" type="button">Cut</button>
          <button class="ghost" id="pair-status-btn" type="button">Pair status</button>
        </div>
      </details>
      <details class="group" id="group-scorch">
        <summary>Scorched Earth</summary>
        <p>The local advisory stays on this computer. A remote wipe request is refused.</p>
        <div class="row">
          <button class="ghost" id="scorch-local-btn" type="button">Local advisory</button>
          <button class="ghost" id="scorch-remote-btn" type="button">Remote wipe</button>
        </div>
      </details>
      <details class="group" id="group-records">
        <summary>Records</summary>
        <p>Pipeline cite and the last response, when you ask for them.</p>
        <div class="row">
          <button class="ghost" id="cycle-btn" type="button">Refresh page record</button>
          <button class="ghost" id="pipeline-btn" type="button">Pipeline cite</button>
        </div>
      </details>
      <details class="group" id="response-json">
        <summary>Response JSON</summary>
        <pre id="json-out">No response yet.</pre>
      </details>
      <details class="group" id="about">
        <summary>Notes</summary>
        <p>AZInterface __VERSION__ (__SPEC__) records a one-time genesis hash, an integrity check, and the sealed page cycle on this computer. The seed is hashed and discarded. Vault contents are not shown. Witness rows are metadata.</p>
        <p>Scorched Earth here is a local advisory. AZHub is separate software under the same FragGate door. Agents use that door with slug azinterface. This page is __LOOPBACK__ only.</p>
        <p>Author: __AUTHOR__. Apache-2.0. Forks are welcome.</p>
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
  var nextName = null;
  function textOf(obj) {
    var lines = [];
    var display = obj && obj.display;
    if (display && display.title) lines.push(String(display.title));
    if (display && display.summary) lines.push(String(display.summary));
    var fields = (display && display.fields) || [];
    for (var i = 0; i < fields.length; i++) {
      var row = fields[i];
      if (row && row.label != null) lines.push(String(row.label) + ": " + String(row.value));
    }
    if (!lines.length) lines.push((obj && (obj.error || obj.code)) || "Done.");
    if (obj && obj.ok === false && obj.code) lines.push("Code: " + obj.code);
    if (obj && obj.ok && obj.integrity_ok && obj.current === "integrity" && !obj.living_presence) {
      lines.push("Next: open Advanced and press ON.");
    }
    return lines.join("\\n");
  }
  function show(obj) {
    var result = document.getElementById("result");
    result.textContent = textOf(obj);
    var pre = document.getElementById("json-out");
    pre.textContent = JSON.stringify(obj, null, 2);
  }
  function failed() {
    document.getElementById("result").textContent = "The local page could not complete that request. Stay on this computer and try again.";
  }
  function statusText(cycle) {
    var page = cycle.current || cycle.site_state || "OFF";
    var integrity = cycle.integrity_ok ? "Integrity is recorded." : "Integrity is not recorded yet.";
    var living = cycle.living_presence
      ? "Living presence is on. AZHome can be used."
      : "Living presence is off until the page is ON after integrity.";
    var next = cycle.page_cycle && cycle.page_cycle.next;
    var step = next ? "Next sealed step: " + next + "." : "MEMORIAL stays in place.";
    var genesis = cycle.genesis_keyed ? "Genesis key is set." : "Genesis key is not set yet.";
    return "Page is " + page + ". " + integrity + " " + living + " " + step + " " + genesis;
  }
  function paint(cycle) {
    var page = cycle.current || cycle.site_state || "OFF";
    document.getElementById("status").textContent = statusText(cycle);
    var items = document.querySelectorAll(".cycle li");
    for (var i = 0; i < items.length; i++) {
      if (items[i].getAttribute("data-step") === page) items[i].setAttribute("aria-current", "step");
      else items[i].removeAttribute("aria-current");
    }
    nextName = (cycle.page_cycle && cycle.page_cycle.next) || null;
    var nextBtn = document.getElementById("next-step-btn");
    if (!nextName) {
      nextBtn.textContent = "MEMORIAL stays in place";
      nextBtn.disabled = true;
      nextBtn.removeAttribute("data-action");
    } else if (!cycle.integrity_ok) {
      nextBtn.disabled = false;
      nextBtn.textContent = "Integrity check";
      nextBtn.setAttribute("data-action", "integrity");
    } else {
      nextBtn.disabled = false;
      nextBtn.textContent = "Continue to " + nextName;
      nextBtn.setAttribute("data-action", "step");
    }
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
    paint(cycle);
    return cycle;
  }
  async function run(btn, op, payload) {
    if (btn) btn.disabled = true;
    try {
      var out = await call(op, payload);
      show(out);
      if (op === "integrity_check" || op === "site_state_set" || op === "genesis_boot" || op === "hold" || op === "withdraw" || op === "scorch_local") {
        await refresh();
      }
      return out;
    } catch (e) {
      failed();
    } finally {
      if (btn && btn.id !== "next-step-btn") btn.disabled = false;
      if (btn && btn.id === "next-step-btn" && nextName) btn.disabled = false;
    }
  }
  document.getElementById("integrity-btn").addEventListener("click", function () {
    run(document.getElementById("integrity-btn"), "integrity_check", {});
  });
  document.getElementById("health-btn").addEventListener("click", function () {
    run(document.getElementById("health-btn"), "health", {});
  });
  document.getElementById("genesis-btn").addEventListener("click", function () {
    var seed = document.getElementById("seed").value;
    document.getElementById("seed").value = "";
    run(document.getElementById("genesis-btn"), "genesis_boot", { username: seed });
  });
  document.getElementById("genesis-status-btn").addEventListener("click", function () {
    run(document.getElementById("genesis-status-btn"), "genesis_status", {});
  });
  document.getElementById("next-step-btn").addEventListener("click", function () {
    var button = document.getElementById("next-step-btn");
    var action = button.getAttribute("data-action");
    if (action === "integrity") run(button, "integrity_check", {});
    else if (action === "step" && nextName) run(button, "site_state_set", { state: nextName });
  });
  var steps = document.querySelectorAll("[data-state]");
  for (var s = 0; s < steps.length; s++) {
    steps[s].addEventListener("click", function (ev) {
      var button = ev.currentTarget;
      run(button, "site_state_set", { state: button.getAttribute("data-state") });
    });
  }
  document.getElementById("hold-btn").addEventListener("click", function () {
    run(document.getElementById("hold-btn"), "hold", { label: document.getElementById("hold-label").value });
  });
  document.getElementById("withdraw-btn").addEventListener("click", function () {
    run(document.getElementById("withdraw-btn"), "withdraw", {});
  });
  document.getElementById("witness-btn").addEventListener("click", function () {
    run(document.getElementById("witness-btn"), "witness_list", {});
  });
  function pairPayload() {
    return {
      via: document.getElementById("pair-via").value,
      pair_id: document.getElementById("pair-id").value,
      photon_id: document.getElementById("photon-id").value
    };
  }
  document.getElementById("pair-offer-btn").addEventListener("click", async function () {
    var out = await run(document.getElementById("pair-offer-btn"), "pair_offer", pairPayload());
    if (out && out.pair && out.pair.pair_id) document.getElementById("pair-id").value = out.pair.pair_id;
    if (out && out.pair && out.pair.photon_id) document.getElementById("photon-id").value = out.pair.photon_id;
  });
  document.getElementById("pair-accept-btn").addEventListener("click", function () {
    run(document.getElementById("pair-accept-btn"), "pair_accept", pairPayload());
  });
  document.getElementById("pair-seal-btn").addEventListener("click", function () {
    run(document.getElementById("pair-seal-btn"), "pair_seal", pairPayload());
  });
  document.getElementById("pair-cut-btn").addEventListener("click", function () {
    run(document.getElementById("pair-cut-btn"), "pair_cut", pairPayload());
  });
  document.getElementById("pair-status-btn").addEventListener("click", function () {
    run(document.getElementById("pair-status-btn"), "pair_status", {});
  });
  document.getElementById("scorch-local-btn").addEventListener("click", function () {
    run(document.getElementById("scorch-local-btn"), "scorch_local", {});
  });
  document.getElementById("scorch-remote-btn").addEventListener("click", function () {
    run(document.getElementById("scorch-remote-btn"), "scorch_remote", {});
  });
  document.getElementById("cycle-btn").addEventListener("click", async function () {
    var btn = document.getElementById("cycle-btn");
    btn.disabled = true;
    try {
      show(await refresh());
    } catch (e) {
      failed();
    } finally {
      btn.disabled = false;
    }
  });
  document.getElementById("pipeline-btn").addEventListener("click", function () {
    run(document.getElementById("pipeline-btn"), "pipeline_arch", {});
  });
  refresh().catch(function () {
    document.getElementById("status").textContent = "The page record is not available yet. Use Integrity check, or reload this tab.";
  });
})();
</script>
</body>
</html>
"""


def operator_html(*, port: int = PORT) -> str:
    return (
        _PAGE.replace("__VERSION__", VERSION)
        .replace("__SPEC__", SPEC)
        .replace("__AUTHOR__", IDENTITY)
        .replace("__LOOPBACK__", LOOPBACK)
        .replace("__PORT__", str(port))
    )
