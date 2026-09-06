"""AZInterface engine — same ops for CLI, Worker /v1, OpenAPI, and FragGate.

Interface is CUSTODY. Never collapse into Hub.
Pre-locked page cycles: OFF → [integrity check] → ON.
FULL SHUTDOWN and MEMORIAL are locked postures.
Living presence is served only after explicit ON following integrity.
"""

from __future__ import annotations

from typing import Any

from .meta import (
    AZHUB,
    AZHOME,
    CLIENTS,
    FRAGGATE,
    FRAGGATE_CALL,
    FRAGGATE_MCP,
    GITHUB,
    HOST,
    IDENTITY,
    LIMITATION,
    NAME,
    PRODUCT,
    RUNTIME,
    SIGIL,
    SPEC,
    SPEC_STRING,
    VERSION,
)
from .receipts import Ledger, sha256_text

SITE_STATES = ("OFF", "ON", "FULL_SHUTDOWN", "MEMORIAL")
LOCKED_STATES = ("OFF", "FULL_SHUTDOWN", "MEMORIAL")
CYCLE_POSTURES = ("OFF", "INTEGRITY", "ON", "FULL_SHUTDOWN", "MEMORIAL")
MODULES = ("azhome", "hold", "withdraw", "witness")

LIVE_OPS = (
    "health",
    "skill",
    "genesis_status",
    "genesis_boot",
    "site_state_get",
    "site_state_set",
    "integrity_check",
    "witness_list",
    "page_cycle_status",
    "hold",
    "withdraw",
    "scorch_local",
)

STUB_OPS = (
    "scorch_remote",
    "scorch",
    "deanonymize",
    "vault_read",
)

OPS = LIVE_OPS + STUB_OPS

ALIASES = {
    "scorch": "scorch_remote",
    "wipe_remote": "scorch_remote",
    "remote_wipe": "scorch_remote",
    "unmask": "deanonymize",
    "identify": "deanonymize",
    "vault": "vault_read",
    "read_vault": "vault_read",
    "genesis": "genesis_boot",
    "boot": "genesis_boot",
    "state_get": "site_state_get",
    "state_set": "site_state_set",
    "cycle": "page_cycle_status",
    "integrity": "integrity_check",
}

GENESIS_DOMAIN = "azinterface|genesis|AIH-WP-1.0"


def display_of(title: str, summary: str, fields: list[tuple[str, Any]] | None = None) -> dict[str, Any]:
    rows = [{"label": k, "value": str(v)} for k, v in (fields or [])]
    return {
        "title": title,
        "summary": summary,
        "fields": rows,
        "next": "Show this output to the user, then take the next input.",
    }


def genesis_hash_key(username: str) -> str:
    """One-time Genesis Hash Key. Username is never stored — hash only."""
    seed = f"{GENESIS_DOMAIN}|{username}"
    return sha256_text(seed)


