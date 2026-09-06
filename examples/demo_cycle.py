"""Offline demo: OFF → integrity → ON → hold → witness → withdraw (sealed order)."""

from azinterface.engine import Engine
from azinterface.receipts import Ledger


def main() -> None:
    eng = Engine(Ledger())
    print("default", eng.page_cycle_status()["cycle"], eng.living_presence())
    print("on refused", eng.site_state_set({"state": "ON"})["code"])
    print("integrity", eng.integrity_check({})["ok"])
    print("on", eng.site_state_set({"state": "ON"})["living_presence"])
    print("hold", eng.hold({"label": "demo"})["hold"]["hold_id"])
    print("witness count", eng.witness_list()["count"])
    print("withdraw", eng.withdraw({})["hold"]["status"])


if __name__ == "__main__":
    main()
