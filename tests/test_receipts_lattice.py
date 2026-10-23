"""Step 7: azinterface receipts join the runtime dual lattice additively; the old chain still verifies."""

import json
import subprocess
from pathlib import Path

import pytest

from azinterface.receipts import (
    Ledger,
    LatticeDouble,
    LatticeSyncNoOffline,
    receipt_hash,
    verify_lattice,
    ZERO,
)
from azinterface.runtime_lattice import runtime_tiebreak

RT = Path("/workspace/lat/aziel-runtime/src/dual-lattice.js")


def test_old_chain_rule_unchanged():
    led = Ledger()
    r = led.append("open", {"a": 1})
    assert r["hash"] == receipt_hash(1, ZERO, "open", r["payload_hash"], r["ts"])
    assert set(r) - {"lattice"} == {"kind", "seq", "ts", "action", "prev", "payload_hash", "hash"}
    assert "tiebreak" not in r["lattice"]


def test_legacy_rows_still_verify(tmp_path):
    led = Ledger()
    for i in range(3):
        led.append("legacy", {"i": i})
    for r in led.entries:
        r.pop("lattice")
    v = led.verify()
    assert v["ok"] and v["lattice"]["legacy_rows"] == 3 and v["lattice"]["lattice_rows"] == 0
    led.append("new", {"i": 9})
    v = led.verify()
    assert v["ok"] and v["lattice"]["lattice_rows"] == 1


def test_persisted_ledger_roundtrip(tmp_path):
    p = tmp_path / "r.jsonl"
    led = Ledger(p)
    for i in range(5):
        led.append("act", {"i": i})
    again = Ledger(p)
    assert again.verify()["ok"] and again.verify()["lattice"]["lattice_rows"] == 5


def test_offline_double_and_tamper():
    led = Ledger()
    led.append("note", {"x": 1}, offline=True, username="aziel")
    with pytest.raises(LatticeDouble):
        led.append("note", {"x": 1}, offline=True, username="aziel")
    led.append("note", {"x": 1}, offline=True, username="other")
    assert led.verify()["ok"]
    led.entries[0]["lattice"]["primary"] = "f" * 64
    assert not led.verify()["ok"]


def test_sync_tiebreak_is_optional_and_leaves_primary_secondary():
    led = Ledger()
    off = led.append("note", {"x": 1}, offline=True, username="aziel")
    plain = led.append("note", {"x": 2})
    off_primary, off_secondary = off["lattice"]["primary"], off["lattice"]["secondary"]
    plain_primary, plain_secondary = plain["lattice"]["primary"], plain["lattice"]["secondary"]
    assert "tiebreak" not in off["lattice"] and "tiebreak" not in plain["lattice"]
    # sync on an offline write is ignored: the offline row still has no tiebreak block
    ignored = Ledger().append("note", {"x": 1}, offline=True, username="aziel", sync=True)
    assert "tiebreak" not in ignored["lattice"]
    assert ignored["lattice"]["primary"] == off_primary and ignored["lattice"]["secondary"] == off_secondary

    syn = led.append("note", {"x": 1}, sync=True, username="aziel")
    assert off["lattice"]["primary"] == off_primary and off["lattice"]["secondary"] == off_secondary
    assert plain["lattice"]["primary"] == plain_primary and plain["lattice"]["secondary"] == plain_secondary
    assert syn["lattice"]["offline"] is False and syn["lattice"]["username"] is None
    assert syn["lattice"]["secondary"] != off_secondary
    tb = syn["lattice"]["tiebreak"]
    assert tb["status"] == "synced" and tb["prev"] == ZERO and tb["offline_secondary"] == off_secondary
    assert tb["hash"] == runtime_tiebreak(ZERO, syn["lattice"]["primary"], off_secondary, "aziel")
    assert syn["hash"] == receipt_hash(3, plain["hash"], "note", syn["payload_hash"], syn["ts"])
    walked = led.verify()
    assert walked["ok"] and walked["lattice"]["tiebreak"]["synced_rows"] == 1
    assert walked["lattice"]["tiebreak"]["tip"] == tb["hash"]

    with pytest.raises(LatticeDouble):
        led.append("note", {"x": 1}, sync=True, username="aziel")
    with pytest.raises(LatticeSyncNoOffline):
        led.append("note", {"x": 9}, sync=True, username="aziel")
    with pytest.raises(LatticeSyncNoOffline):
        led.append("note", {"x": 1}, sync=True, username="other")

    second_off = led.append("other", {"y": 1}, offline=True, username="aziel")
    second = led.append("other", {"y": 1}, sync=True, username="aziel")
    assert second["lattice"]["tiebreak"]["prev"] == tb["hash"]
    assert second["lattice"]["primary"] != syn["lattice"]["primary"]
    assert second_off["lattice"]["secondary"] == second["lattice"]["tiebreak"]["offline_secondary"]
    assert led.verify()["ok"]

    syn["lattice"]["tiebreak"]["hash"] = "f" * 64
    broken = led.verify()
    assert broken["ok"] is False and broken["lattice"]["reason"] == "tiebreak-miss"


def test_pending_tiebreak_verifies_and_does_not_move_the_tip():
    led = Ledger()
    row = led.append("note", {"x": 1}, offline=True, username="aziel")
    row["lattice"]["tiebreak"] = {
        "status": "pending",
        "hash": None,
        "prev": None,
        "offline_secondary": row["lattice"]["secondary"],
    }
    walked = led.verify()
    assert walked["ok"] and walked["lattice"]["tiebreak"]["synced_rows"] == 0
    assert walked["lattice"]["tiebreak"]["tip"] == ZERO
    assert row["lattice"]["primary"] and row["lattice"]["secondary"]


def test_legacy_lattice_rows_without_tiebreak_still_verify():
    led = Ledger()
    for i in range(4):
        led.append("old", {"i": i})
    assert all("tiebreak" not in r["lattice"] for r in led.entries)
    walked = verify_lattice(led.entries)
    assert walked["ok"] and walked["tiebreak"]["synced_rows"] == 0 and walked["tiebreak"]["tip"] == ZERO


@pytest.mark.skipif(not RT.exists(), reason="runtime checkout not present")
def test_matches_runtime_plan_lattice():
    led = Ledger()
    a = led.append("one", {"k": "v"})
    b = led.append("two", {"k": "w"}, offline=True, username="aziel")
    js = f"""
import {{ planLattice }} from "{RT}";
const a = await planLattice({{ document_hash: "{a['lattice']['document_hash']}", rows: [] }});
const b = await planLattice({{ document_hash: "{b['lattice']['document_hash']}", offline: true, username: "aziel", tips: {{ primary: a.primary, secondary: a.secondary }} }});
console.log(JSON.stringify([a.primary, a.secondary, b.primary, b.secondary]));
"""
    out = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [a["lattice"]["primary"], a["lattice"]["secondary"], b["lattice"]["primary"], b["lattice"]["secondary"]]
