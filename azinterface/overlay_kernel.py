"""AZ-OS overlay kernel on the existing suite door.

Boot creates a session folder. A later command reads and writes only
inside that folder. The host kernel is not started and is not replaced.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_VERBS = frozenset({"write", "cat", "echo", "pwd"})


def sessions_root(vendor: Path) -> Path:
    return Path(vendor) / "azos-sessions"


def boot_session(root: Path) -> dict[str, Any]:
    session = "os-" + uuid4().hex[:12]
    folder = _session_dir(root, session)
    folder.mkdir(parents=True, exist_ok=True)
    receipt = {
        "session": session,
        "booted_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "host_kernel": False,
    }
    (folder / "BOOT").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    read_back = json.loads((folder / "BOOT").read_text(encoding="utf-8"))
    if read_back.get("session") != session:
        return {
            "ok": False,
            "booted": False,
            "host_kernel": False,
            "error": "The session did not boot.",
            "status": "The session did not boot.",
        }
    return {
        "ok": True,
        "booted": True,
        "session": session,
        "host_kernel": False,
        "status": "The overlay session booted. The host kernel stays the host kernel.",
    }


def run_command(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    session = str(payload.get("session") or "").strip()
    verb = str(payload.get("op") or payload.get("command") or "").strip().lower()
    folder = _session_dir(root, session) if session.startswith("os-") and "/" not in session else None
    if folder is None or not (folder / "BOOT").is_file():
        return {
            "ok": False,
            "ran": False,
            "host_kernel": False,
            "error": "Boot a session before running a command.",
            "status": "The command did not run.",
        }
    if verb not in _VERBS:
        return {
            "ok": False,
            "ran": False,
            "host_kernel": False,
            "error": "That command is not registered.",
            "status": "The command did not run.",
        }
    if verb == "pwd":
        return {"ok": True, "ran": True, "host_kernel": False, "output": "/", "status": "The command ran inside the session."}
    if verb == "echo":
        text = str(payload.get("text") or "")
        return {"ok": True, "ran": True, "host_kernel": False, "output": text, "status": "The command ran inside the session."}
    rel = str(payload.get("path") or "").strip()
    try:
        target = _inside(folder, rel)
    except (ValueError, OSError):
        return {
            "ok": False,
            "ran": False,
            "host_kernel": False,
            "error": "That path stays inside the session.",
            "status": "The command did not run.",
        }
    if verb == "write":
        text = str(payload.get("text") if payload.get("text") is not None else "")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        read_back = target.read_text(encoding="utf-8")
        if read_back != text:
            return {
                "ok": False,
                "ran": False,
                "host_kernel": False,
                "error": "The file did not read back.",
                "status": "The command did not run.",
            }
        return {
            "ok": True,
            "ran": True,
            "host_kernel": False,
            "path": rel,
            "output": read_back,
            "status": "The command wrote the file and read it back.",
        }
    if not target.is_file():
        return {
            "ok": False,
            "ran": False,
            "host_kernel": False,
            "error": "That file is not in the session.",
            "status": "The command did not run.",
        }
    output = target.read_text(encoding="utf-8")
    return {
        "ok": True,
        "ran": True,
        "host_kernel": False,
        "path": rel,
        "output": output,
        "status": "The command read the file back.",
    }


def kernel_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZ-OS</title>
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
button { font:inherit; min-height:44px; border-radius:10px; border:1px solid var(--line); background:transparent; color:inherit; padding:0.4rem 0.7rem; margin-right:0.4rem; }
button.primary { background:#c9a227; color:#1a1404; border:0; font-weight:650; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
#status { min-height:1.5rem; white-space:pre-wrap; }
</style>
</head>
<body>
<main>
  <h1>AZ-OS</h1>
  <p>The overlay kernel boots a session and runs a command inside it. The host kernel stays the host kernel.</p>
  <p><button class="primary" id="boot" type="button">Boot session</button></p>
  <label for="path">File</label>
  <input id="path" value="marker.txt" autocomplete="off">
  <label for="text">Text</label>
  <input id="text" autocomplete="off">
  <p>
    <button id="write" type="button">Write</button>
    <button id="cat" type="button">Read back</button>
  </p>
  <p id="status" role="status">No session is booted.</p>
</main>
<script>
(function () {
  var session = "";
  var status = document.getElementById("status");
  function post(path, body) {
    return fetch(path, {
      method: "POST",
      headers: { "content-type": "application/json", "accept": "application/json" },
      body: JSON.stringify(body)
    }).then(function (res) { return res.json(); });
  }
  document.getElementById("boot").addEventListener("click", function () {
    post("/suite/azos/boot", {}).then(function (data) {
      session = data.session || "";
      status.textContent = data.status || data.error || "The session did not boot.";
    }).catch(function () { status.textContent = "The session did not boot."; });
  });
  document.getElementById("write").addEventListener("click", function () {
    post("/suite/azos/command", {
      session: session,
      op: "write",
      path: document.getElementById("path").value,
      text: document.getElementById("text").value
    }).then(function (data) {
      status.textContent = data.status || data.error || "The command did not run.";
    }).catch(function () { status.textContent = "The command did not run."; });
  });
  document.getElementById("cat").addEventListener("click", function () {
    post("/suite/azos/command", {
      session: session,
      op: "cat",
      path: document.getElementById("path").value
    }).then(function (data) {
      status.textContent = data.output != null && data.ran ? data.output : (data.status || data.error || "The command did not run.");
    }).catch(function () { status.textContent = "The command did not run."; });
  });
})();
</script>
</body>
</html>
"""


def _session_dir(root: Path, session: str) -> Path:
    return Path(root) / session


def _inside(folder: Path, rel: str) -> Path:
    if not rel or rel.startswith("/") or "\\" in rel:
        raise ValueError("outside")
    folder = folder.resolve()
    target = (folder / rel).resolve()
    target.relative_to(folder)
    return target
