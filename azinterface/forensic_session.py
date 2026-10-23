"""AZInterface tether for AZBot Node Collaborative Forensic Design 1.0.

The local desk (127.0.0.1) keeps the sealed page cycles, packages a FragGate
call for AZBot at 127.0.0.1, and shares session tips. It does not send that
call, open a public port, enable mesh radios, or add a door.

AZBot owns the azbot repository. Softwares OVERRIDE is a separate change.
The public worker cites this contract and stores no session.

Author: Aziel Eliab. Apache-2.0.
"""

from __future__ import annotations

import re
from typing import Any

from .engine import PAGE_CYCLES, detect_forbidden_event, display_of
from .meta import FRAGGATE_CALL, LOOPBACK
from .receipts import sha256_text

SPEC = "AZBOT-NODE-COLLABORATIVE-FORENSIC-1.0"
AZBOT_BIND = LOOPBACK
ZERO = "0" * 64
SESSION_CAP = 64
PARTY_CAP = 16
CAP7_SENTENCE = "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP."

REMAIN_OFF = {
    "mesh_auto_enable": False,
    "get_v1_mesh_enables": False,
    "azos_public_exec": False,
    "vault_destructive_public": False,
    "deanonymize": False,
    "invent_mark": False,
    "backdate": False,
    "public_rollback": False,
    "second_public_door": False,
    "radios_enabled": False,
    "cap7_is_icann": False,
}

_HEX = re.compile(r"^[a-f0-9]{64}$")
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_OP = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_NAME_ONLY = {"cap7", "cap-7", "icann", "cap7-egress"}
_USERNAME_KEYS = {"username", "user_name", "user"}
_REMAIN_KEYS = {
    "deanonymize",
    "invent_mark",
    "backdate",
    "rollback",
    "public_rollback",
    "scorch",
    "scorch_remote",
    "wipe",
    "unlock",
    "shell",
    "exec",
    "vault",
    "vault_read",
    "mesh_enable",
    "auto_enable",
}


def name_only(value: Any) -> bool:
    """Cap-7, ICANN, and .aziel are names. They are not an exit."""
    raw = str(value or "").strip().lower()
    if not raw:
        return False
    if _name_only_text(raw):
        return True
    host = raw
    if "://" in raw:
        host = raw.split("://", 1)[1].split("/", 1)[0].split("@")[-1].split(":")[0]
    return _name_only_text(host.strip("[]"))


def _name_only_text(raw: str) -> bool:
    compact = raw.replace("_", "-")
    return compact in _NAME_ONLY or raw.endswith(".aziel")


def _walk(value: Any, depth: int = 0):
    if depth > 4:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), item
            yield from _walk(item, depth + 1)
    elif isinstance(value, list):
        for item in value[:32]:
            yield from _walk(item, depth + 1)


def _username_present(payload: dict[str, Any]) -> bool:
    for key, item in _walk(payload):
        if key.lower().replace("-", "_") in _USERNAME_KEYS and item not in (None, "", False):
            return True
    return False


def _remain_off_key(payload: dict[str, Any]) -> str | None:
    for key, item in _walk(payload):
        folded = key.lower().replace("-", "_")
        if folded in _REMAIN_KEYS and item not in (None, "", False):
            return folded
    return None


def _name_only_payload(payload: dict[str, Any]) -> bool:
    for key, item in _walk(payload):
        if name_only(key) or (isinstance(item, str) and name_only(item)):
            return True
    return False


def admission(cycle: dict[str, Any] | None) -> tuple[bool, str | None, str]:
    """Handoff and tip append follow the sealed cycle. One step. No skip."""
    src = cycle if isinstance(cycle, dict) else {}
    current = str(src.get("current") or src.get("site_state") or src.get("cycle") or "OFF")
    if current not in PAGE_CYCLES:
        current = "OFF"
    living = src.get("living_presence") is True and current == "ON" and src.get("integrity_ok") is True
    if living:
        return True, None, current
    if current == "MEMORIAL":
        return False, "AIH-CYCLE-TERMINAL", current
    if current == "FULL SHUTDOWN":
        return False, "AIH-CYCLE-REFUSE", current
    return False, "PRE_LOCKED", current


