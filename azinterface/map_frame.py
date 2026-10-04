"""Running 4DMap on the existing local map door.

A card has a clock time, an optional interval, trajectory, and pattern,
and a SHA-256 over the canonical fields. A news pin is a different record.
The map is running only after a stored card is read back and its hash matches.
"""

from __future__ import annotations

import json
import re
import threading
from hashlib import sha256
from typing import Any
from uuid import uuid4

GENESIS_PREV = "0" * 64
PI_EMPTY = "Π-EMPTY"
_LOCK = threading.Lock()
_CLOCK = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_IDENTITY = re.compile(r"\b(legal\s+name|home\s+address|county\s+of)\b", re.I)
_INTENT = re.compile(r"\b(intent|motive|guilt|meant to)\b", re.I)


def lattice_path(vendor) -> Any:
    from pathlib import Path

    return Path(vendor) / "lattice.json"


def place_card(path, payload: dict[str, Any]) -> dict[str, Any]:
    problem = _card_problem(payload)
    if problem:
        view = map_view(path)
        view["ok"] = False
        view["error"] = problem
        return view
    with _LOCK:
        rows = _read(path)
        prev = str(rows[-1]["h"]) if rows else GENESIS_PREV
        card = _make(payload, prev)
        rows.append(card)
        _write(path, rows)
    view = map_view(path)
    stored = next((row for row in view["cards"] if row.get("id") == card["id"]), None)
    if stored is None or stored.get("h") != card["h"] or _hash(stored) != stored.get("h"):
        view["ok"] = False
        view["map_running"] = _running(view["cards"], ignore=card["id"])
        view["error"] = "The card did not read back."
        view["status"] = "No card is on the clock yet." if not view["map_running"] else "A card is on the clock."
        return view
    view["ok"] = True
    view["card"] = stored
    view["map_running"] = True
    view["status"] = "A card is on the clock."
    return view


def map_view(path) -> dict[str, Any]:
    cards = []
    for row in _read(path):
        if _hash(row) == row.get("h"):
            cards.append(dict(row))
    running = _running(cards)
    return {
        "ok": True,
        "map_running": running,
        "status": "A card is on the clock." if running else "No card is on the clock yet.",
        "count": len(cards),
        "cards": cards,
        "axes": {
            "T": [row["id"] for row in cards if row.get("axis") == "T"],
            "DELTA": [row["id"] for row in cards if row.get("axis") == "DELTA"],
            "GAMMA": [row["id"] for row in cards if row.get("axis") == "GAMMA"],
            "PI": [row["id"] for row in cards if row.get("axis") == "PI"],
        },
    }


def _running(cards: list[dict[str, Any]], ignore: str | None = None) -> bool:
    return any(row.get("id") != ignore and row.get("axis") == "T" and row.get("t") for row in cards)


def _card_problem(payload: dict[str, Any]) -> str | None:
    clock = str(payload.get("t") or "").strip()
    if not _CLOCK.fullmatch(clock):
        return "A map card needs a clock time like 2026-10-04T18:00:00Z."
    note = str(payload.get("note") or "")
    blob = " ".join(str(payload.get(key) or "") for key in ("note", "delta", "gamma", "pi"))
    if _IDENTITY.search(note) or _IDENTITY.search(blob):
        return "The card cannot store a legal name, a home, or a county."
    if _INTENT.search(note) or _INTENT.search(blob):
        return "The card does not record intent."
    return None


def _make(payload: dict[str, Any], prev: str) -> dict[str, Any]:
    delta = _axis_value(payload.get("delta"))
    gamma = _axis_value(payload.get("gamma"))
    pi = _axis_value(payload.get("pi"))
    card = {
        "id": "4dm-" + uuid4().hex[:12],
        "t": str(payload.get("t") or "").strip(),
        "delta": delta,
        "gamma": gamma,
        "pi": PI_EMPTY if pi is None else pi,
        "prev": prev,
        "src": "azinterface",
        "note": str(payload.get("note") or "").strip()[:240],
    }
    card["h"] = _hash(card)
    card["axis"] = _axis(card)
    return card


def _axis(card: dict[str, Any]) -> str:
    if card.get("delta") not in (None, ""):
        return "DELTA"
    if card.get("gamma") not in (None, ""):
        return "GAMMA"
    if card.get("pi") not in (None, "", PI_EMPTY):
        return "PI"
    return "T"


def _axis_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return value


def _hash(card: dict[str, Any]) -> str:
    payload = {
        "delta": card.get("delta"),
        "gamma": card.get("gamma"),
        "id": str(card.get("id") or ""),
        "note": str(card.get("note") or ""),
        "pi": card.get("pi"),
        "prev": str(card.get("prev") or GENESIS_PREV),
        "src": str(card.get("src") or ""),
        "t": card.get("t"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(raw).hexdigest()


def _read(path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = data.get("cards") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _write(path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cards": rows}, indent=2) + "\n", encoding="utf-8")
