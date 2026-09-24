"""Local ShadowLock link record and the suite desks that read it.

A link is a Software plus an optional input handle and a business label.
File drops store the file name only. File contents are not read.
4DMap reads this same record. An empty record stays empty.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

BUCKETS = ("plain", "gate", "lock")


def links_path(vendor: Path) -> Path:
    return Path(vendor) / "shadow-links.json"


def list_links(path: Path) -> dict[str, Any]:
    rows = _read(path)
    return {
        "ok": True,
        "count": len(rows),
        "empty": not rows,
        "links": rows,
    }


def add_link(path: Path, payload: dict[str, Any], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    slug = str(payload.get("slug") or "").strip()
    card = next((row for row in catalog if row.get("slug") == slug), None)
    if card is None:
        return {
            "ok": False,
            "error": f"No Software named {slug or 'that'} is in this catalog.",
            "next": "Link a name from the suite list.",
            "links": _read(path),
        }
    bucket = card.get("bucket") if card.get("bucket") in BUCKETS else None
    label = _clip(payload.get("label"), 80)
    raw_input = _clip(payload.get("input"), 240)
    input_from = str(payload.get("input_from") or "typed").strip()
    if input_from not in {"typed", "file-name"}:
        input_from = "typed"
    note = None
    if raw_input and input_from == "file-name":
        note = "File name only. Contents were not read."
    linked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    record = {
        "id": _link_id(slug, raw_input, label, linked_at),
        "slug": slug,
        "name": str(card.get("name") or slug),
        "bucket": bucket,
        "input": raw_input,
        "input_from": input_from if raw_input else None,
        "input_note": note,
        "label": label,
        "linked_at": linked_at,
    }
    rows = _read(path)
    rows.append(record)
    _write(path, rows)
    body = list_links(path)
    body["link"] = record
    return body


def remove_link(path: Path, link_id: str) -> dict[str, Any]:
    wanted = str(link_id or "").strip()
    rows = _read(path)
    kept = [row for row in rows if row.get("id") != wanted]
    if len(kept) == len(rows):
        body = list_links(path)
        body["ok"] = False
        body["error"] = "That link is not in the local record."
        return body
    _write(path, kept)
    return list_links(path)


def shadow_desk_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShadowLock links</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --card:#fffdf8; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --card:#1c1b17; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
* { box-sizing: border-box; }
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; }
h1 { font-size:1.35rem; margin:0 0 0.35rem; }
p, label { color:var(--muted); }
label { display:block; margin:0.45rem 0 0.15rem; }
input { font:inherit; width:100%; min-height:44px; padding:0.4rem 0.55rem; border:1px solid var(--line); border-radius:10px; background:transparent; color:inherit; }
button { font:inherit; min-height:44px; border-radius:10px; border:1px solid var(--line); background:transparent; color:inherit; padding:0.4rem 0.7rem; }
button.primary { background:#c9a227; color:#1a1404; border:0; font-weight:650; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
.fields { display:grid; gap:0.4rem; margin-bottom:0.8rem; }
.columns { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:0.7rem; }
.col { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:0.7rem; min-width:0; }
.col.hot { outline:2px solid #c9a227; }
.col h2 { margin:0 0 0.4rem; font-size:1rem; }
.chip, .linkrow { display:flex; justify-content:space-between; gap:0.4rem; align-items:center; margin:0.35rem 0; }
.chip span, .linkrow span { overflow-wrap:anywhere; }
.muted { color:var(--muted); font-size:0.92rem; }
#status { min-height:1.5rem; white-space:pre-wrap; }
@media (max-width: 420px) {
  .columns { grid-template-columns:1fr; }
}
</style>
</head>
<body>
<main>
  <h1>ShadowLock</h1>
  <p>Link any Software into ShadowLock. Drop a chip on its kind, or press Link. A file drop stores the file name only.</p>
  <div class="fields">
    <label for="biz">Business label</label>
    <input id="biz" autocomplete="off" placeholder="Desk or matter">
    <label for="input-path">Input id or path</label>
    <input id="input-path" autocomplete="off" placeholder="Optional input handle">
  </div>
  <p id="status" role="status">Nothing is linked yet.</p>
  <div class="columns" id="columns"></div>
</main>
<script>
(function () {
  var status = document.getElementById("status");
  var columns = document.getElementById("columns");
  var inputFrom = "typed";
  var kinds = [
    ["plain", "Plain"],
    ["gate", "Gate"],
    ["lock", "Lock"],
    ["unclassified", "Unclassified"]
  ];

  function fields() {
    return {
      label: document.getElementById("biz").value,
      input: document.getElementById("input-path").value
    };
  }

  async function linkOne(slug) {
    var body = fields();
    body.slug = slug;
    body.input_from = inputFrom;
    status.textContent = "Linking " + slug + "…";
    var res = await fetch("/suite/shadowlock/link", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    });
    var data = await res.json();
    if (!data.ok) {
      status.textContent = (data.error || "The link was not saved.") + (data.next ? " " + data.next : "");
      return;
    }
    var saved = data.link || {};
    var kind = saved.bucket || "unclassified";
    status.textContent = "Linked " + (saved.name || slug) + " as " + kind + ".";
    if (saved.input_note) status.textContent += " " + saved.input_note;
    inputFrom = "typed";
    await paint();
  }

  function chip(row) {
    var wrap = document.createElement("div");
    wrap.className = "chip";
    wrap.draggable = true;
    wrap.dataset.slug = row.slug;
    wrap.dataset.bucket = row.bucket || "unclassified";
    var name = document.createElement("span");
    name.textContent = row.name;
    var button = document.createElement("button");
    button.type = "button";
    button.className = "primary";
    button.textContent = "Link";
    button.addEventListener("click", function () { linkOne(row.slug); });
    wrap.addEventListener("dragstart", function (ev) {
      ev.dataTransfer.setData("text/plain", row.slug);
      ev.dataTransfer.setData("application/x-az-bucket", wrap.dataset.bucket);
      document.querySelectorAll(".col").forEach(function (col) {
        col.classList.toggle("hot", col.dataset.bucket === wrap.dataset.bucket);
      });
    });
    wrap.addEventListener("dragend", function () {
      document.querySelectorAll(".col").forEach(function (col) { col.classList.remove("hot"); });
    });
    wrap.appendChild(name);
    wrap.appendChild(button);
    return wrap;
  }

  function linkRow(row) {
    var wrap = document.createElement("div");
    wrap.className = "linkrow";
    var text = document.createElement("span");
    var bits = [row.name || row.slug];
    if (row.input) bits.push(row.input);
    else bits.push("no input path");
    if (row.label) bits.push(row.label);
    else bits.push("no business label");
    text.textContent = bits.join(" · ");
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = "Unlink";
    button.addEventListener("click", async function () {
      await fetch("/suite/shadowlock/unlink", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: row.id })
      });
      await paint();
    });
    wrap.appendChild(text);
    wrap.appendChild(button);
    return wrap;
  }

  async function paint() {
    var soft = await (await fetch("/suite/software")).json();
    var saved = await (await fetch("/suite/shadowlock/links")).json();
    var rows = soft.software || [];
    var links = saved.links || [];
    columns.replaceChildren();
    kinds.forEach(function (pair) {
      var key = pair[0];
      var title = pair[1];
      var mine = rows.filter(function (row) { return (row.bucket || "unclassified") === key; });
      var linked = links.filter(function (row) { return (row.bucket || "unclassified") === key; });
      if (key === "unclassified" && !mine.length && !linked.length) return;
      var col = document.createElement("section");
      col.className = "col";
      col.dataset.bucket = key;
      var h = document.createElement("h2");
      h.textContent = title;
      col.appendChild(h);
      if (linked.length) {
        var cap = document.createElement("p");
        cap.className = "muted";
        cap.textContent = "Linked";
        col.appendChild(cap);
        linked.forEach(function (row) { col.appendChild(linkRow(row)); });
      }
      if (!mine.length) {
        var empty = document.createElement("p");
        empty.className = "muted";
        empty.textContent = "No " + title.toLowerCase() + " Software in this catalog.";
        col.appendChild(empty);
      }
      mine.forEach(function (row) { col.appendChild(chip(row)); });
      col.addEventListener("dragover", function (ev) { ev.preventDefault(); });
      col.addEventListener("drop", function (ev) {
        ev.preventDefault();
        var slug = ev.dataTransfer.getData("text/plain");
        if (slug) {
          linkOne(slug);
          return;
        }
        var file = ev.dataTransfer.files && ev.dataTransfer.files[0];
        if (!file) return;
        document.getElementById("input-path").value = file.name;
        inputFrom = "file-name";
        status.textContent = "Kept the file name " + file.name + ". Press Link on a Software. Contents were not read.";
      });
      columns.appendChild(col);
    });
    if (!links.length) status.textContent = "Nothing is linked yet.";
    else status.textContent = links.length + (links.length === 1 ? " link saved." : " links saved.");
  }

  paint().catch(function () {
    status.textContent = "The link desk could not read the suite list.";
  });
})();
</script>
</body>
</html>
"""


