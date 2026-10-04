"""The suite door places a map card, submits SMTP, fetches a URL, and boots a session."""

from __future__ import annotations

import json
import socket
import threading
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from azinterface.engine import Engine
from azinterface.pipeline import pipeline_arch
from azinterface.receipts import Ledger
from azinterface.suite import Suite
from azinterface.ui import make_server

CLOCK = "2026-10-04T18:04:00Z"
STORY = "The harbor master posted a written notice about the morning tide."


def test_catalog_sentences_match_the_doors_and_omit_the_live_label() -> None:
    cited = {
        row["slug"]: row["status"]
        for domain in pipeline_arch()["domain_map"]
        for row in domain["softwares"]
    }
    assert pipeline_arch()["software_count"] == 33
    assert len(cited) == 33
    assert "aznews" not in cited
    expected = {
        "4dmap": "This row is in the catalog. The map places a card on the clock and reads that card back.",
        "azmail": "This row is in the catalog. Mail send submits the message over SMTP.",
        "aznet": "This row is in the catalog. The internet door fetches a URL and returns the response body.",
        "azos": "This row is in the catalog. The overlay kernel boots a session and runs a command inside it.",
    }
    for slug, status in expected.items():
        assert cited[slug] == status
        assert "live" not in status.lower()
    assert Engine(Ledger()).site_state == "OFF"


def test_clock_card_reads_back_and_a_news_pin_does_not_place_one(tmp_path: Path) -> None:
    suite = _suite(tmp_path)
    empty = suite.map_state()
    assert empty["map_running"] is False
    assert empty["cards"] == []
    refused = suite.place_map_card({"t": "", "note": "missing"})
    assert refused["ok"] is False
    assert refused["map_running"] is False
    placed = suite.place_map_card({"t": CLOCK, "note": "morning tide"})
    assert placed["ok"] is True
    assert placed["map_running"] is True
    card = placed["card"]
    assert card["axis"] == "T"
    assert card["t"] == CLOCK
    assert card["prev"] == "0" * 64
    assert card["h"] == _expected_hash(card)
    stored = json.loads((tmp_path / "vendor" / "lattice.json").read_text(encoding="utf-8"))
    assert stored["cards"][0]["h"] == card["h"]
    again = suite.map_state()
    assert again["cards"][0]["note"] == "morning tide"
    assert again["axes"]["T"] == [card["id"]]
    second = suite.place_map_card({"t": "2026-10-04T19:00:00Z", "note": "next hour"})
    assert second["card"]["prev"] == card["h"]
    saved = suite.add_news({"headline": "Harbor notice", "body": STORY})
    pinned = suite.pin_news({"id": saved["item"]["id"]})
    assert pinned["join_live"] is True
    assert suite.map_state()["count"] == 2
    assert suite.news_view()["running_map"] is False


def test_mail_send_is_watched_by_an_smtp_server(tmp_path: Path) -> None:
    box: list[bytes] = []
    port = _smtp(box)
    suite = _suite(tmp_path)
    missing = suite.send_mail({"from": "a@example.com", "to": "b@example.com", "subject": "Tide", "body": STORY})
    assert missing["sent"] is False
    sent = suite.send_mail(
        {
            "from": "harbor@example.com",
            "to": "desk@example.com",
            "subject": "Morning tide",
            "body": STORY,
            "host": "127.0.0.1",
            "port": port,
        }
    )
    assert sent["ok"] is True
    assert sent["sent"] is True
    assert sent["accepted"] == ["desk@example.com"]
    assert box, "the SMTP server did not see a message"
    raw = box[0].decode("utf-8", "replace")
    assert "harbor@example.com" in raw
    assert "desk@example.com" in raw
    assert STORY in raw


