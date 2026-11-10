"""AZInterface adoption of the signed install and update path.

Calls the AZ-UPDATE-MANIFEST-1.0 verifier and the AZ-AUTO-UPDATE-1.0 apply
engine. Default OFF. ``live`` stays false. A userspace generation under
``.azinterface/update`` is the operator tree. It is not a kernel boot, not a
phone bundle, and not a store install.

Every artifact byte is authenticated before activation, recovery, or a floor
change. Length and sha256 are checked when the file is empty. A group-writable
or world-writable trust anchor is not configured. A symlink is not followed.
One exclusive lock covers recovery and apply. The floor is not lowered.

The published runtime pin does not vouch for product ``azinterface``. No
release URL is invented. Mesh membership flags are not a carrier. Paid
satellite relay stays HELD.

Author: Aziel Eliab. SPDX-License-Identifier: Apache-2.0
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import io
import json
import os
import stat
import tarfile
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping
from urllib.parse import urlparse

from azinterface import update_engine as U
from azinterface import update_verify as V

TRUST_SPEC = "AZINTERFACE-UPDATE-TRUST-1.0"
PRODUCTS = frozenset({"azinterface", "aziel-runtime"})
PLATFORMS = frozenset({"userspace", "android", "ios", "macos", "windows", "worker"})
STORE_PLATFORMS = frozenset({"android", "ios", "macos", "windows"})
EVENTS = frozenset({"ui-start", "suite-start", "cli", "sidenet"})
ABS_MAX = 32 * 1024 * 1024
DEFAULT_MAX = 8 * 1024 * 1024
ENVELOPE_MAX = 64 * 1024
MEMBER_CAP = 512
NAME_CAP = 200
LOCK_WAIT = 0.75
ESTABLISHED_RELEASE_API = "https://api.github.com/repos/AzielEliab/aziel-runtime/releases/latest"
RELEASE_MANIFEST_NAME = "auto-update-manifest.json"
GITHUB_HOSTS = frozenset(
    {
        "api.github.com",
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
_FORBIDDEN_TRUST = frozenset(
    {"private_key", "private", "pem", "seed", "secret", "signing_key", "AUTO_UPDATE_SIGNING_KEY"}
)
_LOOSE = stat.S_IWGRP | stat.S_IWOTH
_URL_CAP = 512
_NOFOLLOW = os.O_NOFOLLOW if hasattr(os, "O_NOFOLLOW") else 0

TRUST_NEED: tuple[str, ...] = (
    "Create .azinterface/update/trust.json. Never put a private key, seed, or PEM in that file.",
    "The file must be a regular file owned by this user. Group write and world write are refused. A symlink is not followed.",
    "The update directory must not be group-writable, world-writable, or a symlink.",
    "spec must be AZINTERFACE-UPDATE-TRUST-1.0.",
    "product must be azinterface or aziel-runtime.",
    "public_key must be the raw 32-byte Ed25519 release public key for that product, base64url. AZInterface does not generate one and does not ship an azinterface pin.",
    "The published runtime pin vouches for product aziel-runtime only. Its fingerprint is "
    + V.RELEASE_KEY_FINGERPRINT
    + ". Using that pin for product azinterface is UPDATE-NO-KEY.",
    "auto_update must be true to apply. The default is false (UPDATE-OFF). AUTO_UPDATE=on is the same switch.",
    "platform defaults to userspace. android, ios, macos, windows, and worker stage a verified artifact and do not activate it.",
    "Offline artifact directory: .azinterface/update/incoming/ with manifest.json, manifest.sig, and the file named by artifact.name. envelope.json is accepted in place of the two manifest files.",
    "A peer file inbox is .azinterface/update/peer-inbox/ with the same files. It uses the same signature check. It is not a radio, not LAN hardware, and not a second device.",
    "release_url, when set, must be an https URL of an auto-update envelope the operator already holds. AZInterface does not invent one. http, redirects, and URLs with userinfo are refused.",
    "For product aziel-runtime, established_runtime_release true fetches "
    + ESTABLISHED_RELEASE_API
    + " and the asset "
    + RELEASE_MANIFEST_NAME
    + ". No such asset is assumed to exist. The fetch fails closed when it is missing. That flag does not vouch for azinterface.",
    "max_bytes is optional and cannot exceed 33554432. Declared sizes above the cap are UPDATE-BOUND and are not read.",
    "Paid satellite_relay stays HELD. mesh_node_live, alt_internet_live, and packet_path_live are membership flags. They do not make a carrier present.",
)

BOUNDARY: tuple[str, ...] = (
    "Activation on platform userspace is a generation directory under .azinterface/update/generations. It does not replace the running interpreter, a phone bundle, or a store signature.",
    "android, ios, macos, windows, and worker stage a verified artifact and leave activated false. install_route is system or unsupported. platform_signature_bypassed stays false.",
    "The published runtime pin vouches for product aziel-runtime only. No AZInterface release key is shipped.",
    "Artifact bytes are authenticated by length and sha256, including a zero-length file, before activation, recovery, or a floor increase.",
    "The trust anchor is refused when it is a symlink, or when the file or update directory is group-writable or world-writable.",
    "Recovery and apply share one exclusive lock file. The floor is not lowered.",
    "Track 2 LAN sessions are not implemented. mesh:file is a local inbox, not a second device and not a radio.",
    "Paid satellite_relay stays HELD. Carrier hardware on this process is absent. Membership flags are not delivery.",
    "The worker does not replace itself. No published auto-update-manifest.json is assumed. A missing asset is UPDATE-NO-RELEASE.",
    "The runtime repository and the AZ-OS repository are not modified by this module.",
)

NEXT: tuple[str, ...] = (
    "Operator writes .azinterface/update/trust.json mode 0600 or 0644, with a real azinterface release public key and auto_update true.",
    "A signed stable manifest and artifact, offline in incoming/, or an operator https release_url.",
    "A phone or store build stays staged until the operator uses that system's installer. This module does not apply it.",
    "A Track 2 session with a demonstrated LAN peer would be required before mesh:lan could mean hardware. It is not implemented.",
    "A published azinterface auto-update-manifest.json is not assumed.",
)


class _Anchor(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class _Bound(Exception):
    """Declared size or a read exceeded the cap."""


class _Transport(Exception):
    """The release fetch did not return a body."""


class _Unsafe(Exception):
    """The archive or the generation is not safe to activate."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise _Transport("redirect refused")


def bytes_match(data: bytes | bytearray, artifact: object) -> bool:
    """True only when length and sha256 both match. Empty bytes are hashed."""
    if not isinstance(data, (bytes, bytearray)) or not isinstance(artifact, dict):
        return False
    size = artifact.get("size")
    digest = artifact.get("sha256")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        return False
    if not isinstance(digest, str):
        return False
    if len(data) != size:
        return False
    return hashlib.sha256(bytes(data)).hexdigest() == digest


def operator_root() -> Path:
    raw = os.environ.get("AZINTERFACE_HOME")
    if isinstance(raw, str) and raw.strip():
        return Path(raw).expanduser()
    return Path.home() / ".azinterface"


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_symlink(path: Path) -> bool:
    try:
        return stat.S_ISLNK(path.lstat().st_mode)
    except OSError:
        return False


