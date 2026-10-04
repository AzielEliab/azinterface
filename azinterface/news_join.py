"""AZNews and 4DMap on the existing local 4DMap door.

AZNews can store a story with no pin. 4DMap can show the shadow-link
layer with no story. The join is a pin of one stored story on that same
door. join_live is true only after the story is read back as a pin.
This is not a catalog row, not a second FragGate door, and not a running map.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()
_PLACEHOLDERS = frozenset(
    {
        "test",
        "todo",
        "tbd",
        "placeholder",
        "synthetic",
        "sample",
        "lorem",
        "lorem ipsum",
        "n/a",
        "na",
        "none",
        "pin",
        "join",
        "news",
        "aznews",
        "4dmap",
    }
)

NOT_A_RUNNING_MAP = "This row is in the catalog. It is not a running map."
NO_PIN = "No news item has landed as a pin."
LANDED = "A news item landed as a pin."


def news_path(vendor: Path) -> Path:
    return Path(vendor) / "aznews.json"


def add_news(path: Path, payload: dict[str, Any], *, shadow_links: int = 0) -> dict[str, Any]:
    headline = _clip(payload.get("headline"), 140)
    body = _clip(payload.get("body"), 2000)
    problem = _real_item(headline, body)
    if problem:
        view = join_view(path, shadow_links=shadow_links)
        view["ok"] = False
        view["error"] = problem
        view["join_live"] = _join_live(view["pins"])
        view["status"] = NO_PIN if not view["join_live"] else LANDED
        view["display"] = _display(view["join_live"], view["status"])
        return view
    created_at = _now()
    record = {
        "id": _item_id(headline or "", body or "", created_at),
        "headline": headline,
        "body": body,
        "created_at": created_at,
        "pinned_at": None,
    }
    with _LOCK:
        rows = _read(path)
        rows.append(record)
        if payload.get("pin") is True:
            record["pinned_at"] = _now()
        _write(path, rows)
    return _after_write(path, shadow_links=shadow_links, item_id=record["id"], pinned=record["pinned_at"] is not None)


def pin_news(path: Path, payload: dict[str, Any], *, shadow_links: int = 0) -> dict[str, Any]:
    wanted = str(payload.get("id") or "").strip()
    with _LOCK:
        rows = _read(path)
        row = next((item for item in rows if item.get("id") == wanted), None)
        if row is None:
            missing = join_view(path, shadow_links=shadow_links)
            missing["ok"] = False
            missing["error"] = "That story is not stored."
            missing["join_live"] = _join_live(missing["pins"])
            missing["status"] = LANDED if missing["join_live"] else NO_PIN
            missing["display"] = _display(missing["join_live"], missing["status"])
            return missing
        problem = _real_item(row.get("headline"), row.get("body"))
        if problem:
            view = join_view(path, shadow_links=shadow_links)
            view["ok"] = False
            view["error"] = problem
            view["display"] = _display(view["join_live"], view["status"])
            return view
        if not row.get("pinned_at"):
            row["pinned_at"] = _now()
            _write(path, rows)
        item_id = str(row.get("id"))
    return _after_write(path, shadow_links=shadow_links, item_id=item_id, pinned=True)


def unpin_news(path: Path, payload: dict[str, Any], *, shadow_links: int = 0) -> dict[str, Any]:
    wanted = str(payload.get("id") or "").strip()
    with _LOCK:
        rows = _read(path)
        row = next((item for item in rows if item.get("id") == wanted), None)
        if row is None:
            missing = join_view(path, shadow_links=shadow_links)
            missing["ok"] = False
            missing["error"] = "That story is not stored."
            missing["display"] = _display(missing["join_live"], missing["status"])
            return missing
        row["pinned_at"] = None
        _write(path, rows)
    view = join_view(path, shadow_links=shadow_links)
    view["item"] = next((item for item in view["items"] if item.get("id") == wanted), None)
    return view


def join_view(path: Path, *, shadow_links: int = 0) -> dict[str, Any]:
    rows = _public_rows(_read(path))
    pins = [row for row in rows if row.get("pinned_at") and _real_item(row.get("headline"), row.get("body")) is None]
    join_live = _join_live(pins)
    status = LANDED if join_live else NO_PIN
    return {
        "ok": True,
        "aznews_standalone": True,
        "fourdmap_standalone": True,
        "running_map": False,
        "catalog_status": NOT_A_RUNNING_MAP,
        "shadow_links": shadow_links,
        "joined": join_live,
        "join_live": join_live,
        "status": status,
        "count": len(rows),
        "items": rows,
        "pins": pins,
        "display": _display(join_live, status),
    }


def news_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZNews</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --card:#fffdf8; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --card:#1c1b17; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
* { box-sizing: border-box; }
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; max-width:44rem; }
h1 { font-size:1.35rem; margin:0 0 0.35rem; }
p, label { color:var(--muted); }
label { display:block; margin:0.45rem 0 0.15rem; }
input, textarea { font:inherit; width:100%; padding:0.4rem 0.55rem; border:1px solid var(--line); border-radius:10px; background:transparent; color:inherit; }
textarea { min-height:7rem; }
button { font:inherit; min-height:44px; border-radius:10px; border:1px solid var(--line); background:transparent; color:inherit; padding:0.4rem 0.7rem; }
button.primary { background:#c9a227; color:#1a1404; border:0; font-weight:650; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
article { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:0.7rem; margin:0 0 0.6rem; }
article p { margin:0.2rem 0; color:inherit; }
.row { display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.45rem; }
#status { min-height:1.5rem; white-space:pre-wrap; }
a { color:inherit; }
</style>
</head>
<body>
<main>
  <h1>AZNews</h1>
  <p>AZNews stands on its own. A story stays here until it is pinned. 4DMap stands on its own. The shadow layer does not require a story. The join is not live until a news item lands as a pin.</p>
  <p><a href="/suite/4dmap">Open the 4DMap shadow layer</a></p>
  <label for="headline">Headline</label>
  <input id="headline" autocomplete="off">
  <label for="body">Story</label>
  <textarea id="body"></textarea>
  <p class="row"><button class="primary" id="save" type="button">Save story</button></p>
  <p id="status" role="status">No news item has landed as a pin.</p>
  <div id="list"></div>
</main>
<script>
(function () {
  var status = document.getElementById("status");
  var list = document.getElementById("list");

  function storyBody() {
    return {
      headline: document.getElementById("headline").value,
      body: document.getElementById("body").value
    };
  }

  async function post(path, body) {
    var res = await fetch(path, {
      method: "POST",
      headers: { "content-type": "application/json", "accept": "application/json" },
      body: JSON.stringify(body)
    });
    return res.json();
  }

  function paint(data) {
    status.textContent = data.error ? data.error : (data.status || "No news item has landed as a pin.");
    list.replaceChildren();
    (data.items || []).forEach(function (item) {
      var card = document.createElement("article");
      var title = document.createElement("h2");
      title.textContent = item.headline || "";
      var copy = document.createElement("p");
      copy.textContent = item.body || "";
      var when = document.createElement("p");
      when.textContent = item.pinned_at ? "This story is pinned on 4DMap." : "This story is not pinned.";
      var actions = document.createElement("div");
      actions.className = "row";
      var pin = document.createElement("button");
      pin.type = "button";
      pin.className = "primary";
      pin.textContent = item.pinned_at ? "Unpin" : "Pin on 4DMap";
      pin.addEventListener("click", function () {
        var path = item.pinned_at ? "/suite/4dmap/unpin" : "/suite/4dmap/pin";
        post(path, { id: item.id }).then(paint).catch(function () {
          status.textContent = "The story could not be updated.";
        });
      });
      actions.appendChild(pin);
      card.appendChild(title);
      card.appendChild(copy);
      card.appendChild(when);
      card.appendChild(actions);
      list.appendChild(card);
    });
  }

  document.getElementById("save").addEventListener("click", function () {
    post("/suite/4dmap/news", storyBody()).then(function (data) {
      paint(data);
    }).catch(function () {
      status.textContent = "The story could not be saved.";
    });
  });

  fetch("/suite/4dmap/pins", { headers: { "accept": "application/json" } })
    .then(function (res) { return res.json(); })
    .then(paint)
    .catch(function () { status.textContent = "The story list could not be read."; });
})();
</script>
</body>
</html>
"""


