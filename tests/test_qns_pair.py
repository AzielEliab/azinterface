"""QNS-CD-1.0 pair custody + AIH-WP-1.0 cycle gating."""

import json
from pathlib import Path

from azinterface.engine import Engine, LIVE_OPS, normalize_via, qns_cross_map
from azinterface.meta import QNS_CD, QNSD_BIND
from azinterface.receipts import Ledger


def _on(eng: Engine) -> None:
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})


def test_pair_ops_are_live() -> None:
    for op in ("pair_offer", "pair_accept", "pair_seal", "pair_cut", "pair_status"):
        assert op in LIVE_OPS


def test_cross_map_is_honest() -> None:
    m = qns_cross_map()
    assert m["spec"] == QNS_CD
    assert m["via_runs_in"] == "qnsd"
    assert m["qnsd"] == QNSD_BIND
    assert m["softwares_tab_qns"] is False
    assert m["get_enables_mesh"] is False
    assert m["node_gate"] is False
    assert m["untraceable_origin"] is False
    assert m["remote_wipe"] is False
    assert m["vault_contents"] is False
    assert "qnm-node" in m["canonical"]


def test_normalize_via_walker_list() -> None:
    assert normalize_via(None) == "local"
    assert normalize_via("bt") == "bt"
    assert normalize_via("bluetooth") == "bt"
    assert normalize_via("invented") is None


def test_pair_status_readable_while_off() -> None:
    eng = Engine(Ledger())
    st = eng.pair_status({})
    assert st["ok"] is True
    assert st["count"] == 0
    assert st["vault_contents"] is False
    assert st["qns"]["softwares_tab_qns"] is False


def test_pair_mutate_refused_off_integrity_shutdown_memorial() -> None:
    eng = Engine(Ledger())
    off = eng.pair_offer({"via": "local"})
    assert off["code"] == "PRE_LOCKED"
    eng.integrity_check({})
    integ = eng.pair_accept({})
    assert integ["code"] == "PRE_LOCKED"
    eng.site_state_set({"state": "ON"})
    offer = eng.pair_offer({"via": "local"})
    assert offer["ok"] is True
    shut = eng.site_state_set({"state": "FULL_SHUTDOWN"})
    assert shut["ok"] is True
    refused = eng.pair_seal({})
    assert refused["code"] == "QNS-CYCLE-REFUSE"
    mem = eng.site_state_set({"state": "MEMORIAL"})
    assert mem["ok"] is True
    terminal = eng.pair_cut({})
    assert terminal["code"] == "AIH-CYCLE-TERMINAL"
    listed = eng.pair_status({})
    assert listed["ok"] is True
    assert listed["count"] == 1
    assert listed["pairs"][0]["handshake"] == "OFFER"


def test_offer_accept_seal_cut_and_witness_cites() -> None:
    eng = Engine(Ledger())
    _on(eng)
    offer = eng.pair_offer({"via": "lan", "photon_id": "qns1-cite-demo"})
    assert offer["ok"] is True
    assert offer["handshake"] == "OFFER"
    assert offer["pair"]["via"] == "lan"
    assert offer["pair"]["photon_id"] == "qns1-cite-demo"
    assert offer["pair"]["via_runs_in"] == "qnsd"
    assert offer["pair"]["transferred"] is False
    assert offer["vault_contents"] is False
    pair_id = offer["pair"]["pair_id"]
    acc = eng.pair_accept({"pair_id": pair_id})
    assert acc["handshake"] == "ACCEPT"
    skip = eng.pair_accept({"pair_id": pair_id})
    assert skip["code"] == "QNS-HANDSHAKE-LOCKED"
    seal = eng.pair_seal({"pair_id": pair_id})
    assert seal["ok"] is True
    assert seal["handshake"] == "SEAL"
    hold = eng.hold({"label": "secret-box", "pair_id": pair_id, "photon_id": "qns1-cite-demo"})
    assert hold["ok"] is True
    assert hold["hold"]["pair_id"] == pair_id
    blob = json.dumps(hold)
    assert "secret-box" not in blob
    listed = eng.witness_list({})
    kinds = {w.get("kind") for w in listed["witnesses"]}
    assert {"pair_offer", "pair_accept", "pair_seal", "hold"} <= kinds
    assert any(w.get("pair_id") == pair_id for w in listed["witnesses"])
    assert listed["vault_contents"] is False
    cut = eng.pair_cut({"pair_id": pair_id})
    assert cut["ok"] is True
    assert cut["handshake"] == "CUT"
    assert cut["remote_wipe"] is False


def test_walker_restricts_via_change_and_unknown() -> None:
    eng = Engine(Ledger())
    _on(eng)
    bad = eng.pair_offer({"via": "wormhole"})
    assert bad["code"] == "QNS-VIA-UNKNOWN"
    offer = eng.pair_offer({"via": "plc"})
    hop = eng.pair_accept({"pair_id": offer["pair"]["pair_id"], "via": "rf"})
    assert hop["code"] == "QNS-WALKER-RESTRICT"


def test_pair_wipe_is_stub() -> None:
    eng = Engine(Ledger())
    out = eng.dispatch("pair_wipe", {})
    assert out["ok"] is False
    assert out["code"] == "STUB"
    assert out["remote_wipe"] is False
    assert eng.dispatch("wipe_pair", {})["code"] == "STUB"


def test_pair_state_persists(tmp_path: Path) -> None:
    ledger = tmp_path / "r.jsonl"
    state = tmp_path / "r.state.json"
    first = Engine(Ledger(ledger), state_path=state)
    _on(first)
    offer = first.pair_offer({"via": "local"})
    second = Engine(Ledger(ledger), state_path=state)
    assert second.pairs[0]["pair_id"] == offer["pair"]["pair_id"]
    st = second.pair_status({})
    assert st["count"] == 1


def test_aliases_and_health_cite_qns() -> None:
    eng = Engine(Ledger())
    health = eng.health({})
    assert health["qns"]["spec"] == QNS_CD
    assert health["qns"]["qnsd"] == "127.0.0.1"
    _on(eng)
    offer = eng.dispatch("offer", {"via": "operator"})
    assert offer["ok"] is True
    assert offer["pair"]["via"] == "operator"
    st = eng.dispatch("pair", {})
    assert st["count"] == 1
