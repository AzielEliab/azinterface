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
from .suite import SLUG_RE, Suite
from .suite_page import suite_html

_ENGINE = Engine(Ledger())
SUITE = Suite()


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


def desk_html(port: int | None = None) -> str:
    bound = PORT if port is None else port
    return suite_html(port=bound, vendor=str(SUITE.vendor))


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
                doc = home_document(_ENGINE, str(host), int(bound_port))
                cards = SUITE.cards()
                doc["suite"] = True
                doc["software_count"] = len(cards)
                doc["software_source"] = SUITE.source
                self._json(doc)
                return
            self._html(desk_html(port=int(bound_port)))
            return
        if path == "/custody":
            host, bound_port = self.server.server_address[:2]
            self._html(local_html(port=int(bound_port)))
            return
        if path == "/suite/software":
            self._json(SUITE.document())
            return
        if path == "/suite/azvpn":
            self._html(SUITE.azvpn_html())
            return
        if path == "/suite/trajectorylock":
            self._html(SUITE.trajectory_html())
            return
        if path == "/suite/shadowlock":
            self._html(SUITE.shadow_html())
            return
        if path == "/suite/4dmap":
            self._html(SUITE.map_html())
            return
        if path == "/suite/shadowlock/links":
            self._json(SUITE.shadow_links())
            return
        if path.startswith("/suite/fraggate/"):
            slug = path.rsplit("/", 1)[-1]
            if not SLUG_RE.fullmatch(slug):
                self._json({"ok": False, "error": "Unknown Software."}, 404)
                return
            page = SUITE.fraggate_html(slug)
            if page is None:
                self._html(
                    "<!DOCTYPE html><html lang=\"en\"><body><p>This Software is not on FragGate. "
                    "Open its local page from the suite when it is installed.</p></body></html>"
                )
                return
            self._html(page)
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
        if path == "/suite/start":
            self._json(SUITE.start())
            return
        if path == "/suite/azvpn/rotate":
            self._json(SUITE.rotate_azvpn())
            return
        if path == "/suite/trajectorylock/review":
            if not isinstance(payload, dict):
                self._json({"ok": False, "error": "The review body must be a JSON object."}, 400)
                return
            self._json(SUITE.review_trajectory(payload))
            return
        if path == "/suite/shadowlock/link":
            if not isinstance(payload, dict):
                self._json({"ok": False, "error": "The link body must be a JSON object."}, 400)
                return
            self._json(SUITE.shadow_link(payload))
            return
        if path == "/suite/shadowlock/unlink":
            if not isinstance(payload, dict):
                self._json({"ok": False, "error": "The link body must be a JSON object."}, 400)
                return
            self._json(SUITE.shadow_unlink(payload))
            return
        if path == "/suite/boot":
            slug = str(payload.get("slug") or "") if isinstance(payload, dict) else ""
            self._json(SUITE.boot(slug))
            return
        if path == "/suite/fraggate":
            if not isinstance(payload, dict):
                self._json({"ok": False, "error": "The session body must be a JSON object."}, 400)
                return
            body = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            self._json(SUITE.fraggate_call(str(payload.get("slug") or ""), str(payload.get("op") or ""), body))
            return
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
        SUITE.stop()
        httpd.server_close()
    return 0
