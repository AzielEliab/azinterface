"""Pre-locked page cycles. OFF → [integrity] → ON. No cloud-asleep."""

from azinterface.engine import Engine
from azinterface.receipts import Ledger


def test_default_is_pre_locked() -> None:
    eng = Engine(Ledger())
    cycle = eng.page_cycle_status()
    assert cycle["site_state"] == "OFF"
    assert cycle["cycle"] == "OFF"
    assert cycle["pre_locked"] is True
    assert cycle["living_presence"] is False
    assert cycle["cloud_asleep"] is False
    assert cycle["modules"]["azhome"]["served"] is False


def test_on_requires_integrity() -> None:
    eng = Engine(Ledger())
    out = eng.site_state_set({"state": "ON"})
    assert out["ok"] is False
    assert out["code"] == "NEED_INTEGRITY"
    assert out["living_presence"] is False


def test_integrity_then_on_serves_azhome() -> None:
    eng = Engine(Ledger())
    integ = eng.integrity_check({})
    assert integ["ok"] is True
    assert integ["living_presence"] is False
    on = eng.site_state_set({"state": "ON"})
    assert on["ok"] is True
    assert on["living_presence"] is True
    assert on["cycle"]["modules"]["azhome"]["served"] is True


def test_full_shutdown_and_memorial_lock() -> None:
    eng = Engine(Ledger())
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    shut = eng.site_state_set({"state": "FULL_SHUTDOWN"})
    assert shut["living_presence"] is False
    assert shut["cycle"]["cycle"] == "FULL_SHUTDOWN"
    mem = eng.site_state_set({"state": "MEMORIAL"})
    assert mem["living_presence"] is False
    assert mem["site_state"] == "MEMORIAL"
    again = eng.site_state_set({"state": "ON"})
    assert again["code"] == "NEED_INTEGRITY"


def test_off_after_on_requires_fresh_integrity() -> None:
    eng = Engine(Ledger())
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    eng.site_state_set({"state": "OFF"})
    again = eng.site_state_set({"state": "ON"})
    assert again["code"] == "NEED_INTEGRITY"
