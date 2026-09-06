"""Hold / withdraw / witness. No vault contents."""

import json

from azinterface.engine import Engine
from azinterface.receipts import Ledger


def test_hold_withdraw_locked_until_on() -> None:
    eng = Engine(Ledger())
    assert eng.hold({"label": "box"})["code"] == "PRE_LOCKED"
    assert eng.withdraw({})["code"] == "PRE_LOCKED"
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    hold = eng.hold({"label": "secret-box"})
    assert hold["ok"] is True
    assert hold["vault_contents"] is False
    listed = eng.witness_list({})
    blob = json.dumps(listed)
    assert "secret-box" not in blob
    assert listed["vault_contents"] is False
    assert listed["count"] >= 1
    out = eng.withdraw({})
    assert out["hold"]["status"] == "withdrawn"


def test_stubs_refuse() -> None:
    eng = Engine(Ledger())
    for op in ("scorch_remote", "deanonymize", "vault_read", "scorch"):
        out = eng.dispatch(op, {})
        assert out["ok"] is False
        assert out["code"] == "STUB"
        assert out.get("remote_wipe") is False
    local = eng.scorch_local({})
    assert local["ok"] is True
    assert local["local_only"] is True
    assert local["remote_wipe"] is False


def test_unknown_op_is_hallucination() -> None:
    out = Engine(Ledger()).dispatch("not_real", {})
    assert out["code"] == "FG-HALLUC-TOOL"


def test_not_hub() -> None:
    health = Engine(Ledger()).health({})
    assert health["hub_collapse"] is False
    assert health["role"] == "custody"
    assert "azhub" in health["sibling_hub"]