def _bearer(authorization: str | None, payload: dict[str, Any]) -> str:
    header = str(authorization or "")
    matched = re.match(r"^Bearer\s+(\S+)\s*$", header, re.I)
    if matched:
        return matched.group(1)
    for key in ("bearer", "token"):
        raw = payload.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return ""


class ForensicDesk:
    """In-process multi-party tip ledger. Tips are hashes. Payloads are not kept."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, Any]] = {}

    def reset(self) -> None:
        self.sessions.clear()

    def _frame(self) -> dict[str, Any]:
        return {
            "spec": SPEC,
            "author": "Aziel Eliab",
            "bind": AZBOT_BIND,
            "public_port": False,
            "door": "fraggate",
            "second_door": False,
            "agent_path": FRAGGATE_CALL,
            "executed": False,
            "stored_payload": False,
            "username_stored": False,
            "share_tips_only": True,
            "rewrite": False,
            "mesh_enabled": False,
            "radios_enabled": False,
            "cap7_names_only": True,
            "icann": False,
            "cap7_sentence": CAP7_SENTENCE,
            "remain_off": dict(REMAIN_OFF),
            "cycles": list(PAGE_CYCLES),
            "skip_forbidden": True,
            "cloud_asleep": False,
        }

    def _refuse(self, code: str, status: int, summary: str, **extra: Any) -> tuple[dict[str, Any], int]:
        body = self._frame()
        body.update(ok=False, code=code, written=False, admitted=False, **extra)
        body["display"] = display_of("AZInterface forensic tether", summary, [("code", code), ("door", "fraggate")])
        return body, status

    def _guard(self, payload: dict[str, Any]) -> tuple[dict[str, Any], int] | None:
        if _name_only_payload(payload):
            return self._refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE)
        if _username_present(payload):
            return self._refuse("USERNAME-NOT-STORED", 403, "A username is not stored.")
        hit = detect_forbidden_event(payload)
        if not hit:
            inner = payload.get("payload")
            hit = detect_forbidden_event(inner if isinstance(inner, dict) else None)
        if hit:
            return self._refuse(hit["code"], 403, "Remain-OFF. The sealed cycle does not take this event.")
        remain = _remain_off_key(payload)
        if remain:
            return self._refuse("REMAIN-OFF", 403, "Remain-OFF. This tether does not enable that verb.", event=remain)
        return None

    def handoff_cite(self, cycle: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
        admitted, code, current = admission(cycle)
        body = self._frame()
        body.update(
            ok=admitted,
            code=code or "FORENSIC-HANDOFF",
            admitted=admitted,
            written=False,
            page_cycle=current,
            living_presence=admitted,
            azbot="127.0.0.1",
            package=None,
            note=(
                "AZBot at 127.0.0.1 packages slug + op + payload as a FragGate call. "
                "Interface does not open that socket and does not send the call."
            ),
        )
        title = "Handoff admitted" if admitted else "Handoff waits on the page cycle"
        body["display"] = display_of(title, body["note"], [("page_cycle", current), ("bind", AZBOT_BIND)])
        return body, 200 if admitted else 403

    def package_handoff(self, payload: dict[str, Any] | None, cycle: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
        payload = payload if isinstance(payload, dict) else {}
        guarded = self._guard(payload)
        if guarded:
            return guarded
        host = payload.get("host") or payload.get("bind") or payload.get("url")
        if host not in (None, "", AZBOT_BIND, "localhost"):
            if name_only(host):
                return self._refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE)
            return self._refuse("AZBOT-BIND-LOOPBACK", 403, "AZBot handoff stays on 127.0.0.1.")
        admitted, code, current = admission(cycle)
        if not admitted:
            body, status = self._refuse(
                code or "PRE_LOCKED",
                403,
                "Handoff is admitted only at ON after integrity. The cycle was not advanced.",
            )
            body["page_cycle"] = current
            body["living_presence"] = False
            return body, status
        slug = str(payload.get("slug") or "").strip().lower()
        op = str(payload.get("op") or "").strip().lower()
        if not _SLUG.fullmatch(slug) or not _OP.fullmatch(op):
            return self._refuse("FORENSIC-INPUT", 400, "A handoff needs a FragGate slug and op.")
        inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        body = self._frame()
        body.update(
            ok=True,
            code="FORENSIC-HANDOFF",
            admitted=True,
            written=False,
            page_cycle=current,
            living_presence=True,
            azbot="127.0.0.1",
            package={
                "slug": slug,
                "op": op,
                "payload": inner,
                "payload_sha256": sha256_text(_canon_payload(inner)),
                "door": FRAGGATE_CALL,
            },
            note="Packaged for AZBot at 127.0.0.1. Interface did not send it.",
        )
        body["display"] = display_of(
            "FragGate package",
            body["note"],
            [("slug", slug), ("op", op), ("executed", False)],
        )
        return body, 200

    def read_tip(self, session_id: str | None = None) -> tuple[dict[str, Any], int]:
        if session_id is not None and name_only(session_id):
            return self._refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE)
        body = self._frame()
        body.update(ok=True, code="FORENSIC-TIP", written=False, stored_here=True)
        if session_id is None or session_id == "":
            body["sessions"] = [_public_row(row)["sessions"][0] for row in self.sessions.values()]
            body["tip"] = None
            body["display"] = display_of("Session tips", "Share tips only. A tip cannot be rewritten.", [("sessions", len(body["sessions"]))])
            return body, 200
        if not _ID.fullmatch(session_id):
            return self._refuse("FORENSIC-INPUT", 400, "session_id is a short local label.")
        row = self.sessions.get(session_id)
        if row is None:
            body.update(ok=False, code="FORENSIC-SESSION-ABSENT", sessions=[], tip=None, session_id=session_id)
            body["display"] = display_of("No session tip", "This desk has no tip for that session.", [("session_id", session_id)])
            return body, 404
        shown = _public_row(row)
        body.update(session_id=session_id, tip=shown["tip"], prev=shown["prev"], seq=shown["seq"], parties=shown["parties"], sessions=shown["sessions"])
        body["display"] = display_of("Session tip", "The tip is readable. It is not rewritten.", [("tip", row["tip"]), ("seq", row["seq"])])
        return body, 200

    def append_tip(self, payload: dict[str, Any] | None, cycle: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
        payload = payload if isinstance(payload, dict) else {}
        guarded = self._guard(payload)
        if guarded:
            return guarded
        if payload.get("rewrite") is True or payload.get("replace") is True:
            return self._refuse("TIP-REWRITE-REFUSED", 409, "Other parties can read the tip. They cannot rewrite it.")
        admitted, code, current = admission(cycle)
        if not admitted:
            body, status = self._refuse(code or "PRE_LOCKED", 403, "A tip is appended only at ON after integrity.")
            body["page_cycle"] = current
            return body, status
        session_id = str(payload.get("session_id") or "").strip().lower()
        if not _ID.fullmatch(session_id):
            return self._refuse("FORENSIC-INPUT", 400, "session_id is a short local label.")
        tip = str(payload.get("tip") or "").strip().lower()
        if not _HEX.fullmatch(tip):
            return self._refuse("FORENSIC-INPUT", 400, "tip is a 64-character receipt hash.")
        prev_raw = payload.get("prev")
        prev = ZERO if prev_raw in (None, "") else str(prev_raw).strip().lower()
        if not _HEX.fullmatch(prev):
            return self._refuse("FORENSIC-INPUT", 400, "prev is the previous tip hash.")
        party = payload.get("party")
        party_id = None
        if party not in (None, ""):
            party_id = str(party).strip().lower()
            if name_only(party_id):
                return self._refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE)
            if not _ID.fullmatch(party_id):
                return self._refuse("FORENSIC-INPUT", 400, "party is a short local label.")
        current_row = self.sessions.get(session_id)
        if current_row is None:
            if len(self.sessions) >= SESSION_CAP:
                return self._refuse("SESSION-CAP", 403, "The local tip ledger is at its session cap.")
            if prev != ZERO:
                return self._refuse("TIP-REWRITE-REFUSED", 409, "A new session starts at the zero tip. It does not rewrite one.")
            row = {
                "session_id": session_id,
                "tip": tip,
                "prev": ZERO,
                "seq": 1,
                "parties": [party_id] if party_id else [],
                "opened_cycle": current,
                "rewrite": False,
            }
            self.sessions[session_id] = row
            body = self._frame()
            body.update(ok=True, code="FORENSIC-TIP", written=True, admitted=True, page_cycle=current, **_public_row(row))
            body["display"] = display_of("Tip appended", "The session tip is shared. The payload was not stored.", [("tip", tip), ("seq", 1)])
            return body, 200
        if tip == current_row["tip"]:
            if party_id and party_id not in current_row["parties"]:
                if len(current_row["parties"]) >= PARTY_CAP:
                    return self._refuse("SESSION-CAP", 403, "The session is at its party cap.")
                current_row["parties"].append(party_id)
            body = self._frame()
            body.update(ok=True, code="FORENSIC-TIP", written=False, admitted=True, page_cycle=current, **_public_row(current_row))
            body["display"] = display_of("Tip unchanged", "The same tip was read. It was not rewritten.", [("tip", current_row["tip"])])
            return body, 200
        if prev != current_row["tip"]:
            return self._refuse("TIP-REWRITE-REFUSED", 409, "The tip links forward from the current tip. It is not replaced.", session_id=session_id, tip=current_row["tip"])
        if party_id and party_id not in current_row["parties"] and len(current_row["parties"]) >= PARTY_CAP:
            return self._refuse("SESSION-CAP", 403, "The session is at its party cap.")
        row = {
            "session_id": session_id,
            "tip": tip,
            "prev": current_row["tip"],
            "seq": current_row["seq"] + 1,
            "parties": list(current_row["parties"]),
            "opened_cycle": current_row["opened_cycle"],
            "rewrite": False,
        }
        if party_id and party_id not in row["parties"]:
            row["parties"].append(party_id)
        self.sessions[session_id] = row
        body = self._frame()
        body.update(ok=True, code="FORENSIC-TIP", written=True, admitted=True, page_cycle=current, **_public_row(row))
        body["display"] = display_of("Tip advanced", "The new tip links to the previous tip. The old tip was not replaced in place.", [("tip", tip), ("prev", row["prev"])])
        return body, 200

    def expose_tether(self, authorization: str | None, payload: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
        payload = payload if isinstance(payload, dict) else {}
        guarded = self._guard(payload)
        if guarded:
            guarded[0]["exposed"] = False
            return guarded
        token = _bearer(authorization, payload)
        if name_only(token):
            return self._refuse("MG-NO-IP-EXIT", 403, CAP7_SENTENCE, exposed=False)
        if not token:
            return self._refuse(
                "MESH-NEED-BEARER",
                401,
                "AzielTether is exposed under an operator bearer. Mesh radios stay off.",
                exposed=False,
            )
        body = self._frame()
        body.update(
            ok=True,
            code="AZIELTETHER-CITE",
            exposed=True,
            bearer="present",
            written=False,
            tether={
                "name": "AzielTether",
                "slug": "azieltether",
                "door": "fraggate",
                "under_bearer": True,
                "second_door": False,
                "spec": "AZRT-AZOS-TETHER-1.0",
            },
            anchors=["AZRT-AZOS-TETHER-1.0", "azieltether", "external-anchors-cite-only"],
            note="AzielTether is cited under bearer. The bearer is not stored. Radios stay off. FragGate stays the one door.",
        )
        body["display"] = display_of("AzielTether", body["note"], [("slug", "azieltether"), ("mesh_enabled", False)])
        return body, 200


def _canon_payload(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _public_row(row: dict[str, Any]) -> dict[str, Any]:
    shown = {
        "session_id": row["session_id"],
        "tip": row["tip"],
        "prev": row["prev"],
        "seq": row["seq"],
        "parties": list(row["parties"]),
        "opened_cycle": row["opened_cycle"],
        "rewrite": False,
    }
    return {
        "session_id": shown["session_id"],
        "tip": shown["tip"],
        "prev": shown["prev"],
        "seq": shown["seq"],
        "parties": list(shown["parties"]),
        "sessions": [shown],
    }
