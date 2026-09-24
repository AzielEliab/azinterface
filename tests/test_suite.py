"""Suite desk: honest roster, install-then-boot, and FragGate when there is no local page."""

from __future__ import annotations

import json
import tarfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from azinterface.suite import Suite, bundled_software
from azinterface.suite_page import suite_html
from azinterface.ui import SUITE as LIVE_SUITE
from azinterface.ui import make_server


def test_snapshot_lists_every_software() -> None:
    rows = bundled_software()
    slugs = {row["slug"] for row in rows}
    assert len(rows) == 42
    assert "azinterface" in slugs
    assert "veillock" in slugs
    assert "aziel-corpus" in slugs
    assert "vibelock" in slugs
    veillock = next(row for row in rows if row["slug"] == "veillock")
    assert veillock["local_only"] is True
    corpus = next(row for row in rows if row["slug"] == "aziel-corpus")
    assert corpus["ui_cmd"] is None


def test_suite_page_leads_with_start() -> None:
    html = suite_html(port=8880, vendor="/tmp/azinterface-suite")
    assert 'id="start-suite"' in html
    assert "Start suite" in html
    assert "AZVPN starts with the suite" in html
    assert "Rotate IP" in html
    assert html.find('id="start-suite"') < html.find('id="advanced"')
    assert "/custody" in html.split('id="advanced"', 1)[1]
    assert "prefers-color-scheme" in html
    assert ":focus-visible" in html
    assert "#c9a227" in html
    assert 'name="viewport"' in html
    assert "Aziel Eliab" in html
    assert "One-click install" not in html
    assert "THIS IS NOT" not in html


def test_idle_status_is_honest() -> None:
    suite = Suite(
        refresh=False,
        vendor=Path("/tmp/azinterface-suite-missing"),
        catalog=[
            {
                "name": "AZInterface",
                "slug": "azinterface",
                "ui_cmd": "azinterface ui",
                "ui_port": 8880,
                "fraggate_status": "live",
                "door": "fraggate",
            },
            {
                "name": "VeilLock",
                "slug": "veillock",
                "ui_cmd": "veillock ui",
                "ui_port": 9,
                "local_only": True,
                "download_url": "https://example.invalid/veillock",
                "door": "none",
                "fraggate_status": "local_only",
            },
            {
                "name": "Library",
                "slug": "aziel-corpus",
                "ui_cmd": None,
                "fraggate_status": "live",
                "door": "fraggate",
                "download_url": "https://example.invalid/library",
            },
            {
                "name": "AZVPN",
                "slug": "azvpn",
                "ui_cmd": "azvpn ui",
                "ui_port": 8787,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            },
        ],
    )
    doc = suite.document()
    by = {row["slug"]: row for row in doc["software"]}
    assert by["azinterface"]["posture"] == "ready"
    assert by["veillock"]["posture"] == "local-only"
    assert by["aziel-corpus"]["posture"] == "fraggate-only"
    assert by["azvpn"]["always_on"] is True
    assert by["azvpn"]["posture"] == "repair"
    assert "opt-out" in by["azvpn"]["next"]
    vpn = suite.boot("azvpn", allow_install=False)
    assert vpn["outcome"] in {None, "repair"}
    assert vpn["url"] == "/suite/azvpn"
    assert vpn["mode"] == "vpn"
    page = suite.azvpn_html()
    assert "Rotate IP" in page
    assert ">Disable<" not in page
    assert ">Stop<" not in page
    assert ">Off<" not in page
    assert suite.boot("aziel-corpus")["mode"] == "fraggate"
    assert suite.boot("aziel-corpus")["url"] == "/suite/fraggate/aziel-corpus"
    opened = suite.boot("azinterface")
    assert opened["outcome"] == "booted"
    assert opened["url"] == "/custody"
    assert opened["mode"] == "suite"
    # A missing local-only command is not reported as open.
    skipped = suite.boot("veillock", allow_install=False)
    assert skipped["outcome"] in {None, "failed"}
    assert skipped.get("url") in {None, ""}


