"""Append-only custody receipts. No receipt = no action."""

from __future__ import annotations

import hashlib
import json
import os
import re
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
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_USER_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")


class LatticeDouble(ValueError):
    code = "LATTICE-DOUBLE"


class LatticeSyncNoOffline(ValueError):
    code = "LATTICE-SYNC-NO-OFFLINE"


def _hex64(value: Any) -> bool:
    return isinstance(value, str) and _HEX64.fullmatch(value) is not None


def _sync_username(username: str | None) -> str:
    name = "" if username is None else str(username).strip()
    if _USER_RE.fullmatch(name) is None:
        raise ValueError("LATTICE-USERNAME-ABSENT: a tiebreak sync needs a short username handle")
    return name


def tiebreak_tip(entries: list[dict[str, Any]]) -> str:
    tip = ZERO
    for row in entries:
        lat = row.get("lattice") if isinstance(row, dict) else None
        tb = lat.get("tiebreak") if isinstance(lat, dict) else None
        if isinstance(tb, dict) and tb.get("status") == "synced" and _hex64(tb.get("hash")):
            tip = tb["hash"]
    return tip


def tiebreak_index_key(username: str, document_hash: str) -> str:
    return f"{username}\x00{document_hash}"


def lattice_document_hash(action: str, payload_hash: str) -> str:
    """Document content for the dual lattice: action + payload hash (no seq, no time)."""
    return sha256_text(canon({"action": action, "payload_hash": payload_hash}))


def plan_lattice(
    document_hash: str,
    tips: dict[str, str],
    offline: bool = False,
    username: str | None = None,
    rows: list[dict[str, Any]] | None = None,
    sync: bool = False,
    tiebreak_prev: str | None = None,
) -> dict[str, Any]:
    from azinterface.runtime_lattice import runtime_offline_secondary, runtime_online_secondary, runtime_primary, runtime_tiebreak

    primary = runtime_primary(document_hash, tips["primary"])
    if offline:
        if not username:
            raise ValueError("LATTICE-USERNAME-ABSENT: an offline receipt needs a short username handle")
        secondary = runtime_offline_secondary(document_hash, username)
    else:
        secondary = runtime_online_secondary(primary, tips["secondary"])
    block = {
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
    # A plain offline or online row carries no tiebreak block, so its primary and secondary stay put.
    if offline or sync is not True:
        return block
    name = _sync_username(username)
    off_secondary = runtime_offline_secondary(document_hash, name)
    found = False
    synced = False
    for row in rows or []:
        lat = row.get("lattice") if isinstance(row, dict) else None
        if not isinstance(lat, dict) or lat.get("document_hash") != document_hash:
            continue
        if lat.get("offline") is True and lat.get("secondary") == off_secondary:
            found = True
        tb = lat.get("tiebreak")
        if isinstance(tb, dict) and tb.get("status") == "synced" and tb.get("offline_secondary") == off_secondary:
            synced = True
    if synced:
        raise LatticeDouble("LATTICE-DOUBLE: this user's offline document is already synced; not written twice")
    if not found:
        raise LatticeSyncNoOffline(
            "LATTICE-SYNC-NO-OFFLINE: no offline write by this user exists for this document, so there is nothing to sync"
        )
    tprev = tiebreak_prev if _hex64(tiebreak_prev) else tiebreak_tip(rows or [])
    tiebreak = {
        "status": "synced",
        "hash": runtime_tiebreak(tprev, primary, off_secondary, name),
        "prev": tprev,
        "offline_secondary": off_secondary,
    }
    return {"tiebreak": tiebreak, **block}


def _check_tiebreak(
    lat: dict[str, Any],
    tiebreak_prev: str,
    offline_user: dict[str, dict[str, str]],
    synced_keys: set[str],
) -> str | None:
    from azinterface.runtime_lattice import runtime_tiebreak

    tb = lat.get("tiebreak")
    if not isinstance(tb, dict):
        return "tiebreak-shape"
    if tb.get("status") == "pending":
        if lat.get("offline") is not True or tb.get("offline_secondary") != lat.get("secondary") or tb.get("hash") is not None:
            return "tiebreak-pending"
        return None
    if tb.get("status") != "synced" or lat.get("offline") is True:
        return "tiebreak-status"
    if not _hex64(tb.get("hash")) or not _hex64(tb.get("offline_secondary")):
        return "tiebreak-shape"
    if tb.get("prev") != tiebreak_prev:
        return "tiebreak-prev"
    off = offline_user.get(tb["offline_secondary"])
    if not off or off.get("document_hash") != lat.get("document_hash"):
        return "tiebreak-no-offline"
    key = tiebreak_index_key(off["username"], lat["document_hash"])
    if key in synced_keys:
        return "tiebreak-double"
    want = runtime_tiebreak(tb["prev"], lat["primary"], tb["offline_secondary"], off["username"])
    if want != tb["hash"]:
        return "tiebreak-miss"
    synced_keys.add(key)
    return None


def verify_lattice(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Walk the additive lattice block. Rows without one are legacy (before the lattice)."""
    from azinterface.runtime_lattice import TIEBREAK_SPEC, runtime_offline_secondary, runtime_online_secondary, runtime_primary

    tips = {"primary": ZERO, "secondary": ZERO}
    seen: set[str] = set()
    offline_user: dict[str, dict[str, str]] = {}
    synced_keys: set[str] = set()
    tb_prev = ZERO
    tb_rows = 0
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
            offline_user[lat["secondary"]] = {
                "username": str(lat.get("username") or ""),
                "document_hash": lat["document_hash"],
            }
        else:
            want = runtime_online_secondary(lat["primary"], lat["secondary_prev"])
        if want != lat.get("secondary"):
            return {"ok": False, "broken_at": i, "reason": "lattice-secondary-miss"}
        if lat.get("tiebreak") is not None:
            reason = _check_tiebreak(lat, tb_prev, offline_user, synced_keys)
            if reason:
                return {"ok": False, "broken_at": i, "reason": reason}
            if lat["tiebreak"].get("status") == "synced":
                tb_prev = lat["tiebreak"]["hash"]
                tb_rows += 1
        tips = {"primary": lat["primary"], "secondary": lat["secondary"]}
        n += 1
    return {
        "ok": True,
        "spec": LATTICE_SPEC,
        "lattice_rows": n,
        "legacy_rows": legacy,
        "tips": tips,
        "tiebreak": {"spec": TIEBREAK_SPEC, "synced_rows": tb_rows, "tip": tb_prev},
    }


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

    def append(
        self,
        action: str,
        payload: dict[str, Any] | None = None,
        offline: bool = False,
        username: str | None = None,
        sync: bool = False,
    ) -> dict[str, Any]:
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
        # sync=True adds an optional tiebreak object. Offline and plain online rows omit it.
        lat = plan_lattice(
            lattice_document_hash(action, payload_hash),
            self.lattice_tips(),
            offline=offline,
            username=username,
            rows=self.entries,
            sync=sync,
        )
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
