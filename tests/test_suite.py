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
    assert next(row for row in rows if row["slug"] == "4dmap")["bucket"] == "plain"
    assert next(row for row in rows if row["slug"] == "decisiongate")["bucket"] == "gate"
    assert next(row for row in rows if row["slug"] == "shadowlock")["bucket"] == "lock"


def test_suite_page_leads_with_start() -> None:
    html = suite_html(port=8880, vendor="/tmp/azinterface-suite")
    assert 'id="start-suite"' in html
    assert "Start suite" in html
    assert "AZVPN starts with the suite" in html
    assert "AZCoherence stays in the background" in html
    assert "satellite imagery" in html
    assert "row.background" in html
    assert 'action = "Review"' in html
    assert 'action = "Link"' in html
    assert 'action = "Map"' in html
    assert "ShadowLock links any Software" in html
    assert "4DMap shows those links" in html
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


def test_json_home_names_live_catalog_when_fetch_wins(tmp_path: Path, monkeypatch) -> None:
    live = [
        {
            "name": "Live Only",
            "slug": "liveonly",
            "fraggate_status": "live",
            "door": "fraggate",
        }
    ]
    monkeypatch.setattr("azinterface.suite._fetch_live", lambda: live)
    suite = Suite(refresh=True, vendor=tmp_path / "vendor")
    monkeypatch.setattr("azinterface.ui.SUITE", suite)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        raw = urlopen(
            Request(f"http://127.0.0.1:{port}/", headers={"Accept": "application/json"})
        ).read().decode()
        data = json.loads(raw)
        listed = json.loads(urlopen(f"http://127.0.0.1:{port}/suite/software").read().decode())
        assert data["ok"] is True
        assert data["software_source"] == "GET /v1/software"
        assert data["software_source"] != "bundled snapshot"
        assert data["software_source"] == listed["source"]
        assert data["software_count"] == listed["count"] == 1
        assert listed["software"][0]["slug"] == "liveonly"
    finally:
        httpd.shutdown()
        httpd.server_close()
        suite.stop()