def _loose(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except OSError:
        return True
    if stat.S_ISLNK(mode):
        return True
    return bool(mode & _LOOSE)


def _fchmod_dir(path: Path, mode: int) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | _NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid():
            raise _Anchor("UPDATE-TRUST-REFUSED")
        os.fchmod(fd, mode)
    finally:
        os.close(fd)


def _dir_unsafe(path: Path) -> bool:
    """True when the update directory exists and cannot anchor trust."""
    if not path.exists() and not _is_symlink(path):
        return False
    try:
        info = path.lstat()
    except OSError:
        return True
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        return True
    if info.st_mode & _LOOSE or info.st_uid != os.geteuid():
        return True
    return False


def _ensure_home(root: Path) -> Path:
    home = Path(root) / "update"
    if _dir_unsafe(home):
        raise _Anchor("UPDATE-TRUST-REFUSED")
    if home.exists():
        return home
    try:
        home.mkdir(mode=0o700)
    except FileExistsError:
        if _dir_unsafe(home):
            raise _Anchor("UPDATE-TRUST-REFUSED")
        return home
    _fchmod_dir(home, 0o700)
    return home


class UpdateLock:
    """One flock shared by app open, the CLI, the side-net, and recovery.

    The kernel drops the lock if this process is killed. A live holder is not
    waited out: the other caller returns UPDATE-LOCK.
    """

    def __init__(self, home: Path) -> None:
        self.home = Path(home)
        self.fd: int | None = None

    def acquire(self, wait: float = LOCK_WAIT) -> bool:
        flags = os.O_CREAT | os.O_RDWR | _NOFOLLOW
        self.fd = os.open(self.home / "lock", flags, 0o600)
        os.fchmod(self.fd, 0o600)
        deadline = time.monotonic() + max(0.0, wait)
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(self.fd)
                    self.fd = None
                    return False
                time.sleep(0.02)

    def release(self) -> None:
        if self.fd is None:
            return
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
        finally:
            os.close(self.fd)
            self.fd = None


@contextlib.contextmanager
def _exclusive(root: Path) -> Iterator[Path]:
    home = _ensure_home(root)
    lock = UpdateLock(home)
    if not lock.acquire(LOCK_WAIT):
        raise _Anchor("UPDATE-LOCK")
    try:
        if _dir_unsafe(home):
            raise _Anchor("UPDATE-TRUST-REFUSED")
        yield home
    finally:
        lock.release()


def _blank_trust(code: str, *, enabled: bool = False, refused: bool = False) -> dict[str, Any]:
    return {
        "configured": False,
        "enabled": enabled,
        "product": "azinterface",
        "public_key": None,
        "key_fingerprint": None,
        "release_url": None,
        "established_runtime_release": False,
        "platform": "userspace",
        "max_bytes": DEFAULT_MAX,
        "code": code,
        "need": list(TRUST_NEED),
        "trust_refused": refused,
    }


def _auto_on(trust_flag: object) -> bool:
    if trust_flag is True:
        return True
    return os.environ.get("AUTO_UPDATE") == "on"


def _read_anchor(path: Path, cap: int) -> bytes | None | str:
    """Bytes from a private regular file. ``None`` if missing. ``refused`` if unsafe."""
    flags = os.O_RDONLY | _NOFOLLOW
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        return None
    except OSError:
        return "refused"
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & _LOOSE:
            return "refused"
        if info.st_size > cap:
            return "refused"
        return os.read(fd, info.st_size)
    finally:
        os.close(fd)


def load_trust(root: Path | str) -> dict[str, Any]:
    """Read operator trust. Does not create directories and does not invent a key."""
    home = Path(root) / "update"
    switched = _auto_on(False)
    if _dir_unsafe(home):
        base = _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
        base["enabled"] = False
        return base
    raw = _read_anchor(home / "trust.json", ENVELOPE_MAX)
    if raw is None:
        code = "UPDATE-NO-KEY" if switched else "UPDATE-OFF"
        base = _blank_trust(code, enabled=switched)
        return base
    if raw == "refused":
        return _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
    try:
        text = raw.decode("utf-8")
        loaded = json.loads(text)
    except (UnicodeError, json.JSONDecodeError):
        return _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
    if not isinstance(loaded, dict):
        return _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
    if _FORBIDDEN_TRUST.intersection(loaded):
        base = _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
        base["need"] = ["trust.json contains a private-key field. Remove it. AZInterface accepts only a public key."]
        return base
    if loaded.get("spec") != TRUST_SPEC or loaded.get("product") not in PRODUCTS:
        return _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
    product = str(loaded["product"])
    platform = loaded.get("platform", "userspace")
    if platform not in PLATFORMS:
        return _blank_trust("UPDATE-TRUST-REFUSED", refused=True)
    base = _blank_trust("UPDATE-NO-KEY")
    base["product"] = product
    base["platform"] = platform
    base["enabled"] = _auto_on(loaded.get("auto_update") is True)
    base["max_bytes"] = _cap_of(loaded.get("max_bytes"))
    established = loaded.get("established_runtime_release") is True and product == "aziel-runtime"
    base["established_runtime_release"] = established
    release = _https_url(loaded.get("release_url")) if isinstance(loaded.get("release_url"), str) else None
    base["release_url"] = release
    key_text = loaded.get("public_key")
    if key_text in (None, "") and product == "aziel-runtime":
        key_text = V.RELEASE_PUBLIC_KEY
    if not isinstance(key_text, str) or "PRIVATE" in key_text or "BEGIN " in key_text:
        base["code"] = "UPDATE-NO-KEY"
        return base
    digest = V.fingerprint(key_text.strip())
    if digest is None:
        base["code"] = "UPDATE-NO-KEY"
        return base
    if key_text.strip() == V.RELEASE_PUBLIC_KEY and product not in V.RELEASE_KEY_PRODUCTS:
        base["configured"] = False
        base["public_key"] = None
        base["code"] = "UPDATE-NO-KEY"
        base["need"] = [
            "The published runtime pin does not vouch for product azinterface. Put an azinterface release public key in public_key, or set product to aziel-runtime."
        ]
        return base
    base["public_key"] = key_text.strip()
    base["key_fingerprint"] = digest
    base["configured"] = True
    base["code"] = "UPDATE-OK"
    base["need"] = []
    return base


def _cap_of(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return DEFAULT_MAX
    if value < 1:
        return DEFAULT_MAX
    return min(value, ABS_MAX)


def _https_url(url: object, *, hosts: frozenset[str] | None = None) -> str | None:
    if not isinstance(url, str) or not url or len(url) > _URL_CAP:
        return None
    if any(ch in url for ch in ("\n", "\r", " ")):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        return None
    host = (parsed.hostname or "").lower()
    if not host:
        return None
    if hosts is not None and host not in hosts:
        return None
    return url


def _read_limited(response: Any, cap: int) -> bytes:
    header = response.headers.get("Content-Length") if getattr(response, "headers", None) else None
    if header is not None:
        try:
            declared = int(header)
        except ValueError as exc:
            raise _Bound from exc
        if declared < 0 or declared > cap:
            raise _Bound
    buf = bytearray()
    while len(buf) <= cap:
        chunk = response.read(min(65536, cap - len(buf) + 1))
        if not chunk:
            break
        buf += chunk
        if len(buf) > cap:
            raise _Bound
    return bytes(buf)


def _urllib_get(url: str, cap: int, timeout: float) -> bytes:
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            return _read_limited(response, cap)
    except _Bound:
        raise
    except Exception as exc:
        raise _Transport(str(exc)) from exc


def _pull(url: str, cap: int, timeout: float, hooks: Mapping[str, Any]) -> bytes:
    if "opener" in hooks:
        opener = hooks.get("opener")
        if not callable(opener):
            raise _Transport("opener refused")
        try:
            data = opener(url, timeout)
        except _Bound:
            raise
        except Exception as exc:
            raise _Transport(str(exc)) from exc
        if not isinstance(data, (bytes, bytearray)) or len(data) > cap:
            raise _Bound
        return bytes(data)
    checked = _https_url(url)
    if checked is None:
        raise _Transport("url refused")
    return _urllib_get(checked, cap, timeout)


def _parse_envelope(raw: bytes) -> dict[str, Any] | None:
    if len(raw) > ENVELOPE_MAX:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return None
    loaded = V.parse_manifest_text(text)
    if not isinstance(loaded, dict):
        return None
    if "manifest" in loaded:
        manifest = loaded.get("manifest")
        signature = loaded.get("signature")
        artifact_url = loaded.get("url") if isinstance(loaded.get("url"), str) else None
    else:
        manifest = loaded
        signature = None
        artifact_url = None
    if not isinstance(manifest, dict) or not isinstance(signature, str):
        return None
    return {"manifest": manifest, "signature": signature, "artifact_url": artifact_url}


def _local_candidate(directory: Path, cap: int) -> dict[str, Any] | None | str:
    if _is_symlink(directory) or not directory.is_dir():
        return None
    envelope_path = directory / "envelope.json"
    if envelope_path.is_file() and not _is_symlink(envelope_path):
        raw = _read_anchor(envelope_path, ENVELOPE_MAX)
        if raw in (None, "refused") or not isinstance(raw, (bytes, bytearray)):
            return "shape"
        parsed = _parse_envelope(bytes(raw))
        if parsed is None:
            return "shape"
        manifest = parsed["manifest"]
        signature = parsed["signature"]
    else:
        manifest_path = directory / "manifest.json"
        sig_path = directory / "manifest.sig"
        if _is_symlink(manifest_path) or _is_symlink(sig_path):
            return "path"
        if not manifest_path.is_file():
            return None
        if not sig_path.is_file():
            return "shape"
        raw_manifest = _read_anchor(manifest_path, ENVELOPE_MAX)
        raw_sig = _read_anchor(sig_path, 512)
        if raw_manifest == "refused" or raw_sig == "refused":
            return "path"
        if not isinstance(raw_manifest, (bytes, bytearray)) or not isinstance(raw_sig, (bytes, bytearray)):
            return "shape"
        try:
            manifest = V.parse_manifest_text(bytes(raw_manifest).decode("utf-8"))
            signature = bytes(raw_sig).decode("utf-8").strip()
        except UnicodeError:
            return "shape"
        if not isinstance(manifest, dict) or not signature:
            return "shape"
    if not V.shape_ok(manifest):
        return {"manifest": manifest, "signature": signature, "data": b"", "skip_read": True}
    declared = int(manifest["artifact"]["size"])
    if declared > cap:
        return {"manifest": manifest, "signature": signature, "data": b"", "bound": True}
    name = manifest["artifact"]["name"]
    artifact = directory / name
    if artifact.parent != directory or _is_symlink(artifact):
        return {"manifest": manifest, "signature": signature, "data": b"", "path": True}
    if not artifact.is_file():
        return {"manifest": manifest, "signature": signature, "data": b"", "bound": False}
    try:
        info = artifact.lstat()
    except OSError:
        return {"manifest": manifest, "signature": signature, "data": b"", "path": True}
    if not stat.S_ISREG(info.st_mode) or info.st_size > cap:
        return {"manifest": manifest, "signature": signature, "data": b"", "bound": info.st_size > cap, "path": not stat.S_ISREG(info.st_mode)}
    data = _read_regular(artifact, cap)
    if data is None:
        return {"manifest": manifest, "signature": signature, "data": b"", "path": True}
    if len(data) > cap:
        return {"manifest": manifest, "signature": signature, "data": b"", "bound": True}
    return {"manifest": manifest, "signature": signature, "data": data, "bound": False}


def _read_regular(path: Path, cap: int) -> bytes | None:
    """Read a regular file. Empty is ``b''``. A symlink or special file is None."""
    flags = os.O_RDONLY | _NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError:
        return None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > cap or info.st_size < 0:
            return None
        if info.st_size == 0:
            return b""
        buf = bytearray()
        remaining = info.st_size
        while remaining:
            piece = os.read(fd, min(65536, remaining))
            if not piece:
                return None
            if len(piece) > remaining:
                return None
            buf += piece
            remaining -= len(piece)
        return bytes(buf)
    finally:
        os.close(fd)


def _safe_member_name(name: str) -> Path | None:
    if not name or len(name) > NAME_CAP or "\\" in name or "\x00" in name:
        return None
    if name.startswith("/") or (len(name) >= 2 and name[1] == ":"):
        return None
    parts = [part for part in Path(name).parts if part not in ("", ".")]
    if not parts or any(part == ".." or part.startswith("/") for part in parts):
        return None
    if any(V.WIN_RESERVED.fullmatch(part) for part in parts):
        return None
    return Path(*parts)


def _tar_problem(blob: bytes, cap: int) -> str | None:
    try:
        handle = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    except tarfile.TarError:
        return None
    total = 0
    count = 0
    with handle:
        for member in handle.getmembers():
            count += 1
            if count > MEMBER_CAP:
                return "bound"
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                return "path"
            mode = member.mode or 0
            if mode & 0o6000:
                return "path"
            if member.isdir():
                if _safe_member_name(member.name) is None:
                    return "path"
                continue
            if _safe_member_name(member.name) is None:
                return "path"
            if member.size < 0 or member.size > cap or total + member.size > cap:
                return "bound"
            total += member.size
    return None


def _extract(blob: bytes, dest: Path, cap: int, after_member: Callable[[int], None] | None) -> None:
    tree = dest / "tree"
    tree.mkdir(mode=0o700)
    try:
        handle = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    except tarfile.TarError:
        _write_file(tree / "payload", blob if len(blob) <= cap else b"")
        if len(blob) > cap:
            raise _Bound
        return
    total = 0
    count = 0
    with handle:
        for member in handle.getmembers():
            count += 1
            if count > MEMBER_CAP:
                raise _Bound
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise _Unsafe("refused member type")
            if (member.mode or 0) & 0o6000:
                raise _Unsafe("refused mode")
            rel = _safe_member_name(member.name)
            if rel is None:
                raise _Unsafe("refused member name")
            target = tree / rel
            if not _inside(tree, target):
                raise _Unsafe("escape")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
                continue
            if member.size < 0 or member.size > cap or total + member.size > cap:
                raise _Bound
            source = handle.extractfile(member)
            if source is None:
                raise _Unsafe("missing body")
            remaining = member.size
            chunks = bytearray()
            while remaining:
                piece = source.read(min(65536, remaining))
                if not piece:
                    raise _Unsafe("short member")
                if len(piece) > remaining:
                    raise _Bound
                chunks += piece
                remaining -= len(piece)
                total += len(piece)
                if total > cap:
                    raise _Bound
            _write_file(target, bytes(chunks))
            if after_member is not None:
                after_member(count)


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | _NOFOLLOW
    fd = os.open(path, flags, 0o644)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_atomic(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + ".tmp")
    if _is_symlink(tmp):
        raise _Unsafe("temp symlink")
    if tmp.exists():
        tmp.unlink()
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | _NOFOLLOW
    fd = os.open(tmp, flags, mode)
    try:
        os.fchmod(fd, mode)
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)
    dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | _NOFOLLOW)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


