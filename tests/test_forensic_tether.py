"""AZInterface tether for AZBot Node Collaborative Forensic Design 1.0."""

from __future__ import annotations

import json
import threading
from urllib.request import Request, urlopen

from azinterface.engine import LIVE_OPS, Engine
from azinterface.forensic_session import SPEC, ForensicDesk, name_only
from azinterface.receipts import Ledger
from azinterface.ui import FORENSIC, _ENGINE, make_server

TIP = "a" * 64
NEXT = "b" * 64
TOKEN = "operator-token-9f3a"
ON = {"current": "ON", "site_state": "ON", "living_presence": True, "integrity_ok": True}
OFF = {"current": "OFF", "site_state": "OFF", "living_presence": False, "integrity_ok": False}


def test_name_only_is_not_icann() -> None:
    assert name_only("cap-7")
    assert name_only("ICANN")
    assert name_only("node.aziel")
    assert name_only("https://cap-7/egress")
    assert not name_only("127.0.0.1")


def test_pre_locked_cycle_refuses_handoff_and_keeps_the_step() -> None:
    desk = ForensicDesk()
    body, status = desk.handoff_cite(OFF)
    assert status == 403
    assert body["code"] == "PRE_LOCKED"
    assert body["executed"] is False
    assert body["admitted"] is False
    assert body["second_door"] is False
    assert body["door"] == "fraggate"
    assert body["bind"] == "127.0.0.1"
    assert body["public_port"] is False
    assert body["skip_forbidden"] is True
    assert body["cloud_asleep"] is False
    assert body["remain_off"]["mesh_auto_enable"] is False
    assert body["remain_off"]["cap7_is_icann"] is False
    packaged, code = desk.package_handoff({"slug": "azinterface", "op": "page_cycle_status"}, OFF)
    assert code == 403
    assert packaged["code"] == "PRE_LOCKED"
    assert packaged.get("package") is None
    assert packaged["executed"] is False
    memorial, mem_status = desk.package_handoff(
        {"slug": "azinterface", "op": "health"},
        {"current": "MEMORIAL", "living_presence": False, "integrity_ok": True},
    )
    assert mem_status == 403
    assert memorial["code"] == "AIH-CYCLE-TERMINAL"


def test_on_after_integrity_packages_fraggate_and_does_not_send() -> None:
    desk = ForensicDesk()
    body, status = desk.package_handoff(
        {"slug": "azinterface", "op": "page_cycle_status", "payload": {"note": "tide"}},
        ON,
    )
    assert status == 200
    assert body["ok"] is True
    assert body["executed"] is False
    assert body["stored_payload"] is False
    assert body["second_door"] is False
    assert body["package"]["slug"] == "azinterface"
    assert body["package"]["op"] == "page_cycle_status"
    assert body["package"]["door"].endswith("/v1/fraggate/call")
    assert body["package"]["payload"] == {"note": "tide"}
    assert body["azbot"] == "127.0.0.1"
    refused, status = desk.package_handoff({"slug": "azinterface", "op": "health", "host": "cap-7"}, ON)
    assert status == 403
    assert refused["code"] == "MG-NO-IP-EXIT"
    assert refused["icann"] is False
    public, status = desk.package_handoff({"slug": "azinterface", "op": "health", "host": "203.0.113.9"}, ON)
    assert public["code"] == "AZBOT-BIND-LOOPBACK"
    assert "forensic_session" not in LIVE_OPS
    assert "azieltether" not in LIVE_OPS


def test_parties_share_the_tip_and_cannot_rewrite_it() -> None:
    desk = ForensicDesk()
    blocked, status = desk.append_tip({"session_id": "node-a", "tip": TIP, "party": "human-a"}, OFF)
    assert status == 403
    assert blocked["code"] == "PRE_LOCKED"
    assert desk.sessions == {}
    opened, status = desk.append_tip({"session_id": "node-a", "tip": TIP, "party": "human-a"}, ON)
    assert status == 200
    assert opened["written"] is True
    assert opened["tip"] == TIP
    assert opened["prev"] == "0" * 64
    assert opened["username_stored"] is False
    other, status = desk.read_tip("node-a")
    assert status == 200
    assert other["tip"] == TIP
    assert other["share_tips_only"] is True
    assert other["rewrite"] is False
    same, status = desk.append_tip({"session_id": "node-a", "tip": TIP, "party": "human-b"}, ON)
    assert same["written"] is False
    assert same["parties"] == ["human-a", "human-b"]
    rewrite, status = desk.append_tip({"session_id": "node-a", "tip": NEXT, "prev": "c" * 64}, ON)
    assert status == 409
    assert rewrite["code"] == "TIP-REWRITE-REFUSED"
    assert desk.sessions["node-a"]["tip"] == TIP
    forced, status = desk.append_tip({"session_id": "node-a", "tip": NEXT, "rewrite": True}, ON)
    assert forced["code"] == "TIP-REWRITE-REFUSED"
    linked, status = desk.append_tip({"session_id": "node-a", "tip": NEXT, "prev": TIP, "party": "human-b"}, ON)
    assert status == 200
    assert linked["tip"] == NEXT
    assert linked["prev"] == TIP
    assert linked["seq"] == 2
    named, status = desk.append_tip({"session_id": "node-a", "tip": TIP, "username": "kept"}, ON)
    assert named["code"] == "USERNAME-NOT-STORED"
    assert "kept" not in json.dumps(desk.sessions)


