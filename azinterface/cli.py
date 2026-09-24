"""AZInterface CLI — human by default, JSON when asked.

Machine output (`--json`) is the engine object. Agent HTTP/MCP shapes are unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

from pathlib import Path

from .engine import LIVE_OPS, STUB_OPS, Engine
from .meta import IDENTITY, LOOPBACK, PORT, SPEC, VERSION
from .doctor import run_doctor
from .receipts import Ledger

ROOT_HELP = f"""\
AZInterface — custody on this computer (hold, withdraw, witness).

Usage:
  azinterface
  azinterface <command> [options]

Start here:
  azinterface                 What this is, and what to run next
  azinterface ui              Open http://{LOOPBACK}:{PORT}/
  azinterface doctor          Check this install
  azinterface integrity       Record an integrity check

Everyday:
  azinterface genesis <seed>  One-time genesis key (the seed is hashed and discarded)
  azinterface state           Show the page cycle
  azinterface state-set STEP  Advance one sealed step
  azinterface hold --label NAME
  azinterface witness
  azinterface withdraw

Advanced:
  azinterface health
  azinterface genesis-status
  azinterface cycle
  azinterface pipeline
  azinterface ops
  azinterface scorch-local
  azinterface pair-offer [--via local]
  azinterface pair-accept
  azinterface pair-seal
  azinterface pair-cut
  azinterface pair-status
  azinterface call OP [--payload '{{}}']
  azinterface version

Options:
  --json            Print the machine JSON for a command
  --ledger PATH     Receipt file (default: ./azinterface_receipts.jsonl)
  -h, --help        Show this help
  --version         Print the version

Page cycle (one step only): OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL

Author: {IDENTITY}
"""

WELCOME = f"""\
AZInterface keeps custody on this computer. Hold, withdraw, and witness stay on a sealed page cycle: OFF, then integrity, then ON, then full shutdown, then memorial.

Open the local page and run Integrity check.

  azinterface ui
  azinterface doctor
  azinterface --help