def normalize_state(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip().upper().replace(" ", "_").replace("-", "_")
    aliases = {
        "FULLSHUTDOWN": "FULL_SHUTDOWN",
        "FULL_STOP": "FULL_SHUTDOWN",
        "SHUTDOWN": "FULL_SHUTDOWN",
        "MEM": "MEMORIAL",
        "OFFLINE": "OFF",
        "ONLINE": "ON",
    }
    text = aliases.get(text, text)
    return text if text in SITE_STATES else None


class Engine:
    """In-process custodial engine. Ephemeral session; optional JSONL receipts."""

    def __init__(self, ledger: Ledger | None = None) -> None:
        self.ledger = ledger or Ledger()
        self.site_state = "OFF"
        self.integrity_ok = False
        self.integrity_ts: str | None = None
        self.integrity_digest: str | None = None
        self.genesis_hash: str | None = None
        self.genesis_keyed = False
        self.holds: list[dict[str, Any]] = []
        self.witnesses: list[dict[str, Any]] = []

    def _receipt(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.ledger.append(action, payload or {})

    def _base(self, **extra: Any) -> dict[str, Any]:
        out = {
            "product": PRODUCT,
            "name": NAME,
            "version": VERSION,
            "spec": SPEC,
            "spec_string": SPEC_STRING,
            "identity": IDENTITY,
            "author": IDENTITY,
            "slug": PRODUCT,
            "door": "fraggate",
            "role": "custody",
            "hub_collapse": False,
            "sibling_hub": AZHUB,
            "kv_increment": False,
            "stored": False,
            "vault_contents": False,
            "cloud_asleep": False,
            "remote_wipe": False,
            "username_stored": False,
            "limitation": LIMITATION,
            "agent_path": FRAGGATE_CALL,
            "runtime": RUNTIME,
            "kernel": FRAGGATE,
            "host": HOST,
            "sigil": SIGIL,
            "azhome": AZHOME,
        }
        out.update(extra)
        return out

    def living_presence(self) -> bool:
        return self.site_state == "ON" and self.integrity_ok is True

    def cycle_posture(self) -> str:
        if self.site_state == "FULL_SHUTDOWN":
            return "FULL_SHUTDOWN"
        if self.site_state == "MEMORIAL":
            return "MEMORIAL"
        if self.site_state == "ON" and self.integrity_ok:
            return "ON"
        if self.site_state == "OFF" and self.integrity_ok:
            return "INTEGRITY"
        return "OFF"

    def locked(self) -> bool:
        return not self.living_presence()

    def module_surface(self, name: str) -> dict[str, Any]:
        living = self.living_presence()
        if name == "witness":
            return {
                "module": name,
                "served": True,
                "living_presence": living,
                "posture": "living" if living else "locked_list_only",
                "vault_contents": False,
                "note": "Witness list is metadata only. Vault contents are never served.",
            }
        return {
            "module": name,
            "served": living,
            "living_presence": living,
            "posture": "living" if living else "pre_locked",
            "note": (
                "Living presence."
                if living
                else "Pre-locked. Content does not serve as living presence until ON after integrity."
            ),
        }

    def page_cycle_snapshot(self) -> dict[str, Any]:
        posture = self.cycle_posture()
        living = self.living_presence()
        return {
            "site_state": self.site_state,
            "cycle": posture,
            "cycle_path": "OFF → [integrity check] → ON",
            "also": ["FULL_SHUTDOWN", "MEMORIAL"],
            "locked": not living,
            "pre_locked": not living,
            "living_presence": living,
            "integrity_ok": self.integrity_ok,
            "integrity_ts": self.integrity_ts,
            "genesis_keyed": self.genesis_keyed,
            "genesis_hash": self.genesis_hash,
            "cloud_asleep": False,
            "modules": {name: self.module_surface(name) for name in MODULES},
            "note": (
                "Living presence enabled."
                if living
                else "Pre-locked page cycle. Apps do not render as living presence until the operator enables ON after integrity. No cloud-asleep availability."
            ),
        }

    def health(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("health", {"site_state": self.site_state})
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            runtime_true=True,
            live_ops=list(LIVE_OPS),
            stub_ops=list(STUB_OPS),
            ops=list(OPS),
            site_state=self.site_state,
            living_presence=cycle["living_presence"],
            catalog_mcp=FRAGGATE_MCP,
            github=GITHUB,
            clients=list(CLIENTS),
            receipt=rec,
            display=display_of(
                "AZInterface health",
                "Custodial operating environment. Interface is CUSTODY — not Hub.",
                [
                    ("version", VERSION),
                    ("spec", SPEC),
                    ("site_state", self.site_state),
                    ("living_presence", cycle["living_presence"]),
                    ("hub_collapse", False),
                ],
            ),
        )

    def skill(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        from pathlib import Path

        skill = Path(__file__).resolve().parent.parent / "SKILL.md"
        text = skill.read_text(encoding="utf-8") if skill.exists() else LIMITATION
        return self._base(ok=True, markdown=text)

    def genesis_status(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("genesis_status", {"keyed": self.genesis_keyed})
        return self._base(
            ok=True,
            keyed=self.genesis_keyed,
            genesis_keyed=self.genesis_keyed,
            genesis_hash=self.genesis_hash,
            username_stored=False,
            one_time=True,
            receipt=rec,
            display=display_of(
                "Genesis status",
                "One-time keying. Hash only. Username is never stored.",
                [
                    ("keyed", self.genesis_keyed),
                    ("genesis_hash", self.genesis_hash or ""),
                    ("username_stored", False),
                ],
            ),
        )

    def genesis_boot(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        username = str(payload.get("username") or payload.get("seed") or payload.get("name") or "").strip()
        if self.genesis_keyed:
            rec = self._receipt("genesis_boot_refused", {"reason": "already_keyed"})
            return self._base(
                ok=False,
                code="GENESIS_ALREADY_KEYED",
                keyed=True,
                genesis_keyed=True,
                genesis_hash=self.genesis_hash,
                username_stored=False,
                receipt=rec,
                display=display_of(
                    "Genesis already keyed",
                    "One-time only. Existing Genesis Hash Key is shown. Username was never stored.",
                    [("genesis_hash", self.genesis_hash or ""), ("username_stored", False)],
                ),
            )
        if not username:
            return self._base(
                ok=False,
                code="GENESIS_SEED_REQUIRED",
                keyed=False,
                error="username seed required (used once, never stored)",
                display=display_of("Genesis seed required", "Provide a one-time username seed. It is hashed and discarded."),
            )
        digest = genesis_hash_key(username)
        # Username leaves this frame. Only the hash is retained.
        username = ""
        self.genesis_hash = digest
        self.genesis_keyed = True
        rec = self._receipt("genesis_boot", {"keyed": True, "hash_prefix": digest[:16]})
        return self._base(
            ok=True,
            keyed=True,
            genesis_keyed=True,
            genesis_hash=digest,
            genesis_hash_key=digest,
            username_stored=False,
            one_time=True,
            receipt=rec,
            display=display_of(
                "Genesis Hash Key",
                "One-time keying complete. Display is the hash only. Username discarded.",
                [("genesis_hash", digest), ("username_stored", False)],
            ),
        )

    def site_state_get(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("site_state_get", {"site_state": self.site_state})
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            site_state=self.site_state,
            allowed=list(SITE_STATES),
            living_presence=cycle["living_presence"],
            cycle=cycle,
            receipt=rec,
            display=display_of(
                "Site state",
                f"Current posture {self.site_state}. Living presence only after ON following integrity.",
                [("site_state", self.site_state), ("living_presence", cycle["living_presence"])],
            ),
        )

    def site_state_set(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        wanted = normalize_state(payload.get("state") or payload.get("site_state") or payload.get("to"))
        if not wanted:
            return self._base(
                ok=False,
                code="SITE_STATE_UNKNOWN",
                error="state must be ON, OFF, FULL_SHUTDOWN, or MEMORIAL",
                allowed=list(SITE_STATES),
                site_state=self.site_state,
            )
        if wanted == "ON" and not self.integrity_ok:
            rec = self._receipt("site_state_set_refused", {"wanted": "ON", "reason": "need_integrity"})
            return self._base(
                ok=False,
                code="NEED_INTEGRITY",
                error="ON requires a passing integrity check in this cycle. Pre-locked. No cloud-asleep availability.",
                site_state=self.site_state,
                living_presence=False,
                need_integrity=True,
                receipt=rec,
                display=display_of(
                    "Integrity required",
                    "OFF → [integrity check] → ON. Living presence is not served until the operator enables ON after integrity.",
                    [("site_state", self.site_state), ("integrity_ok", False)],
                ),
            )
        prev = self.site_state
        self.site_state = wanted
        if prev == "ON" and wanted != "ON":
            # Leaving living presence closes the cycle. ON again needs a fresh integrity check.
            self.integrity_ok = False
            self.integrity_ts = None
            self.integrity_digest = None
        if wanted in ("FULL_SHUTDOWN", "MEMORIAL"):
            self.integrity_ok = False
            self.integrity_ts = None
            self.integrity_digest = None
        rec = self._receipt("site_state_set", {"from": prev, "to": wanted, "living": self.living_presence()})
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            site_state=self.site_state,
            previous=prev,
            living_presence=cycle["living_presence"],
            cycle=cycle,
            receipt=rec,
            display=display_of(
                f"Site state {wanted}",
                "Living presence." if cycle["living_presence"] else "Locked posture. No living app serve.",
                [("from", prev), ("to", wanted), ("living_presence", cycle["living_presence"])],
            ),
        )

    def integrity_check(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        fail = bool(payload.get("fail") or payload.get("force_fail"))
        if fail:
            self.integrity_ok = False
            self.integrity_ts = None
            self.integrity_digest = None
            if self.site_state == "ON":
                self.site_state = "OFF"
            rec = self._receipt("integrity_fail", {"ok": False})
            return self._base(
                ok=False,
                code="INTEGRITY_FAIL",
                integrity_ok=False,
                living_presence=False,
                site_state=self.site_state,
                receipt=rec,
                display=display_of("Integrity failed", "Cycle remains pre-locked. ON is refused."),
            )
        digest = sha256_text(
            f"azinterface|integrity|{SPEC}|{self.genesis_hash or 'ungekeyed'}|{self.ledger.tip}"
        )
        self.integrity_ok = True
        from .receipts import now_iso

        self.integrity_ts = now_iso()
        self.integrity_digest = digest
        rec = self._receipt("integrity_check", {"ok": True, "digest_prefix": digest[:16]})
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            integrity_ok=True,
            integrity_digest=digest,
            integrity_ts=self.integrity_ts,
            site_state=self.site_state,
            living_presence=cycle["living_presence"],
            cycle=cycle,
            receipt=rec,
            display=display_of(
                "Integrity passed",
                "Operator may now enable ON. Living presence is still locked until ON.",
                [("integrity_ok", True), ("site_state", self.site_state), ("digest", digest)],
            ),
        )

    def page_cycle_status(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("page_cycle_status", {"cycle": self.cycle_posture()})
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            **cycle,
            receipt=rec,
            display=display_of(
                "Page cycle",
                cycle["note"],
                [
                    ("site_state", cycle["site_state"]),
                    ("cycle", cycle["cycle"]),
                    ("living_presence", cycle["living_presence"]),
                    ("cloud_asleep", False),
                ],
            ),
        )

    def _witness_row(self, kind: str, hold_id: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt(kind, {"hold_id": hold_id, **(extra or {})})
        row = {
            "kind": kind,
            "hold_id": hold_id,
            "hash": rec["hash"],
            "ts": rec["ts"],
            "seq": rec["seq"],
            "vault_contents": False,
        }
        self.witnesses.append(row)
        return row

    def witness_list(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("witness_list", {"count": len(self.witnesses)})
        rows = [{k: v for k, v in w.items() if k != "contents"} for w in self.witnesses]
        return self._base(
            ok=True,
            witnesses=rows,
            count=len(rows),
            vault_contents=False,
            receipt=rec,
            display=display_of(
                "Witness list",
                "Custody witnesses only. Vault contents are never listed.",
                [("count", len(rows)), ("vault_contents", False)],
            ),
        )

    def hold(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        if not self.living_presence():
            rec = self._receipt("hold_refused", {"reason": "pre_locked"})
            return self._base(
                ok=False,
                code="PRE_LOCKED",
                error="Hold is a living-presence act. Enable ON after integrity.",
                living_presence=False,
                site_state=self.site_state,
                receipt=rec,
                display=display_of("Pre-locked", "Hold does not run until ON after integrity."),
            )
        label = str(payload.get("label") or payload.get("name") or "hold").strip()[:80]
        label_hash = sha256_text(f"azinterface|hold|{label}")
        hold_id = "hold-" + label_hash[:12]
        row = {
            "hold_id": hold_id,
            "label_hash": label_hash,
            "status": "held",
            "vault_contents": False,
        }
        self.holds.append(row)
        witness = self._witness_row("hold", hold_id, {"label_hash": label_hash})
        return self._base(
            ok=True,
            hold=row,
            witness=witness,
            vault_contents=False,
            display=display_of(
                "Hold",
                "Custody hold recorded. Label hashed. Vault contents not stored.",
                [("hold_id", hold_id), ("status", "held"), ("vault_contents", False)],
            ),
        )

    def withdraw(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        if not self.living_presence():
            rec = self._receipt("withdraw_refused", {"reason": "pre_locked"})
            return self._base(
                ok=False,
                code="PRE_LOCKED",
                error="Withdraw is a living-presence act. Enable ON after integrity.",
                living_presence=False,
                site_state=self.site_state,
                receipt=rec,
                display=display_of("Pre-locked", "Withdraw does not run until ON after integrity."),
            )
        hold_id = str(payload.get("hold_id") or payload.get("id") or "").strip()
        target = None
        if hold_id:
            for row in self.holds:
                if row["hold_id"] == hold_id:
                    target = row
                    break
        elif self.holds:
            target = next((h for h in reversed(self.holds) if h["status"] == "held"), None)
        if not target:
            return self._base(
                ok=False,
                code="HOLD_NOT_FOUND",
                error="No matching hold. Witness list shows ids only — never vault contents.",
                vault_contents=False,
            )
        target["status"] = "withdrawn"
        witness = self._witness_row("withdraw", target["hold_id"])
        return self._base(
            ok=True,
            hold=target,
            witness=witness,
            vault_contents=False,
            display=display_of(
                "Withdraw",
                "Custody withdraw recorded. Vault contents were never stored on this Worker.",
                [("hold_id", target["hold_id"]), ("status", "withdrawn")],
            ),
        )

    def scorch_local(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("scorch_local_advisory", {"remote_wipe": False})
        return self._base(
            ok=True,
            advisory=True,
            local_only=True,
            remote_wipe=False,
            code="SCORCH_LOCAL_ADVISORY",
            note="Scorched Earth on the hosted Worker is a local stub/advisory only. It never remotely wipes user devices.",
            receipt=rec,
            display=display_of(
                "Scorched Earth (local advisory)",
                "Hosted Worker will not remotely wipe devices. Local operator machines stay under local control.",
                [("remote_wipe", False), ("local_only", True)],
            ),
        )

    def _stub(self, op: str) -> dict[str, Any]:
        rec = self._receipt("stub_refuse", {"op": op})
        reasons = {
            "scorch_remote": "Hosted Scorched Earth never remotely wipes user devices. Local stub/advisory only (scorch_local).",
            "deanonymize": "AZInterface does not deanonymize. Identity is Aziel Eliab only.",
            "vault_read": "Hosted Worker never serves vault contents. Witness list is metadata only.",
        }
        return self._base(
            ok=False,
            code="STUB",
            stub=True,
            op=op,
            error=reasons.get(op, "stub"),
            note=reasons.get(op, "stub"),
            receipt=rec,
            display=display_of("Stub refused", reasons.get(op, "stub"), [("op", op), ("code", "STUB")]),
        )

    def scorch_remote(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._stub("scorch_remote")

    def deanonymize(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._stub("deanonymize")

    def vault_read(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._stub("vault_read")

    def dispatch(self, op: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        name = str(op or "").strip().lower().replace("-", "_")
        name = ALIASES.get(name, name)
        if name not in OPS:
            return {
                "ok": False,
                "code": "FG-HALLUC-TOOL",
                "error": "unknown op",
                "op": op,
                "ops": list(LIVE_OPS),
                "stub_ops": list(STUB_OPS),
                "limitation": LIMITATION,
                "agent_path": FRAGGATE_CALL,
            }
        handler = getattr(self, name)
        return handler(payload or {})