def _clear(path: Path) -> None:
    if _is_symlink(path) or path.is_file():
        path.unlink()
        return
    if not path.exists():
        return
    for child in list(path.iterdir()):
        _clear(child)
    path.rmdir()


def _tree_safe(tree: Path) -> bool:
    if _is_symlink(tree) or not tree.is_dir():
        return False
    count = 0
    for path in tree.rglob("*"):
        count += 1
        if count > MEMBER_CAP or _is_symlink(path) or not _inside(tree, path):
            return False
    return True


def _tree_matches(tree: Path, blob: bytes) -> bool:
    """Extracted files must be the signed artifact, not a second copy of the bytes."""
    if not _tree_safe(tree):
        return False
    try:
        handle = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    except tarfile.TarError:
        payload = tree / "payload"
        names = sorted(path.relative_to(tree).as_posix() for path in tree.rglob("*") if not path.is_dir())
        if _is_symlink(payload) or not payload.is_file() or names != ["payload"]:
            return False
        return payload.read_bytes() == blob
    expected: dict[str, bytes] = {}
    try:
        with handle:
            for member in handle.getmembers():
                if member.isdir():
                    continue
                if member.issym() or member.islnk() or not member.isfile() or (member.mode or 0) & 0o6000:
                    return False
                rel = _safe_member_name(member.name)
                if rel is None:
                    return False
                source = handle.extractfile(member)
                if source is None:
                    return False
                expected[rel.as_posix()] = source.read()
    except (tarfile.TarError, OSError):
        return False
    actual: dict[str, bytes] = {}
    for path in tree.rglob("*"):
        if path.is_dir():
            continue
        if _is_symlink(path) or not path.is_file() or not _inside(tree, path):
            return False
        actual[path.relative_to(tree).as_posix()] = path.read_bytes()
    return actual == expected


