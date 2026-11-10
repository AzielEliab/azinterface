"""Signed install and update adoption.

Keys in this file are generated in the test process and thrown away.
They are not an AZInterface pin and not the runtime pin.
No production URL is fetched.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import tarfile
import threading
import time
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from azinterface import update_verify as V
from azinterface.cli import main
from azinterface.sidenet import signed_update
from azinterface.suite import Suite
from azinterface.update_apply import (
    LOCK_WAIT,
    UpdateLock,
    _NoRedirect,
    _Transport,
    ancestor_verdict,
    apply_candidate,
    bytes_match,
    on_app_lifecycle,
)
from azinterface.update_verify import RELEASE_KEY_FINGERPRINT, RELEASE_PUBLIC_KEY
from azinterface.ui import serve

GIT = "0123456789abcdef0123456789abcdef01234567"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _no_production_network(monkeypatch):
    calls: list[str] = []

    def boom(*_args, **_kwargs):
        calls.append("urllib")
        raise AssertionError("production network")

    monkeypatch.setattr("azinterface.update_apply._urllib_get", boom)
    monkeypatch.setattr("urllib.request.urlopen", boom)
    monkeypatch.delenv("AUTO_UPDATE", raising=False)
    yield calls
    assert calls == []


def _keys():
    private = Ed25519PrivateKey.generate()
    public = V.b64u_encode(private.public_key().public_bytes_raw())
    return private, public


def _sign(private, manifest: dict) -> str:
    return V.b64u_encode(private.sign(V.canon(manifest).encode()))


def _manifest(blob: bytes, *, seq: int, product: str = "azinterface", channel: str = "stable", name: str = "payload.bin") -> dict:
    return {
        "artifact": {"name": name, "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob)},
        "channel": channel,
        "git_sha": GIT,
        "issued_at": "2026-11-10T00:00:00Z",
        "prev_manifest_hash": None,
        "product": product,
        "spec": "AZ-UPDATE-MANIFEST-1.0",
        "version": f"0.{seq}.0",
        "version_seq": seq,
    }


def _trust(root: Path, public: str | None, **extra) -> Path:
    home = root / "update"
    home.mkdir(parents=True, exist_ok=True)
    os.chmod(home, 0o700)
    body = {
        "spec": "AZINTERFACE-UPDATE-TRUST-1.0",
        "product": extra.pop("product", "azinterface"),
        "auto_update": extra.pop("auto_update", True),
    }
    if public is not None:
        body["public_key"] = public
    body.update(extra)
    path = home / "trust.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    os.chmod(path, 0o600)
    return path


def _drop(root: Path, manifest: dict, signature: str, blob: bytes, folder: str = "incoming") -> None:
    directory = root / "update" / folder
    directory.mkdir(parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    manifest_path = directory / "manifest.json"
    sig_path = directory / "manifest.sig"
    artifact = directory / manifest["artifact"]["name"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    sig_path.write_text(signature + "\n", encoding="utf-8")
    artifact.write_bytes(blob)
    os.chmod(manifest_path, 0o644)
    os.chmod(sig_path, 0o644)
    os.chmod(artifact, 0o644)


def _tar(files: dict[str, bytes], *, mode: int = 0o644) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, data in files.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mode = mode
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def _rewind(root: Path, floor: int, installed: int) -> None:
    path = root / "update" / "state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["installed_seq"] = installed
    state["floor_seq"] = floor
    state["manifest_hash"] = None
    state["last_code"] = None
    path.write_text(json.dumps(state), encoding="utf-8")
    os.chmod(path, 0o600)
    incoming = root / "update" / "incoming"
    if incoming.is_dir():
        for child in list(incoming.iterdir()):
            if child.is_file() or child.is_symlink():
                child.unlink()


def _active(root: Path) -> bytes | None:
    path = root / "update" / "generations" / "current" / "artifact.bin"
    if not path.is_file() or path.is_symlink():
        return None
    return path.read_bytes()


def _floor(root: Path):
    path = root / "update" / "state.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("floor_seq")


def _run(root: Path, private, blob: bytes, seq: int, **manifest_kw):
    manifest = _manifest(blob, seq=seq, **manifest_kw)
    _drop(root, manifest, _sign(private, manifest), blob)
    return on_app_lifecycle(root, "cli"), manifest


def test_canon_and_runtime_pin_scope() -> None:
    assert V.canon({"b": 1, "a": "x"}) == '{"a":"x","b":1}'
    assert V.fingerprint(RELEASE_PUBLIC_KEY) == RELEASE_KEY_FINGERPRINT
    assert len(V.b64u(RELEASE_PUBLIC_KEY)) == 32
    assert V.parse_manifest_text('{"version_seq": 1.0}') is None
    assert V.pin_vouches_for("aziel-runtime") is True
    assert V.pin_vouches_for("azinterface") is False
    assert bytes_match(b"", {"size": 0, "sha256": hashlib.sha256(b"").hexdigest()}) is True
    assert bytes_match(b"", {"size": 4, "sha256": hashlib.sha256(b"note").hexdigest()}) is False
    assert bytes_match(b"\x00", {"size": 0, "sha256": hashlib.sha256(b"").hexdigest()}) is False


def test_missing_trust_is_off_and_switch_without_a_key_is_not_ready(tmp_path: Path, monkeypatch) -> None:
    result = on_app_lifecycle(tmp_path, "cli")
    assert result["code"] == "UPDATE-OFF"
    assert result["configured"] is False
    assert result["applied"] is False
    assert result["activated"] is False
    assert result["live"] is False
    assert result["booted"] is False
    assert result["installed"] is False
    assert result["event"] == "cli"
    assert "trust.json" in "\n".join(result["need"])
    assert any(RELEASE_KEY_FINGERPRINT in item for item in result["need"])
    monkeypatch.setenv("AUTO_UPDATE", "on")
    switched = on_app_lifecycle(tmp_path, "cli")
    assert switched["code"] == "UPDATE-NO-KEY"
    assert switched["enabled"] is True
    assert switched["configured"] is False
    assert switched["applied"] is False
    assert switched["live"] is False


def test_private_key_field_is_not_echoed(tmp_path: Path) -> None:
    sentinel = "SENTINEL-PRIVATE-KEY-MATERIAL"
    path = _trust(tmp_path, "abc")
    body = json.loads(path.read_text(encoding="utf-8"))
    body["private_key"] = sentinel
    path.write_text(json.dumps(body), encoding="utf-8")
    os.chmod(path, 0o600)
    result = on_app_lifecycle(tmp_path, "cli")
    assert result["code"] == "UPDATE-TRUST-REFUSED"
    assert result["configured"] is False
    assert result["applied"] is False
    assert sentinel not in json.dumps(result)


def test_runtime_pin_does_not_vouch_for_azinterface(tmp_path: Path) -> None:
    _trust(tmp_path, RELEASE_PUBLIC_KEY, product="azinterface")
    result = on_app_lifecycle(tmp_path, "cli")
    assert result["code"] == "UPDATE-NO-KEY"
    assert result["configured"] is False
    assert result["applied"] is False
    assert result["key_pinned"] is False


def test_offline_generation_activates_without_booting(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    blob = b"note"
    result, _manifest_row = _run(tmp_path, private, blob, 4)
    assert result["code"] == "UPDATE-OK"
    assert result["activated"] is True
    assert result["downloaded"] is True
    assert result["verified"] is True
    assert result["applied"] is True
    assert result["floor_seq"] == 4
    assert result["installed_seq"] == 4
    assert result["live"] is False
    assert result["booted"] is False
    assert result["installed"] is False
    assert result["os_yet"] is False
    assert result["one_click_install_live"] is False
    assert result["hardware"] is False
    assert result["radio_phy"] is False
    assert result["second_device"] is False
    assert result["satellite_relay"] == "HELD"
    assert result["membership_only"] is True
    assert result["mesh"]["carriers_present"] == []
    assert _active(tmp_path) == blob
    tree = tmp_path / "update" / "generations" / "current" / "tree" / "payload"
    assert tree.read_bytes() == blob


def test_switch_off_does_not_adopt(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public, auto_update=False)
    result, _manifest_row = _run(tmp_path, private, b"note", 3)
    assert result["code"] == "UPDATE-OFF"
    assert result["activated"] is False
    assert result["applied"] is False
    assert _active(tmp_path) is None


def test_exact_empty_is_valid_and_other_empty_bytes_are_not(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    adopted, _manifest_row = _run(tmp_path, private, b"", 1)
    assert adopted["code"] == "UPDATE-OK"
    assert _active(tmp_path) == b""
    artifact = tmp_path / "update" / "generations" / "current" / "artifact.bin"
    artifact.write_bytes(b"\x00")
    _rewind(tmp_path, 0, 0)
    poisoned = on_app_lifecycle(tmp_path, "cli")
    assert poisoned["recovered"] == "current-rejected"
    assert poisoned["code"] != "UPDATE-OK"
    assert poisoned["installed_seq"] in (None, 0)
    assert _floor(tmp_path) in (None, 0)
    assert _active(tmp_path) != b"\x00"

    seq = 1
    for length in (1, 4, 32):
        payload = bytes(range(length))
        seq += 1
        _run(tmp_path, private, payload, seq)
        current = tmp_path / "update" / "generations" / "current" / "artifact.bin"
        current.write_bytes(b"")
        _rewind(tmp_path, 0, 0)
        emptied = on_app_lifecycle(tmp_path, "cli")
        assert emptied["recovered"] != "commit-finished"
        assert emptied["code"] != "UPDATE-OK"
        assert emptied["installed_seq"] in (None, 0)
        assert _floor(tmp_path) in (None, 0)
        assert _active(tmp_path) != b""
        seq += 1
        _run(tmp_path, private, payload, seq)
        current = tmp_path / "update" / "generations" / "current" / "artifact.bin"
        current.write_bytes(payload[:-1])
        _rewind(tmp_path, seq, seq)
        truncated = on_app_lifecycle(tmp_path, "cli")
        assert truncated["applied"] is False
        assert truncated["activated"] is False
        assert _floor(tmp_path) == seq
        assert _active(tmp_path) != payload[:-1]
        seq += 1
        _run(tmp_path, private, payload, seq)
        missing = tmp_path / "update" / "generations" / "current" / "artifact.bin"
        missing.unlink()
        _rewind(tmp_path, seq, seq)
        gone = on_app_lifecycle(tmp_path, "cli")
        assert gone["recovered"] == "current-rejected"
        assert gone["applied"] is False
        assert _floor(tmp_path) == seq


def test_exact_empty_recovers_when_the_bytes_still_match(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    _run(tmp_path, private, b"", 2)
    _rewind(tmp_path, 0, 0)
    recovered = on_app_lifecycle(tmp_path, "cli")
    assert recovered["recovered"] == "commit-finished"
    assert recovered["floor_seq"] == 2
    assert _active(tmp_path) == b""


def test_tamper_downgrade_and_bad_signature_keep_the_floor(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    _run(tmp_path, private, b"good", 5)
    manifest = _manifest(b"good", seq=6)
    signature = _sign(private, manifest)
    _drop(tmp_path, manifest, signature, b"baad")
    tampered = on_app_lifecycle(tmp_path, "cli")
    assert tampered["code"] == "UPDATE-HASH"
    assert _floor(tmp_path) == 5
    assert _active(tmp_path) == b"good"
    _run(tmp_path, private, b"good", 5)
    again = on_app_lifecycle(tmp_path, "cli")
    assert again["code"] == "UPDATE-DOWNGRADE"
    assert _floor(tmp_path) == 5
    bad = _sign(private, _manifest(b"next", seq=7)) + "AA"
    _drop(tmp_path, _manifest(b"next", seq=7), bad, b"next")
    refused = on_app_lifecycle(tmp_path, "cli")
    assert refused["code"] == "UPDATE-SIG"
    assert _floor(tmp_path) == 5
    assert _active(tmp_path) == b"good"


def test_channel_path_symlink_and_setuid_do_not_escape(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    rc = _manifest(b"rc", seq=1, channel="rc")
    _drop(tmp_path, rc, _sign(private, rc), b"rc")
    assert on_app_lifecycle(tmp_path, "cli")["code"] == "UPDATE-CHANNEL-REFUSED"
    outside = tmp_path / "outside.txt"
    blob = io.BytesIO()
    with tarfile.open(fileobj=blob, mode="w") as archive:
        info = tarfile.TarInfo("../outside.txt")
        info.size = 4
        archive.addfile(info, io.BytesIO(b"leak"))
        link = tarfile.TarInfo("link")
        link.type = tarfile.SYMTYPE
        link.linkname = "outside.txt"
        archive.addfile(link)
    raw = blob.getvalue()
    escaped = _manifest(raw, seq=2, name="escape.tar")
    _drop(tmp_path, escaped, _sign(private, escaped), raw)
    path = on_app_lifecycle(tmp_path, "cli")
    assert path["code"] == "UPDATE-PATH"
    assert path["activated"] is False
    assert not outside.exists()
    sticky = _tar({"hello.txt": b"nope"}, mode=0o4755)
    sticky_manifest = _manifest(sticky, seq=3, name="sticky.tar")
    _drop(tmp_path, sticky_manifest, _sign(private, sticky_manifest), sticky)
    assert on_app_lifecycle(tmp_path, "cli")["code"] == "UPDATE-PATH"
    link_only = io.BytesIO()
    with tarfile.open(fileobj=link_only, mode="w") as archive:
        link = tarfile.TarInfo("alone")
        link.type = tarfile.SYMTYPE
        link.linkname = "/tmp"
        archive.addfile(link)
    raw_link = link_only.getvalue()
    link_manifest = _manifest(raw_link, seq=4, name="link.tar")
    _drop(tmp_path, link_manifest, _sign(private, link_manifest), raw_link)
    assert on_app_lifecycle(tmp_path, "cli")["code"] == "UPDATE-PATH"
    assert _active(tmp_path) is None


def test_tree_bytes_must_match_the_signed_artifact(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    blob = _tar({"hello.txt": b"signed\n"})
    manifest = _manifest(blob, seq=3, name="tree.tar")
    _drop(tmp_path, manifest, _sign(private, manifest), blob)
    adopted = on_app_lifecycle(tmp_path, "cli")
    assert adopted["code"] == "UPDATE-OK"
    hello = tmp_path / "update" / "generations" / "current" / "tree" / "hello.txt"
    assert hello.read_bytes() == b"signed\n"
    hello.write_bytes(b"tampered\n")
    _rewind(tmp_path, 3, 3)
    rejected = on_app_lifecycle(tmp_path, "cli")
    assert rejected["applied"] is False
    assert rejected["activated"] is False
    assert rejected["recovered"] == "current-rejected"
    assert _floor(tmp_path) == 3
    assert not hello.exists() or hello.read_bytes() != b"tampered\n"


def test_interrupt_discards_staging_and_keeps_the_floor(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    _run(tmp_path, private, b"kept", 2)
    blob = _tar({"a.txt": b"one", "b.txt": b"two"})
    manifest = _manifest(blob, seq=3, name="split.tar")
    _drop(tmp_path, manifest, _sign(private, manifest), blob)

    def after_member(_count: int) -> None:
        raise RuntimeError("interrupt")

    stopped = on_app_lifecycle(tmp_path, "cli", {"after_member": after_member})
    assert stopped["code"] == "UPDATE-HEALTH"
    assert _floor(tmp_path) == 2
    assert _active(tmp_path) == b"kept"
    assert not (tmp_path / "update" / "generations" / "staging").exists()


def test_crash_after_a_good_swap_finishes_without_lowering_the_floor(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    _run(tmp_path, private, b"kept", 4)
    _run(tmp_path, private, b"newer", 7)
    _rewind(tmp_path, 4, 4)
    (tmp_path / "update" / "generations" / "current" / "artifact.bin").write_bytes(b"newer")
    recovered = on_app_lifecycle(tmp_path, "cli")
    assert recovered["recovered"] == "commit-finished"
    assert recovered["floor_seq"] == 7
    assert _active(tmp_path) == b"newer"
    _rewind(tmp_path, 7, 7)
    state = tmp_path / "update" / "state.json"
    state.write_text("{", encoding="utf-8")
    os.chmod(state, 0o600)
    _drop(tmp_path, *_signed(private, b"later", 8))
    corrupt = on_app_lifecycle(tmp_path, "cli")
    assert corrupt["code"] == "UPDATE-STATE"
    assert state.read_text(encoding="utf-8").startswith("{")
    assert "later" not in state.read_text(encoding="utf-8")


def _signed(private, blob: bytes, seq: int):
    manifest = _manifest(blob, seq=seq)
    return manifest, _sign(private, manifest), blob


def test_paused_and_oversized_fail_closed(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public, max_bytes=64)
    _run(tmp_path, private, b"kept", 2)
    state_path = tmp_path / "update" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["paused"] = True
    state_path.write_text(json.dumps(state), encoding="utf-8")
    os.chmod(state_path, 0o600)
    paused, _manifest_row = _run(tmp_path, private, b"next", 3)
    assert paused["code"] == "UPDATE-PAUSED"
    assert _floor(tmp_path) == 2
    assert _active(tmp_path) == b"kept"
    state["paused"] = False
    state_path.write_text(json.dumps(state), encoding="utf-8")
    os.chmod(state_path, 0o600)
    huge = b"h" * 80
    manifest = _manifest(huge, seq=4)
    artifact = tmp_path / "update" / "incoming" / manifest["artifact"]["name"]
    _drop(tmp_path, manifest, _sign(private, manifest), huge)
    os.chmod(artifact, 0)
    bounded = on_app_lifecycle(tmp_path, "cli")
    assert bounded["code"] == "UPDATE-BOUND"
    assert _floor(tmp_path) == 2
    os.chmod(artifact, 0o644)


def test_mesh_inbox_is_not_a_radio(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    manifest = _manifest(b"peer", seq=2)
    _drop(tmp_path, manifest, _sign(private, manifest), b"peer", folder="peer-inbox")
    result = signed_update(tmp_path)
    assert result["code"] == "UPDATE-OK"
    assert result["source"] == "mesh:file"
    assert result["activated"] is True
    assert result["hardware"] is False
    assert result["radio_phy"] is False
    assert result["second_device"] is False
    assert result["satellite_relay"] == "HELD"
    assert result["membership_only"] is True
    assert result["sidenet"] == "AZINTERFACE-SIDENET-1.0"
    assert result["mesh"]["carriers_present"] == []
    assert result["mesh"]["code"] == "UPDATE-CARRIER-ABSENT"
    lan = apply_candidate(tmp_path, manifest, _sign(private, manifest), b"peer", "mesh:lan")
    assert lan["hardware"] is False
    assert lan["second_device"] is False
    assert lan["code"] == "UPDATE-DOWNGRADE"


def test_internet_uses_the_injected_opener_only(tmp_path: Path) -> None:
    private, public = _keys()
    blob = b"from-net"
    manifest = _manifest(blob, seq=2)
    signature = _sign(private, manifest)
    release = "https://updates.example/envelope.json"
    artifact = "https://updates.example/payload.bin"
    _trust(tmp_path, public, release_url=release)
    seen: list[str] = []

    def opener(url, _timeout):
        seen.append(url)
        if url == release:
            return json.dumps({"manifest": manifest, "signature": signature, "url": artifact}).encode()
        if url == artifact:
            return blob
        raise AssertionError(url)

    adopted = on_app_lifecycle(tmp_path, "cli", {"opener": opener})
    assert adopted["code"] == "UPDATE-OK"
    assert adopted["activated"] is True
    assert seen == [release, artifact]
    assert _active(tmp_path) == blob
    _trust(tmp_path, public, release_url="http://updates.example/envelope.json")
    def refuse(_url, _timeout):
        raise AssertionError("http was fetched")

    offline = on_app_lifecycle(tmp_path, "cli", {"opener": refuse})
    assert offline["code"] == "UPDATE-NO-RELEASE"
    assert offline["internet"]["attempted"] is False
    with pytest.raises(_Transport):
        _NoRedirect().redirect_request(None, None, 302, "found", {}, "https://updates.example/next")


def test_established_runtime_release_without_an_asset_is_not_invented(tmp_path: Path) -> None:
    _trust(tmp_path, None, product="aziel-runtime", established_runtime_release=True)
    seen: list[str] = []

    def opener(url, _timeout):
        seen.append(url)
        return json.dumps({"tag_name": "v0", "draft": False, "prerelease": False, "assets": []}).encode()

    result = on_app_lifecycle(tmp_path, "cli", {"opener": opener})
    assert result["code"] == "UPDATE-NO-RELEASE"
    assert result["applied"] is False
    assert result["product"] == "aziel-runtime"
    assert seen == ["https://api.github.com/repos/AzielEliab/aziel-runtime/releases/latest"]
    _trust(tmp_path, None, product="azinterface", established_runtime_release=True)
    def unused(_url, _timeout):
        raise AssertionError("azinterface invented a runtime fetch")

    local = on_app_lifecycle(tmp_path, "cli", {"opener": unused})
    assert local["code"] == "UPDATE-NO-KEY"
    assert local["configured"] is False


def test_store_and_worker_stage_without_activating(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public, platform="android")
    result, _manifest_row = _run(tmp_path, private, b"phone", 2)
    assert result["code"] == "UPDATE-PLATFORM-STAGE"
    assert result["downloaded"] is True
    assert result["verified"] is True
    assert result["activated"] is False
    assert result["applied"] is False
    assert result["install_route"] == "system"
    assert result["self_patch"] is False
    assert result["platform_signature_bypassed"] is False
    assert result["floor_seq"] in (None, 0)
    assert _active(tmp_path) is None
    staged = tmp_path / "update" / "staged" / "2" / "artifact.bin"
    assert staged.read_bytes() == b"phone"
    forced = on_app_lifecycle(tmp_path, "cli", {"platform": "userspace"})
    assert forced["activated"] is False
    assert forced["platform"] == "android"
    _trust(tmp_path, public, platform="worker")
    worker, _manifest_row = _run(tmp_path, private, b"worker", 3)
    assert worker["install_route"] == "unsupported"
    assert worker["activated"] is False
    assert worker["verified"] is True


def test_mode_0777_ancestor_does_not_activate(tmp_path: Path) -> None:
    private, public = _keys()
    _trust(tmp_path, public)
    os.chmod(tmp_path, 0o777)
    result, _manifest_row = _run(tmp_path, private, b"ancestor", 1)
    assert result["code"] == "UPDATE-TRUST-REFUSED"
    assert result["configured"] is False
    assert result["applied"] is False
    assert result["activated"] is False
    assert public not in json.dumps(result)
    assert _active(tmp_path) is None
    os.chmod(tmp_path, 0o775)
    grouped = on_app_lifecycle(tmp_path, "cli")
    assert grouped["code"] == "UPDATE-TRUST-REFUSED"
    assert grouped["activated"] is False


def test_sticky_ancestor_is_a_boundary_and_a_symlink_ancestor_is_refused(tmp_path: Path) -> None:
    private, public = _keys()
    sticky = tmp_path / "sticky"
    sticky.mkdir()
    os.chmod(sticky, 0o1777)
    app = sticky / "app"
    app.mkdir(mode=0o700)
    os.chmod(app, 0o700)
    _trust(app, public)
    adopted, _manifest_row = _run(app, private, b"inside-sticky", 1)
    assert adopted["code"] == "UPDATE-OK"
    assert adopted["activated"] is True
    assert _active(app) == b"inside-sticky"
    real = tmp_path / "real"
    real.mkdir(mode=0o700)
    os.chmod(real, 0o700)
    _trust(real, public)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    refused, _manifest_row = _run(link, private, b"via-link", 1)
    assert refused["code"] == "UPDATE-TRUST-REFUSED"
    assert refused["activated"] is False
    assert _active(real) is None


def test_ancestor_verdict_refuses_another_non_root_owner() -> None:
    assert ancestor_verdict(0o40777, 1000, 1000) == "unsafe"
    assert ancestor_verdict(0o40775, 1000, 1000) == "unsafe"
    assert ancestor_verdict(0o40755, 50, 1000) == "unsafe"
    assert ancestor_verdict(0o40755, 0, 1000) == "continue"
    assert ancestor_verdict(0o41777, 0, 1000) == "boundary"
    assert ancestor_verdict(0o41777, 1000, 1000) == "continue"
    assert ancestor_verdict(0o40700, 1000, 1000) == "continue"


def test_self_owned_sticky_does_not_hide_a_world_writable_parent(tmp_path: Path) -> None:
    private, public = _keys()
    loose = tmp_path / "loose"
    loose.mkdir()
    os.chmod(loose, 0o777)
    sticky = loose / "sticky"
    sticky.mkdir()
    os.chmod(sticky, 0o1777)
    app = sticky / "app"
    app.mkdir(mode=0o700)
    os.chmod(app, 0o700)
    _trust(app, public)
    result, _manifest_row = _run(app, private, b"swapped", 1)
    assert result["code"] == "UPDATE-TRUST-REFUSED"
    assert result["applied"] is False
    assert result["activated"] is False
    assert public not in json.dumps(result)
    assert _active(app) is None


def test_parent_chmod_inside_the_lock_blocks_the_rename(tmp_path: Path) -> None:
    private, public = _keys()
    app = tmp_path / "app"
    app.mkdir()
    os.chmod(app, 0o755)
    _trust(app, public)
    blob = b"late-chmod"
    manifest = _manifest(blob, seq=1)
    _drop(app, manifest, _sign(private, manifest), blob)

    def before_ready(_staging: Path) -> None:
        os.chmod(app, 0o777)

    result = on_app_lifecycle(app, "cli", {"before_ready": before_ready})
    assert result["code"] == "UPDATE-TRUST-REFUSED"
    assert result["applied"] is False
    assert result["activated"] is False
    assert _active(app) is None
    assert _floor(app) in (None, 0)


def test_trust_anchor_refuses_group_write_symlink_and_other_owner(tmp_path: Path, monkeypatch) -> None:
    private, public = _keys()
    blob = _tar({"hello.txt": b"secret-path\n"})
    manifest = _manifest(blob, seq=1, name="hello.tar")
    path = _trust(tmp_path, public)
    path.chmod(0o666)
    _drop(tmp_path, manifest, _sign(private, manifest), blob)
    refused = on_app_lifecycle(tmp_path, "cli")
    assert refused["code"] == "UPDATE-TRUST-REFUSED"
    assert refused["configured"] is False
    assert refused["applied"] is False
    assert public not in json.dumps(refused)
    assert not (tmp_path / "update" / "generations" / "current" / "tree" / "hello.txt").exists()
    path.chmod(0o600)
    directory = path.parent
    directory.chmod(0o777)
    open_dir = on_app_lifecycle(tmp_path, "cli")
    assert open_dir["code"] == "UPDATE-TRUST-REFUSED"
    assert open_dir["applied"] is False
    directory.chmod(0o700)
    linked = tmp_path / "elsewhere-trust.json"
    linked.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(linked, 0o600)
    path.unlink()
    path.symlink_to(linked)
    assert on_app_lifecycle(tmp_path, "cli")["code"] == "UPDATE-TRUST-REFUSED"
    path.unlink()
    path.write_text(linked.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(path, 0o600)
    real = os.geteuid()
    monkeypatch.setattr(os, "geteuid", lambda: real + 1)
    owned = on_app_lifecycle(tmp_path, "cli")
    assert owned["code"] == "UPDATE-TRUST-REFUSED"
    assert owned["applied"] is False
    assert owned["configured"] is False


def _apply_job(root: str, manifest: dict, signature: str, blob: bytes, sink) -> None:
    from azinterface.update_apply import apply_candidate as adopt_one

    result = adopt_one(root, manifest, signature, blob, "offline")
    sink.put((result.get("code"), result.get("floor_seq"), result.get("installed_seq")))


def _hold_lock(home: str, ready: str, seconds: float) -> None:
    lock = UpdateLock(Path(home))
    assert lock.acquire(wait=0.2)
    Path(ready).write_text("held", encoding="utf-8")
    try:
        time.sleep(seconds)
    finally:
        lock.release()


def _hold_until_killed(home: str, ready: str) -> None:
    lock = UpdateLock(Path(home))
    assert lock.acquire(wait=0.2)
    Path(ready).write_text("held", encoding="utf-8")
    time.sleep(30)


def test_concurrent_updates_share_a_lock_and_a_killed_holder_does_not_stick(tmp_path: Path) -> None:
    import multiprocessing

    private, public = _keys()
    _trust(tmp_path, public)
    low = b"low-seq"
    high = b"high-seq-bytes"
    low_manifest = _manifest(low, seq=2, name="low.bin")
    high_manifest = _manifest(high, seq=6, name="high.bin")
    ctx = multiprocessing.get_context("fork")
    sink = ctx.Queue()
    env_root = str(ROOT)
    previous_path = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = env_root if not previous_path else env_root + os.pathsep + previous_path
    first = ctx.Process(target=_apply_job, args=(str(tmp_path), low_manifest, _sign(private, low_manifest), low, sink))
    second = ctx.Process(target=_apply_job, args=(str(tmp_path), high_manifest, _sign(private, high_manifest), high, sink))
    first.start()
    second.start()
    first.join(15)
    second.join(15)
    assert first.exitcode == 0 and second.exitcode == 0
    codes = [sink.get(timeout=5), sink.get(timeout=5)]
    assert _floor(tmp_path) == 6
    assert _active(tmp_path) == high
    assert any(item[0] == "UPDATE-OK" for item in codes)
    assert all(item[1] is None or item[1] <= 6 for item in codes)
    same = b"same-bytes"
    same_manifest = _manifest(same, seq=8, name="same.bin")
    same_sig = _sign(private, same_manifest)
    again = ctx.Queue()
    left = ctx.Process(target=_apply_job, args=(str(tmp_path), same_manifest, same_sig, same, again))
    right = ctx.Process(target=_apply_job, args=(str(tmp_path), same_manifest, same_sig, same, again))
    left.start()
    right.start()
    left.join(15)
    right.join(15)
    assert left.exitcode == 0 and right.exitcode == 0
    pair = [again.get(timeout=5)[0], again.get(timeout=5)[0]]
    assert pair.count("UPDATE-OK") == 1
    assert "UPDATE-DOWNGRADE" in pair
    assert _floor(tmp_path) == 8
    assert _active(tmp_path) == same
    ready = tmp_path / "lock-ready"
    holder = ctx.Process(target=_hold_lock, args=(str(tmp_path / "update"), str(ready), LOCK_WAIT + 1.5))
    holder.start()
    for _ in range(50):
        if ready.is_file():
            break
        time.sleep(0.05)
    blocked = on_app_lifecycle(tmp_path, "cli")
    assert blocked["code"] == "UPDATE-LOCK"
    assert blocked["applied"] is False
    assert blocked["activated"] is False
    previous_home = os.environ.get("AZINTERFACE_HOME")
    os.environ["AZINTERFACE_HOME"] = str(tmp_path)
    try:
        cli_blocked = main(["update", "--json"])
    finally:
        if previous_home is None:
            os.environ.pop("AZINTERFACE_HOME", None)
        else:
            os.environ["AZINTERFACE_HOME"] = previous_home
        if previous_path is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = previous_path
    assert _floor(tmp_path) == 8
    assert _active(tmp_path) == same
    holder.join(10)
    assert cli_blocked == 2
    crashed = ctx.Process(target=_hold_until_killed, args=(str(tmp_path / "update"), str(ready)))
    ready.unlink()
    crashed.start()
    for _ in range(50):
        if ready.is_file():
            break
        time.sleep(0.05)
    assert crashed.pid is not None
    os.kill(crashed.pid, 9)
    crashed.join(10)
    resumed = on_app_lifecycle(tmp_path, "sidenet")
    assert resumed["code"] != "UPDATE-LOCK"
    assert _floor(tmp_path) == 8
    assert _active(tmp_path) == same


def test_cli_sidenet_suite_and_ui_call_the_same_check(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AZINTERFACE_HOME", str(tmp_path))
    assert main(["update", "--json"]) == 2
    body = json.loads(capsys.readouterr().out)
    assert body["event"] == "cli"
    assert body["code"] == "UPDATE-OFF"
    assert body["live"] is False
    assert (tmp_path / "update" / "lock").is_file()
    assert main(["node", "update", "--json"]) == 2
    side = json.loads(capsys.readouterr().out)
    assert side["event"] == "sidenet"
    assert side["code"] == "UPDATE-OFF"
    assert side["sidenet"] == "AZINTERFACE-SIDENET-1.0"
    assert side["radio_phy"] is False
    suite = Suite(refresh=False, vendor=tmp_path / "vendor", catalog=[])
    suite.start()
    report = None
    for _ in range(100):
        report = suite.update_report
        if report is not None and suite._job is False:
            break
        time.sleep(0.02)
    assert report is not None
    assert report["event"] == "suite-start"
    assert report["code"] == "UPDATE-OFF"
    seen: dict[str, object] = {}

    def ready(result, httpd) -> None:
        seen["result"] = result
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    serve(port=0, ready=ready)
    assert seen["result"]["event"] == "ui-start"
    assert seen["result"]["code"] == "UPDATE-OFF"
    assert seen["result"]["live"] is False