def test_azieltether_needs_a_bearer_and_stays_on_fraggate() -> None:
    desk = ForensicDesk()
    missing, status = desk.expose_tether(None, {})
    assert status == 401
    assert missing["code"] == "MESH-NEED-BEARER"
    assert missing["exposed"] is False
    assert missing["mesh_enabled"] is False
    assert missing["radios_enabled"] is False
    named, status = desk.expose_tether("Bearer cap-7", {})
    assert named["code"] == "MG-NO-IP-EXIT"
    assert named["icann"] is False
    shown, status = desk.expose_tether(f"Bearer {TOKEN}", {})
    assert status == 200
    assert shown["exposed"] is True
    assert shown["bearer"] == "present"
    assert shown["tether"]["slug"] == "azieltether"
    assert shown["tether"]["door"] == "fraggate"
    assert shown["tether"]["second_door"] is False
    assert shown["second_door"] is False
    assert shown["mesh_enabled"] is False
    assert TOKEN not in json.dumps(shown)
    assert shown["spec"] == SPEC
    remain, status = desk.expose_tether(f"Bearer {TOKEN}", {"mesh_enable": True})
    assert remain["code"] == "REMAIN-OFF"
    assert remain["mesh_enabled"] is False


def test_loopback_desk_cooperates_with_the_page_cycle() -> None:
    saved = (_ENGINE.cycle_index, _ENGINE.integrity_ok, _ENGINE.integrity_ts, _ENGINE.integrity_digest)
    FORENSIC.reset()
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    try:
        early = _get(base + "/v1/forensic/handoff")
        assert early["code"] == "PRE_LOCKED"
        assert early["executed"] is False
        _post(base + "/v1/integrity_check", {})
        _post(base + "/v1/site_state_set", {"state": "ON"})
        opened = _post(base + "/v1/forensic/session", {"session_id": "desk-1", "tip": TIP, "party": "human-a"})
        assert opened["ok"] is True
        assert opened["tip"] == TIP
        seen = _get(base + "/v1/forensic/tip?session_id=desk-1")
        assert seen["tip"] == TIP
        assert seen["parties"] == ["human-a"]
        rewrite = _post(base + "/v1/forensic/session", {"session_id": "desk-1", "tip": NEXT, "replace": True})
        assert rewrite["code"] == "TIP-REWRITE-REFUSED"
        again = _get(base + "/v1/forensic/tip?session_id=desk-1")
        assert again["tip"] == TIP
        packed = _post(base + "/v1/forensic/handoff", {"slug": "azinterface", "op": "witness_list", "payload": {}})
        assert packed["executed"] is False
        assert packed["package"]["door"].endswith("/v1/fraggate/call")
        assert packed["second_door"] is False
        denied = _get(base + "/v1/azieltether")
        assert denied["code"] == "MESH-NEED-BEARER"
        cited = json.loads(
            urlopen(Request(base + "/v1/azieltether", headers={"Authorization": f"Bearer {TOKEN}"})).read().decode()
        )
        assert cited["tether"]["slug"] == "azieltether"
        assert cited["mesh_enabled"] is False
        assert TOKEN not in json.dumps(cited)
        cap = _post(base + "/v1/forensic/handoff", {"slug": "azinterface", "op": "health", "host": "https://icann/x"})
        assert cap["code"] == "MG-NO-IP-EXIT"
    finally:
        httpd.shutdown()
        httpd.server_close()
        _ENGINE.cycle_index, _ENGINE.integrity_ok, _ENGINE.integrity_ts, _ENGINE.integrity_digest = saved
        FORENSIC.reset()
        assert Engine(Ledger()).site_state == "OFF"
        assert _ENGINE.site_state == "OFF"


def _get(url: str) -> dict:
    return _open(url)


def _open(url: str, payload: dict | None = None, headers: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    hdrs = dict(headers or {})
    if payload is not None:
        hdrs["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=hdrs)
    try:
        raw = urlopen(req).read().decode()
    except Exception as exc:
        if not hasattr(exc, "read"):
            raise
        raw = exc.read().decode()
    return json.loads(raw)


def _post(url: str, payload: dict) -> dict:
    return _open(url, payload)