def test_json_home_keeps_bundled_snapshot_when_live_fetch_fails(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("azinterface.suite._fetch_live", lambda: None)
    suite = Suite(refresh=True, vendor=tmp_path / "vendor")
    monkeypatch.setattr("azinterface.ui.SUITE", suite)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        raw = urlopen(
            Request(f"http://127.0.0.1:{port}/", headers={"Accept": "application/json"})
        ).read().decode()
        data = json.loads(raw)
        listed = json.loads(urlopen(f"http://127.0.0.1:{port}/suite/software").read().decode())
        assert data["software_source"] == "bundled snapshot"
        assert data["software_source"] == listed["source"]
        assert data["software_count"] == listed["count"] == len(bundled_software())
    finally:
        httpd.shutdown()
        httpd.server_close()
        suite.stop()


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


def test_coherence_tile_is_status_only(monkeypatch) -> None:
    suite = Suite(
        refresh=False,
        vendor=Path("/tmp/azinterface-suite-missing"),
        catalog=[
            {
                "name": "AZCoherence",
                "slug": "azcoherence",
                "ui_cmd": "azcoherence ui",
                "ui_port": 9,
                "download_url": "https://example.invalid/azcoherence",
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    quiet = suite.boot("azcoherence", allow_install=False)
    assert quiet["background"] is True
    assert quiet["posture"] == "quiet"
    assert quiet["label"] == "Quiet"
    assert quiet["url"] is None
    assert quiet["mode"] == "background"
    assert "review page" in quiet["next"]
    monkeypatch.setattr(suite, "_coherence_health", lambda card: True)

    def fake_boot(slug: str, allow_install: bool = True) -> dict[str, object]:
        card = suite._card(slug)
        assert card is not None
        return suite._save(
            card,
            posture="ready",
            mode="local",
            url="http://127.0.0.1:8871/",
            outcome="booted",
            reason="Open at http://127.0.0.1:8871/.",
            nxt="Use the page.",
        )

    monkeypatch.setattr(suite, "_boot_impl", fake_boot)
    running = suite.boot("azcoherence")
    assert running["posture"] == "running"
    assert running["label"] == "Running"
    assert running["url"] is None
    assert running["mode"] == "background"
    assert "background" in running["reason"]


def test_trajectory_review_pane_and_real_jpeg(tmp_path: Path) -> None:
    from azinterface.trajectory_review import review_event, review_html

    suite = Suite(
        refresh=False,
        vendor=tmp_path / "vendor",
        catalog=[
            {
                "name": "TrajectoryLock",
                "slug": "trajectorylock",
                "ui_cmd": "trajectorylock ui",
                "ui_port": 9,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    opened = suite.boot("trajectorylock", allow_install=False)
    assert opened["review"] is True
    assert opened["posture"] == "review"
    assert opened["url"] == "/suite/trajectorylock"
    assert opened["mode"] == "review"
    assert opened["outcome"] != "booted"
    assert "NASA GIBS" in opened["reason"]
    assert "invent" in opened["reason"]
    page = suite.trajectory_html()
    assert page == review_html()
    assert 'id="run-check"' in page
    assert "Run check" in page
    assert "data:image/" not in page.split("<script>", 1)[0]

    jpeg = b"\xff\xd8\xff" + b"frame-bytes"
    calls: list[str] = []

    def fetch(url: str) -> tuple[int, bytes]:
        calls.append(url)
        if "nominatim" in url:
            body = b'[{"lat":"34.05","lon":"-118.25","display_name":"Los Angeles"}]'
            return 200, body
        if "2020-06-17" in url:
            return 200, jpeg
        return 404, b"no"

    found = review_event(place="Los Angeles", when="2020-06-15T18:00:00Z", fetch=fetch)
    assert found["ok"] is True
    assert found["image_jpeg_b64"]
    assert found["source"] == "NASA GIBS"
    assert found["frame_time"] == "2020-06-17"
    assert found["time_delta_days"] == 2
    assert found["source_url"]
    assert "Gaps:" in found["trace"]
    assert any("2020-06-17" in gap for gap in found["gaps"])
    assert any("nominatim" in url for url in calls)

    def html_fetch(url: str) -> tuple[int, bytes]:
        return 200, b"<html>not a picture</html>"

    missing = review_event(lat=34.05, lon=-118.25, when="2020-06-15", fetch=html_fetch)
    assert missing["image_jpeg_b64"] is None
    assert missing["source_url"] is None
    assert missing["ok"] is False
    assert any("no JPEG" in gap for gap in missing["gaps"])
    assert "Imagery evidence: none" in missing["trace"]


def test_shadowlock_links_and_map_read_the_same_record(tmp_path: Path) -> None:
    catalog = [
        {"name": "4DMap", "slug": "4dmap", "bucket": "plain", "ui_cmd": "4dmap ui", "fraggate_status": "live", "door": "fraggate"},
        {"name": "DecisionGATE", "slug": "decisiongate", "bucket": "gate", "ui_cmd": "decisiongate ui", "fraggate_status": "live", "door": "fraggate"},
        {"name": "ShadowLock", "slug": "shadowlock", "bucket": "lock", "ui_cmd": "shadowlock ui", "download_url": None, "fraggate_status": "live", "door": "fraggate"},
        {"name": "Odd", "slug": "oddware", "ui_cmd": "oddware ui", "fraggate_status": "live", "door": "fraggate"},
    ]
    suite = Suite(refresh=False, vendor=tmp_path / "vendor", catalog=catalog)
    idle = {row["slug"]: row for row in suite.document()["software"]}
    assert idle["shadowlock"]["link"] is True
    assert idle["shadowlock"]["posture"] == "link"
    assert idle["shadowlock"]["url"] == "/suite/shadowlock"
    assert idle["4dmap"]["map"] is True
    assert idle["4dmap"]["url"] == "/suite/4dmap"
    assert idle["4dmap"]["bucket"] == "plain"
    assert idle["oddware"]["bucket"] is None
    empty = suite.shadow_links()
    assert empty["empty"] is True
    assert empty["links"] == []
    opened = suite.boot("shadowlock", allow_install=False)
    assert opened["url"] == "/suite/shadowlock"
    assert opened["mode"] == "link"
    assert opened["outcome"] != "booted"
    mapped = suite.boot("4dmap", allow_install=False)
    assert mapped["url"] == "/suite/4dmap"
    assert mapped["mode"] == "map"
    desk = suite.shadow_html()
    assert "Nothing is linked yet" in desk
    assert "draggable = true" in desk
    assert 'textContent = "Link"' in desk
    page = suite.map_html()
    assert "Softwares · Shadow" in page
    assert "does not invent marks" in page
    refused = suite.shadow_link({"slug": "missing", "label": "North", "input": "in/a"})
    assert refused["ok"] is False
    assert suite.shadow_links()["count"] == 0
    saved = suite.shadow_link({"slug": "shadowlock", "label": "North desk", "input": "intake/batch", "bucket": "plain"})
    assert saved["ok"] is True
    link = saved["link"]
    assert link["bucket"] == "lock"
    assert link["label"] == "North desk"
    assert link["input"] == "intake/batch"
    assert link["input_note"] is None
    named = suite.shadow_link({"slug": "decisiongate", "input": "memo.pdf", "input_from": "file-name"})
    assert named["link"]["bucket"] == "gate"
    assert named["link"]["input_note"] == "File name only. Contents were not read."
    assert named["link"]["label"] is None
    both = suite.shadow_links()
    assert both["count"] == 2
    assert both["empty"] is False
    assert [row["slug"] for row in both["links"]] == ["shadowlock", "decisiongate"]
    gone = suite.shadow_unlink({"id": link["id"]})
    assert gone["ok"] is True
    assert gone["count"] == 1
    missing = suite.shadow_unlink({"id": "sl-nope"})
    assert missing["ok"] is False
    assert missing["count"] == 1


def _hold_page(title: str) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            body = f"<title>{title}</title><p>held</p>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: object) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def _write_exe(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    path.chmod(0o755)


def test_busy_port_moves_and_foreign_page_is_not_attached(tmp_path: Path) -> None:
    held = _hold_page("Other App")
    busy = int(held.server_address[1])
    try:
        vendor = tmp_path / "suite"
        _write_exe(
            vendor / "demoui" / "bin" / "demoui",
            f"""#!/usr/bin/env python3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
argv = sys.argv[1:]
if argv[:1] == ["--help"] or "--help" in argv:
    print("usage: demoui {{ui}}")
    print("  ui                  Serve the local UI on 127.0.0.1.")
    print("  --host HOST         Loopback host (default 127.0.0.1).")
    print("  --port PORT         Port (default {busy}).")
    raise SystemExit(0)
port = {busy}
if "--port" in argv:
    port = int(argv[argv.index("--port") + 1])
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<title>Demoui</title><p>open</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        return
print("http://127.0.0.1:%s/" % port, flush=True)
ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
""",
        )
        suite = Suite(
            refresh=False,
            vendor=vendor,
            catalog=[
                {
                    "name": "Demoui",
                    "slug": "demoui",
                    "ui_cmd": "demoui ui",
                    "ui_port": busy,
                    "download_url": None,
                    "fraggate_status": "live",
                    "door": "fraggate",
                }
            ],
        )
        opened = suite.boot("demoui", allow_install=False)
        assert opened["outcome"] == "booted"
        assert opened["posture"] == "ready"
        assert opened["url"] != f"http://127.0.0.1:{busy}/"
        assert "already in use" in opened["reason"]
        with urlopen(opened["url"], timeout=2) as resp:
            page = resp.read().decode()
        assert "<title>Demoui</title>" in page
        suite.stop()
    finally:
        held.shutdown()
        held.server_close()


def test_attach_only_when_the_page_names_the_product(tmp_path: Path) -> None:
    held = _hold_page("Demoui desk")
    busy = int(held.server_address[1])
    try:
        suite = Suite(
            refresh=False,
            vendor=tmp_path / "suite",
            catalog=[
                {
                    "name": "Demoui",
                    "slug": "demoui",
                    "ui_cmd": "demoui ui",
                    "ui_port": busy,
                    "download_url": None,
                    "fraggate_status": "live",
                    "door": "fraggate",
                }
            ],
        )
        opened = suite.boot("demoui", allow_install=False)
        assert opened["outcome"] == "booted"
        assert opened["url"] == f"http://127.0.0.1:{busy}/"
        assert "names Demoui" in opened["reason"]
    finally:
        held.shutdown()
        held.server_close()


def test_missing_ui_command_opens_fraggate(tmp_path: Path) -> None:
    vendor = tmp_path / "suite"
    _write_exe(
        vendor / "codelock" / "bin" / "codelock",
        """#!/usr/bin/env python3
import sys
argv = sys.argv[1:]
if argv[:1] == ["--help"] or "--help" in argv:
    print("usage: codelock {gate-status,render,version}")
    print("  gate-status         Print gate")
    print("  render              Write HTML")
    print("  version             Print the version")
    raise SystemExit(0)
print("invalid choice: 'ui'", file=sys.stderr)
raise SystemExit(2)
""",
    )
    suite = Suite(
        refresh=False,
        vendor=vendor,
        catalog=[
            {
                "name": "CodeLock",
                "slug": "codelock",
                "ui_cmd": "codelock ui",
                "ui_port": None,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    opened = suite.boot("codelock", allow_install=False)
    assert opened["mode"] == "fraggate"
    assert opened["outcome"] == "fraggate"
    assert opened["posture"] == "fraggate-only"
    assert opened["label"] != "Could not open"
    assert "did not invent a local page" in opened["reason"]


def test_localhost_subcommand_is_used_when_ui_is_absent(tmp_path: Path) -> None:
    vendor = tmp_path / "suite"
    _write_exe(
        vendor / "mialock" / "bin" / "mialock",
        """#!/usr/bin/env python3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
argv = sys.argv[1:]
if argv[:1] == ["--help"] or (argv and argv[0] != "map" and "--help" in argv):
    print("usage: mialock {map,people}")
    print("  map                 Open localhost map UI")
    print("  people              List subjects")
    raise SystemExit(0)
if argv[:1] == ["map"] and "--help" in argv:
    print("usage: mialock map [--port PORT]")
    raise SystemExit(0)
if argv[:1] != ["map"]:
    print("invalid choice: 'ui'", file=sys.stderr)
    raise SystemExit(2)
port = 0
if "--port" in argv:
    port = int(argv[argv.index("--port") + 1])
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<title>M.I.A.Lock</title><p>map</p>"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        return
httpd = ThreadingHTTPServer(("127.0.0.1", port), H)
print("http://127.0.0.1:%s/" % httpd.server_address[1], flush=True)
httpd.serve_forever()
""",
    )
    suite = Suite(
        refresh=False,
        vendor=vendor,
        catalog=[
            {
                "name": "M.I.A.Lock",
                "slug": "mialock",
                "ui_cmd": "mialock ui",
                "ui_port": None,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    opened = suite.boot("mialock", allow_install=False)
    try:
        assert opened["outcome"] == "booted"
        assert opened["posture"] == "ready"
        assert "mialock map" in opened["reason"]
        with urlopen(opened["url"], timeout=2) as resp:
            assert b"M.I.A.Lock" in resp.read()
    finally:
        suite.stop()


def test_static_download_is_served_without_a_fake_ui(tmp_path: Path) -> None:
    vendor = tmp_path / "suite"
    page = vendor / "whitestone" / "src" / "whitestone" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<title>Whitestone — advisor</title><p>session</p>", encoding="utf-8")
    suite = Suite(
        refresh=False,
        vendor=vendor,
        catalog=[
            {
                "name": "Whitestone",
                "slug": "whitestone",
                "ui_cmd": "whitestone ui",
                "ui_port": None,
                "download_url": "https://whitestone.example/download",
                "fraggate_status": "none",
                "door": "none",
            }
        ],
    )
    opened = suite.boot("whitestone", allow_install=False)
    try:
        assert opened["outcome"] == "booted"
        assert opened["posture"] == "ready"
        assert "static page" in opened["reason"]
        with urlopen(opened["url"], timeout=2) as resp:
            assert b"Whitestone" in resp.read()
    finally:
        suite.stop()


def test_console_script_name_is_used_when_catalog_name_is_absent(tmp_path: Path) -> None:
    vendor = tmp_path / "suite"
    _write_exe(
        vendor / "zsolver" / ".venv" / "bin" / "zion-solver",
        """#!/usr/bin/env python3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
argv = sys.argv[1:]
if "--help" in argv or argv[:1] == ["--help"]:
    print("usage: zion-solver {ui,version}")
    print("  ui                  Localhost UI")
    raise SystemExit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<title>ZionPattern Solver</title>"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        return
httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
print("http://127.0.0.1:%s/" % httpd.server_address[1], flush=True)
httpd.serve_forever()
""",
    )
    suite = Suite(
        refresh=False,
        vendor=vendor,
        catalog=[
            {
                "name": "ZionPattern Solver",
                "slug": "zsolver",
                "ui_cmd": "zsolver ui",
                "ui_port": None,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    opened = suite.boot("zsolver", allow_install=False)
    try:
        assert opened["outcome"] == "booted"
        assert "zion-solver" in opened["reason"]
        with urlopen(opened["url"], timeout=2) as resp:
            assert b"ZionPattern Solver" in resp.read()
    finally:
        suite.stop()


def test_trajectory_ui_failure_stays_on_the_review_tile(tmp_path: Path) -> None:
    vendor = tmp_path / "suite"
    _write_exe(
        vendor / "trajectorylock" / "bin" / "trajectorylock",
        """#!/usr/bin/env python3
import sys
print("OSError: [Errno 98] Address already in use ('127.0.0.1', 8874)", file=sys.stderr)
raise SystemExit(1)
""",
    )
    suite = Suite(
        refresh=False,
        vendor=vendor,
        catalog=[
            {
                "name": "TrajectoryLock",
                "slug": "trajectorylock",
                "ui_cmd": "trajectorylock ui",
                "ui_port": 8874,
                "download_url": None,
                "fraggate_status": "live",
                "door": "fraggate",
            }
        ],
    )
    opened = suite.boot("trajectorylock", allow_install=False)
    assert opened["posture"] == "review"
    assert opened["label"] == "Review"
    assert opened["outcome"] is None
    assert opened["url"] == "/suite/trajectorylock"
    assert "Could not open" not in opened["label"]
    assert "does not invent pixels" in opened["reason"]
