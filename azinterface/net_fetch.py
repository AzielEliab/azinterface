"""One URL fetch on the existing suite door.

The desk requests one http or https URL and returns the status and body
it actually received. That fetch is not the packet path and not an
alternative internet. WARN-5 stands.
"""

from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_LIMIT = 200_000


def _local(body: dict[str, Any]) -> dict[str, Any]:
    body["packet_path"] = False
    body["alt_internet"] = False
    body["warn_5"] = "stands"
    return body


def fetch_url(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return _local({
            "ok": False,
            "fetched": False,
            "error": "The desk needs an http or https URL.",
            "status": "The response did not come back.",
        })
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    try:
        with urlopen(request, timeout=5) as resp:
            status = int(getattr(resp, "status", 0) or resp.getcode() or 0)
            payload_bytes = resp.read(_LIMIT + 1)
            final_url = resp.geturl()
    except HTTPError as exc:
        status = int(exc.code)
        payload_bytes = exc.read(_LIMIT + 1)
        final_url = url
    except (URLError, OSError, TimeoutError, ValueError) as exc:
        return _local({
            "ok": False,
            "fetched": False,
            "error": f"The response did not come back. {exc}",
            "status": "The response did not come back.",
        })
    body = payload_bytes[:_LIMIT].decode("utf-8", "replace")
    return _local({
        "ok": 200 <= status < 400,
        "fetched": True,
        "http_status": status,
        "url": final_url,
        "body": body,
        "truncated": len(payload_bytes) > _LIMIT,
        "status": "The response body came back." if 200 <= status < 400 else "The server answered and the body came back.",
    })


def net_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZNet</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
* { box-sizing: border-box; }
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; max-width:40rem; }
h1 { font-size:1.35rem; margin:0 0 0.35rem; }
p, label { color:var(--muted); }
label { display:block; margin:0.45rem 0 0.15rem; }
input { font:inherit; width:100%; min-height:44px; padding:0.4rem 0.55rem; border:1px solid var(--line); border-radius:10px; background:transparent; color:inherit; }
button { font:inherit; min-height:44px; border-radius:10px; background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.45rem 0.8rem; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
#status, #body { white-space:pre-wrap; overflow-wrap:anywhere; }
</style>
</head>
<body>
<main>
  <h1>AZNet</h1>
  <p>This desk fetches one http or https URL and shows the body. That fetch is not the packet path. An alternative internet does not run. WARN-5 stands.</p>
  <label for="url">URL</label>
  <input id="url" autocomplete="off" placeholder="https://">
  <p><button id="fetch" type="button">Fetch</button></p>
  <p id="status" role="status">No response yet.</p>
  <p id="body"></p>
</main>
<script>
document.getElementById("fetch").addEventListener("click", function () {
  var status = document.getElementById("status");
  var body = document.getElementById("body");
  status.textContent = "Fetching…";
  body.textContent = "";
  fetch("/suite/aznet/fetch", {
    method: "POST",
    headers: { "content-type": "application/json", "accept": "application/json" },
    body: JSON.stringify({ url: document.getElementById("url").value })
  }).then(function (res) { return res.json(); }).then(function (data) {
    status.textContent = data.status || data.error || "The response did not come back.";
    body.textContent = data.body || "";
  }).catch(function () {
    status.textContent = "The response did not come back.";
  });
});
</script>
</body>
</html>
"""
