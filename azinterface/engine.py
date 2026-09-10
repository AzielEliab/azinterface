"""AZInterface engine — same ops for CLI, Worker /v1, OpenAPI, and FragGate.

Interface is CUSTODY. Never collapse into Hub.
AIH-WP-1.0 pre-locked page cycles (sealed order, one step only):
OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL.
Living presence is served only at ON after integrity.
AZHub is separate software under the one FragGate door.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .meta import (
    AIH_PAIR,
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
    PAIR_STEPS,
    PRODUCT,
    QNM_BUILD,
    QNM_NODE,
    QNS_CD,
    QNS_DOC,
    QNS_VIAS,
    QNSD_BIND,
    RUNTIME,
    SIGIL,
    SPEC,
    SPEC_STRING,
    VERSION,
)
from .pipeline import FOURDMAP_FRAME, PIPELINE_PATH, pipeline_arch
from .receipts import Ledger, sha256_text

PAGE_CYCLES = ("OFF", "integrity", "ON", "FULL SHUTDOWN", "MEMORIAL")
SITE_STATES = PAGE_CYCLES
LOCKED_STATES = ("OFF", "integrity", "FULL SHUTDOWN", "MEMORIAL")
CYCLE_POSTURES = PAGE_CYCLES
MODULES = ("azhome", "hold", "withdraw", "witness")
WITNESS_CAP = 64
LABEL_CAP = 160
ID_CAP = 80

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
    "pipeline_arch",
    "hold",
    "withdraw",
    "scorch_local",
    "pair_offer",
    "pair_accept",
    "pair_seal",
    "pair_cut",
    "pair_status",
)

STUB_OPS = (
    "scorch_remote",
    "scorch",
    "pair_wipe",
    "deanonymize",
    "vault_read",
    "auto_unlock",
    "ranking",
    "completeness_detect",
    "unlock",
    "complete",
    "completeness",
    "rank",
    "skip_cycle",
    "invent_cycle",
)

FORBIDDEN_EVENT_KEYS = (
    "auto_unlock",
    "autounlock",
    "autoUnlock",
    "unlock_auto",
    "completeness",
    "completeness_detect",
    "completeness_event",
    "complete_event",
    "ranking",
    "rank",
    "scorch_remote",
    "scorch",
    "skip_cycle",
    "invent_cycle",
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
    "pipeline": "pipeline_arch",
    "arch": "pipeline_arch",
    "integrity": "integrity_check",
    "offer": "pair_offer",
    "accept": "pair_accept",
    "seal": "pair_seal",
    "cut": "pair_cut",
    "pair": "pair_status",
    "wipe_pair": "pair_wipe",
    "pair_remote_wipe": "pair_wipe",
}

PAIR_CAP = 64
QNS_VIA_ALIASES = {
    "bluetooth": "bt",
    "loopback": "local",
    "localhost": "local",
}


def normalize_via(raw: Any) -> str | None:
    """Sealed QNS-CD vias only. Empty defaults to local (qnsd loopback)."""
    if raw is None or raw == "":
        return "local"
    text = str(raw).strip().lower().replace("_", "-")
    text = QNS_VIA_ALIASES.get(text, text)
    if text in QNS_VIAS:
        return text
    return None


def qns_cross_map() -> dict[str, Any]:
    return {
        "spec": QNS_CD,
        "handshake": AIH_PAIR,
        "handshake_steps": list(PAIR_STEPS),
        "ops": ["pair_offer", "pair_accept", "pair_seal", "pair_cut", "pair_status"],
        "vias": list(QNS_VIAS),
        "walker_restricted": True,
        "packet": "QNS1",
        "via_runs_in": "qnsd",
        "qnsd": QNSD_BIND,
        "canonical": QNM_NODE,
        "doc": QNS_DOC,
        "catalog": "azinterface",
        "softwares_tab_qns": False,
        "mesh": QNM_BUILD,
        "mesh_default": "OFF",
        "get_enables_mesh": False,
        "node_gate": False,
        "untraceable_origin": False,
        "remote_wipe": False,
        "vault_contents": False,
        "pair_memorial": "azinterface custody",
        "note": "Vias run in local qnsd (127.0.0.1). Interface holds pair memorial cites only.",
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
    """Accept AIH-WP-1.0 cycle names plus Worker UI aliases (FULL_SHUTDOWN)."""
    return normalize_cycle(raw)


def normalize_cycle(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if text in PAGE_CYCLES:
        return text
    folded = text.lower().replace("_", " ").replace("-", " ")
    folded = " ".join(folded.split())
    aliases = {
        "off": "OFF",
        "offline": "OFF",
        "integrity": "integrity",
        "on": "ON",
        "online": "ON",
        "full shutdown": "FULL SHUTDOWN",
        "fullshutdown": "FULL SHUTDOWN",
        "full stop": "FULL SHUTDOWN",
        "shutdown": "FULL SHUTDOWN",
        "memorial": "MEMORIAL",
        "mem": "MEMORIAL",
    }
    return aliases.get(folded)


def cycle_index(name: str) -> int:
    try:
        return PAGE_CYCLES.index(name)
    except ValueError:
        return -1


def detect_forbidden_event(payload: dict[str, Any] | None) -> dict[str, str] | None:
    src = payload if isinstance(payload, dict) else {}
    for key in FORBIDDEN_EVENT_KEYS:
        if key not in src:
            continue
        val = src[key]
        if val is False or val is None or val == "":
            continue
        if key in ("ranking", "rank"):
            return {"kind": "ranking", "key": key, "code": "AIH-RANKING-REFUSE"}
        if key in ("scorch_remote", "scorch"):
            return {"kind": "scorch_remote", "key": key, "code": "AIH-SCORCH-REFUSE"}
        if "complete" in key:
            return {"kind": "completeness", "key": key, "code": "AIH-COMPLETENESS-REFUSE"}
        if key in ("skip_cycle", "invent_cycle"):
            return {"kind": "cycle_skip", "key": key, "code": "AIH-CYCLE-LOCKED"}
        return {"kind": "auto_unlock", "key": key, "code": "AIH-AUTO-UNLOCK-REFUSE"}
    banned = re.compile(
        r"\b(auto[-_ ]?unlock|completeness([-_ ]detect|[-_ ]?event)?|rank(ing)?|"
        r"scorch([-_ ]remote)?|skip[-_ ]cycle|invent[-_ ]cycle)\b",
        re.I,
    )
    for val in src.values():
        if not isinstance(val, str) or not banned.search(val):
            continue
        text = val.lower()
        if "complete" in text:
            return {"kind": "completeness", "key": "text", "code": "AIH-COMPLETENESS-REFUSE"}
        if "rank" in text:
            return {"kind": "ranking", "key": "text", "code": "AIH-RANKING-REFUSE"}
        if "scorch" in text:
            return {"kind": "scorch_remote", "key": "text", "code": "AIH-SCORCH-REFUSE"}
        if "skip" in text or "invent" in text:
            return {"kind": "cycle_skip", "key": "text", "code": "AIH-CYCLE-LOCKED"}
        return {"kind": "auto_unlock", "key": "text", "code": "AIH-AUTO-UNLOCK-REFUSE"}
    return None


class Engine:
    """In-process custodial engine. Optional JSONL receipts + companion state file."""

    def __init__(
        self,
        ledger: Ledger | None = None,
        state_path: str | Path | None = None,
    ) -> None:
        self.ledger = ledger or Ledger()
        self.state_path = Path(state_path) if state_path else None
        self.cycle_index = 0
        self.integrity_ok = False
        self.integrity_ts: str | None = None
        self.integrity_digest: str | None = None
        self.genesis_hash: str | None = None
        self.genesis_keyed = False
        self.holds: list[dict[str, Any]] = []
        self.witnesses: list[dict[str, Any]] = []
        self.pairs: list[dict[str, Any]] = []
        self._load_state()

    @property
    def site_state(self) -> str:
        return PAGE_CYCLES[self.cycle_index]

    def _load_state(self) -> None:
        if not self.state_path or not self.state_path.exists():
            return
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        idx = data.get("cycle_index")
        if isinstance(idx, int) and 0 <= idx < len(PAGE_CYCLES):
            self.cycle_index = idx
        self.integrity_ok = bool(data.get("integrity_ok"))
        self.integrity_ts = data.get("integrity_ts")
        self.integrity_digest = data.get("integrity_digest")
        self.genesis_hash = data.get("genesis_hash")
        self.genesis_keyed = bool(data.get("genesis_keyed"))
        if isinstance(data.get("holds"), list):
            self.holds = list(data["holds"])
        if isinstance(data.get("witnesses"), list):
            self.witnesses = list(data["witnesses"])
        if isinstance(data.get("pairs"), list):
            self.pairs = list(data["pairs"])

    def _save_state(self) -> None:
        if not self.state_path:
            return
        payload = {
            "cycle_index": self.cycle_index,
            "integrity_ok": self.integrity_ok,
            "integrity_ts": self.integrity_ts,
            "integrity_digest": self.integrity_digest,
            "genesis_hash": self.genesis_hash,
            "genesis_keyed": self.genesis_keyed,
            "holds": self.holds,
            "witnesses": self.witnesses,
            "pairs": self.pairs,
        }
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

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
            "qns": qns_cross_map(),
            "pipeline": pipeline_arch(),
        }
        out.update(extra)
        return out

    def living_presence(self) -> bool:
        return self.site_state == "ON" and self.integrity_ok is True

    def cycle_posture(self) -> str:
        return self.site_state

    def cycle_view(self) -> dict[str, Any]:
        current = self.site_state
        nxt = PAGE_CYCLES[self.cycle_index + 1] if self.cycle_index < len(PAGE_CYCLES) - 1 else None
        return {
            "pre_locked": True,
            "locked_order": True,
            "skip_forbidden": True,
            "invent_forbidden": True,
            "auto_unlock": False,
            "cycles": list(PAGE_CYCLES),
            "current": current,
            "index": self.cycle_index,
            "next": nxt,
            "terminal": current == "MEMORIAL",
        }

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
        view = self.cycle_view()
        living = self.living_presence()
        return {
            "site_state": self.site_state,
            "cycle": view["current"],
            "current": view["current"],
            "cycle_index": self.cycle_index,
            "cycles": list(PAGE_CYCLES),
            "cycle_path": "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL",
            "page_cycle": view,
            "OFF": view["current"] == "OFF",
            "integrity": view["current"] == "integrity",
            "ON": view["current"] == "ON",
            "FULL SHUTDOWN": view["current"] == "FULL SHUTDOWN",
            "MEMORIAL": view["current"] == "MEMORIAL",
            "locked": not living,
            "pre_locked": True,
            "living_presence": living,
            "integrity_ok": self.integrity_ok,
            "integrity_ts": self.integrity_ts,
            "genesis_keyed": self.genesis_keyed,
            "genesis_hash": self.genesis_hash,
            "genesis_sealed": True,
            "cloud_asleep": False,
            "auto_unlock": False,
            "completeness": False,
            "ranking": False,
            "separate_from": "azhub",
            "modules": {name: self.module_surface(name) for name in MODULES},
            "pipeline": pipeline_arch(),
            "pipeline_path": PIPELINE_PATH,
            "note": (
                "Living presence enabled."
                if living
                else "AIH-WP-1.0 pre-locked page cycles: OFF / integrity / ON / FULL SHUTDOWN / MEMORIAL. One step only. No skip. No cloud-asleep availability."
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
                    ("qns_cd", QNS_CD),
                    ("qnsd", QNSD_BIND),
                    ("pipeline_owner", "aziel-runtime"),
                    ("lambgate", False),
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
        view = self.cycle_view()
        return self._base(
            ok=True,
            keyed=self.genesis_keyed,
            genesis_keyed=self.genesis_keyed,
            genesis_hash=self.genesis_hash,
            genesis_sealed=True,
            cycles_sealed=True,
            cycles=list(PAGE_CYCLES),
            page_cycle=view,
            username_stored=False,
            one_time=True,
            receipt=rec,
            display=display_of(
                "Genesis status",
                "Five page cycles sealed at genesis. Username hash is one-time and never stored.",
                [
                    ("keyed", self.genesis_keyed),
                    ("genesis_hash", self.genesis_hash or ""),
                    ("genesis_sealed", True),
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
        self._save_state()
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
        wanted = normalize_cycle(
            payload.get("cycle") or payload.get("state") or payload.get("site_state") or payload.get("page_cycle") or payload.get("to")
        )
        if not wanted:
            return self._base(
                ok=False,
                code="AIH-CYCLE-UNKNOWN",
                refused=True,
                error="Only the five pre-locked cycles are accepted: OFF, integrity, ON, FULL SHUTDOWN, MEMORIAL.",
                allowed=list(PAGE_CYCLES),
                site_state=self.site_state,
                current=self.site_state,
                page_cycle=self.cycle_view(),
            )
        target = cycle_index(wanted)
        current = self.cycle_index
        if target == current:
            rec = self._receipt("site_state_set", {"unchanged": wanted})
            cycle = self.page_cycle_snapshot()
            return self._base(
                ok=True,
                unchanged=True,
                site_state=self.site_state,
                current=self.site_state,
                living_presence=cycle["living_presence"],
                cycle=cycle,
                page_cycle=cycle["page_cycle"],
                receipt=rec,
                display=display_of("Site state unchanged", f"Already {wanted}.", [("current", wanted)]),
            )
        if PAGE_CYCLES[current] == "MEMORIAL":
            rec = self._receipt("site_state_set_refused", {"wanted": wanted, "reason": "terminal"})
            return self._base(
                ok=False,
                code="AIH-CYCLE-TERMINAL",
                refused=True,
                error="MEMORIAL is terminal. Page cycles stay pre-locked.",
                site_state=self.site_state,
                current=self.site_state,
                living_presence=False,
                page_cycle=self.cycle_view(),
                receipt=rec,
                display=display_of("Memorial is terminal", "Cannot leave MEMORIAL. Cycles stay pre-locked."),
            )
        if target != current + 1:
            rec = self._receipt("site_state_set_refused", {"wanted": wanted, "reason": "locked_order"})
            view = self.cycle_view()
            return self._base(
                ok=False,
                code="AIH-CYCLE-LOCKED",
                refused=True,
                error="Pre-locked cycles advance one step only. Auto-unlock / skip / invent stay refused.",
                requested=wanted,
                site_state=self.site_state,
                current=self.site_state,
                living_presence=False,
                need_integrity=wanted == "ON" and not self.integrity_ok,
                page_cycle=view,
                receipt=rec,
                display=display_of(
                    "Cycle locked",
                    "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL. One step only.",
                    [("current", self.site_state), ("requested", wanted), ("next", view["next"] or "")],
                ),
            )
        if wanted == "ON" and not self.integrity_ok:
            rec = self._receipt("site_state_set_refused", {"wanted": "ON", "reason": "need_integrity"})
            return self._base(
                ok=False,
                code="AIH-INTEGRITY-REQUIRED",
                refused=True,
                error="ON requires a passing integrity_check. Auto-unlock is refused.",
                site_state=self.site_state,
                current=self.site_state,
                living_presence=False,
                need_integrity=True,
                page_cycle=self.cycle_view(),
                receipt=rec,
                display=display_of(
                    "Integrity required",
                    "ON requires a passing integrity check. Integrity does not auto-unlock to ON.",
                    [("site_state", self.site_state), ("integrity_ok", False)],
                ),
            )
        prev = self.site_state
        self.cycle_index = target
        rec = self._receipt("site_state_set", {"from": prev, "to": wanted, "living": self.living_presence()})
        self._save_state()
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            advanced=True,
            site_state=self.site_state,
            current=self.site_state,
            previous=prev,
            living_presence=cycle["living_presence"],
            cycle=cycle,
            page_cycle=cycle["page_cycle"],
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
            rec = self._receipt("integrity_fail", {"ok": False})
            return self._base(
                ok=False,
                code="INTEGRITY_FAIL",
                integrity_ok=False,
                living_presence=False,
                site_state=self.site_state,
                current=self.site_state,
                page_cycle=self.cycle_view(),
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
        witness_id = str(payload.get("witness") or payload.get("witness_id") or payload.get("id") or "").strip()[:ID_CAP]
        label = str(payload.get("label") or payload.get("note") or "").strip()[:LABEL_CAP]
        if witness_id and len(self.witnesses) < WITNESS_CAP and not any(w.get("id") == witness_id for w in self.witnesses):
            self.witnesses.append(
                {
                    "id": witness_id,
                    "kind": "integrity",
                    "label": label or witness_id,
                    "hold_id": None,
                    "hash": digest,
                    "ts": self.integrity_ts,
                    "vault_contents": False,
                }
            )
        if self.site_state == "OFF":
            self.cycle_index = cycle_index("integrity")
        rec = self._receipt("integrity_check", {"ok": True, "digest_prefix": digest[:16]})
        self._save_state()
        cycle = self.page_cycle_snapshot()
        return self._base(
            ok=True,
            integrity_ok=True,
            integrity_digest=digest,
            integrity_ts=self.integrity_ts,
            site_state=self.site_state,
            current=self.site_state,
            living_presence=cycle["living_presence"],
            cycle=cycle,
            page_cycle=cycle["page_cycle"],
            witnesses=len(self.witnesses),
            receipt=rec,
            display=display_of(
                "Integrity passed",
                "Integrity recorded. Does not auto-unlock to ON.",
                [("integrity_ok", True), ("current", self.site_state), ("digest", digest)],
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
                    ("current", cycle["current"]),
                    ("cycle", cycle["cycle"]),
                    ("living_presence", cycle["living_presence"]),
                    ("next", (cycle["page_cycle"] or {}).get("next") or ""),
                    ("cloud_asleep", False),
                    ("pipeline", cycle.get("pipeline_path") or PIPELINE_PATH),
                    ("4dmap", FOURDMAP_FRAME),
                ],
            ),
        )

    def pipeline_arch(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("pipeline_arch", {"locked": True})
        pipe = pipeline_arch()
        return self._base(
            ok=True,
            **pipe,
            receipt=rec,
            display=display_of(
                "LOCKED pipeline",
                pipe["note"],
                [
                    ("path", pipe["path"]),
                    ("owner", pipe["owner"]),
                    ("lambgate", False),
                    ("4dmap", FOURDMAP_FRAME),
                    ("software_tab", False),
                ],
            ),
        )

    def _witness_row(self, kind: str, hold_id: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        extra = extra or {}
        rec = self._receipt(kind, {"hold_id": hold_id, **extra})
        row = {
            "kind": kind,
            "hold_id": hold_id,
            "hash": rec["hash"],
            "ts": rec["ts"],
            "seq": rec["seq"],
            "vault_contents": False,
        }
        pair_id = extra.get("pair_id")
        photon_id = extra.get("photon_id")
        if pair_id:
            row["pair_id"] = pair_id
        if photon_id:
            row["photon_id"] = photon_id
        self.witnesses.append(row)
        return row

    def _cite_ids(self, payload: dict[str, Any]) -> tuple[str, str]:
        pair_id = str(payload.get("pair_id") or payload.get("pair") or "").strip()[:ID_CAP]
        photon_id = str(payload.get("photon_id") or payload.get("photon") or "").strip()[:ID_CAP]
        return pair_id, photon_id

    def _pair_public(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "pair_id": row.get("pair_id"),
            "photon_id": row.get("photon_id"),
            "via": row.get("via"),
            "handshake": row.get("handshake"),
            "walker_restricted": True,
            "packet": "QNS1",
            "via_runs_in": "qnsd",
            "qnsd": QNSD_BIND,
            "spec": QNS_CD,
            "handshake_spec": AIH_PAIR,
            "vault_contents": False,
            "remote_wipe": False,
            "untraceable_origin": False,
            "transferred": False,
        }

    def _find_pair(self, pair_id: str) -> dict[str, Any] | None:
        if not pair_id:
            return None
        for row in self.pairs:
            if row.get("pair_id") == pair_id:
                return row
        return None

    def _latest_pair(self, handshake: str | None = None) -> dict[str, Any] | None:
        for row in reversed(self.pairs):
            if handshake is None or row.get("handshake") == handshake:
                return row
        return None

    def _pair_cycle_refuse(self, op: str) -> dict[str, Any] | None:
        current = self.site_state
        if self.living_presence():
            return None
        if current == "MEMORIAL":
            rec = self._receipt(f"{op}_refused", {"reason": "memorial"})
            return self._base(
                ok=False,
                code="AIH-CYCLE-TERMINAL",
                refused=True,
                error="MEMORIAL is terminal. Pair memorial cites remain readable; pair mutate is refused.",
                living_presence=False,
                site_state=current,
                current=current,
                qns_cd=QNS_CD,
                receipt=rec,
                display=display_of("Memorial is terminal", "QNS pair mutate does not run in MEMORIAL. pair_status still reads cites."),
            )
        if current == "FULL SHUTDOWN":
            rec = self._receipt(f"{op}_refused", {"reason": "full_shutdown"})
            return self._base(
                ok=False,
                code="QNS-CYCLE-REFUSE",
                refused=True,
                error="QNS pair ops require living presence (ON after integrity). FULL SHUTDOWN refuses pair mutate.",
                living_presence=False,
                site_state=current,
                current=current,
                qns_cd=QNS_CD,
                receipt=rec,
                display=display_of("Cycle refuses pair", "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL. Pair mutate only at ON."),
            )
        rec = self._receipt(f"{op}_refused", {"reason": "pre_locked"})
        return self._base(
            ok=False,
            code="PRE_LOCKED",
            error="QNS pair ops are living-presence acts. Enable ON after integrity.",
            living_presence=False,
            site_state=current,
            receipt=rec,
            display=display_of("Pre-locked", "pair_offer / pair_accept / pair_seal / pair_cut do not run until ON after integrity."),
        )

    def _via_or_refuse(self, payload: dict[str, Any], existing: str | None = None) -> tuple[str | None, dict[str, Any] | None]:
        raw = payload.get("via") if "via" in payload else payload.get("bearer")
        if raw is None or raw == "":
            return existing or "local", None
        via = normalize_via(raw)
        if via is None:
            return None, self._base(
                ok=False,
                code="QNS-VIA-UNKNOWN",
                refused=True,
                error="Walker restriction: only lan/plc/bt/rf/light/qns/operator/local. Vias run in local qnsd.",
                allowed=list(QNS_VIAS),
                walker_restricted=True,
                via_runs_in="qnsd",
                qnsd=QNSD_BIND,
                display=display_of("Via refused", "Unknown via. Walker cannot invent a hop.", [("allowed", ",".join(QNS_VIAS))]),
            )
        if existing and via != existing:
            return None, self._base(
                ok=False,
                code="QNS-WALKER-RESTRICT",
                refused=True,
                error="Walker restriction: via cannot change mid-handshake. qnsd owns the hop; Interface cites one via.",
                via=existing,
                requested=via,
                walker_restricted=True,
                via_runs_in="qnsd",
                qnsd=QNSD_BIND,
                display=display_of("Walker restricted", "Via is sealed on offer. Packet hops stay in local qnsd.", [("via", existing), ("requested", via)]),
            )
        return via, None

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
        pair_id, photon_id = self._cite_ids(payload)
        row = {
            "hold_id": hold_id,
            "label_hash": label_hash,
            "status": "held",
            "vault_contents": False,
        }
        if pair_id:
            row["pair_id"] = pair_id
        if photon_id:
            row["photon_id"] = photon_id
        self.holds.append(row)
        extra = {"label_hash": label_hash}
        if pair_id:
            extra["pair_id"] = pair_id
        if photon_id:
            extra["photon_id"] = photon_id
        witness = self._witness_row("hold", hold_id, extra)
        self._save_state()
        fields = [("hold_id", hold_id), ("status", "held"), ("vault_contents", False)]
        if pair_id:
            fields.append(("pair_id", pair_id))
        if photon_id:
            fields.append(("photon_id", photon_id))
        return self._base(
            ok=True,
            hold=row,
            witness=witness,
            vault_contents=False,
            display=display_of(
                "Hold",
                "Custody hold recorded. Label hashed. Pair/photon cites only — vault contents not stored.",
                fields,
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
        self._save_state()
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

    def pair_offer(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        gated = self._pair_cycle_refuse("pair_offer")
        if gated:
            return gated
        via, via_err = self._via_or_refuse(payload)
        if via_err:
            return via_err
        if len(self.pairs) >= PAIR_CAP:
            return self._base(ok=False, code="PAIR_CAP", error="Pair memorial cap reached. Witness list is metadata only.")
        pair_id, photon_id = self._cite_ids(payload)
        if not pair_id:
            seed = sha256_text(f"azinterface|qns|{QNS_CD}|{via}|{self.ledger.tip}|{len(self.pairs)}")
            pair_id = "pair-" + seed[:12]
        if self._find_pair(pair_id):
            return self._base(
                ok=False,
                code="PAIR_EXISTS",
                error="pair_id already memorialized. Use pair_accept / pair_seal / pair_cut.",
                pair_id=pair_id,
            )
        if not photon_id:
            photon_id = "qns1-" + sha256_text(f"azinterface|photon|{pair_id}|{via}")[:12]
        row = {
            "pair_id": pair_id,
            "photon_id": photon_id,
            "via": via,
            "handshake": "OFFER",
            "vault_contents": False,
        }
        self.pairs.append(row)
        witness = self._witness_row("pair_offer", None, {"pair_id": pair_id, "photon_id": photon_id, "via": via})
        self._save_state()
        pub = self._pair_public(row)
        return self._base(
            ok=True,
            pair=pub,
            handshake="OFFER",
            witness=witness,
            vault_contents=False,
            remote_wipe=False,
            display=display_of(
                "Pair OFFER",
                "AIH-WP-1.3 offer recorded. QNS1 via cite only — qnsd on 127.0.0.1 runs the hop.",
                [("pair_id", pair_id), ("photon_id", photon_id), ("via", via or ""), ("handshake", "OFFER")],
            ),
        )

    def pair_accept(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        gated = self._pair_cycle_refuse("pair_accept")
        if gated:
            return gated
        pair_id, _photon = self._cite_ids(payload)
        target = self._find_pair(pair_id) if pair_id else self._latest_pair("OFFER")
        if not target:
            return self._base(
                ok=False,
                code="PAIR_NOT_FOUND",
                error="No matching OFFER. pair_status lists pair_id cites only — never vault contents.",
                vault_contents=False,
            )
        if target.get("handshake") != "OFFER":
            return self._base(
                ok=False,
                code="QNS-HANDSHAKE-LOCKED",
                refused=True,
                error="AIH-WP-1.3 handshake is OFFER → ACCEPT → SEAL. Accept only from OFFER.",
                pair=self._pair_public(target),
                display=display_of("Handshake locked", "Accept only from OFFER.", [("handshake", target.get("handshake") or "")]),
            )
        _via, via_err = self._via_or_refuse(payload, existing=target.get("via"))
        if via_err:
            return via_err
        photon_cite = _photon or target.get("photon_id")
        if photon_cite:
            target["photon_id"] = photon_cite
        target["handshake"] = "ACCEPT"
        witness = self._witness_row("pair_accept", None, {"pair_id": target["pair_id"], "photon_id": target.get("photon_id"), "via": target.get("via")})
        self._save_state()
        pub = self._pair_public(target)
        return self._base(
            ok=True,
            pair=pub,
            handshake="ACCEPT",
            witness=witness,
            vault_contents=False,
            remote_wipe=False,
            display=display_of(
                "Pair ACCEPT",
                "AIH-WP-1.3 accept recorded. Via still cited; qnsd runs the packet.",
                [("pair_id", target["pair_id"]), ("photon_id", target.get("photon_id") or ""), ("handshake", "ACCEPT")],
            ),
        )

    def pair_seal(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        gated = self._pair_cycle_refuse("pair_seal")
        if gated:
            return gated
        pair_id, _photon = self._cite_ids(payload)
        target = self._find_pair(pair_id) if pair_id else self._latest_pair("ACCEPT")
        if not target:
            return self._base(
                ok=False,
                code="PAIR_NOT_FOUND",
                error="No matching ACCEPT. Seal only after accept. Witness list is metadata only.",
                vault_contents=False,
            )
        if target.get("handshake") != "ACCEPT":
            return self._base(
                ok=False,
                code="QNS-HANDSHAKE-LOCKED",
                refused=True,
                error="AIH-WP-1.3 handshake is OFFER → ACCEPT → SEAL. Seal only from ACCEPT.",
                pair=self._pair_public(target),
                display=display_of("Handshake locked", "Seal only from ACCEPT.", [("handshake", target.get("handshake") or "")]),
            )
        _via, via_err = self._via_or_refuse(payload, existing=target.get("via"))
        if via_err:
            return via_err
        target["handshake"] = "SEAL"
        witness = self._witness_row("pair_seal", None, {"pair_id": target["pair_id"], "photon_id": target.get("photon_id"), "via": target.get("via")})
        self._save_state()
        pub = self._pair_public(target)
        return self._base(
            ok=True,
            pair=pub,
            handshake="SEAL",
            witness=witness,
            memorial=True,
            vault_contents=False,
            remote_wipe=False,
            display=display_of(
                "Pair SEAL",
                "Pair memorial sealed. Interface holds cites only. qnsd on 127.0.0.1 owns the via.",
                [("pair_id", target["pair_id"]), ("photon_id", target.get("photon_id") or ""), ("handshake", "SEAL")],
            ),
        )

    def pair_cut(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        gated = self._pair_cycle_refuse("pair_cut")
        if gated:
            return gated
        pair_id, _photon = self._cite_ids(payload)
        target = self._find_pair(pair_id) if pair_id else None
        if not target:
            for row in reversed(self.pairs):
                if row.get("handshake") != "CUT":
                    target = row
                    break
        if not target:
            return self._base(
                ok=False,
                code="PAIR_NOT_FOUND",
                error="No living pair to cut. Cut is a dissolve — not a remote wipe.",
                vault_contents=False,
                remote_wipe=False,
            )
        if target.get("handshake") == "CUT":
            rec = self._receipt("pair_cut", {"unchanged": target["pair_id"]})
            return self._base(
                ok=True,
                unchanged=True,
                pair=self._pair_public(target),
                handshake="CUT",
                remote_wipe=False,
                receipt=rec,
                display=display_of("Pair already cut", "Memorial cite remains. No remote wipe.", [("pair_id", target["pair_id"])]),
            )
        prev = target.get("handshake")
        target["handshake"] = "CUT"
        witness = self._witness_row("pair_cut", None, {"pair_id": target["pair_id"], "photon_id": target.get("photon_id"), "from": prev})
        self._save_state()
        pub = self._pair_public(target)
        return self._base(
            ok=True,
            pair=pub,
            handshake="CUT",
            previous=prev,
            witness=witness,
            vault_contents=False,
            remote_wipe=False,
            local_only=True,
            display=display_of(
                "Pair CUT",
                "Pair dissolved. Memorial cite kept. Hosted Worker never remotely wipes devices.",
                [("pair_id", target["pair_id"]), ("from", prev or ""), ("remote_wipe", False)],
            ),
        )

    def pair_status(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = self._receipt("pair_status", {"count": len(self.pairs)})
        rows = [self._pair_public(p) for p in self.pairs]
        return self._base(
            ok=True,
            pairs=rows,
            count=len(rows),
            vault_contents=False,
            remote_wipe=False,
            living_presence=self.living_presence(),
            site_state=self.site_state,
            receipt=rec,
            display=display_of(
                "Pair memorial",
                "QNS-CD pair cites only. Vias run in local qnsd. Vault contents are never listed.",
                [("count", len(rows)), ("qnsd", QNSD_BIND), ("vault_contents", False), ("softwares_tab_qns", False)],
            ),
        )

    def pair_wipe(self, _payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._stub("pair_wipe")

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
            "pair_wipe": "Pair cut is a local dissolve of memorial cites. Hosted Worker never remotely wipes user devices.",
            "deanonymize": "AZInterface does not deanonymize. Identity is Aziel Eliab only.",
            "vault_read": "Hosted Worker never serves vault contents. Witness list is metadata only.",
            "auto_unlock": "Auto-unlock is refused. Cycles advance one explicit step only.",
            "unlock": "Unlock is refused. ON requires integrity, then an explicit site_state_set.",
            "ranking": "AZInterface does not rank. Witness list is metadata only.",
            "rank": "AZInterface does not rank. Witness list is metadata only.",
            "completeness_detect": "Completeness detection is refused. Hub/Interface stay separate software.",
            "complete": "Completeness is refused.",
            "completeness": "Completeness is refused.",
            "skip_cycle": "Skip is refused. Cycles are sealed: OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL.",
            "invent_cycle": "Invented cycles are refused. Only the five sealed AIH-WP-1.0 cycles exist.",
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

    def _forbidden(self, hit: dict[str, str], op: str) -> dict[str, Any]:
        rec = self._receipt("forbidden_refuse", {"op": op, "event": hit["kind"]})
        return self._base(
            ok=False,
            code=hit["code"],
            refused=True,
            event=hit["kind"],
            op=op,
            site_state=self.site_state,
            current=self.site_state,
            cycles=list(PAGE_CYCLES),
            page_cycle=self.cycle_view(),
            receipt=rec,
            display=display_of("Refused", hit["code"], [("op", op), ("event", hit["kind"])]),
        )

    def dispatch(self, op: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        hit = detect_forbidden_event(payload)
        if hit:
            out = self._forbidden(hit, str(op or ""))
            self._save_state()
            return out
        name = str(op or "").strip().lower().replace("-", "_")
        name = ALIASES.get(name, name)
        if name in STUB_OPS:
            out = self._stub(name)
            self._save_state()
            return out
        if name not in LIVE_OPS:
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
        out = handler(payload)
        self._save_state()
        return out
