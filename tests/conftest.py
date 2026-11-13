"""Default pytest run stays on this machine.

AZINTERFACE_LIVE_NETWORK=1 turns the fence off and leaves the public catalog
URL in place. The default does not resolve or connect off-box.
"""

from __future__ import annotations

import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

_ATTEMPTS: list[tuple[str, str]] = []
_LIVE = os.environ.get("AZINTERFACE_LIVE_NETWORK") == "1"
_LOOPBACK = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "::"}


def _host_text(host: object) -> str:
    if isinstance(host, bytes):
        return host.decode("utf-8", "replace")
    return "" if host is None else str(host)


def _loopback(host: object) -> bool:
    text = _host_text(host).strip("[]")
    if text in _LOOPBACK:
        return True
    try:
        import ipaddress

        return ipaddress.ip_address(text).is_loopback
    except ValueError:
        return False


class _Catalog(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0].rstrip("/") == "/v1/software":
            body = b'{"software":[]}'
            kind = "application/json"
        else:
            body = b"Example Domain"
            kind = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return


@pytest.fixture(scope="session", autouse=True)
def network_fence():
    """Fail the run if any test resolves or connects past loopback."""
    if _LIVE:
        yield []
        return
    _ATTEMPTS.clear()
    original_info = socket.getaddrinfo
    original_create = socket.create_connection
    original_connect = socket.socket.connect

    def getaddrinfo(host, port, *args, **kwargs):  # noqa: ANN001
        if not _loopback(host):
            _ATTEMPTS.append(("getaddrinfo", _host_text(host)))
            raise OSError(f"external network blocked: {_host_text(host)}")
        return original_info(host, port, *args, **kwargs)

    def create_connection(address, *args, **kwargs):  # noqa: ANN001
        host = address[0] if isinstance(address, tuple) and address else None
        if host is not None and not _loopback(host):
            _ATTEMPTS.append(("connect", _host_text(host)))
            raise OSError(f"external network blocked: {_host_text(host)}")
        return original_create(address, *args, **kwargs)

    def connect(self, address):  # noqa: ANN001
        host = address[0] if isinstance(address, tuple) and address else None
        if host is not None and not _loopback(host):
            _ATTEMPTS.append(("connect", _host_text(host)))
            raise OSError(f"external network blocked: {_host_text(host)}")
        return original_connect(self, address)

    socket.getaddrinfo = getaddrinfo
    socket.create_connection = create_connection
    socket.socket.connect = connect
    try:
        yield _ATTEMPTS
    finally:
        socket.getaddrinfo = original_info
        socket.create_connection = original_create
        socket.socket.connect = original_connect
    assert _ATTEMPTS == [], f"external network attempts: {_ATTEMPTS}"


@pytest.fixture(scope="session", autouse=True)
def local_catalog(network_fence):
    """Stand in for GET /v1/software so the suite does not resolve the public host."""
    del network_fence
    if _LIVE:
        yield None
        return
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Catalog)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    os.environ["AZINTERFACE_TEST_CATALOG"] = base + "/v1/software"
    yield base
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(autouse=True)
def catalog_stays_local(monkeypatch, local_catalog):
    if local_catalog:
        monkeypatch.setattr("azinterface.suite.CATALOG_URL", local_catalog + "/v1/software")
