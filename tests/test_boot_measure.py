"""Boot self-measure: match, mismatch, missing manifest, and a dropped hash."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from azinterface import update_verify as V
from azinterface.boot_measure import SPEC, compare_release, hash_tree, markup, measure_root, startup_measure
from azinterface.honesty import standing_facts
from azinterface.suite_page import suite_html
from azinterface.ui import make_server
from azinterface.web_page import home_html


def _keys():
    private = Ed25519PrivateKey.generate()
    public = V.b64u_encode(private.public_key().public_bytes_raw())
    return private, public


def _sign(private, manifest: dict) -> str:
    return V.b64u_encode(private.sign(V.canon(manifest).encode()))


def _install(tmp_path: Path) -> Path:
    root = tmp_path / "app"
    (root / "nested").mkdir(parents=True)
    (root / "app.txt").write_bytes(b"hello")
    (root / "nested" / "b.txt").write_bytes(b"world")
    return root


def _manifest(root: Path) -> dict:
    files, code = hash_tree(root)
    assert code is None and files
    return {"files": files, "product": "azinterface", "spec": SPEC}


def _publish(root: Path, manifest: dict, signature: str) -> None:
    (root / "boot-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "boot-manifest.sig").write_text(signature + "\n", encoding="utf-8")


def _trust(home: Path, public: str) -> None:
    home.mkdir(parents=True, exist_ok=True)
    os.chmod(home, 0o700)
    update = home / "update"
    update.mkdir(parents=True, exist_ok=True)
    os.chmod(update, 0o700)
    path = update / "trust.json"
    path.write_text(
        json.dumps({"spec": "AZINTERFACE-UPDATE-TRUST-1.0", "product": "azinterface", "public_key": public, "auto_update": False}),
        encoding="utf-8",
    )
    os.chmod(path, 0o600)


def test_match_is_verified_only_when_the_signature_and_files_agree(tmp_path: Path) -> None:
    root = _install(tmp_path)
    private, public = _keys()
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest))
    report = measure_root(root, public_key=public)
    assert report["status"] == "verified"
    assert report["verified"] is True
    assert report["signature_ok"] is True
    assert report["hashed"] is True
    assert report["hash_dropped"] is False
    assert report["code"] == "BOOT-MEASURE-VERIFIED"
    assert report["file_count"] == 2
    assert report["sentence"].startswith("Boot measure: verified.")
    assert report["mesh_node_live"] is True
    assert report["alt_internet_live"] is True
    assert report["packet_path_live"] is True
    assert report["cap7_registrar_live"] is False
    assert report["public_icann"] is False
    assert report["satellite_relay"] == "HELD"
    assert report["paid_satellite"] == "HELD"
    assert report["remain_off"] is True
    assert report["installed"] is False
    assert report["booted"] is False
    assert report["live"] is False


def test_mismatch_when_an_installed_file_changes(tmp_path: Path) -> None:
    root = _install(tmp_path)
    private, public = _keys()
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest))
    (root / "app.txt").write_bytes(b"hello!")
    report = measure_root(root, public_key=public)
    assert report["status"] == "mismatch"
    assert report["verified"] is False
    assert report["signature_ok"] is True
    assert report["hash_dropped"] is False
    assert report["code"] == "BOOT-MEASURE-MISMATCH"
    assert report["sentence"].startswith("Boot measure: mismatch.")
    assert not report["sentence"].startswith("Boot measure: verified")


def test_missing_manifest_is_unknown_and_not_verified(tmp_path: Path) -> None:
    root = _install(tmp_path)
    report = measure_root(root)
    assert report["status"] == "unknown"
    assert report["verified"] is False
    assert report["signature_ok"] is False
    assert report["manifest_present"] is False
    assert report["hash_dropped"] is False
    assert report["hashed"] is True
    assert report["code"] == "BOOT-MEASURE-NO-MANIFEST"
    assert report["file_count"] == 2
    assert report["sentence"].startswith("Boot measure: unknown.")
    assert "Boot measure: verified" not in report["sentence"]


def test_dropped_hash_does_not_fall_back_to_verified(tmp_path: Path) -> None:
    root = _install(tmp_path)
    private, public = _keys()
    manifest = _manifest(root)
    signature = _sign(private, manifest)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"secret")
    (root / "link.txt").symlink_to(outside)
    dropped = measure_root(root, public_key=public)
    assert dropped["status"] == "unknown"
    assert dropped["verified"] is False
    assert dropped["hash_dropped"] is True
    assert dropped["hashed"] is False
    assert dropped["tree_sha256"] is None
    assert dropped["file_count"] == 0
    assert dropped["code"] == "BOOT-MEASURE-UNSAFE"
    assert dropped["sentence"].startswith("Boot measure: unknown.")
    # A signed manifest of the readable files must not be consulted after the hash is dropped.
    fallback = compare_release(
        manifest["files"],
        manifest,
        signature,
        public,
        hashed=False,
        read_code="BOOT-MEASURE-UNREADABLE",
        manifest_present=True,
    )
    assert fallback["status"] == "unknown"
    assert fallback["verified"] is False
    assert fallback["hash_dropped"] is True
    assert fallback["code"] == "BOOT-MEASURE-UNREADABLE"
    assert fallback["code"] != "BOOT-MEASURE-VERIFIED"
    assert fallback["code"] != "BOOT-MEASURE-MISMATCH"


def test_bad_signature_and_runtime_pin_cannot_become_verified(tmp_path: Path) -> None:
    root = _install(tmp_path)
    private, public = _keys()
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest)[:-4] + "AAAA")
    bad = measure_root(root, public_key=public)
    assert bad["status"] == "unknown"
    assert bad["verified"] is False
    assert bad["code"] == "BOOT-MEASURE-UNSIGNED"
    pinned = compare_release(manifest["files"], manifest, _sign(private, manifest), V.RELEASE_PUBLIC_KEY, manifest_present=True)
    assert pinned["status"] == "unknown"
    assert pinned["verified"] is False
    assert pinned["code"] == "BOOT-MEASURE-KEY-SCOPE"
    still = measure_root(root, public_key=public)
    assert still["verified"] is False
    assert still["status"] == "unknown"


def test_this_install_hashes_and_stays_unknown() -> None:
    before = standing_facts()
    report = startup_measure()
    after = standing_facts()
    assert before["mesh_node_live"] is True and after["mesh_node_live"] is True
    assert before["alt_internet_live"] is True and after["alt_internet_live"] is True
    assert before["packet_path_live"] is True and after["packet_path_live"] is True
    assert report["status"] == "unknown"
    assert report["verified"] is False
    assert report["hashed"] is True
    assert report["hash_dropped"] is False
    assert report["file_count"] >= 1
    page = suite_html(port=8880, vendor="vendor")
    assert 'id="boot-measure"' in page
    assert 'data-status="unknown"' in page
    assert "The installed files were hashed." in page
    assert "Boot measure: verified" not in page
    public = home_html(views=1, downloads=2, github={"stars": 0})
    assert 'id="boot-measure"' in public
    assert 'data-status="unknown"' in public
    assert "The file hash was not completed." in public
    assert "Boot measure: verified" not in public
    forged = markup({"status": "verified", "verified": True, "signature_ok": False, "hashed": False, "hash_dropped": True, "manifest_present": True})
    assert 'data-status="unknown"' in forged
    assert "Boot measure: verified" not in forged


def test_api_returns_the_startup_measure_and_ignores_a_posted_verified(monkeypatch) -> None:
    monkeypatch.setattr("azinterface.suite._fetch_live", lambda: None)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.loads(urlopen(f"http://127.0.0.1:{port}/v1/boot_measure").read().decode())
        home = json.loads(urlopen(Request(f"http://127.0.0.1:{port}/", headers={"Accept": "application/json"})).read().decode())
        page = urlopen(Request(f"http://127.0.0.1:{port}/", headers={"Accept": "text/html"})).read().decode()
        try:
            urlopen(
                Request(
                    f"http://127.0.0.1:{port}/v1/boot_measure",
                    data=b'{"status":"verified","verified":true}',
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
            )
            raise AssertionError("POST was allowed")
        except HTTPError as exc:
            assert exc.code == 405
            posted = json.loads(exc.read().decode())
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert body["status"] == "unknown"
    assert body["verified"] is False
    assert body["hashed"] is True
    assert body["hash_dropped"] is False
    assert body["file_count"] > 0
    assert body["mesh_node_live"] is True
    assert body["alt_internet_live"] is True
    assert body["packet_path_live"] is True
    assert body["cap7_registrar_live"] is False
    assert body["satellite_relay"] == "HELD"
    assert home["boot_measure"]["status"] == "unknown"
    assert home["boot_measure"]["verified"] is False
    assert 'data-status="unknown"' in page
    assert "Boot measure: verified" not in page
    assert posted["status"] == "unknown"
    assert posted["verified"] is False
    assert posted["code"] == "BOOT-MEASURE-METHOD"
    assert posted != body


def test_key_inside_the_install_cannot_verify(tmp_path: Path) -> None:
    """An attacker-signed manifest and public key beside the app files stay unknown."""
    root = _install(tmp_path)
    (root / "__init__.py").write_bytes(b"tampered")
    private, public = _keys()
    (root / "boot-measure.pub").write_text(public + "\n", encoding="utf-8")
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest))
    report = measure_root(root)
    assert report["status"] == "unknown"
    assert report["verified"] is False
    assert report["signature_ok"] is False
    assert "Boot measure: verified" not in report["sentence"]

    planted = _install(tmp_path / "planted")
    (planted / "__init__.py").write_bytes(b"tampered")
    update = planted / "update"
    update.mkdir()
    os.chmod(update, 0o700)
    trust = update / "trust.json"
    trust.write_text(
        json.dumps({"spec": "AZINTERFACE-UPDATE-TRUST-1.0", "product": "azinterface", "public_key": public, "auto_update": False}),
        encoding="utf-8",
    )
    os.chmod(trust, 0o600)
    planted_manifest = _manifest(planted)
    _publish(planted, planted_manifest, _sign(private, planted_manifest))
    inside = measure_root(planted, trust_root=planted)
    assert inside["status"] == "unknown"
    assert inside["verified"] is False
    assert inside["signature_ok"] is False


def test_external_trust_root_verifies_when_it_is_outside_the_install(tmp_path: Path) -> None:
    root = _install(tmp_path / "app")
    private, public = _keys()
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest))
    home = tmp_path / "operator"
    _trust(home, public)
    report = measure_root(root, trust_root=home)
    assert report["status"] == "verified"
    assert report["verified"] is True
    assert report["signature_ok"] is True


def test_unmanifested_pyc_is_mismatch(tmp_path: Path) -> None:
    root = _install(tmp_path)
    (root / "meta.py").write_bytes(b"print('ok')\n")
    private, public = _keys()
    manifest = _manifest(root)
    assert not any(row["path"].endswith(".pyc") for row in manifest["files"])
    _publish(root, manifest, _sign(private, manifest))
    honest = measure_root(root, public_key=public)
    assert honest["status"] == "verified"
    assert honest["verified"] is True
    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "meta.pyc").write_bytes(b"PWNED_FROM_PYC")
    poisoned = measure_root(root, public_key=public)
    assert poisoned["status"] == "mismatch"
    assert poisoned["verified"] is False
    assert poisoned["signature_ok"] is True
    assert poisoned["code"] == "BOOT-MEASURE-MISMATCH"
    (cache / "meta.pyc").write_bytes(b"listed-bytecode")
    listed = _manifest(root)
    assert any(row["path"] == "__pycache__/meta.pyc" for row in listed["files"])
    _publish(root, listed, _sign(private, listed))
    kept = measure_root(root, public_key=public)
    assert kept["status"] == "verified"
    assert kept["verified"] is True
    (cache / "meta.pyc").unlink()
    dropped = measure_root(root, public_key=public)
    assert dropped["status"] == "mismatch"
    assert dropped["verified"] is False


def test_only_the_top_level_git_and_manifest_are_excluded(tmp_path: Path) -> None:
    root = _install(tmp_path)
    private, public = _keys()
    manifest = _manifest(root)
    _publish(root, manifest, _sign(private, manifest))
    git = root / ".git"
    git.mkdir()
    (git / "config").write_bytes(b"real-git")
    still = measure_root(root, public_key=public)
    assert still["status"] == "verified"
    assert still["verified"] is True
    nested = root / "pkg" / ".git"
    nested.mkdir(parents=True)
    (nested / "config").write_bytes(b"hidden")
    (root / "pkg" / "boot-manifest.json").write_bytes(b"nested-claim")
    hidden = measure_root(root, public_key=public)
    assert hidden["status"] == "mismatch"
    assert hidden["verified"] is False