def _after_write(path: Path, *, shadow_links: int, item_id: str, pinned: bool) -> dict[str, Any]:
    view = join_view(path, shadow_links=shadow_links)
    item = next((row for row in view["items"] if row.get("id") == item_id), None)
    pin = next((row for row in view["pins"] if row.get("id") == item_id), None)
    view["item"] = item
    if pinned:
        if pin is None or item is None or pin.get("headline") != item.get("headline") or pin.get("body") != item.get("body"):
            view["ok"] = False
            view["join_live"] = _join_live([row for row in view["pins"] if row.get("id") != item_id])
            view["joined"] = view["join_live"]
            view["status"] = LANDED if view["join_live"] else "The pin did not land."
            view["error"] = "The pin did not land."
            view["display"] = _display(view["join_live"], view["status"])
            return view
        view["pin"] = pin
        view["status"] = LANDED
        view["join_live"] = True
        view["joined"] = True
        view["display"] = _display(True, LANDED)
    return view


def _display(join_live: bool, summary: str) -> dict[str, Any]:
    return {
        "title": "News pin" if join_live else "No news pin",
        "summary": summary,
        "fields": [{"label": "join_live", "value": join_live}],
    }


def _join_live(pins: list[dict[str, Any]]) -> bool:
    return any(_real_item(pin.get("headline"), pin.get("body")) is None and pin.get("pinned_at") for pin in pins)


def _real_item(headline: Any, body: Any) -> str | None:
    title = headline if isinstance(headline, str) else ""
    story = body if isinstance(body, str) else ""
    if not title or not story:
        return "A news item needs a headline and a body."
    if len(title) < 3 or len(story) < 12:
        return "That text is too short to be a news item."
    if title.casefold() in _PLACEHOLDERS or story.casefold() in _PLACEHOLDERS:
        return "That text is not a news item."
    if title.casefold() == story.casefold():
        return "The body has to say more than the headline."
    if not any(ch.isalpha() for ch in title) or not any(ch.isalpha() for ch in story):
        return "A news item needs words."
    return None


def _clip(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:limit]


def _item_id(headline: str, body: str, created_at: str) -> str:
    digest = sha256(f"{headline}|{body}|{created_at}".encode("utf-8")).hexdigest()
    return "nw-" + digest[:12]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _public_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public = []
    for row in rows:
        public.append(
            {
                "id": row.get("id"),
                "headline": row.get("headline"),
                "body": row.get("body"),
                "created_at": row.get("created_at"),
                "pinned_at": row.get("pinned_at"),
            }
        )
    return public


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = data.get("items") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"items": rows}, indent=2) + "\n", encoding="utf-8")
