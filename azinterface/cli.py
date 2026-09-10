"""AZInterface CLI — custody cycle, genesis, witness, loopback UI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from pathlib import Path

from .engine import LIVE_OPS, STUB_OPS, Engine
from .meta import HOST, LIMITATION, LOOPBACK, PORT, SPEC, VERSION
from .doctor import run_doctor
from .receipts import Ledger


def _engine(args: argparse.Namespace) -> Engine:
    path = getattr(args, "ledger", None) or os.environ.get("AZINTERFACE_LEDGER") or "./azinterface_receipts.jsonl"
    state_path = Path(path).with_name(Path(path).stem + ".state.json")
    return Engine(Ledger(path), state_path=state_path)


def _print(obj: object) -> int:
    if isinstance(obj, dict) and obj.get("display"):
        d = obj["display"]
        print(d.get("title") or "AZInterface")
        print(d.get("summary") or "")
        for row in d.get("fields") or []:
            print(f"  {row.get('label')}: {row.get('value')}")
        print()
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0 if (not isinstance(obj, dict) or obj.get("ok", True)) else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="azinterface",
        description="AZInterface (AIH-WP-1.0) custodial operating environment. Author Aziel Eliab.",
    )
    p.add_argument("--ledger", default=os.environ.get("AZINTERFACE_LEDGER", "./azinterface_receipts.jsonl"))
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version")
    sub.add_parser("doctor")
    ui = sub.add_parser("ui")
    ui.add_argument("--port", type=int, default=PORT)
    sub.add_parser("health")
    sub.add_parser("ops")
    sub.add_parser("genesis-status")
    boot = sub.add_parser("genesis")
    boot.add_argument("username", help="One-time username seed. Hashed and discarded.")
    sub.add_parser("state")
    st = sub.add_parser("state-set")
    st.add_argument("state", help="OFF | integrity | ON | FULL SHUTDOWN | MEMORIAL (one sealed step)")
    sub.add_parser("integrity")
    sub.add_parser("cycle")
    sub.add_parser("pipeline")
    sub.add_parser("witness")
    h = sub.add_parser("hold")
    h.add_argument("--label", default="hold")
    w = sub.add_parser("withdraw")
    w.add_argument("--hold-id", default="")
    sub.add_parser("scorch-local")
    offer = sub.add_parser("pair-offer")
    offer.add_argument("--via", default="local")
    offer.add_argument("--pair-id", default="")
    offer.add_argument("--photon-id", default="")
    accept = sub.add_parser("pair-accept")
    accept.add_argument("--pair-id", default="")
    accept.add_argument("--via", default="")
    seal = sub.add_parser("pair-seal")
    seal.add_argument("--pair-id", default="")
    cut = sub.add_parser("pair-cut")
    cut.add_argument("--pair-id", default="")
    sub.add_parser("pair-status")
    c = sub.add_parser("call")
    c.add_argument("op")
    c.add_argument("--payload", default="{}")

    args = p.parse_args(argv)
    if args.cmd == "version":
        print(f"AZInterface {VERSION} ({SPEC})")
        print(LIMITATION)
        print("Worker:", HOST)
        print(f"Local UI: http://{LOOPBACK}:{PORT} (loopback only)")
        return 0
    if args.cmd == "doctor":
        return run_doctor()
    if args.cmd == "ui":
        from .ui import serve

        return serve(port=int(args.port))

    eng = _engine(args)
    if args.cmd == "ops":
        return _print({"ok": True, "live_ops": list(LIVE_OPS), "stub_ops": list(STUB_OPS)})
    if args.cmd == "health":
        return _print(eng.health({}))
    if args.cmd == "genesis-status":
        return _print(eng.genesis_status({}))
    if args.cmd == "genesis":
        return _print(eng.genesis_boot({"username": args.username}))
    if args.cmd == "state":
        return _print(eng.site_state_get({}))
    if args.cmd == "state-set":
        return _print(eng.site_state_set({"state": args.state}))
    if args.cmd == "integrity":
        return _print(eng.integrity_check({}))
    if args.cmd == "cycle":
        return _print(eng.page_cycle_status({}))
    if args.cmd == "pipeline":
        return _print(eng.pipeline_arch({}))
    if args.cmd == "witness":
        return _print(eng.witness_list({}))
    if args.cmd == "hold":
        return _print(eng.hold({"label": args.label}))
    if args.cmd == "withdraw":
        return _print(eng.withdraw({"hold_id": args.hold_id}))
    if args.cmd == "scorch-local":
        return _print(eng.scorch_local({}))
    if args.cmd == "pair-offer":
        return _print(eng.pair_offer({"via": args.via, "pair_id": args.pair_id, "photon_id": args.photon_id}))
    if args.cmd == "pair-accept":
        payload: dict[str, Any] = {"pair_id": args.pair_id}
        if args.via:
            payload["via"] = args.via
        return _print(eng.pair_accept(payload))
    if args.cmd == "pair-seal":
        return _print(eng.pair_seal({"pair_id": args.pair_id}))
    if args.cmd == "pair-cut":
        return _print(eng.pair_cut({"pair_id": args.pair_id}))
    if args.cmd == "pair-status":
        return _print(eng.pair_status({}))
    if args.cmd == "call":
        try:
            payload: dict[str, Any] = json.loads(args.payload)
        except json.JSONDecodeError:
            print("payload must be JSON", file=sys.stderr)
            return 2
        return _print(eng.dispatch(args.op, payload))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
