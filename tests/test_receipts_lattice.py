"""Step 7: azinterface receipts join the runtime dual lattice additively; the old chain still verifies."""

import json
import subprocess
from pathlib import Path

import pytest

from azinterface.receipts import Ledger, LatticeDouble, receipt_hash, verify_lattice, ZERO

RT = Path("/workspace/lat/aziel-runtime/src/dual-lattice.js")


def test_old_chain_rule_unchanged():
    led = Ledger()
    r = led.append("open", {"a": 1})
    assert r["hash"] == receipt_hash(1, ZERO, "open", r["payload_hash"], r["ts"])
    assert set(r) - {"lattice"} == {"kind", "seq", "ts", "action", "prev", "payload_hash", "hash"}


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
