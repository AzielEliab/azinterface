"""Sentences for people. Machine callers keep the JSON object."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

HUMAN_JS = Path(__file__).with_name("plain.js").read_text(encoding="utf-8")

_CODE_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,}$")
_EXPLAINED = re.compile(
    r"refus|cannot|can't|terminal|failed|stub|required|unknown|not one of|not accepted|never",
    re.IGNORECASE,
)
_KNOWN = {
    "AIH-CYCLE-TERMINAL": "Memorial is the last page. It cannot be left.",
    "AIH-CYCLE-LOCKED": "That step is refused. The page moves one step at a time.",
    "AIH-CYCLE-UNKNOWN": "That name is not one of the five sealed pages.",
    "AIH-INTEGRITY-REQUIRED": "ON is refused until an integrity check has passed.",
    "GENESIS_SEED_REQUIRED": "A one-time seed is required. It is hashed and then discarded.",
    "GENESIS_ALREADY_KEYED": "The genesis key is already set. It cannot be set again.",
    "INTEGRITY_FAIL": "Integrity failed. The page stays locked, and ON is refused.",
    "STUB": "This action is refused. It is not live.",
    "FG-HALLUC-TOOL": "That operation is not known.",
    "PRE_LOCKED": "The page is still locked. Living presence is off.",
    "HOLD_NOT_FOUND": "That hold is not in the witness list.",
    "PAIR_NOT_FOUND": "That pair cite is not stored.",
    "PAIR_EXISTS": "That pair cite is already stored.",
    "PAIR_CAP": "The pair list is full. No new cite was stored.",
    "QNS-HANDSHAKE-LOCKED": "That pair step is refused. The handshake is not at the required stage.",
    "SCORCH_LOCAL_ADVISORY": "This is a local advisory. It does not wipe another device.",
}


def human_lines(obj: object) -> list[str]:
    lines: list[str] = []

    def push(text: str) -> None:
        if text and text not in lines:
            lines.append(text)

    if not isinstance(obj, dict):
        push("Done.")
        return lines
    display = obj.get("display") if isinstance(obj.get("display"), dict) else None
    if display and display.get("title"):
        push(_sentence(display.get("title")))
    if display and display.get("summary"):
        push(_code_to_sentence(display.get("summary")))
    fields = display.get("fields") if display else None
    if isinstance(fields, list):
        for row in fields:
            if not isinstance(row, dict) or row.get("label") is None:
                continue
            push(_field_sentence(str(row.get("label")), row.get("value"), obj))
    if display is None:
        if obj.get("error"):
            push(_sentence(obj.get("error")))
        elif obj.get("note"):
            push(_sentence(obj.get("note")))
    pairs = obj.get("pairs")
    if isinstance(pairs, list):
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            ident = pair.get("pair_id") or "a cite"
            hand = f" The handshake is {pair.get('handshake')}." if pair.get("handshake") else ""
            via = f" The via is {pair.get('via')}." if pair.get("via") else ""
            push(f"A pair cite {ident} is stored.{hand}{via}")
    witnesses = obj.get("witnesses")
    if isinstance(witnesses, list):
        count = sum(1 for row in witnesses if isinstance(row, dict))
        if count == 1:
            push("1 witness is listed. The row is metadata.")
        elif count:
            push(f"{count} witnesses are listed. The rows are metadata.")
    if obj.get("ok") is False:
        blob = " ".join(lines)
        if not _EXPLAINED.search(blob):
            err = _sentence(obj.get("error")) if obj.get("error") else ""
            code = str(obj.get("code") or "")
            if err and err not in lines:
                push(err)
            elif code and _KNOWN.get(code):
                push(_KNOWN[code])
            elif code:
                push(f"This request was refused. The reason is {code}.")
            else:
                push("This request was refused.")
        if not re.search(r"refus", " ".join(lines), re.IGNORECASE):
            push("This step is refused.")
    nxt = obj.get("next")
    if isinstance(nxt, str) and nxt and nxt not in " ".join(lines):
        push(f"Next: {nxt}")
    if not lines:
        push("Done.")
    return lines


def human_text(obj: object) -> str:
    return "\n".join(human_lines(obj))


def _sentence(text: object) -> str:
    raw = "" if text is None else str(text).strip()
    if not raw:
        return ""
    if raw[-1] in ".!?":
        return raw
    return raw + "."


def _looks_like_code(text: object) -> bool:
    return bool(_CODE_RE.match(str(text or "").strip()))


def _code_to_sentence(text: object) -> str:
    raw = str(text or "").strip()
    known = _KNOWN.get(raw, "")
    if known:
        return known
    if _looks_like_code(raw):
        return f"This request was refused. The reason is {raw}."
    return _sentence(raw)


def _yn(value: object) -> bool | None:
    if value is True or value in {"true", "True"}:
        return True
    if value is False or value in {"false", "False"}:
        return False
    return None


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _field_sentence(label: str, value: object, obj: dict[str, Any]) -> str:
    flag = _yn(value)
    text = _text(value)
    if label in {"site_state", "current", "cycle"}:
        return f"The page is {text or 'OFF'}."
    if label == "living_presence":
        return "Living presence is off." if flag is False else "Living presence is on."
    if label == "integrity_ok":
        return "Integrity has not passed." if flag is False else "Integrity has passed."
    if label == "next":
        return f"The next sealed step is {text}." if text else "There is no next step. Memorial stays in place."
    if label == "requested":
        return f"The requested step was {text}."
    if label == "from":
        return f"It moved from {text}."
    if label == "to":
        return f"It moved to {text}."
    if label == "genesis_hash":
        return f"The genesis hash is {text}." if text else "No genesis hash is stored."
    if label in {"keyed", "genesis_keyed"}:
        return "A genesis key is not set." if flag is False else "A genesis key is set."
    if label == "username_stored":
        return "The username was stored." if flag is True else "The username is not stored."
    if label in {"genesis_sealed", "cycles_sealed"}:
        return "The five page steps are sealed."
    if label == "cloud_asleep":
        return "There is no cloud-asleep mode."
    if label == "remote_wipe":
        return "This does not wipe another device."
    if label == "local_only":
        return "This stays on this computer."
    if label == "vault_contents":
        return "Vault contents are not shown."
    if label == "hub_collapse":
        return "Interface is not Hub."
    if label == "lambgate":
        return "LambGate is not part of this path."
    if label in {"software_tab", "softwares_tab_qns"}:
        return "This is not an extra door."
    if label == "version":
        return f"The version is {text}."
    if label == "spec":
        return f"The spec is {text}."
    if label == "digest":
        return f"The integrity record is {text}." if text else ""
    if label in {"pipeline", "path"}:
        return "The path is cited. FragGate remains the door."
    if label in {"owner", "pipeline_owner"}:
        return f"The fabric owner is {text or 'aziel-runtime'}."
    if label == "4dmap":
        return "4DMap is an inspection frame on aziel-runtime. It is not live as a map on this page, and it is not an extra door."
    if label == "qns_cd":
        return f"Pair custody follows {text}."
    if label == "qnsd":
        return f"The via runs on {text}."
    if label == "count":
        return f"The count is {text}."
    if label == "op":
        return f"The operation was {text.replace('_', ' ')}."
    if label == "code":
        if obj.get("ok") is False:
            return _KNOWN.get(text) or f"This request was refused. The reason is {text}."
        if text == "SCORCH_LOCAL_ADVISORY":
            return "This is a local advisory. It does not wipe another device."
        return ""
    if label == "event":
        return f"The refused event was {text.replace('_', ' ')}."
    if label == "allowed":
        return f"The allowed vias are {text}."
    if label == "handshake":
        return f"The handshake is {text}." if text else ""
    if label == "via":
        return f"The via is {text}." if text else ""
    if label == "pair_id":
        return f"The pair cite is {text}." if text else ""
    if label == "photon_id":
        return f"The photon cite is {text}." if text else ""
    if label == "hold_id":
        return f"The hold cite is {text}." if text else ""
    if label == "status":
        return f"The record is {text}." if text else ""
    if flag is False:
        return f"The {label.replace('_', ' ')} is off."
    if flag is True:
        return f"The {label.replace('_', ' ')} is on."
    if not text:
        return ""
    if _looks_like_code(text):
        return _code_to_sentence(text)
    return _sentence(f"{label.replace('_', ' ')} is {text}")
