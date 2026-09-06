"""Local AZInterface — loopback only. Same custody cycle as the Worker."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .engine import Engine
from .meta import HOST, IDENTITY, LIMITATION, LOOPBACK, PORT, SIGIL, SPEC, VERSION
from .receipts import Ledger

_ENGINE = Engine(Ledger())


def local_html() -> str:
    from .web_page import home_html

    return home_html(views=0, downloads=0, github={}, local=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "AZ-Interface/0.1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _json(self, body: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, body: str) -> None:
        raw = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/":
            self._html(local_html())
            return
        if path == "/v1/health":
            self._json(_ENGINE.health({}))
            return
        if path in ("/v1/genesis_status", "/v1/site_state_get", "/v1/page_cycle_status", "/v1/witness_list"):
            op = path.rsplit("/", 1)[-1]
            self._json(_ENGINE.dispatch(op, {}))
            return
        if path == "/v1/skill":
            self._json(_ENGINE.skill({}))
            return
        self._json({"error": "not found", "limitation": LIMITATION}, 404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            payload = {}
        if not path.startswith("/v1/"):
            self._json({"error": "not found"}, 404)
            return
        op = path[len("/v1/") :]
        if "/" in op:
            self._json({"error": "not a local op", "code": "NOT_LOCAL_OP"}, 404)
            return
        out = _ENGINE.dispatch(op, payload if isinstance(payload, dict) else {})
        status = 200
        if out.get("code") == "FG-HALLUC-TOOL":
            status = 404
        self._json(out, status)


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    if host not in {LOOPBACK, "localhost"}:
        raise ValueError("AZ Interface binds loopback only (127.0.0.1)")
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = LOOPBACK, port: int = PORT) -> int:
    httpd = make_server(host, port)
    bound = httpd.server_address
    print(
        f"AZInterface {VERSION} ({SPEC}) http://{bound[0]}:{bound[1]}  "
        f"loopback only. Author: {IDENTITY}."
    )
    print(LIMITATION)
    print("Counted Worker:", HOST)
    print("Sigil:", SIGIL)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("halted. Custody receipts remain local.")
    finally:
        httpd.server_close()
    return 0