def test_internet_door_returns_the_body_the_server_sent(tmp_path: Path) -> None:
    seen: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            seen.append(self.path)
            body = b"tide-marker"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        suite = _suite(tmp_path)
        refused = suite.fetch_internet({"url": "file:///etc/passwd"})
        assert refused["fetched"] is False
        fetched = suite.fetch_internet({"url": f"http://127.0.0.1:{port}/marker"})
        assert fetched["fetched"] is True
        assert fetched["http_status"] == 200
        assert fetched["body"] == "tide-marker"
        assert seen == ["/marker"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_internet_door_fetches_a_public_page() -> None:
    from azinterface.net_fetch import fetch_url

    fetched = fetch_url({"url": "https://example.com/"})
    assert fetched["fetched"] is True
    assert fetched["http_status"] == 200
    assert "Example Domain" in fetched["body"]


def test_overlay_kernel_boots_and_reads_a_file_back(tmp_path: Path) -> None:
    suite = _suite(tmp_path)
    cold = suite.kernel_command({"session": "os-missing", "op": "cat", "path": "marker.txt"})
    assert cold["ran"] is False
    booted = suite.boot_kernel()
    assert booted["booted"] is True
    assert booted["host_kernel"] is False
    session = booted["session"]
    folder = tmp_path / "vendor" / "azos-sessions" / session
    receipt = json.loads((folder / "BOOT").read_text(encoding="utf-8"))
    assert receipt["session"] == session
    assert receipt["host_kernel"] is False
    wrote = suite.kernel_command({"session": session, "op": "write", "path": "marker.txt", "text": "kernel-marker"})
    assert wrote["ran"] is True
    assert wrote["output"] == "kernel-marker"
    assert (folder / "marker.txt").read_text(encoding="utf-8") == "kernel-marker"
    read = suite.kernel_command({"session": session, "op": "cat", "path": "marker.txt"})
    assert read["output"] == "kernel-marker"
    escaped = suite.kernel_command({"session": session, "op": "write", "path": "../outside.txt", "text": "no"})
    assert escaped["ran"] is False
    assert not (tmp_path / "vendor" / "azos-sessions" / "outside.txt").exists()
    assert Engine(Ledger()).health({})["site_state"] == "OFF"


def test_http_doors_stay_json_and_leave_the_site_off(tmp_path: Path, monkeypatch) -> None:
    suite = _suite(tmp_path)
    monkeypatch.setattr("azinterface.ui.SUITE", suite)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    box: list[bytes] = []
    smtp_port = _smtp(box)
    try:
        before = json.loads(urlopen(base + "/v1/health").read().decode())
        assert before["site_state"] == "OFF"
        page = urlopen(Request(base + "/suite/4dmap", headers={"Accept": "text/html"})).read().decode()
        assert "Place on the clock" in page
        assert not page.lstrip().startswith("{")
        placed = _post(base + "/suite/4dmap/map/pin", {"t": CLOCK, "note": "from http"})
        assert placed["map_running"] is True
        assert placed["card"]["h"] == _expected_hash(placed["card"])
        mail_page = urlopen(Request(base + "/suite/azmail", headers={"Accept": "text/html"})).read().decode()
        assert "Mail send submits the message over SMTP." in mail_page
        sent = _post(
            base + "/suite/azmail/send",
            {
                "from": "harbor@example.com",
                "to": "desk@example.com",
                "subject": "Morning tide",
                "body": STORY,
                "host": "127.0.0.1",
                "port": smtp_port,
            },
        )
        assert sent["sent"] is True
        assert STORY in box[-1].decode("utf-8", "replace")
        net_json = json.loads(urlopen(Request(base + "/suite/aznet", headers={"Accept": "application/json"})).read().decode())
        assert net_json["status"].startswith("The internet door fetches")
        booted = _post(base + "/suite/azos/boot", {})
        assert booted["booted"] is True
        assert booted["host_kernel"] is False
        wrote = _post(
            base + "/suite/azos/command",
            {"session": booted["session"], "op": "write", "path": "marker.txt", "text": "kernel-marker"},
        )
        assert wrote["output"] == "kernel-marker"
        after = json.loads(urlopen(base + "/v1/health").read().decode())
        assert after["site_state"] == "OFF"
        cycle = json.loads(urlopen(base + "/v1/page_cycle_status").read().decode())
        assert cycle["pipeline"]["software_count"] == 33
    finally:
        httpd.shutdown()
        httpd.server_close()
        suite.stop()


def _suite(tmp_path: Path) -> Suite:
    return Suite(refresh=False, vendor=tmp_path / "vendor", catalog=[])


def _expected_hash(card: dict) -> str:
    payload = {
        "delta": card.get("delta"),
        "gamma": card.get("gamma"),
        "id": card.get("id"),
        "note": card.get("note") or "",
        "pi": card.get("pi"),
        "prev": card.get("prev"),
        "src": card.get("src"),
        "t": card.get("t"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(raw).hexdigest()


def _post(url: str, body: dict) -> dict:
    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    return json.loads(urlopen(req).read().decode())


def _smtp(box: list[bytes]) -> int:
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = int(server.getsockname()[1])

    def run() -> None:
        conn, _addr = server.accept()
        try:
            conn.sendall(b"220 azinterface.local ESMTP\r\n")
            data_mode = False
            lines: list[bytes] = []
            while True:
                line = b""
                while not line.endswith(b"\n"):
                    chunk = conn.recv(1)
                    if not chunk:
                        return
                    line += chunk
                if data_mode:
                    if line == b".\r\n":
                        data_mode = False
                        box.append(b"".join(lines))
                        conn.sendall(b"250 ok\r\n")
                    else:
                        lines.append(line)
                    continue
                text = line.decode("utf-8", "replace").strip().upper()
                if text.startswith("EHLO") or text.startswith("HELO"):
                    conn.sendall(b"250-azinterface.local\r\n250 HELP\r\n")
                elif text.startswith("DATA"):
                    data_mode = True
                    lines = []
                    conn.sendall(b"354 end\r\n")
                elif text.startswith("QUIT"):
                    conn.sendall(b"221 bye\r\n")
                    return
                else:
                    conn.sendall(b"250 ok\r\n")
        finally:
            conn.close()
            server.close()

    threading.Thread(target=run, daemon=True).start()
    return port
