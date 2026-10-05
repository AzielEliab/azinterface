"""The packet path is watched on this machine and stays refused without a second device."""

from __future__ import annotations

from pathlib import Path

from azinterface.engine import Engine
from azinterface.packet_path import (
    PUBLIC_SENTENCE,
    RADIO_ABSENT,
    path_report,
    second_device,
)
from azinterface.pipeline import pipeline_arch
from azinterface.receipts import Ledger
from azinterface.web_page import home_html


def test_same_machine_frame_is_not_a_live_public_path() -> None:
    report = path_report(refresh=True)
    assert report["carrier_order"] == ["lan", "wifi", "bluetooth", "rf", "photon"]
    assert report["cap7_name_only"] is True
    assert report["dot_aziel_name_only"] is True
    assert report["public_icann"] is False
    assert report["bgp"] is False
    assert report["public_door"] == "FG-STUB"
    assert report["d2d_status"] == "NOT-READY"
    assert report["warn5"] == "STANDS-until-demonstrated"
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
        assert f"LAN is present on {lan['hardware']}." in report["status"]
        assert "The frame stayed on this machine." in report["status"]
        assert "A frame that stays on this machine is not a live public path." in report["status"]
        assert "A second device stays false while both ends share one machine id." in report["status"]
    else:
        assert lan["code"] == RADIO_ABSENT
        assert "LAN hardware is absent." in report["status"]
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
    assert report["status"].count("The packet path is not live.") == 1
    assert "The alternative internet is not live." in report["status"]
    assert "Device-to-device packet carriers stay NOT-READY." in report["status"]
    assert "WARN-5 stands." in report["status"]
    assert "Internet base is present. Not live." in report["status"]
    assert "Still missing: a packet that leaves this machine and arrives on a different machine id." in report["status"]
    assert "Cap-7 and .aziel stay names only." in report["status"]
    for ident, name in (("wifi", "Wi-Fi"), ("bluetooth", "Bluetooth"), ("rf", "RF"), ("photon", "Photon")):
        row = next(item for item in report["carriers"] if item["id"] == ident)
        if row["state"] != "HW-PRESENT":
            assert row["code"] == RADIO_ABSENT
            assert row["hardware"] is False
            assert f"{name} hardware is absent." in report["status"]


def test_absent_radio_and_name_plane_do_not_become_a_path() -> None:
    wifi = path_report({"carrier": "wifi", "alt_internet_live": True, "packet_path_live": True})
    wifi_row = next(row for row in wifi["carriers"] if row["id"] == "wifi")
    assert wifi["packet_path_live"] is False
    assert wifi["alt_internet_live"] is False
    assert wifi["second_device"] is False
    if wifi_row["state"] != "HW-PRESENT":
        assert wifi["code"] == RADIO_ABSENT
        assert "Wi-Fi hardware is absent." in wifi["status"]
    else:
        assert wifi["code"] == "PACKET-NOT-CARRIED"
        assert wifi["off_machine"] is False
    for name in ("cap7", "cap-7", "node.aziel"):
        refused = path_report({"carrier": name, "alt_internet_live": True})
        assert refused["ok"] is False
        assert refused["code"] == "MG-NO-IP-EXIT"
        assert refused["packet_path_live"] is False
        assert refused["alt_internet_live"] is False
        assert refused["cap7_name_only"] is True
        assert "Cap-7 and .aziel stay names only." in refused["status"]
        assert f"{name} is a name only." in refused["status"]
    assert second_device("a" * 32, "a" * 32) is False
    assert second_device("a" * 32, "b" * 32) is True
    ignored = path_report({"alt_internet_live": True, "remote_host": "b" * 32}, refresh=True)
    assert ignored["alt_internet_live"] is False
    assert ignored["second_device"] is False


def test_public_sentence_matches_the_worker_and_the_count_stays() -> None:
    html = home_html(views=0, downloads=0)
    assert PUBLIC_SENTENCE in html
    assert "Internet is not live." not in html
    assert pipeline_arch()["software_count"] == 33
    assert Engine(Ledger()).site_state == "OFF"
    assert "One-click install" not in html