def _platform_of(trust: Mapping[str, Any], hooks: Mapping[str, Any]) -> str:
    declared = trust.get("platform") or "userspace"
    if declared not in PLATFORMS:
        raise _Anchor("UPDATE-TRUST-REFUSED")
    override = hooks.get("platform")
    if override is None:
        return str(declared)
    if override not in PLATFORMS:
        raise _Anchor("UPDATE-TRUST-REFUSED")
    if declared != "userspace" and override == "userspace":
        return str(declared)
    return str(override)


def _install_route(platform: str, activated: bool, staged: bool) -> str | None:
    if platform == "userspace" and activated:
        return "userspace-generation"
    if staged and platform in STORE_PLATFORMS:
        return "system"
    if staged and platform == "worker":
        return "unsupported"
    return None


class InterfaceUpdateHost:
    """Disk host. Bytes, permissions, and the floor are checked under the caller lock."""

    def __init__(self, root: Path, trust: Mapping[str, Any], hooks: Mapping[str, Any] | None = None) -> None:
        self.root = Path(root)
        self.trust = trust
        self.hooks = dict(hooks or {})
        self.home = self.root / "update"
        self.gen = self.home / "generations"
        self.state_path = self.home / "state.json"
        self.receipt_path = self.home / "receipts.jsonl"
        self.intent_path = self.home / "intent.json"
        self.product = str(trust.get("product") or "azinterface")
        self.public_key = trust.get("public_key") if trust.get("configured") is True else None
        self.enabled = trust.get("enabled") is True and trust.get("trust_refused") is not True
        self.cap = int(trust.get("max_bytes") or DEFAULT_MAX)
        self.platform = _platform_of(trust, self.hooks)
        self.node_id = "azinterface-update"
        self.offline = True
        self._state_bad = False
        self._swapped = False
        self._pending_signature = ""
        self._offer: dict[str, Any] | None = None
        self._reach_cached: bool | None = None
        self._bound = False
        self.recovered: str | None = None

    def now(self) -> str:
        return _now()

    def _state_kind(self) -> str:
        try:
            info = self.state_path.lstat()
        except FileNotFoundError:
            return "missing"
        except OSError:
            return "bad"
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            return "bad"
        if info.st_mode & _LOOSE or info.st_uid != os.geteuid():
            return "bad"
        return "ok"

    def load(self) -> dict[str, Any]:
        if self._state_bad:
            return self._bad_state()
        kind = self._state_kind()
        if kind == "missing":
            return U.initial_state(self.product, 0)
        if kind == "bad":
            self._state_bad = True
            return self._bad_state()
        raw = _read_anchor(self.state_path, ENVELOPE_MAX)
        if not isinstance(raw, (bytes, bytearray)):
            self._state_bad = True
            return self._bad_state()
        try:
            loaded = json.loads(bytes(raw).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._state_bad = True
            return self._bad_state()
        if not isinstance(loaded, dict) or loaded.get("product") != self.product:
            self._state_bad = True
            return self._bad_state()
        if loaded.get("installed_seq") is None and loaded.get("floor_seq") is None:
            self._state_bad = True
            return self._bad_state()
        if not _seq_field(loaded.get("installed_seq")) or not _seq_field(loaded.get("floor_seq")):
            self._state_bad = True
            return self._bad_state()
        return json.loads(json.dumps(loaded))

    def _bad_state(self) -> dict[str, Any]:
        state = U.initial_state(self.product, 0)
        state["installed_seq"] = None
        state["floor_seq"] = None
        return state

    def _disk_floor(self) -> int | None:
        if self._state_kind() != "ok":
            return None
        raw = _read_anchor(self.state_path, ENVELOPE_MAX)
        if not isinstance(raw, (bytes, bytearray)):
            return None
        try:
            loaded = json.loads(bytes(raw).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        if isinstance(loaded, dict) and V.sint(loaded.get("floor_seq")) and loaded["floor_seq"] >= 0:
            return int(loaded["floor_seq"])
        return None

    def save(self, state: dict[str, Any]) -> None:
        if self._state_bad:
            return
        new_floor = state.get("floor_seq")
        disk_floor = self._disk_floor()
        hook = self.hooks.get("on_floor")
        if isinstance(disk_floor, int) and isinstance(new_floor, int) and new_floor < disk_floor:
            if callable(hook):
                hook(disk_floor, new_floor, False)
            return
        if callable(hook) and isinstance(new_floor, int):
            hook(disk_floor if isinstance(disk_floor, int) else 0, new_floor, True)
        payload = json.dumps(state, indent=2, sort_keys=True) + "\n"
        _write_atomic(self.state_path, payload.encode("utf-8"), 0o600)
        self._clear_intent()

    def write_receipt(self, row: dict[str, Any]) -> None:
        line = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
        flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY | _NOFOLLOW
        fd = os.open(self.receipt_path, flags, 0o600)
        try:
            os.fchmod(fd, 0o600)
            os.write(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)

    def carrier_present(self, carrier: str) -> bool:
        del carrier
        return False

    def peer_hello(self, carrier: str) -> dict[str, Any]:
        del carrier
        return {"refused": True, "code": "UPDATE-PEER-NO-ROUTE"}

    def peer_fetch(self, carrier: str, manifest: object) -> dict[str, Any]:
        del carrier, manifest
        return {"refused": True, "code": "UPDATE-PEER-NO-ARTIFACT"}

    def internet_reachable(self) -> bool:
        if self._reach_cached is not None:
            return self._reach_cached
        try:
            offer = self._fetch_envelope()
        except _Transport:
            self._offer = None
            self._reach_cached = False
            return False
        except _Bound:
            self._bound = True
            self._offer = None
            self._reach_cached = True
            return True
        self._offer = offer
        if (
            isinstance(offer, dict)
            and isinstance(offer.get("manifest"), dict)
            and V.sint(offer["manifest"].get("artifact", {}).get("size"))
            and offer["manifest"]["artifact"]["size"] > self.cap
        ):
            self._bound = True
        self._reach_cached = True
        return True

    def fetch_release(self) -> dict[str, Any] | None:
        if self._offer is None and self._reach_cached is None:
            self.internet_reachable()
        offer = self._offer
        if isinstance(offer, dict) and isinstance(offer.get("signature"), str):
            self._pending_signature = offer["signature"]
        return offer

    def fetch_artifact(self, manifest: dict[str, Any]) -> bytes | None:
        if self._bound or manifest["artifact"]["size"] > self.cap:
            raise _Bound
        url = self._offer.get("artifact_url") if isinstance(self._offer, dict) else None
        if not isinstance(url, str):
            return None
        hosts = GITHUB_HOSTS if self.trust.get("established_runtime_release") is True else None
        checked = _https_url(url, hosts=hosts)
        if checked is None:
            return None
        data = _pull(checked, self.cap, 8.0, self.hooks)
        if len(data) > self.cap or not bytes_match(data, manifest["artifact"]):
            raise _Bound if len(data) > self.cap else _Unsafe("artifact bytes")
        return data

    def _fetch_envelope(self) -> dict[str, Any] | None:
        if self.trust.get("established_runtime_release") is True:
            listing = _pull(ESTABLISHED_RELEASE_API, ENVELOPE_MAX, 8.0, self.hooks)
            try:
                meta = json.loads(listing.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                return {"refused": True, "code": "UPDATE-NO-RELEASE"}
            if not isinstance(meta, dict) or meta.get("prerelease") is True or meta.get("draft") is True:
                return {"refused": True, "code": "UPDATE-NO-RELEASE"}
            assets = meta.get("assets") if isinstance(meta.get("assets"), list) else []
            asset_url = None
            for asset in assets:
                if (
                    isinstance(asset, dict)
                    and asset.get("name") == RELEASE_MANIFEST_NAME
                    and isinstance(asset.get("browser_download_url"), str)
                ):
                    asset_url = _https_url(asset["browser_download_url"], hosts=GITHUB_HOSTS)
                    break
            if asset_url is None:
                return {"refused": True, "code": "UPDATE-NO-RELEASE"}
            body = _pull(asset_url, ENVELOPE_MAX, 8.0, self.hooks)
        else:
            release = self.trust.get("release_url")
            if not isinstance(release, str):
                return {"refused": True, "code": "UPDATE-NO-RELEASE"}
            body = _pull(release, ENVELOPE_MAX, 8.0, self.hooks)
        parsed = _parse_envelope(body)
        if parsed is None:
            return {"refused": True, "code": "UPDATE-NO-RELEASE"}
        artifact_url = parsed.get("artifact_url")
        hosts = GITHUB_HOSTS if self.trust.get("established_runtime_release") is True else None
        if isinstance(artifact_url, str):
            checked = _https_url(artifact_url, hosts=hosts)
            if checked is None:
                return {"refused": True, "code": "UPDATE-NO-RELEASE"}
            parsed["artifact_url"] = checked
        return {"manifest": parsed["manifest"], "signature": parsed["signature"], "artifact_url": parsed.get("artifact_url")}

    def stage(self, data: bytes, manifest: dict[str, Any]) -> None:
        if not bytes_match(data, manifest.get("artifact")):
            raise _Unsafe("staged bytes do not authenticate")
        staging = self.gen / "staging"
        _clear(staging)
        self.gen.mkdir(parents=True, exist_ok=True, mode=0o700)
        staging.mkdir(mode=0o700)
        try:
            _write_file(staging / "artifact.bin", data)
            after = self.hooks.get("after_member")
            _extract(data, staging, self.cap, after if callable(after) else None)
            _write_atomic(staging / "manifest.json", (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8"), 0o644)
            _write_atomic(staging / "signature.txt", (self._pending_signature + "\n").encode("utf-8"), 0o644)
            before = self.hooks.get("before_ready")
            if callable(before):
                before(staging)
            _write_atomic(staging / "READY", b"ready\n", 0o644)
            if self._proof(staging) is None:
                raise _Unsafe("staged generation failed authentication")
        except Exception:
            _clear(staging)
            raise

    def swap(self) -> None:
        current = self.gen / "current"
        previous = self.gen / "previous"
        staging = self.gen / "staging"
        proof = self._proof(staging)
        if proof is None:
            raise _Unsafe("staged bytes do not authenticate")
        _write_atomic(
            self.intent_path,
            json.dumps({"op": "swap", "product": self.product, "version_seq": proof["seq"], "sha256": proof["sha256"], "size": proof["size"]}).encode("utf-8"),
            0o600,
        )
        if previous.exists() or _is_symlink(previous):
            _clear(previous)
        if current.exists() or _is_symlink(current):
            os.replace(current, previous)
        os.replace(staging, current)
        self._swapped = True

    def health_check(self) -> bool:
        return self._proof(self.gen / "current") is not None

    def rollback(self) -> None:
        current = self.gen / "current"
        previous = self.gen / "previous"
        staging = self.gen / "staging"
        partial = (not current.exists() and not _is_symlink(current)) and (previous.exists() or _is_symlink(previous))
        if self._swapped or partial:
            if current.exists() or _is_symlink(current):
                _clear(current)
            if previous.is_dir() and not _is_symlink(previous) and self._proof(previous) is not None:
                os.replace(previous, current)
            elif previous.exists() or _is_symlink(previous):
                _clear(previous)
        _clear(staging)
        self._swapped = False
        self._clear_intent()

    def recover(self) -> None:
        """Authenticate the current generation. Empty or mismatched bytes do not raise the floor."""
        self._repair_partial_swap()
        if not self.public_key:
            self._clear_intent()
            return
        current = self.gen / "current"
        if _is_symlink(current):
            self._reject_current()
            self.recovered = "current-rejected"
            self._clear_intent()
            return
        if not current.exists():
            self._clear_intent()
            return
        proof = self._proof(current)
        if proof is None:
            self._reject_current()
            self.recovered = "current-rejected"
            self._clear_intent()
            return
        state = self.load()
        if self._state_bad:
            self._clear_intent()
            return
        installed = state.get("installed_seq") if V.sint(state.get("installed_seq")) else 0
        floor = state.get("floor_seq") if V.sint(state.get("floor_seq")) else 0
        if self.enabled and proof["seq"] > max(installed, floor):
            state["installed_seq"] = proof["seq"]
            state["floor_seq"] = max(floor, proof["seq"])
            state["manifest_hash"] = proof["manifest_hash"]
            state["served_manifest"] = {"manifest": proof["manifest"], "signature": proof["signature"]}
            state["last_code"] = "UPDATE-OK"
            state["product"] = self.product
            again = self._proof(current)
            if again is None or again["seq"] != proof["seq"] or again["sha256"] != proof["sha256"]:
                self._reject_current()
                self.recovered = "current-rejected"
                self._clear_intent()
                return
            self.save(state)
            self.recovered = "commit-finished"
            return
        self._clear_intent()

    def _repair_partial_swap(self) -> None:
        if not self.intent_path.is_file() or _is_symlink(self.intent_path):
            self._discard_staging()
            return
        current = self.gen / "current"
        previous = self.gen / "previous"
        if current.exists() and not _is_symlink(current):
            self._discard_staging()
            return
        if previous.is_dir() and not _is_symlink(previous) and self._proof(previous) is not None and not current.exists():
            os.replace(previous, current)
            self.recovered = "swap-rolled-back"
        self._discard_staging()

    def _discard_staging(self) -> None:
        staging = self.gen / "staging"
        if staging.exists() or _is_symlink(staging):
            _clear(staging)
            if self.recovered is None:
                self.recovered = "staging-discarded"

    def _proof(self, directory: Path) -> dict[str, Any] | None:
        """Signature plus the actual artifact bytes. Empty bytes are not skipped."""
        if _is_symlink(directory) or not directory.is_dir() or not self.public_key:
            return None
        ready = directory / "READY"
        manifest_path = directory / "manifest.json"
        signature_path = directory / "signature.txt"
        blob = directory / "artifact.bin"
        if any(_is_symlink(path) for path in (ready, manifest_path, signature_path, blob)):
            return None
        if not ready.is_file() or not manifest_path.is_file() or not signature_path.is_file():
            return None
        raw_manifest = _read_regular(manifest_path, ENVELOPE_MAX)
        raw_sig = _read_regular(signature_path, 512)
        data = _read_regular(blob, self.cap)
        if raw_manifest is None or raw_sig is None or data is None:
            return None
        try:
            manifest = json.loads(raw_manifest.decode("utf-8"))
            signature = raw_sig.decode("utf-8").strip()
        except (UnicodeError, json.JSONDecodeError):
            return None
        if not isinstance(manifest, dict) or not V.shape_ok(manifest):
            return None
        if manifest.get("product") != self.product or manifest.get("channel") not in V.ACCEPTED_CHANNELS:
            return None
        artifact = manifest.get("artifact")
        if not bytes_match(data, artifact):
            return None
        if not V.sig_ok(self.public_key, manifest, signature):
            return None
        if not _tree_matches(directory / "tree", data):
            return None
        return {
            "ok": True,
            "seq": int(manifest["version_seq"]),
            "manifest": manifest,
            "signature": signature,
            "manifest_hash": V.manifest_hash(manifest),
            "sha256": artifact["sha256"],
            "size": artifact["size"],
        }

    def _reject_current(self) -> None:
        current = self.gen / "current"
        previous = self.gen / "previous"
        rejected = self.gen / "rejected"
        previous_ok = previous.is_dir() and not _is_symlink(previous) and self._proof(previous) is not None
        if previous_ok:
            if rejected.exists() or _is_symlink(rejected):
                _clear(rejected)
            if current.exists() or _is_symlink(current):
                os.replace(current, rejected)
            os.replace(previous, current)
            return
        if rejected.exists() or _is_symlink(rejected):
            _clear(rejected)
        if current.exists() or _is_symlink(current):
            os.replace(current, rejected)

    def _clear_intent(self) -> None:
        if self.intent_path.exists() or _is_symlink(self.intent_path):
            if _is_symlink(self.intent_path) or self.intent_path.is_file():
                self.intent_path.unlink()


def _seq_field(value: object) -> bool:
    return value is None or (V.sint(value) and value >= 0)


def _refuse(host: InterfaceUpdateHost, code: str, source: str) -> dict[str, Any]:
    state = host.load()
    state["last_check"] = host.now()
    state["last_code"] = code
    row = U.update_receipt(
        host,
        state,
        {
            "product": state.get("product"),
            "from_seq": state.get("installed_seq"),
            "to_seq": None,
            "manifest_hash": None,
            "source": source,
            "outcome": "refused",
            "code": code,
            "at": state["last_check"],
        },
    )
    host.save(state)
    return {"ok": False, "code": code, "row": row, "live": False, "applied": False}


def _apply_candidate(host: InterfaceUpdateHost, candidate: Mapping[str, Any], source: str) -> dict[str, Any]:
    manifest = candidate.get("manifest")
    signature = candidate.get("signature")
    data = candidate.get("data") if isinstance(candidate.get("data"), (bytes, bytearray)) else b""
    if candidate.get("path") is True:
        return _refuse(host, "UPDATE-PATH", source)
    pre = V.verify_manifest(manifest, signature, host.load(), host.public_key)
    if candidate.get("skip_read") is True and pre.get("ok") is not True:
        return U.apply_offer(host, {"manifest": manifest, "signature": signature}, source, lambda _manifest: None, host.public_key)
    if pre.get("ok") is True and isinstance(manifest, dict):
        declared = manifest["artifact"]["size"]
        if candidate.get("bound") is True or declared > host.cap or len(data) > host.cap:
            return _refuse(host, "UPDATE-BOUND", source)
        if not bytes_match(data, manifest["artifact"]):
            return _refuse(host, "UPDATE-HASH", source)
        problem = _tar_problem(bytes(data), host.cap)
        if problem == "path":
            return _refuse(host, "UPDATE-PATH", source)
        if problem == "bound":
            return _refuse(host, "UPDATE-BOUND", source)
        if host.platform != "userspace":
            return _stage_platform(host, manifest, signature, bytes(data), source, pre.get("manifest_hash"))
    host._pending_signature = signature if isinstance(signature, str) else ""
    return U.apply_offer(
        host,
        {"manifest": manifest, "signature": signature},
        source,
        lambda _manifest: bytes(data),
        host.public_key,
    )


def _stage_platform(
    host: InterfaceUpdateHost,
    manifest: dict[str, Any],
    signature: str,
    data: bytes,
    source: str,
    manifest_hash: object,
) -> dict[str, Any]:
    """Verified bytes are staged. The floor does not move and nothing is activated."""
    if not bytes_match(data, manifest.get("artifact")):
        return _refuse(host, "UPDATE-HASH", source)
    seq = int(manifest["version_seq"])
    dest = host.home / "staged" / str(seq)
    if dest.exists() or _is_symlink(dest):
        _clear(dest)
    dest.mkdir(parents=True, mode=0o700)
    try:
        _write_file(dest / "artifact.bin", data)
        _write_atomic(dest / "manifest.json", (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8"), 0o644)
        _write_atomic(dest / "signature.txt", (signature + "\n").encode("utf-8"), 0o644)
        _write_atomic(dest / "PHASE", b"downloaded\nverified\n", 0o644)
    except Exception:
        _clear(dest)
        return _refuse(host, "UPDATE-HEALTH", source)
    readback = _read_regular(dest / "artifact.bin", host.cap)
    if readback is None or not bytes_match(readback, manifest["artifact"]):
        _clear(dest)
        return _refuse(host, "UPDATE-HASH", source)
    state = host.load()
    state["last_check"] = host.now()
    state["last_code"] = "UPDATE-PLATFORM-STAGE"
    row = U.update_receipt(
        host,
        state,
        {
            "product": state.get("product"),
            "from_seq": state.get("installed_seq"),
            "to_seq": seq,
            "manifest_hash": manifest_hash if isinstance(manifest_hash, str) else None,
            "source": source,
            "outcome": "staged",
            "code": "UPDATE-PLATFORM-STAGE",
            "at": state["last_check"],
        },
    )
    host.save(state)
    return {"ok": True, "code": "UPDATE-PLATFORM-STAGE", "row": row, "live": False, "applied": False, "staged_dir": str(dest)}


def apply_candidate(
    root: Path | str,
    manifest: dict[str, Any],
    signature: str,
    data: bytes,
    source: str,
    *,
    hooks: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply one in-memory offer. ``mesh:lan`` still reports hardware false."""
    return adopt(root, event="cli", hooks=hooks, candidate={"manifest": manifest, "signature": signature, "data": data, "source": source})


def on_app_lifecycle(root: Path | str, event: str, hooks: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """App open, suite start, or the explicit update command."""
    if event not in EVENTS:
        return _static_report("UPDATE-EVENT-UNKNOWN", event, configured=False)
    return adopt(root, event=event, hooks=hooks)


def on_connectivity(root: Path | str, hooks: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Side-net connectivity event. Same adopt path. Membership is not a carrier."""
    return on_app_lifecycle(root, "sidenet", hooks)


def adopt(
    root: Path | str,
    *,
    event: str,
    hooks: Mapping[str, Any] | None = None,
    candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    try:
        with _exclusive(root_path) as home:
            return _adopt_locked(root_path, home, event, hooks or {}, candidate)
    except _Anchor as exc:
        return _static_report(exc.code, event, configured=False, refused=True)
    except AssertionError:
        raise
    except Exception:
        return _static_report("UPDATE-STATE", event, configured=False)


def _adopt_locked(
    root: Path,
    home: Path,
    event: str,
    hooks: Mapping[str, Any],
    candidate: Mapping[str, Any] | None,
) -> dict[str, Any]:
    del home
    trust = load_trust(root)
    host = InterfaceUpdateHost(root, trust, hooks)
    mark = hooks.get("inside_lock")
    if callable(mark):
        mark("enter")
    try:
        return _adopt_body(root, trust, host, event, hooks, candidate)
    finally:
        if callable(mark):
            mark("leave")


def _adopt_body(
    root: Path,
    trust: Mapping[str, Any],
    host: InterfaceUpdateHost,
    event: str,
    hooks: Mapping[str, Any],
    candidate: Mapping[str, Any] | None,
) -> dict[str, Any]:
    del root, hooks
    host.recover()
    if trust.get("trust_refused") is True:
        decision = _refuse(host, "UPDATE-TRUST-REFUSED", "offline")
        return _public(host, trust, decision, event, mesh=None, internet={"attempted": False, "code": None})
    if host.enabled is not True:
        decision = U.apply_offer(host, None, "offline", lambda _manifest: None, host.public_key)
        return _public(host, trust, decision, event, mesh=None, internet={"attempted": False, "code": None})
    if trust.get("configured") is not True or not host.public_key:
        decision = U.apply_offer(host, None, "offline", lambda _manifest: None, None)
        return _public(host, trust, decision, event, mesh=None, internet={"attempted": False, "code": None})

    host.offline = True
    mesh = U.on_peer_contact(host, host.public_key)
    if candidate is not None:
        source = str(candidate.get("source") or "offline")
        if source.startswith("mesh:"):
            host.offline = True
        decision = _apply_candidate(host, candidate, source)
        return _public(host, trust, decision, event, mesh=mesh, internet={"attempted": False, "code": None})

    incoming = _local_candidate(host.home / "incoming", host.cap)
    inbox = _local_candidate(host.home / "peer-inbox", host.cap)
    chosen = incoming if incoming is not None else inbox
    source = "offline" if incoming is not None else "mesh:file"
    if chosen == "shape" or chosen == "path":
        code = "UPDATE-PATH" if chosen == "path" else "UPDATE-MANIFEST-SHAPE"
        decision = _refuse(host, code, source)
        return _public(host, trust, decision, event, mesh=mesh, internet={"attempted": False, "code": None})
    if isinstance(chosen, dict):
        host.offline = True
        decision = _apply_candidate(host, chosen, source)
        return _public(
            host,
            trust,
            decision,
            event,
            mesh=mesh,
            internet={"attempted": False, "code": None, "reason": "a local signed artifact was the candidate"},
        )

    release_configured = bool(trust.get("release_url")) or trust.get("established_runtime_release") is True
    if not release_configured:
        decision = _refuse(host, "UPDATE-NO-RELEASE", "online")
        return _public(host, trust, decision, event, mesh=mesh, internet={"attempted": False, "code": "UPDATE-NO-RELEASE"})

    host.offline = False
    host.internet_reachable()
    offer = host._offer if isinstance(host._offer, dict) else None
    pre_ok = False
    if isinstance(offer, dict) and isinstance(offer.get("manifest"), dict):
        pre_ok = V.verify_manifest(offer.get("manifest"), offer.get("signature"), host.load(), host.public_key).get("ok") is True
    if host._bound and pre_ok and offer is not None and offer.get("refused") is not True:
        decision = _refuse(host, "UPDATE-BOUND", "online")
        return _public(host, trust, decision, event, mesh=mesh, internet={"attempted": True, "code": "UPDATE-BOUND"})
    decision = U.on_internet_reach(host, host.public_key)
    internet = {"attempted": True, "code": decision.get("code"), "live": False}
    return _public(host, trust, decision, event, mesh=mesh, internet=internet)


def _read_state(host: InterfaceUpdateHost) -> dict[str, Any]:
    if host._state_kind() != "ok":
        return {}
    raw = _read_anchor(host.state_path, ENVELOPE_MAX)
    if not isinstance(raw, (bytes, bytearray)):
        return {}
    try:
        loaded = json.loads(bytes(raw).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _public(
    host: InterfaceUpdateHost,
    trust: Mapping[str, Any],
    decision: Mapping[str, Any],
    event: str,
    *,
    mesh: Mapping[str, Any] | None,
    internet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    state = _read_state(host)
    code = decision.get("code") if isinstance(decision.get("code"), str) else "UPDATE-STATE"
    row = decision.get("row") if isinstance(decision.get("row"), dict) else {}
    outcome = row.get("outcome") if isinstance(row.get("outcome"), str) else None
    current = host.gen / "current"
    proof = host._proof(current) if host.public_key else None
    applied = code == "UPDATE-OK" and outcome == "applied" and proof is not None and state.get("installed_seq") == proof["seq"]
    if code == "UPDATE-OK" and not applied:
        code = "UPDATE-HASH"
        outcome = "refused"
        applied = False
    staged = code == "UPDATE-PLATFORM-STAGE" and outcome == "staged"
    staged_dir = decision.get("staged_dir") if isinstance(decision.get("staged_dir"), str) else None
    if staged and staged_dir is not None:
        readback = _read_regular(Path(staged_dir) / "artifact.bin", host.cap)
        raw = _read_regular(Path(staged_dir) / "manifest.json", ENVELOPE_MAX)
        staged_ok = False
        if isinstance(raw, (bytes, bytearray)) and readback is not None:
            try:
                staged_manifest = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                staged_manifest = None
            artifact = staged_manifest.get("artifact") if isinstance(staged_manifest, dict) else None
            staged_ok = bytes_match(readback, artifact)
        if not staged_ok:
            staged = False
            code = "UPDATE-HASH"
            outcome = "refused"
    activated = applied and host.platform == "userspace" and proof is not None
    downloaded = activated or staged
    verified = activated or staged
    mesh_view = {
        "attempted": mesh is not None,
        "code": mesh.get("code") if isinstance(mesh, Mapping) else None,
        "carriers_present": [],
        "hardware": False,
        "radio_phy": False,
        "second_device": False,
        "satellite_relay": "HELD",
        "membership_only": True,
        "reason": None if mesh is not None else "updater is off or trust is not configured",
    }
    internet_view = dict(internet or {"attempted": False, "code": None})
    internet_view["live"] = False
    route = _install_route(host.platform, activated, staged)
    summary = _summary(code, activated, staged, host.platform)
    report = {
        "ok": activated or staged,
        "code": code,
        "applied": applied,
        "downloaded": downloaded,
        "verified": verified,
        "activated": activated,
        "staged": staged,
        "install_route": route,
        "self_patch": False,
        "platform_signature_bypassed": False,
        "platform": host.platform,
        "event": event,
        "live": False,
        "booted": False,
        "hardware": False,
        "kernel": False,
        "installed": False,
        "os_yet": False,
        "one_click_install_live": False,
        "host_os": False,
        "radio_phy": False,
        "second_device": False,
        "satellite_relay": "HELD",
        "membership_only": True,
        "mesh_node_live": True,
        "alt_internet_live": True,
        "packet_path_live": True,
        "qnm_membership": True,
        "qns_cite_plane": False,
        "cap7_registrar_live": False,
        "public_icann": False,
        "configured": trust.get("configured") is True,
        "enabled": host.enabled is True,
        "product": host.product,
        "key_pinned": bool(host.public_key) and trust.get("configured") is True,
        "key_fingerprint": trust.get("key_fingerprint") if trust.get("configured") is True else None,
        "need": list(trust.get("need") or []),
        "recovered": host.recovered,
        "source": row.get("source") if isinstance(row.get("source"), str) else None,
        "outcome": outcome,
        "floor_seq": state.get("floor_seq") if V.sint(state.get("floor_seq")) else None,
        "installed_seq": state.get("installed_seq") if V.sint(state.get("installed_seq")) else None,
        "manifest_hash": state.get("manifest_hash") if isinstance(state.get("manifest_hash"), str) else None,
        "bytes_authenticated": proof is not None,
        "mesh": mesh_view,
        "internet": internet_view,
        "channel": "stable",
        "lock": "update/lock",
        "serialized": True,
        "boundary": list(BOUNDARY),
        "next": list(NEXT),
        "generation": str(current) if current.is_dir() and not _is_symlink(current) and proof is not None else None,
        "display": {
            "title": "Signed update",
            "summary": summary,
            "fields": [
                {"label": "code", "value": code},
                {"label": "activated", "value": activated},
                {"label": "downloaded", "value": downloaded},
                {"label": "verified", "value": verified},
            ],
        },
    }
    return report


def _summary(code: str, activated: bool, staged: bool, platform: str) -> str:
    if activated:
        return "A signed generation is active in the operator tree. The machine did not boot. live stays false."
    if staged:
        return (
            "A signed artifact was checked and staged for "
            + platform
            + ". It was not activated. The bundle was not replaced."
        )
    if code == "UPDATE-OFF":
        return "Signed update is off. Operator trust is not configured."
    if code == "UPDATE-NO-KEY":
        return "Signed update is not ready. The trust anchor has no key for this product."
    if code == "UPDATE-TRUST-REFUSED":
        return "The trust anchor was refused. A private key, a symlink, or a writable trust file is not accepted."
    if code == "UPDATE-NO-RELEASE":
        return "No release asset is configured for this product. Nothing was fetched."
    return f"Signed update did not apply. The reason is {code}."


def _static_report(code: str, event: str, *, configured: bool, refused: bool = False) -> dict[str, Any]:
    summary = _summary(code, False, False, "userspace")
    return {
        "ok": False,
        "code": code,
        "applied": False,
        "downloaded": False,
        "verified": False,
        "activated": False,
        "staged": False,
        "install_route": None,
        "self_patch": False,
        "platform_signature_bypassed": False,
        "platform": "userspace",
        "event": event,
        "live": False,
        "booted": False,
        "hardware": False,
        "kernel": False,
        "installed": False,
        "os_yet": False,
        "one_click_install_live": False,
        "radio_phy": False,
        "second_device": False,
        "satellite_relay": "HELD",
        "membership_only": True,
        "mesh_node_live": True,
        "alt_internet_live": True,
        "packet_path_live": True,
        "qnm_membership": True,
        "qns_cite_plane": False,
        "configured": configured,
        "enabled": False,
        "trust_refused": refused,
        "product": "azinterface",
        "need": list(TRUST_NEED),
        "recovered": None,
        "bytes_authenticated": False,
        "lock": "update/lock",
        "serialized": True,
        "boundary": list(BOUNDARY),
        "next": list(NEXT),
        "display": {"title": "Signed update", "summary": summary, "fields": [{"label": "code", "value": code}]},
    }


def trust_view(root: Path | str) -> dict[str, Any]:
    """Read-only trust report. Does not apply and does not write."""
    trust = load_trust(root)
    enabled = trust.get("enabled") is True and trust.get("trust_refused") is not True and trust.get("configured") is True
    code = trust.get("code")
    if trust.get("trust_refused") is True:
        code = "UPDATE-TRUST-REFUSED"
    elif enabled is not True and trust.get("code") != "UPDATE-NO-KEY":
        code = "UPDATE-OFF"
    return {
        "spec": U.UPDATER_SPEC,
        "configured": trust.get("configured") is True,
        "enabled": enabled,
        "live": False,
        "product": trust.get("product"),
        "platform": trust.get("platform"),
        "key_fingerprint": trust.get("key_fingerprint") if trust.get("configured") is True else None,
        "code": code,
        "radio_phy": False,
        "second_device": False,
        "satellite_relay": "HELD",
        "hardware": False,
        "membership_only": True,
        "need": list(trust.get("need") or []),
    }
