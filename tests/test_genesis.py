"""One-time genesis. Hash only. Username never stored."""

import json

from azinterface.engine import Engine, genesis_hash_key
from azinterface.receipts import Ledger


def test_genesis_hash_only_and_one_time() -> None:
    eng = Engine(Ledger())
    first = eng.genesis_boot({"username": "operator-seed-example"})
    assert first["ok"] is True
    assert first["genesis_hash"] == genesis_hash_key("operator-seed-example")
    assert first["username_stored"] is False
    assert "operator-seed-example" not in json.dumps(first)
    second = eng.genesis_boot({"username": "another-name"})
    assert second["ok"] is False
    assert second["code"] == "GENESIS_ALREADY_KEYED"
    assert second["genesis_hash"] == first["genesis_hash"]
    assert "another-name" not in json.dumps(second)


def test_genesis_status_empty() -> None:
    eng = Engine(Ledger())
    st = eng.genesis_status({})
    assert st["keyed"] is False
    assert st["genesis_hash"] is None
    assert st["username_stored"] is False
