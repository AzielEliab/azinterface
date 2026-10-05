"""The packet path stays refused, and the human sentence is the runtime fact."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from azinterface.engine import Engine
from azinterface.packet_path import (
    RADIO_ABSENT,
    host_hardware_visible,
    not_live_sentence,
    path_report,
    second_device,
)
from azinterface.pipeline import pipeline_arch
from azinterface.receipts import Ledger
from azinterface.web_page import home_html

ROOT = Path(__file__).resolve().parents[1]
FACT = (
    "An alternative internet is not live (alt_internet_live is false).",
    "A packet path is not live (packet_path_live is false).",
    "Still missing: a packet that leaves this machine and arrives on a different machine id.",
    "A same-machine mesh frame does not count.",
    "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP.",
    "Public mail send, the kernel, and boot stay not live.",
    "The public door stays FG-STUB.",
)
PUBLIC_SOURCES = (
    "azinterface/packet_path.py",
    "azinterface/web_page.py",
    "azinterface/pipeline.py",
    "azinterface/suite_page.py",
    "workers/download-tracker/src/ui.js",
    "workers/download-tracker/src/pipeline.js",
    "workers/download-tracker/src/alt-internet-fact.js",
)


def _fact(text: str) -> None:
    for line in FACT:
        assert line in text
    assert "is true" not in text
    assert "Internet is not live." not in text


def test_same_machine_frame_is_not_a_live_public_path() -> None:
    report = path_report(refresh=True)
    assert report["status"] == not_live_sentence()
    assert report["carrier_order"] == ["lan", "wifi", "bluetooth", "rf", "photon"]
    assert report["cap7_name_only"] is True
    assert report["dot_aziel_name_only"] is True
    assert report["public_icann"] is False
    assert report["bgp"] is False
    assert report["public_door"] == "FG-STUB"
    assert report["d2d_status"] == "NOT-READY"
    assert report["warn5"] == "STANDS-until-demonstrated"
    _fact(report["status"])
    lan = next(row for row in report["carriers"] if row["id"] == "lan")
    carry = report["carry"]
    assert isinstance(carry, dict)
    if lan["state"] == "HW-PRESENT":
        assert carry.get("bytes_match") is True, carry
        assert carry.get("watched") is True
        local = Path("/etc/machine-id").read_text(encoding="utf-8").strip()
        assert carry["local_host"] == local
        assert carry["remote_host"] == local
        assert carry["remote_addr"] in set(carry["local_addrs"])
        assert carry["sent_to"] in set(carry["local_addrs"])
        assert carry["bytes"] == 16
        assert report["same_machine"] is True
        assert f"LAN interface {lan['hardware']}" in report["status"]
        if lan.get("address"):
            assert f" at {lan['address']}" in report["status"]
        assert "is present on this machine and is not a second device." in report["status"]
        assert "A second device stays false while both ends share that id." in report["status"]
    elif lan.get("up") is False and lan.get("hardware"):
        assert lan["code"] == RADIO_ABSENT
        assert f"LAN interface {lan['hardware']} is down ({RADIO_ABSENT})." in report["status"]
    else:
        assert lan["code"] == RADIO_ABSENT
        assert f"LAN hardware is absent ({RADIO_ABSENT})." in report["status"]
    assert report["second_device"] is False
    assert report["off_machine"] is False
    assert report["packet_path"] is False
    assert report["alt_internet"] is False
    assert report["packet_path_live"] is False
    assert report["alt_internet_live"] is False
    for row in report["carriers"]:
        assert row["packet_live"] is False
        assert row["alt_internet_live"] is False
        assert row["mock"] is False
        assert row["peer_exchange_demonstrated"] is False
        if row["id"] == "lan" or row["state"] == "HW-PRESENT":
            continue
        assert row["code"] == RADIO_ABSENT
        assert row["hardware"] is False
    if host_hardware_visible():
        for ident, clause in (
            ("wifi", "Wi-Fi hardware is absent (QNM-RADIO-ABSENT)."),
            ("bluetooth", "Bluetooth hardware is absent (QNM-RADIO-ABSENT)."),
            ("rf", "RF hardware is absent (QNM-RADIO-ABSENT)."),
            ("photon", "Photon camera or flash is absent (QNM-RADIO-ABSENT)."),
        ):
            row = next(item for item in report["carriers"] if item["id"] == ident)
            if row["state"] != "HW-PRESENT":
                assert clause in report["status"]


def test_absent_radio_and_name_plane_do_not_become_a_path() -> None:
    wifi = path_report({"carrier": "wifi", "alt_internet_live": True, "packet_path_live": True})
    wifi_row = next(row for row in wifi["carriers"] if row["id"] == "wifi")
    assert wifi["status"] == not_live_sentence()
    assert wifi["packet_path_live"] is False
    assert wifi["alt_internet_live"] is False
    assert wifi["second_device"] is False
    if wifi_row["state"] != "HW-PRESENT":
        assert wifi["code"] == RADIO_ABSENT
        assert "Wi-Fi hardware is absent (QNM-RADIO-ABSENT)." in wifi["status"]
    else:
        assert wifi["code"] == "PACKET-NOT-CARRIED"
        assert wifi["off_machine"] is False
    for name in ("cap7", "cap-7", "node.aziel"):
        refused = path_report({"carrier": name, "alt_internet_live": True})
        assert refused["ok"] is False
        assert refused["code"] == "MG-NO-IP-EXIT"
        assert refused["status"] == not_live_sentence()
        assert refused["packet_path_live"] is False
        assert refused["alt_internet_live"] is False
        assert refused["cap7_name_only"] is True
        assert "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP." in refused["status"]
        assert f"{name} is a name only." not in refused["status"]
    assert second_device("a" * 32, "a" * 32) is False
    assert second_device("a" * 32, "b" * 32) is True
    ignored = path_report({"alt_internet_live": True, "packet_path_live": True, "remote_host": "b" * 32}, refresh=True)
    assert ignored["alt_internet_live"] is False
    assert ignored["packet_path_live"] is False
    assert ignored["second_device"] is False


def test_hidden_hardware_does_not_invent_radios(monkeypatch) -> None:
    monkeypatch.setattr("azinterface.packet_path.host_hardware_visible", lambda: False)
    text = not_live_sentence()
    _fact(text)
    assert "This isolate cannot see host hardware (worker_hardware is false)." in text
    assert "LAN hardware is absent" not in text
    assert "Wi-Fi hardware is absent" not in text
    assert "Bluetooth hardware is absent" not in text
    assert "RF hardware is absent" not in text
    assert "Photon camera or flash is absent" not in text
    assert "This machine id is" not in text


def test_public_sentence_matches_the_worker_and_the_count_stays() -> None:
    sentence = not_live_sentence()
    html = home_html(views=0, downloads=0)
    assert sentence in html
    _fact(sentence)
    assert "Internet is not live." not in html
    assert pipeline_arch()["software_count"] == 33
    cited = {
        row["slug"]: row["status"]
        for domain in pipeline_arch()["domain_map"]
        for row in domain["softwares"]
    }
    assert cited["aznet"] == sentence
    assert Engine(Ledger()).site_state == "OFF"
    assert "One-click install" not in html
    script = (
        "import { notLiveSentence } from './workers/download-tracker/src/alt-internet-fact.js';"
        "process.stdout.write(notLiveSentence());"
    )
    out = subprocess.check_output(["node", "--input-type=module", "-e", script], cwd=ROOT)
    assert out.decode() == sentence
    blob = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PUBLIC_SOURCES)
    machine = Path("/etc/machine-id").read_text(encoding="utf-8").strip()
    if re.fullmatch(r"[a-f0-9]{32}", machine):
        assert machine not in blob
    for address in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", sentence):
        assert address not in blob
    assert "LAN hardware is absent." not in (ROOT / "azinterface/web_page.py").read_text(encoding="utf-8")
    assert "LAN hardware is absent." not in (ROOT / "workers/download-tracker/src/ui.js").read_text(encoding="utf-8")
