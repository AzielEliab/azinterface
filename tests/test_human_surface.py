"""Human CLI and loopback page. Engine JSON stays available with --json."""

from __future__ import annotations

import json
import threading
from urllib.request import Request, urlopen

import pytest

from azinterface.cli import main
from azinterface.local_page import operator_html
from azinterface.ui import home_document, make_server, open_line, wants_json
from azinterface.engine import Engine
from azinterface.meta import LOOPBACK, PORT, VERSION
from azinterface.receipts import Ledger


def test_help_text(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    out = capsys.readouterr().out
    assert "azinterface ui" in out
    assert "azinterface doctor" in out
    assert "azinterface integrity" in out
    assert "--json" in out
    assert "Author: Aziel Eliab" in out
    assert "changelog" not in out.lower()
    assert "THIS IS NOT" not in out
    assert "arguments are required" not in out


def test_bare_command_welcomes(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "azinterface ui" in out
    assert "Start suite" in out
    assert "Author: Aziel Eliab" in out
    assert not out.lstrip().startswith("{")
    assert "arguments are required" not in out
    assert "THIS IS NOT" not in out


def test_unknown_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["bogus"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "azinterface --help" in err
    assert "arguments are required" not in err


def test_missing_genesis_seed(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["genesis"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert "seed" in err.lower()
    assert "azinterface genesis <seed>" in err


def test_integrity_human_and_json(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = str(tmp_path / "receipts.jsonl")
    assert main(["--ledger", ledger, "integrity"]) == 0
    human = capsys.readouterr().out
    assert "Integrity passed" in human
    assert "Next: azinterface state-set ON" in human
    assert not human.lstrip().startswith("{")

    assert main(["--json", "--ledger", ledger, "state"]) == 0
    raw = capsys.readouterr().out
    data = json.loads(raw)
    assert data["ok"] is True
    assert data["site_state"] == "integrity"
    assert "display" in data
    assert isinstance(data["display"]["fields"], list)


def test_version_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "version"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["version"] == VERSION
    assert data["author"] == "Aziel Eliab"
    assert data["ok"] is True


def test_doctor_human_skips_essay(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "[ok] version" in out
    assert out.strip().endswith("doctor passed")
    assert "THIS IS NOT" not in out


def test_doctor_json_keeps_machine_fields(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert isinstance(data["checks"], list)
    assert "limitation" in data
    assert data["remote_wipe"] is False


def test_open_line() -> None:
    assert open_line(LOOPBACK, PORT) == "Open http://127.0.0.1:8880/"


def test_wants_json() -> None:
    assert wants_json("application/json")
    assert wants_json("application/json, text/html")
    assert not wants_json("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    assert not wants_json("*/*")
    assert not wants_json(None)


def test_operator_page_is_a_console() -> None:
    html = operator_html()
    assert "Integrity check" in html
    assert 'id="integrity-btn"' in html
    assert 'id="advanced"' in html
    tag = html[html.find("<details class=\"advanced\"") : html.find(">", html.find("<details class=\"advanced\""))]
    assert " open" not in tag
    assert html.find('id="integrity-btn"') < html.find('id="advanced"')
    assert html.find('id="advanced"') < html.find('id="genesis-btn"')
    assert "prefers-color-scheme" in html
    assert ":focus-visible" in html
    assert "#c9a227" in html
    assert 'name="viewport"' in html
    assert "One-click install" not in html
    assert "Download " not in html
    assert "Live Nodes" not in html
    assert "THIS IS NOT" not in html
    assert "Aziel Eliab" in html
    for token in (
        "genesis-btn",
        "hold-btn",
        "witness-btn",
        "withdraw-btn",
        "pair-offer-btn",
        "pair-accept-btn",
        "pair-seal-btn",
        "pair-cut-btn",
        "pair-status-btn",
        "scorch-local-btn",
        "scorch-remote-btn",
        "pipeline-btn",
        'data-state="ON"',
        'data-state="OFF"',
        'data-state="FULL_SHUTDOWN"',
        'data-state="MEMORIAL"',
        "Response JSON",
    ):
        assert token in html


def test_home_json_is_status_not_a_receipt() -> None:
    eng = Engine(Ledger())
    before = len(eng.ledger.entries)
    doc = home_document(eng, LOOPBACK, PORT)
    assert len(eng.ledger.entries) == before
    assert doc["ok"] is True
    assert doc["version"] == VERSION
    assert doc["site_state"] == "OFF"
    assert doc["living_presence"] is False
    assert doc["loopback"] == LOOPBACK


def test_loopback_accept_header() -> None:
    httpd = make_server(LOOPBACK, 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        html = urlopen(
            Request(f"http://{LOOPBACK}:{port}/", headers={"Accept": "text/html"})
        ).read().decode()
        assert 'id="start-suite"' in html
        assert html.find('id="start-suite"') < html.find('id="advanced"')
        assert "One-click install" not in html
        custody = urlopen(f"http://{LOOPBACK}:{port}/custody").read().decode()
        assert 'id="integrity-btn"' in custody
        raw = urlopen(
            Request(f"http://{LOOPBACK}:{port}/", headers={"Accept": "application/json"})
        ).read().decode()
        data = json.loads(raw)
        assert data["ok"] is True
        assert data["port"] == port
        health = json.loads(urlopen(f"http://{LOOPBACK}:{port}/v1/health").read().decode())
        assert health["ok"] is True
        assert health["display"]["title"] == "AZInterface health"
        assert "live_ops" in health
    finally:
        httpd.shutdown()
        httpd.server_close()