def test_install_then_boot_and_failed_download(tmp_path: Path) -> None:
    script = """#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"demo-ready"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        return
httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
print("Open http://127.0.0.1:%s/" % httpd.server_address[1], flush=True)
httpd.serve_forever()
"""
    archive = tmp_path / "demo.tar.gz"
    payload = script.encode()
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("demo/bin/demoui")
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, __import__("io").BytesIO(payload))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/download":
                data = archive.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/page":
                body = b"<html>not a package</html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, fmt: str, *args: object) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    suite = Suite(
        refresh=False,
        vendor=tmp_path / "vendor",
        catalog=[
            {
                "name": "Demo",
                "slug": "demo",
                "ui_cmd": "demoui ui",
                "download_url": f"http://127.0.0.1:{port}/download",
                "door": "none",
                "fraggate_status": "none",
            },
            {
                "name": "Broken",
                "slug": "broken",
                "ui_cmd": "broken ui",
                "download_url": f"http://127.0.0.1:{port}/page",
                "fraggate_status": "live",
                "door": "fraggate",
            },
        ],
    )
    try:
        opened = suite.boot("demo")
        assert opened["outcome"] == "install-then-boot", opened
        assert opened["mode"] == "local"
        assert opened["url"].startswith("http://127.0.0.1:")
        body = urlopen(opened["url"], timeout=3).read()
        assert body == b"demo-ready"
        failed = suite.boot("broken")
        assert failed["outcome"] == "fraggate"
        assert "Install failed" in failed["reason"]
        assert failed["url"] == "/suite/fraggate/broken"
        assert "127.0.0.1:" not in str(failed["url"])
    finally:
        suite.stop()
        httpd.shutdown()
        httpd.server_close()


def test_http_suite_does_not_boot_on_get(tmp_path: Path, monkeypatch) -> None:
    suite = Suite(
        refresh=False,
        vendor=tmp_path / "vendor",
        catalog=[
            {
                "name": "Library",
                "slug": "aziel-corpus",
                "ui_cmd": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    monkeypatch.setattr("azinterface.ui.SUITE", suite)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        html = urlopen(Request(f"http://127.0.0.1:{port}/", headers={"Accept": "text/html"})).read().decode()
        assert "Start suite" in html
        listed = json.loads(urlopen(f"http://127.0.0.1:{port}/suite/software").read().decode())
        assert listed["count"] == 1
        assert listed["software"][0]["posture"] == "fraggate-only"
        assert listed["software"][0]["outcome"] is None
        assert not (tmp_path / "vendor").exists() or not any((tmp_path / "vendor").rglob("*"))
    finally:
        httpd.shutdown()
        httpd.server_close()
        suite.stop()
    assert LIVE_SUITE is not suite


def test_azvpn_starts_before_other_softwares(monkeypatch) -> None:
    suite = Suite(
        refresh=False,
        vendor=Path("/tmp/azinterface-suite-missing"),
        catalog=[
            {"name": "Map", "slug": "4dmap", "ui_cmd": "4dmap ui", "fraggate_status": "live", "door": "fraggate"},
            {"name": "AZVPN", "slug": "azvpn", "ui_cmd": "azvpn ui", "ui_port": 8787, "download_url": None, "fraggate_status": "live", "door": "fraggate"},
        ],
    )
    order: list[tuple[str, bool]] = []

    def fake(slug: str, allow_install: bool = True) -> dict[str, str]:
        order.append((slug, allow_install))
        return {"ok": True}

    monkeypatch.setattr(suite, "boot", fake)
    suite._start_all()
    assert order[0] == ("azvpn", True)
    assert all(item[0] != "azvpn" or item is order[0] for item in order)


def test_azvpn_node_install_then_rotate(tmp_path: Path) -> None:
    script = """const http = require("http");
const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/v1/open") {
    const body = JSON.stringify({ ok: true, op: "open", mode: "onion" });
    res.writeHead(200, { "content-type": "application/json" });
    res.end(body);
    return;
  }
  const page = "<!doctype html><title>AZVPN</title><p>AZVPN lab</p>";
  res.writeHead(200, { "content-type": "text/html" });
  res.end(page);
});
server.listen(0, "127.0.0.1", () => {
  console.log("AZVPN listening http://127.0.0.1:" + server.address().port + "/");
});
"""
    archive = tmp_path / "azvpn.tar.gz"
    payload = script.encode()
    pkg = b'{"name":"azvpn","bin":{"azvpn":"./cli.js"}}\n'
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("pkg/cli.js")
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, __import__("io").BytesIO(payload))
        meta = tarfile.TarInfo("pkg/package.json")
        meta.size = len(pkg)
        tar.addfile(meta, __import__("io").BytesIO(pkg))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            data = archive.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/gzip")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt: str, *args: object) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    suite = Suite(
        refresh=False,
        vendor=tmp_path / "vendor",
        catalog=[
            {
                "name": "AZVPN",
                "slug": "azvpn",
                "ui_cmd": "azvpn ui",
                "ui_port": 1,
                "download_url": f"http://127.0.0.1:{port}/download",
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    try:
        opened = suite.boot("azvpn")
        assert opened["outcome"] == "install-then-boot", opened
        assert opened["url"] == "/suite/azvpn"
        page = suite.azvpn_html()
        assert "Status: ON" in page
        assert "Rotate IP" in page
        rotated = suite.rotate_azvpn()
        assert rotated["ok"] is True
        assert rotated["public_address"] == "unchanged"
        assert "SLOT" in rotated["note"]
    finally:
        suite.stop()
        httpd.shutdown()
        httpd.server_close()
