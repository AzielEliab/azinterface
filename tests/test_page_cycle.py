"""AIH-WP-1.0 pre-locked cycles. OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL."""

from pathlib import Path

from azinterface.engine import PAGE_CYCLES, Engine
from azinterface.receipts import Ledger


def test_default_is_pre_locked() -> None:
    eng = Engine(Ledger())
    cycle = eng.page_cycle_status()
    assert cycle["site_state"] == "OFF"
    assert cycle["current"] == "OFF"
    assert cycle["cycle"] == "OFF"
    assert cycle["pre_locked"] is True
    assert cycle["living_presence"] is False
    assert cycle["cloud_asleep"] is False
    assert cycle["modules"]["azhome"]["served"] is False
    assert cycle["cycles"] == list(PAGE_CYCLES)
    assert cycle["page_cycle"]["skip_forbidden"] is True
    assert cycle["page_cycle"]["locked_order"] is True


def test_on_from_off_is_skip() -> None:
    eng = Engine(Ledger())
    out = eng.site_state_set({"state": "ON"})
    assert out["ok"] is False
    assert out["code"] == "AIH-CYCLE-LOCKED"
    assert out["living_presence"] is False


def test_memorial_from_off_is_skip() -> None:
    eng = Engine(Ledger())
    out = eng.site_state_set({"state": "MEMORIAL"})
    assert out["ok"] is False
    assert out["code"] == "AIH-CYCLE-LOCKED"


def test_integrity_then_on_serves_azhome() -> None:
    eng = Engine(Ledger())
    integ = eng.integrity_check({})
    assert integ["ok"] is True
    assert integ["living_presence"] is False
    assert integ["current"] == "integrity"
    on = eng.site_state_set({"state": "ON"})
    assert on["ok"] is True
    assert on["living_presence"] is True
    assert on["cycle"]["modules"]["azhome"]["served"] is True


def test_integrity_step_without_check_blocks_on() -> None:
    eng = Engine(Ledger())
    step = eng.site_state_set({"cycle": "integrity"})
    assert step["ok"] is True
    again = eng.site_state_set({"cycle": "ON"})
    assert again["ok"] is False
    assert again["code"] == "AIH-INTEGRITY-REQUIRED"


def test_full_shutdown_and_memorial_lock() -> None:
    eng = Engine(Ledger())
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    shut = eng.site_state_set({"state": "FULL_SHUTDOWN"})
    assert shut["living_presence"] is False
    assert shut["current"] == "FULL SHUTDOWN"
    mem = eng.site_state_set({"state": "MEMORIAL"})
    assert mem["living_presence"] is False
    assert mem["site_state"] == "MEMORIAL"
    again = eng.site_state_set({"state": "ON"})
    assert again["code"] == "AIH-CYCLE-TERMINAL"


def test_off_after_on_is_locked() -> None:
    eng = Engine(Ledger())
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    back = eng.site_state_set({"state": "OFF"})
    assert back["code"] == "AIH-CYCLE-LOCKED"


def test_auto_unlock_payload_refused() -> None:
    eng = Engine(Ledger())
    out = eng.dispatch("site_state_set", {"cycle": "ON", "auto_unlock": True})
    assert out["ok"] is False
    assert out["code"] == "AIH-AUTO-UNLOCK-REFUSE"


def test_state_file_persists_cycle(tmp_path: Path) -> None:
    ledger = tmp_path / "r.jsonl"
    state = tmp_path / "r.state.json"
    first = Engine(Ledger(ledger), state_path=state)
    first.integrity_check({})
    first.site_state_set({"state": "ON"})
    assert first.living_presence() is True
    second = Engine(Ledger(ledger), state_path=state)
    assert second.site_state == "ON"
    assert second.living_presence() is True
    hold = second.hold({"label": "persisted"})
    assert hold["ok"] is True
