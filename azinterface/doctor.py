"""Self-check for AZInterface. Offline. No telemetry. No remote wipe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from azinterface.engine import Engine, LIVE_OPS, STUB_OPS, genesis_hash_key
from azinterface.meta import IDENTITY, LIMITATION, LOOPBACK, SPEC, VERSION
from azinterface.receipts import Ledger

Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if VERSION == "0.1.0" and SPEC == "AIH-WP-1.0":
        return _ok("version", f"{VERSION} {SPEC}")
    return _fail("version", f"{VERSION} {SPEC}")


def _check_identity() -> Check:
    if IDENTITY != "Aziel Eliab":
        return _fail("identity", IDENTITY)
    if "Elroi" in IDENTITY or "AKA" in LIMITATION:
        return _fail("identity", "public alias leaked")
    return _ok("identity", IDENTITY)


def _check_default_off() -> Check:
    eng = Engine(Ledger())
    cycle = eng.page_cycle_status()
    if cycle["site_state"] != "OFF":
        return _fail("default off", cycle["site_state"])
    if cycle["living_presence"] or not cycle["pre_locked"] or cycle["cloud_asleep"]:
        return _fail("default off", json.dumps({k: cycle[k] for k in ("living_presence", "pre_locked", "cloud_asleep")}))
    if cycle["modules"]["azhome"]["served"]:
        return _fail("default off", "azhome served while locked")
    return _ok("default off", "pre-locked; no living presence")


def _check_on_needs_integrity() -> Check:
    eng = Engine(Ledger())
    skip = eng.site_state_set({"state": "ON"})
    if skip.get("ok") or skip.get("code") != "AIH-CYCLE-LOCKED":
        return _fail("skip on from off", str(skip.get("code")))
    step = eng.site_state_set({"state": "integrity"})
    if not step.get("ok"):
        return _fail("step integrity", str(step.get("code")))
    out = eng.site_state_set({"state": "ON"})
    if out.get("ok") or out.get("code") != "AIH-INTEGRITY-REQUIRED":
        return _fail("on needs integrity", str(out.get("code")))
    if out.get("living_presence"):
        return _fail("on needs integrity", "living while refused")
    return _ok("on needs integrity", "AIH-CYCLE-LOCKED then AIH-INTEGRITY-REQUIRED")


def _check_cycle_on() -> Check:
    eng = Engine(Ledger())
    integ = eng.integrity_check({})
    if not integ.get("ok") or integ.get("living_presence") or integ.get("current") != "integrity":
        return _fail("cycle on", "integrity should pass without enabling ON")
    on = eng.site_state_set({"state": "ON"})
    if not on.get("ok") or not on.get("living_presence"):
        return _fail("cycle on", str(on.get("code")))
    if on["cycle"]["modules"]["azhome"]["served"] is not True:
        return _fail("cycle on", "azhome not served")
    return _ok("cycle on", "OFF → integrity → ON")


def _check_genesis_one_time() -> Check:
    eng = Engine(Ledger())
    first = eng.genesis_boot({"username": "operator-seed-example"})
    if not first.get("ok") or not first.get("genesis_hash") or first.get("username_stored"):
        return _fail("genesis", str(first.get("code")))
    digest = genesis_hash_key("operator-seed-example")
    if first["genesis_hash"] != digest:
        return _fail("genesis hash", first["genesis_hash"])
    blob = json.dumps(first)
    if "operator-seed-example" in blob:
        return _fail("genesis leak", "username retained")
    second = eng.genesis_boot({"username": "another-name"})
    if second.get("ok") or second.get("code") != "GENESIS_ALREADY_KEYED":
        return _fail("genesis one-time", str(second.get("code")))
    if "another-name" in json.dumps(second):
        return _fail("genesis leak", "second username retained")
    if second.get("genesis_hash") != digest:
        return _fail("genesis one-time", "hash changed")
    return _ok("genesis one-time", "hash only; username discarded")


def _check_witness_no_vault() -> Check:
    eng = Engine(Ledger())
    eng.integrity_check({})
    eng.site_state_set({"state": "ON"})
    hold = eng.hold({"label": "secret-box"})
    if hold.get("vault_contents"):
        return _fail("witness", "hold leaked vault")
    listed = eng.witness_list({})
    blob = json.dumps(listed)
    if "secret-box" in blob or listed.get("vault_contents"):
        return _fail("witness", blob[:200])
    if listed.get("count", 0) < 1:
        return _fail("witness", "empty")
    return _ok("witness no vault", "metadata only")


def _check_withdraw_locked() -> Check:
    eng = Engine(Ledger())
    out = eng.withdraw({})
    if out.get("code") != "PRE_LOCKED":
        return _fail("withdraw locked", str(out.get("code")))
    return _ok("withdraw locked", "PRE_LOCKED")


def _check_stubs() -> Check:
    eng = Engine(Ledger())
    for op in ("scorch_remote", "deanonymize", "vault_read", "scorch", "pair_wipe", "skip_cycle", "invent_cycle", "auto_unlock"):
        out = eng.dispatch(op, {})
        if out.get("ok") or out.get("code") != "STUB":
            return _fail("stubs", f"{op} {out.get('code')}")
        if out.get("remote_wipe"):
            return _fail("stubs", f"{op} claimed remote wipe")
    local = eng.scorch_local({})
    if not local.get("ok") or local.get("remote_wipe") or not local.get("local_only"):
        return _fail("scorch local", str(local))
    return _ok("stubs", "remote wipe / deanonymize / vault_read refused")


def _check_hallucination() -> Check:
    out = Engine(Ledger()).dispatch("not_a_real_op", {})
    if out.get("code") != "FG-HALLUC-TOOL":
        return _fail("hallucination", str(out.get("code")))
    return _ok("hallucination", "FG-HALLUC-TOOL")


def _check_loopback() -> Check:
    from azinterface.ui import make_server

    try:
        make_server("0.0.0.0", 9)
    except ValueError as exc:
        if "loopback" in str(exc).lower() and LOOPBACK == "127.0.0.1":
            return _ok("loopback", "rejects 0.0.0.0")
        return _fail("loopback", str(exc))
    return _fail("loopback", "accepted 0.0.0.0")


def _check_no_remote_wipe() -> Check:
    root = Path(__file__).parent
    banned = ("os.unlink", "shutil.rmtree", "wipe_device", "remote_wipe = True")
    for path in root.glob("*.py"):
        if path.name == "doctor.py":
            continue
        text = path.read_text(encoding="utf-8")
        for token in banned:
            if token in text:
                return _fail("no remote wipe", f"{path.name}: {token}")
    return _ok("no remote wipe", "advisory only")


def _check_not_hub() -> Check:
    if "Never collapse Interface into Hub" not in LIMITATION:
        return _fail("not hub", "limitation missing")
    if "azhub" in LIVE_OPS or "blank_key" in LIVE_OPS:
        return _fail("not hub", "hub ops leaked")
    return _ok("not hub", "Interface stays custody")


def _check_ops() -> Check:
    need = {
        "health",
        "skill",
        "genesis_status",
        "site_state_get",
        "site_state_set",
        "integrity_check",
        "witness_list",
        "page_cycle_status",
        "pair_offer",
        "pair_accept",
        "pair_seal",
        "pair_cut",
        "pair_status",
    }
    if not need <= set(LIVE_OPS):
        return _fail("live ops", str(set(LIVE_OPS)))
    if not {"scorch_remote", "pair_wipe", "deanonymize", "vault_read", "skip_cycle", "invent_cycle"} <= set(STUB_OPS):
        return _fail("stub ops", str(STUB_OPS))
    return _ok("ops", f"{len(LIVE_OPS)} live / {len(STUB_OPS)} stub")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_default_off,
    _check_on_needs_integrity,
    _check_cycle_on,
    _check_genesis_one_time,
    _check_witness_no_vault,
    _check_withdraw_locked,
    _check_stubs,
    _check_hallucination,
    _check_loopback,
    _check_no_remote_wipe,
    _check_not_hub,
    _check_ops,
)


def run_doctor(*, as_json: bool = False) -> int:
    results = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
        mark = "ok" if ok else "FAIL"
        if not as_json:
            print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": VERSION,
        "spec": SPEC,
        "limitation": LIMITATION,
        "network": False,
        "telemetry": False,
        "remote_wipe": False,
        "hub_collapse": False,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("limitation:", LIMITATION)
        print("doctor", "passed" if failed == 0 else "failed")
    return 0 if failed == 0 else 1
