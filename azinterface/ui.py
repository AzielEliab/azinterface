"""Local AZInterface — loopback only. Same custody cycle as the Worker."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .cite import cite_document
from .engine import Engine
from .local_page import operator_html
from .meta import IDENTITY, LIMITATION, LOOPBACK, NAME, PORT, SPEC, VERSION
from .receipts import Ledger

_ENGINE = Engine(Ledger())


def wants_json(accept: str | None) -> bool:
    """True when the client asked for JSON ahead of HTML."""
    if not accept:
        return False
    for part in accept.split(","):
        media = part.split(";", 1)[0].strip().lower()
        if media == "application/json":
            return True
        if media in {"text/html", "application/xhtml+xml"}:
            return False
    return False


def home_document(engine: Engine, host: str, port: int) -> dict[str, Any]:
    """Short status for Accept: application/json on GET /. Does not append a receipt."""
    snap = engine.page_cycle_snapshot()
    view = snap.get("page_cycle") if isinstance(snap.get("page_cycle"), dict) else {}
    return {
        "ok": True,
        "product": NAME,
        "version": VERSION,
        "spec": SPEC,
        "author": IDENTITY,
        "site_state": snap.get("site_state"),
        "living_presence": snap.get("living_presence"),
        "integrity_ok": snap.get("integrity_ok"),
        "genesis_keyed": snap.get("genesis_keyed"),
        "next": view.get("next"),
        "loopback": host,
        "port": port,
    }


def local_html(port: int | None = None) -> str:
    return operator_html(port=PORT if port is None else port)


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
            host, bound_port = self.server.server_address[:2]
            if wants_json(self.headers.get("Accept")):
                self._json(home_document(_ENGINE, str(host), int(bound_port)))
                return
            self._html(local_html(port=int(bound_port)))
            return
        if path == "/cite.json":
            self._json(cite_document())
            return
        if path == "/v1/health":
            self._json(_ENGINE.health({}))
            return
        if path in ("/v1/genesis_status", "/v1/site_state_get", "/v1/page_cycle_status", "/v1/pipeline_arch", "/v1/witness_list", "/v1/pair_status"):
            op = path.rsplit("/", 1)[-1]
            self._json(_ENGINE.dispatch(op, {}))
            return
        if path == "/v1/skill":
            body = _ENGINE.skill({})
            text = str(body.get("markdown") or LIMITATION)
            raw = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Cache-Control", "private, no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
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


def open_line(host: str, port: int) -> str:
    return f"Open http://{host}:{port}/"


def serve(host: str = LOOPBACK, port: int = PORT) -> int:
    httpd = make_server(host, port)
    bound = httpd.server_address
    print(open_line(str(bound[0]), int(bound[1])))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("halted. Custody receipts remain local.")
    finally:
        httpd.server_close()
    return 0