Author: {IDENTITY}
"""


class HumanParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if getattr(self, "root_help", False):
            return ROOT_HELP
        return super().format_help()

    def error(self, message: str) -> None:
        self.exit(2, friendly_error(message) + "\n")


def friendly_error(message: str) -> str:
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice:
        name = choice.group(1)
        return f'Unknown command "{name}". Try: azinterface ui   or   azinterface --help'
    required = re.search(r"the following arguments are required: (.+)", message)
    if required:
        return _missing(required.group(1).strip())
    if message.startswith("unrecognized arguments:"):
        token = message.split(":", 1)[1].strip().split()[0]
        if token in {"--version"}:
            return 'Unknown option "--version" here. Try: azinterface version'
        return f'Unknown option "{token}". Try: azinterface --help'
    if "required: cmd" in message:
        return "Try: azinterface ui   or   azinterface --help"
    return f"{message.rstrip('.')}. Try: azinterface --help"


def _missing(fields: str) -> str:
    if "username" in fields:
        return (
            "Genesis needs a one-time seed. It is hashed and discarded.\n"
            "Try: azinterface genesis <seed>"
        )
    if fields == "state" or fields.endswith(" state"):
        return (
            "Name one sealed step: integrity, ON, FULL SHUTDOWN, or MEMORIAL.\n"
            "Try: azinterface state-set integrity"
        )
    if fields == "op" or fields.endswith(" op"):
        return "Name an operation.\nTry: azinterface call integrity_check"
    return f"Missing {fields}.\nTry: azinterface --help"


def _take_flag(argv: list[str], flag: str) -> tuple[list[str], bool]:
    found = False
    cleaned: list[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--":
            cleaned.extend(argv[i:])
            break
        if token == flag:
            found = True
            i += 1
            continue
        cleaned.append(token)
        i += 1
    return cleaned, found


def _engine(args: argparse.Namespace) -> Engine:
    path = getattr(args, "ledger", None) or os.environ.get("AZINTERFACE_LEDGER") or "./azinterface_receipts.jsonl"
    state_path = Path(path).with_name(Path(path).stem + ".state.json")
    return Engine(Ledger(path), state_path=state_path)


def _hint(obj: dict[str, Any]) -> str:
    code = str(obj.get("code") or "")
    op = str(obj.get("op") or "")
    if code == "STUB" and op in {"scorch_remote", "scorch", "pair_wipe"}:
        return "Try: azinterface scorch-local"
    if code == "STUB" and op == "vault_read":
        return "Try: azinterface witness"
    if code == "PRE_LOCKED":
        return "Try: azinterface integrity"
    hints = {
        "AIH-CYCLE-LOCKED": "Try: azinterface integrity   or   azinterface state",
        "AIH-INTEGRITY-REQUIRED": "Try: azinterface integrity",
        "AIH-CYCLE-UNKNOWN": "Try: azinterface state-set integrity",
        "AIH-CYCLE-TERMINAL": "Try: azinterface state",
        "GENESIS_SEED_REQUIRED": "Try: azinterface genesis <seed>",
        "GENESIS_ALREADY_KEYED": "Try: azinterface genesis-status",
        "HOLD_NOT_FOUND": "Try: azinterface witness",
        "PAIR_NOT_FOUND": "Try: azinterface pair-status",
        "QNS-HANDSHAKE-LOCKED": "Try: azinterface pair-status",
        "FG-HALLUC-TOOL": "Try: azinterface --help",
        "INTEGRITY_FAIL": "Try: azinterface state",
    }
    return hints.get(code, "Try: azinterface --help")


def _human(obj: object) -> int:
    if not isinstance(obj, dict):
        print(obj)
        return 0
    if obj.get("code") == "FG-HALLUC-TOOL":
        op = obj.get("op") or "that operation"
        print(f'Unknown operation "{op}".')
        print("Try: azinterface --help")
        return 2
    ok = bool(obj.get("ok", True))
    display = obj.get("display") if isinstance(obj.get("display"), dict) else None
    if isinstance(obj.get("live_ops"), list) and isinstance(obj.get("stub_ops"), list) and display is None:
        print("Live operations")
        for name in obj["live_ops"]:
            print(f"  {name}")
        print("Stub operations")
        for name in obj["stub_ops"]:
            print(f"  {name}")
        return 0 if ok else 2
    if display:
        title = str(display.get("title") or "AZInterface")
        print(title)
        summary = display.get("summary") or ""
        if summary:
            print(summary)
        for row in display.get("fields") or []:
            if isinstance(row, dict) and row.get("label") is not None:
                print(f"  {row.get('label')}: {row.get('value')}")
    elif obj.get("error"):
        print(str(obj["error"]))
        if obj.get("code"):
            print(f"Code: {obj['code']}")
    elif obj.get("code"):
        print(str(obj["code"]))
    else:
        print("AZInterface")
    witnesses = obj.get("witnesses")
    if isinstance(witnesses, list) and witnesses:
        print("Witnesses")
        for row in witnesses:
            if not isinstance(row, dict):
                continue
            kind = row.get("kind") or "witness"
            ident = row.get("hold_id") or row.get("id") or row.get("pair_id") or ""
            print(f"  {kind}  {ident}".rstrip())
    pairs = obj.get("pairs")
    if isinstance(pairs, list) and pairs and display is not None:
        print("Pairs")
        for row in pairs:
            if not isinstance(row, dict):
                continue
            print(
                f"  {row.get('pair_id') or ''}  {row.get('handshake') or ''}  {row.get('via') or ''}".rstrip()
            )
    if ok and obj.get("integrity_ok") and obj.get("current") == "integrity" and not obj.get("living_presence"):
        print("Next: azinterface state-set ON")
    if not ok:
        if obj.get("code") and display:
            print(f"Code: {obj['code']}")
        print(_hint(obj))
    return 0 if ok else 2


def emit(obj: object, as_json: bool) -> int:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0 if (not isinstance(obj, dict) or obj.get("ok", True)) else 2
    return _human(obj)


def print_version(as_json: bool) -> int:
    if as_json:
        return emit(
            {
                "ok": True,
                "name": "AZInterface",
                "version": VERSION,
                "spec": SPEC,
                "author": IDENTITY,
                "local": f"http://{LOOPBACK}:{PORT}/",
            },
            True,
        )
    print(f"AZInterface {VERSION} ({SPEC})")
    print(f"Author: {IDENTITY}")
    print(f"Local page: http://{LOOPBACK}:{PORT}/")
    return 0


def print_welcome(as_json: bool) -> int:
    if as_json:
        return emit(
            {
                "ok": True,
                "name": "AZInterface",
                "version": VERSION,
                "spec": SPEC,
                "author": IDENTITY,
                "local": f"http://{LOOPBACK}:{PORT}/",
                "next": ["azinterface ui", "azinterface doctor", "azinterface --help"],
            },
            True,
        )
    print(WELCOME, end="")
    return 0


def _parser() -> HumanParser:
    parser = HumanParser(prog="azinterface")
    parser.root_help = True
    parser.add_argument("--ledger", default=os.environ.get("AZINTERFACE_LEDGER", "./azinterface_receipts.jsonl"))
    parser.add_argument("--version", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("version", help="Print the version")
    doctor = sub.add_parser("doctor", help="Check this install")
    doctor.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    ui = sub.add_parser("ui", help=f"Open http://{LOOPBACK}:{PORT}/")
    ui.add_argument("--port", type=int, default=PORT)
    sub.add_parser("health", help="Local health record")
    sub.add_parser("ops", help="List live and stub operations")
    sub.add_parser("genesis-status", help="Show whether the genesis key is set")
    boot = sub.add_parser("genesis", help="One-time genesis key. The seed is hashed and discarded.")
    boot.add_argument("username", help="One-time seed. Hashed and discarded.")
    sub.add_parser("state", help="Show the page cycle")
    st = sub.add_parser("state-set", help="Advance one sealed step")
    st.add_argument("state", help="integrity, ON, FULL SHUTDOWN, or MEMORIAL")
    sub.add_parser("integrity", help="Record an integrity check")
    sub.add_parser("cycle", help="Page cycle record")
    sub.add_parser("pipeline", help="Pipeline cite")
    sub.add_parser("witness", help="Witness list (metadata)")
    hold = sub.add_parser("hold", help="Record a hold when the page is ON")
    hold.add_argument("--label", default="hold")
    withdraw = sub.add_parser("withdraw", help="Withdraw a hold when the page is ON")
    withdraw.add_argument("--hold-id", default="")
    sub.add_parser("scorch-local", help="Local Scorched Earth advisory")
    offer = sub.add_parser("pair-offer", help="Record a pair offer cite")
    offer.add_argument("--via", default="local")
    offer.add_argument("--pair-id", default="")
    offer.add_argument("--photon-id", default="")
    accept = sub.add_parser("pair-accept", help="Accept a pair offer")
    accept.add_argument("--pair-id", default="")
    accept.add_argument("--via", default="")
    seal = sub.add_parser("pair-seal", help="Seal a pair memorial")
    seal.add_argument("--pair-id", default="")
    cut = sub.add_parser("pair-cut", help="Dissolve a pair cite")
    cut.add_argument("--pair-id", default="")
    sub.add_parser("pair-status", help="List pair cites")
    call = sub.add_parser("call", help="Call one operation with a JSON payload")
    call.add_argument("op")
    call.add_argument("--payload", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    raw, as_json = _take_flag(raw, "--json")
    args = _parser().parse_args(raw)
    if args.version:
        return print_version(as_json)
    if not args.cmd:
        return print_welcome(as_json)
    if args.cmd == "version":
        return print_version(as_json)
    if args.cmd == "doctor":
        return run_doctor(as_json=as_json or bool(getattr(args, "json", False)))
    if args.cmd == "ui":
        from .ui import serve

        return serve(port=int(args.port))

    eng = _engine(args)
    if args.cmd == "ops":
        return emit({"ok": True, "live_ops": list(LIVE_OPS), "stub_ops": list(STUB_OPS)}, as_json)
    if args.cmd == "health":
        return emit(eng.health({}), as_json)
    if args.cmd == "genesis-status":
        return emit(eng.genesis_status({}), as_json)
    if args.cmd == "genesis":
        return emit(eng.genesis_boot({"username": args.username}), as_json)
    if args.cmd == "state":
        return emit(eng.site_state_get({}), as_json)
    if args.cmd == "state-set":
        return emit(eng.site_state_set({"state": args.state}), as_json)
    if args.cmd == "integrity":
        return emit(eng.integrity_check({}), as_json)
    if args.cmd == "cycle":
        return emit(eng.page_cycle_status({}), as_json)
    if args.cmd == "pipeline":
        return emit(eng.pipeline_arch({}), as_json)
    if args.cmd == "witness":
        return emit(eng.witness_list({}), as_json)
    if args.cmd == "hold":
        return emit(eng.hold({"label": args.label}), as_json)
    if args.cmd == "withdraw":
        return emit(eng.withdraw({"hold_id": args.hold_id}), as_json)
    if args.cmd == "scorch-local":
        return emit(eng.scorch_local({}), as_json)
    if args.cmd == "pair-offer":
        return emit(
            eng.pair_offer({"via": args.via, "pair_id": args.pair_id, "photon_id": args.photon_id}),
            as_json,
        )
    if args.cmd == "pair-accept":
        payload: dict[str, Any] = {"pair_id": args.pair_id}
        if args.via:
            payload["via"] = args.via
        return emit(eng.pair_accept(payload), as_json)
    if args.cmd == "pair-seal":
        return emit(eng.pair_seal({"pair_id": args.pair_id}), as_json)
    if args.cmd == "pair-cut":
        return emit(eng.pair_cut({"pair_id": args.pair_id}), as_json)
    if args.cmd == "pair-status":
        return emit(eng.pair_status({}), as_json)
    if args.cmd == "call":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            print("That payload is not JSON.", file=sys.stderr)
            print("Try: azinterface call integrity_check --payload '{}'", file=sys.stderr)
            return 2
        if not isinstance(payload, dict):
            print("The payload must be a JSON object.", file=sys.stderr)
            print("Try: azinterface call integrity_check --payload '{}'", file=sys.stderr)
            return 2
        return emit(eng.dispatch(args.op, payload), as_json)
    print('Unknown command. Try: azinterface ui   or   azinterface --help', file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
