"""Boot self-measure. Hash the installed app files and compare them to a signed release manifest.

verified is returned only when the hash set is complete and every file matches the
signed manifest. A dropped or partial hash does not fall through to verified or
mismatch. A missing manifest stays unknown. This module does not write, deploy,
publish DNS, or change mesh_node_live, alt_internet_live, or packet_path_live.

Author: Aziel Eliab. SPDX-License-Identifier: Apache-2.0
"""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path
from typing import Any

from azinterface import update_verify as V

SPEC = "AZINTERFACE-BOOT-MEASURE-1.0"
PRODUCT = "azinterface"
MANIFEST_NAME = "boot-manifest.json"
SIG_NAME = "boot-manifest.sig"
MANIFEST_CAP = 1024 * 1024
SIG_CAP = 512
MAX_FILE = 8 * 1024 * 1024
MAX_FILES = 4000
# Excluded only when they sit directly in the install root. A nested copy is measured.
_TOP_SKIP_DIRS = frozenset({".git"})
_TOP_SKIP_FILES = frozenset({MANIFEST_NAME, SIG_NAME})
_STATUSES = frozenset({"verified", "mismatch", "unknown"})


def path_ok(path: object) -> bool:
    if not isinstance(path, str) or not path or len(path) > 240:
        return False
    if path.startswith("/") or "\\" in path or path.endswith("/"):
        return False
    return all(part not in {"", ".", ".."} for part in path.split("/"))


def _shape_code(manifest: object) -> str | None:
    if not isinstance(manifest, dict) or sorted(manifest) != ["files", "product", "spec"]:
        return "BOOT-MEASURE-SHAPE"
    if manifest.get("spec") != SPEC:
        return "BOOT-MEASURE-SHAPE"
    if manifest.get("product") != PRODUCT:
        return "BOOT-MEASURE-PRODUCT"
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return "BOOT-MEASURE-SHAPE"
    seen: set[str] = set()
    for row in files:
        if not isinstance(row, dict) or sorted(row) != ["path", "sha256", "size"]:
            return "BOOT-MEASURE-SHAPE"
        if not path_ok(row.get("path")) or row["path"] in seen:
            return "BOOT-MEASURE-SHAPE"
        seen.add(row["path"])
        if not isinstance(row.get("sha256"), str) or V.HEX64.fullmatch(row["sha256"]) is None:
            return "BOOT-MEASURE-SHAPE"
        if not V.sint(row.get("size")) or row["size"] < 0:
            return "BOOT-MEASURE-SHAPE"
    return None


def _key_class(public_key: object) -> str:
    if not isinstance(public_key, str) or not public_key.strip():
        return "absent"
    text = public_key.strip()
    if text == V.RELEASE_PUBLIC_KEY:
        return "runtime-pin"
    if V.fingerprint(text) is None:
        return "invalid"
    return "usable"


def _records(files: object) -> list[dict[str, Any]] | None:
    if not isinstance(files, list):
        return None
    rows: list[dict[str, Any]] = []
    for row in files:
        if not isinstance(row, dict) or not path_ok(row.get("path")):
            return None
        digest = row.get("sha256")
        size = row.get("size")
        if not isinstance(digest, str) or V.HEX64.fullmatch(digest) is None:
            return None
        if not V.sint(size) or size < 0:
            return None
        rows.append({"path": row["path"], "sha256": digest, "size": size})
    rows.sort(key=lambda item: item["path"])
    if len({row["path"] for row in rows}) != len(rows):
        return None
    return rows


def tree_sha256(files: list[dict[str, Any]]) -> str:
    return hashlib.sha256(V.canon(files).encode()).hexdigest()


def sentence(report: dict[str, Any]) -> str:
    """The verified sentence is used only for a completed hash match."""
    if (
        report.get("status") == "verified"
        and report.get("verified") is True
        and report.get("signature_ok") is True
        and report.get("hashed") is True
        and report.get("manifest_present") is True
        and report.get("hash_dropped") is not True
    ):
        return "Boot measure: verified. The installed files match the signed release manifest."
    if report.get("status") == "mismatch" and report.get("verified") is False and report.get("signature_ok") is True:
        return "Boot measure: mismatch. The signed release manifest does not match the installed files."
    if report.get("hashed") is True and report.get("hash_dropped") is not True:
        return "Boot measure: unknown. The installed files were hashed. There is no signed release manifest to compare."
    return "Boot measure: unknown. The file hash was not completed. This measure is not verified."


