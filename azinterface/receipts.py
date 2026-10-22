"""Append-only custody receipts. No receipt = no action."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ZERO = "0" * 64
KIND = "azinterface.receipt"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def receipt_hash(seq: int, prev: str, action: str, payload_hash: str, ts: str) -> str:
    return sha256_text(f"{seq}|{prev}|{action}|{payload_hash}|{ts}")


LATTICE_SPEC = "AZRT-DUAL-LATTICE-1.0"
LATTICE_NAMES = ["primary", "secondary"]


class LatticeDouble(ValueError):
    code = "LATTICE-DOUBLE"


def lattice_document_hash(action: str, payload_hash: str) -> str:
    """Document content for the dual lattice: action + payload hash (no seq, no time)."""
    return sha256_text(canon({"action": action, "payload_hash": payload_hash}))


def plan_lattice(document_hash: str, tips: dict[str, str], offline: bool = False, username: str | None = None) -> dict[str, Any]:
    from azinterface.runtime_lattice import runtime_offline_secondary, runtime_online_secondary, runtime_primary

    primary = runtime_primary(document_hash, tips["primary"])
    if offline:
        if not username:
            raise ValueError("LATTICE-USERNAME-ABSENT: an offline receipt needs a short username handle")
        secondary = runtime_offline_secondary(document_hash, username)
    else:
        secondary = runtime_online_secondary(primary, tips["secondary"])
    return {
        "spec": LATTICE_SPEC,
        "document_hash": document_hash,
        "primary": primary,
        "primary_prev": tips["primary"],
        "secondary": secondary,
        "secondary_prev": tips["secondary"],
        "offline": bool(offline),
        "username": username if offline else None,
        "lattices": list(LATTICE_NAMES),
    }


def verify_lattice(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Walk the additive lattice block. Rows without one are legacy (before the lattice)."""
    from azinterface.runtime_lattice import runtime_offline_secondary, runtime_online_secondary, runtime_primary

    tips = {"primary": ZERO, "secondary": ZERO}
    seen: set[str] = set()
    n = legacy = 0
    for i, row in enumerate(entries, start=1):
        lat = row.get("lattice")
        if lat is None:
            if n:
                return {"ok": False, "broken_at": i, "reason": "lattice-missing"}
            legacy += 1
            continue
        if lat.get("primary_prev") != tips["primary"] or lat.get("secondary_prev") != tips["secondary"]:
            return {"ok": False, "broken_at": i, "reason": "lattice-prev"}
        if lat.get("document_hash") != lattice_document_hash(row["action"], row["payload_hash"]):
            return {"ok": False, "broken_at": i, "reason": "lattice-document"}
        if runtime_primary(lat["document_hash"], lat["primary_prev"]) != lat.get("primary"):
            return {"ok": False, "broken_at": i, "reason": "lattice-primary-miss"}
        if lat.get("offline") is True:
            want = runtime_offline_secondary(lat["document_hash"], lat.get("username") or "")
            if lat["secondary"] in seen:
                return {"ok": False, "broken_at": i, "reason": "lattice-double"}
            seen.add(lat["secondary"])
        else:
            want = runtime_online_secondary(lat["primary"], lat["secondary_prev"])
        if want != lat.get("secondary"):
            return {"ok": False, "broken_at": i, "reason": "lattice-secondary-miss"}
        tips = {"primary": lat["primary"], "secondary": lat["secondary"]}
        n += 1
    return {"ok": True, "spec": LATTICE_SPEC, "lattice_rows": n, "legacy_rows": legacy, "tips": tips}


class Ledger:
    """Hash-chained append-only receipt list. Verify walks the chain."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path else None
        self.entries: list[dict[str, Any]] = []
        if self.path and self.path.exists():
            self._load()

    def _load(self) -> None:
        self.entries = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            self.entries.append(json.loads(line))

    def _persist(self, row: dict[str, Any]) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    @property
    def tip(self) -> str:
        return self.entries[-1]["hash"] if self.entries else ZERO

    def lattice_tips(self) -> dict[str, str]:
        for row in reversed(self.entries):
            lat = row.get("lattice")
            if lat:
                return {"primary": lat["primary"], "secondary": lat["secondary"]}
        return {"primary": ZERO, "secondary": ZERO}

    def append(self, action: str, payload: dict[str, Any] | None = None, offline: bool = False, username: str | None = None) -> dict[str, Any]:
        if not action:
            raise ValueError("No receipt = no action: action required")
        payload = dict(payload or {})
        ts = now_iso()
        seq = len(self.entries) + 1
        prev = self.tip
        payload_hash = sha256_text(canon(payload))
        digest = receipt_hash(seq, prev, action, payload_hash, ts)
        row = {
            "kind": KIND,
            "seq": seq,
            "ts": ts,
            "action": action,
            "prev": prev,
            "payload_hash": payload_hash,
            "hash": digest,
        }
        # Additive dual lattice block. Not part of `hash`, so the old chain rule is unchanged.
        lat = plan_lattice(lattice_document_hash(action, payload_hash), self.lattice_tips(), offline=offline, username=username)
        if offline and any((r.get("lattice") or {}).get("offline") is True and r["lattice"]["secondary"] == lat["secondary"] for r in self.entries):
            raise LatticeDouble("LATTICE-DOUBLE: this receipt is already stored for this user while offline; not written twice")
        row["lattice"] = lat
        self.entries.append(row)
        self._persist(row)
        return row

    def verify(self) -> dict[str, Any]:
        prev = ZERO
        for i, row in enumerate(self.entries, start=1):
            expected = receipt_hash(i, prev, row["action"], row["payload_hash"], row["ts"])
            if row.get("hash") != expected or row.get("prev") != prev or row.get("seq") != i:
                return {"ok": False, "broken_at": i, "tip": self.tip}
            prev = row["hash"]
        lattice = verify_lattice(self.entries)
        return {"ok": bool(lattice["ok"]), "count": len(self.entries), "tip": self.tip, "lattice": lattice}