def shadow_map_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>4DMap Shadow layer</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --card:#fffdf8; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --card:#1c1b17; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; max-width:44rem; }
h1 { font-size:1.35rem; margin:0 0 0.35rem; }
h2 { font-size:1.05rem; }
p, li { overflow-wrap:anywhere; }
#empty, .when { color:var(--muted); }
ol { padding-left:1.2rem; }
li { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:0.6rem 0.7rem; margin:0 0 0.5rem; }
button { font:inherit; min-height:44px; border-radius:10px; background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.45rem 0.8rem; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
</style>
</head>
<body>
<main>
  <h1>4DMap</h1>
  <h2>Softwares · Shadow</h2>
  <p id="empty">No ShadowLock links yet. Open the ShadowLock tile and link a Software. This layer does not invent marks.</p>
  <ol id="layer"></ol>
  <p><button id="refresh" type="button">Refresh</button></p>
</main>
<script>
(function () {
  var empty = document.getElementById("empty");
  var layer = document.getElementById("layer");
  async function paint() {
    var data = await (await fetch("/suite/shadowlock/links")).json();
    var rows = data.links || [];
    layer.replaceChildren();
    empty.hidden = rows.length > 0;
    rows.forEach(function (row) {
      var li = document.createElement("li");
      var title = document.createElement("strong");
      title.textContent = (row.name || row.slug) + " · " + (row.bucket || "unclassified");
      var when = document.createElement("div");
      when.className = "when";
      when.textContent = row.linked_at || "";
      var body = document.createElement("div");
      var input = row.input ? row.input : "no input path";
      var label = row.label ? row.label : "no business label";
      body.textContent = input + " · " + label;
      li.appendChild(title);
      li.appendChild(when);
      li.appendChild(body);
      if (row.input_note) {
        var note = document.createElement("div");
        note.className = "when";
        note.textContent = row.input_note;
        li.appendChild(note);
      }
      layer.appendChild(li);
    });
  }
  document.getElementById("refresh").addEventListener("click", function () {
    paint().catch(function () { empty.hidden = false; empty.textContent = "The Shadow layer could not be read."; });
  });
  paint().catch(function () { empty.textContent = "The Shadow layer could not be read."; });
})();
</script>
</body>
</html>
"""


def _clip(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:limit]


def _link_id(slug: str, raw_input: str | None, label: str | None, linked_at: str) -> str:
    digest = sha256(f"{slug}|{raw_input}|{label}|{linked_at}".encode("utf-8")).hexdigest()
    return "sl-" + digest[:12]


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = data.get("links") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"links": rows}, indent=2) + "\n", encoding="utf-8")