def _seal(
    *,
    code: str,
    hashed: bool,
    files: list[dict[str, Any]] | None,
    manifest_present: bool,
    signature_ok: bool,
    matched: bool,
    hash_dropped: bool,
    surface: str,
) -> dict[str, Any]:
    """verified is computed here and nowhere else. A dropped hash cannot match."""
    complete = hashed is True and hash_dropped is False and isinstance(files, list) and len(files) > 0
    verified = bool(matched and signature_ok and manifest_present and complete)
    if verified:
        status = "verified"
        code = "BOOT-MEASURE-VERIFIED"
    elif signature_ok and complete and manifest_present and matched is False:
        status = "mismatch"
        code = "BOOT-MEASURE-MISMATCH"
    else:
        status = "unknown"
        verified = False
        if code in {"BOOT-MEASURE-VERIFIED", "BOOT-MEASURE-MISMATCH"}:
            code = "BOOT-MEASURE-UNREADABLE" if not complete else "BOOT-MEASURE-UNSIGNED"
    if hash_dropped or not complete:
        # Do not publish a partial digest and do not keep a dropped list as the measure.
        if hash_dropped or files is None:
            files = None
            hashed = False
    text = sentence(
        {
            "status": status,
            "verified": verified,
            "signature_ok": signature_ok is True and not hash_dropped,
            "hashed": hashed is True and not hash_dropped,
            "manifest_present": manifest_present,
            "hash_dropped": hash_dropped,
        }
    )
    count = len(files) if isinstance(files, list) else 0
    digest = tree_sha256(files) if isinstance(files, list) and not hash_dropped else None
    return {
        "ok": True,
        "spec": SPEC,
        "product": PRODUCT,
        "surface": surface,
        "status": status,
        "verified": verified,
        "code": code,
        "hashed": hashed is True and not hash_dropped and isinstance(files, list),
        "hash_dropped": hash_dropped is True,
        "file_count": count if not hash_dropped else 0,
        "tree_sha256": digest,
        "manifest_present": manifest_present is True,
        "manifest_hash": None,
        "signature_ok": signature_ok is True and hash_dropped is False and status in {"verified", "mismatch"},
        "read_only": True,
        "writes": False,
        "live": False,
        "booted": False,
        "installed": False,
        "os_yet": False,
        "kernel": False,
        "mesh_node_live": True,
        "alt_internet_live": True,
        "packet_path_live": True,
        "qnm_membership": True,
        "qns_cite_plane": False,
        "cap7_registrar_live": False,
        "public_icann": False,
        "cap7_is_icann": False,
        "satellite_relay": "HELD",
        "paid_satellite": "HELD",
        "remain_off": True,
        "dns_publish": False,
        "api": "/v1/boot_measure",
        "sentence": text,
        "display": {
            "title": "Boot measure",
            "summary": text,
            "fields": [{"label": "status", "value": status}],
        },
    }


def compare_release(
    files: list[dict[str, Any]] | None,
    manifest: object,
    signature: object,
    public_key: object,
    *,
    hashed: bool = True,
    read_code: str | None = None,
    surface: str = "desk",
    manifest_present: bool = False,
) -> dict[str, Any]:
    """Compare a complete hash set. A dropped hash returns unknown and does not match."""
    dropped = read_code is not None or hashed is not True or files is None
    if dropped:
        return _seal(
            code=read_code or "BOOT-MEASURE-UNREADABLE",
            hashed=False,
            files=None,
            manifest_present=manifest_present,
            signature_ok=False,
            matched=False,
            hash_dropped=True,
            surface=surface,
        )
    rows = _records(files)
    if rows is None:
        return _seal(
            code="BOOT-MEASURE-UNREADABLE",
            hashed=False,
            files=None,
            manifest_present=manifest_present,
            signature_ok=False,
            matched=False,
            hash_dropped=True,
            surface=surface,
        )
    if not manifest_present or manifest is None:
        return _seal(
            code="BOOT-MEASURE-NO-MANIFEST",
            hashed=True,
            files=rows,
            manifest_present=False,
            signature_ok=False,
            matched=False,
            hash_dropped=False,
            surface=surface,
        )
    if _key_class(public_key) == "runtime-pin":
        return _seal(
            code="BOOT-MEASURE-KEY-SCOPE",
            hashed=True,
            files=rows,
            manifest_present=True,
            signature_ok=False,
            matched=False,
            hash_dropped=False,
            surface=surface,
        )
    shape = _shape_code(manifest)
    if shape:
        return _seal(
            code=shape,
            hashed=True,
            files=rows,
            manifest_present=True,
            signature_ok=False,
            matched=False,
            hash_dropped=False,
            surface=surface,
        )
    if not isinstance(signature, str) or not signature.strip() or _key_class(public_key) != "usable":
        return _seal(
            code="BOOT-MEASURE-UNSIGNED" if not isinstance(signature, str) or not signature.strip() else "BOOT-MEASURE-NO-KEY",
            hashed=True,
            files=rows,
            manifest_present=True,
            signature_ok=False,
            matched=False,
            hash_dropped=False,
            surface=surface,
        )
    assert isinstance(manifest, dict)
    signed = V.sig_ok(str(public_key).strip(), manifest, signature.strip())
    if not signed:
        return _seal(
            code="BOOT-MEASURE-UNSIGNED",
            hashed=True,
            files=rows,
            manifest_present=True,
            signature_ok=False,
            matched=False,
            hash_dropped=False,
            surface=surface,
        )
    claimed = _records(manifest["files"])
    matched = claimed is not None and claimed == rows
    report = _seal(
        code="BOOT-MEASURE-VERIFIED" if matched else "BOOT-MEASURE-MISMATCH",
        hashed=True,
        files=rows,
        manifest_present=True,
        signature_ok=True,
        matched=matched,
        hash_dropped=False,
        surface=surface,
    )
    if report["signature_ok"] and isinstance(manifest, dict):
        report["manifest_hash"] = V.manifest_hash(manifest)
    return report


def _read_bytes(path: Path, cap: int) -> bytes | None | str:
    try:
        info = path.lstat()
    except OSError:
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        return "unsafe"
    if info.st_size > cap:
        return "bound"
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) != info.st_size:
        return None
    if len(data) > cap:
        return "bound"
    return data


def hash_tree(root: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Hash every regular file, including bytecode. Any unreadable or linked entry drops the whole set.

    ``.git``, ``boot-manifest.json``, and ``boot-manifest.sig`` are skipped only when they
    sit directly in the install root. ``__pycache__`` and ``.pyc`` are never skipped.
    """
    try:
        info = root.lstat()
    except OSError:
        return None, "BOOT-MEASURE-UNREADABLE"
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        return None, "BOOT-MEASURE-UNREADABLE"
    root_key = os.path.normpath(root)
    records: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        at_root = os.path.normpath(dirpath) == root_key
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return None, "BOOT-MEASURE-UNSAFE"
        except OSError:
            return None, "BOOT-MEASURE-UNREADABLE"
        kept: list[str] = []
        for name in dirnames:
            child = current / name
            try:
                child_info = child.lstat()
            except OSError:
                return None, "BOOT-MEASURE-UNREADABLE"
            if stat.S_ISLNK(child_info.st_mode):
                return None, "BOOT-MEASURE-UNSAFE"
            if at_root and name in _TOP_SKIP_DIRS:
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in filenames:
            if at_root and name in _TOP_SKIP_FILES:
                continue
            path = current / name
            rel = path.relative_to(root).as_posix()
            if not path_ok(rel):
                return None, "BOOT-MEASURE-UNSAFE"
            data = _read_bytes(path, MAX_FILE)
            if data == "unsafe":
                return None, "BOOT-MEASURE-UNSAFE"
            if data == "bound":
                return None, "BOOT-MEASURE-BOUND"
            if not isinstance(data, (bytes, bytearray)):
                return None, "BOOT-MEASURE-UNREADABLE"
            records.append({"path": rel, "sha256": hashlib.sha256(bytes(data)).hexdigest(), "size": len(data)})
            if len(records) > MAX_FILES:
                return None, "BOOT-MEASURE-BOUND"
    records.sort(key=lambda item: item["path"])
    return records, None


def _path_inside(parent: Path, child: Path) -> bool:
    """True when ``child`` is ``parent`` or lives under it. Unresolvable paths fail closed."""
    try:
        parent_r = parent.resolve()
        child_r = child.resolve()
    except OSError:
        return True
    if child_r == parent_r:
        return True
    try:
        child_r.relative_to(parent_r)
    except ValueError:
        return False
    return True


def _trust_key(measured: Path, trust_root: Path | None) -> str | None:
    """Public key from an operator trust root that is not inside the measured install.

    ``boot-measure.pub`` beside the app files is never read. No external key means no key.
    """
    from azinterface.update_apply import load_trust, operator_root

    home = trust_root if trust_root is not None else operator_root()
    if _path_inside(measured, home):
        return None
    try:
        trust = load_trust(home)
    except Exception:
        return None
    if not isinstance(trust, dict) or trust.get("configured") is not True:
        return None
    key = trust.get("public_key")
    if not isinstance(key, str) or _key_class(key) != "usable":
        return None
    return key.strip()


def _load_manifest(root: Path) -> tuple[dict[str, Any] | None, str | None, bool, str | None]:
    manifest_path = root / MANIFEST_NAME
    sig_path = root / SIG_NAME
    manifest_there = manifest_path.exists() or manifest_path.is_symlink()
    sig_there = sig_path.exists() or sig_path.is_symlink()
    if not manifest_there and not sig_there:
        return None, None, False, None
    raw = _read_bytes(manifest_path, MANIFEST_CAP)
    if raw == "unsafe":
        return None, None, True, "BOOT-MEASURE-UNSAFE"
    if raw == "bound":
        return None, None, True, "BOOT-MEASURE-BOUND"
    if not isinstance(raw, (bytes, bytearray)):
        return None, None, True, "BOOT-MEASURE-NO-MANIFEST"
    sig_raw = _read_bytes(sig_path, SIG_CAP)
    if sig_raw == "unsafe":
        return None, None, True, "BOOT-MEASURE-UNSAFE"
    if sig_raw == "bound":
        return None, None, True, "BOOT-MEASURE-BOUND"
    signature = ""
    if isinstance(sig_raw, (bytes, bytearray)):
        try:
            signature = bytes(sig_raw).decode("ascii").strip()
        except UnicodeError:
            signature = ""
    try:
        text = bytes(raw).decode("utf-8")
    except UnicodeError:
        return None, signature or None, True, "BOOT-MEASURE-SHAPE"
    parsed = V.parse_manifest_text(text)
    if not isinstance(parsed, dict):
        return None, signature or None, True, "BOOT-MEASURE-SHAPE"
    return parsed, signature or None, True, None


def measure_root(
    root: Path | str,
    public_key: str | None = None,
    *,
    surface: str = "desk",
    trust_root: Path | str | None = None,
) -> dict[str, Any]:
    """Hash one install tree. A failed hash is unknown and is not compared.

    The verifying key is the caller argument, or the operator trust root when that
    root is outside this install. A key file inside the install is not a trust anchor.
    """
    root_path = Path(root)
    files, read_code = hash_tree(root_path)
    if read_code or files is None:
        return compare_release(
            None,
            None,
            None,
            None,
            hashed=False,
            read_code=read_code or "BOOT-MEASURE-UNREADABLE",
            surface=surface,
            manifest_present=False,
        )
    manifest, signature, present, load_code = _load_manifest(root_path)
    if isinstance(public_key, str) and public_key.strip():
        key: str | None = public_key.strip()
    else:
        key = _trust_key(root_path, Path(trust_root) if trust_root is not None else None)
    if load_code and manifest is None:
        code = "BOOT-MEASURE-NO-MANIFEST" if load_code == "BOOT-MEASURE-NO-MANIFEST" or not present else load_code
        report = compare_release(
            files,
            None,
            None,
            key,
            hashed=True,
            surface=surface,
            manifest_present=False,
        )
        if code != "BOOT-MEASURE-NO-MANIFEST":
            report["code"] = code
            report["status"] = "unknown"
            report["verified"] = False
            report["signature_ok"] = False
            report["manifest_hash"] = None
            report["sentence"] = sentence(report)
            report["display"] = {"title": "Boot measure", "summary": report["sentence"], "fields": [{"label": "status", "value": "unknown"}]}
        return report
    return compare_release(
        files,
        manifest,
        signature,
        key,
        hashed=True,
        surface=surface,
        manifest_present=present and manifest is not None,
    )


def isolate_report() -> dict[str, Any]:
    """Public worker. No install tree is visible, so the hash is dropped and stays unknown."""
    return compare_release(
        None,
        None,
        None,
        None,
        hashed=False,
        read_code="BOOT-MEASURE-NO-MANIFEST",
        surface="worker",
        manifest_present=False,
    )


_CACHE: dict[str, Any] | None = None


def startup_measure() -> dict[str, Any]:
    """Hash this install once, at first use after process start."""
    global _CACHE
    if _CACHE is None:
        _CACHE = measure_root(Path(__file__).resolve().parent, surface="desk")
    return _CACHE


def _shown_status(report: dict[str, Any]) -> str:
    if (
        report.get("status") == "verified"
        and report.get("verified") is True
        and report.get("signature_ok") is True
        and report.get("hashed") is True
        and report.get("manifest_present") is True
        and report.get("hash_dropped") is not True
    ):
        return "verified"
    if report.get("status") == "mismatch" and report.get("verified") is False and report.get("signature_ok") is True and report.get("hash_dropped") is not True:
        return "mismatch"
    return "unknown"


def markup(report: dict[str, Any], *, banner: bool = False) -> str:
    from html import escape

    status = _shown_status(report)
    text = sentence({**report, "status": status, "verified": status == "verified", "hash_dropped": report.get("hash_dropped")})
    cls = ' class="banner"' if banner else ""
    return f'<p{cls} id="boot-measure" data-status="{status}" role="status">{escape(text)}</p>'
