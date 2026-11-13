"""QNM RF-band cite. Local device nodes only. No socket and no spend."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from azinterface.mesh_radios import mesh_radios_tile
from azinterface.packet_path import RADIO_ABSENT, path_report
from azinterface.rf_bands import rf_band_cite

ROOT = Path(__file__).resolve().parents[1]
OPEN = ("am", "fm", "sat_rx")
HELD = ("xm_sdars", "satellite_relay")


def _jsonable(body: dict) -> dict:
    return json.loads(json.dumps(body))


def _node_cite(root: Path | None) -> dict:
    script = (
        "import { rfBandCite } from './workers/download-tracker/src/rf-bands.js';"
        "const root = process.argv[1];"
        "process.stdout.write(JSON.stringify(rfBandCite(root || undefined)));"
    )
    argv = ["node", "--input-type=module", "-e", script]
    if root is not None:
        argv.append(str(root))
    out = subprocess.check_output(argv, cwd=ROOT)
    return json.loads(out.decode())


def _assert_not_live(row: dict) -> None:
    assert row["live"] is False
    assert row["hardware_live"] is False
    assert row["packet_live"] is False
    assert row["spend"] is False
    assert row["checkout"] is False
    assert row["mock"] is False


def _assert_cite_locks(cite: dict) -> None:
    assert cite["cap7_is_icann"] is False
    assert cite["public_icann"] is False
    assert cite["cap7_public_icann"] is False
    assert cite["cap7_name_only"] is True
    assert cite["cap7_registrar_live"] is False
    assert cite["traffic_paths_live"] is False
    assert cite["paid_satellite_held"] is True
    assert cite["paid_satellite_spend"] is False
    assert cite["paid_satellite_checkout"] is False
    assert cite["paid_satellite_skus"] is False
    assert cite["paid_satellite_plans"] is False
    assert cite["radio_phy"] is False
    assert cite["get_never_enables"] is True
    assert cite["traffic_paths_open"] == ["lan", "wifi", "bluetooth", "rf", "photon", "am", "fm", "sat_rx"]
    assert cite["traffic_paths_held"] == ["xm_sdars", "satellite_relay"]
    for ident in ("lan", "wifi", "bluetooth", "rf", "photon", *OPEN):
        assert cite["paths"][ident]["enabled"] is True
        _assert_not_live(cite["paths"][ident])
        assert cite["paths"][ident]["held"] is False
    for ident in HELD:
        assert cite["paths"][ident]["enabled"] is False
        assert cite["paths"][ident]["held"] is True
        _assert_not_live(cite["paths"][ident])


def test_absent_sdr_refuses_open_bands_and_holds_paid_paths(tmp_path: Path) -> None:
    cite = rf_band_cite(tmp_path)
    _assert_cite_locks(cite)
    for ident in OPEN:
        row = cite["rf_bands"][ident]
        assert row["enabled"] is True
        assert row["held"] is False
        assert row["transmit"] is False
        assert row["hardware"] is False
        assert row["state"] == "REFUSE"
        assert row["code"] == RADIO_ABSENT
        _assert_not_live(row)
    xm = cite["rf_bands"]["xm_sdars"]
    relay = cite["satellite_relay"]
    assert xm["enabled"] is False
    assert xm["held"] is True
    assert xm["state"] == "HELD"
    assert xm["code"] == RADIO_ABSENT
    assert xm["mesh_traffic"] is False
    assert xm["subscription_held"] is False
    _assert_not_live(xm)
    assert relay["enabled"] is False
    assert relay["held"] is True
    assert relay["transmit"] is False
    assert relay["state"] == "HELD"
    assert relay["code"] == RADIO_ABSENT
    assert relay["hardware"] is False
    _assert_not_live(relay)
    assert _node_cite(tmp_path) == _jsonable(cite)


def test_present_sdr_stays_not_live_and_paid_devices_stay_held(tmp_path: Path) -> None:
    dev = tmp_path / "dev"
    dev.mkdir()
    (dev / "swradio0").write_text("", encoding="utf-8")
    (dev / "siriusxm0").write_text("", encoding="utf-8")
    (dev / "starlink0").write_text("", encoding="utf-8")
    cite = rf_band_cite(tmp_path)
    _assert_cite_locks(cite)
    for ident in OPEN:
        row = cite["rf_bands"][ident]
        assert row["enabled"] is True
        assert row["state"] == "HW-PRESENT"
        assert row["hardware"] == "sdr"
        assert row["code"] is None
        assert row["transmit"] is False
        _assert_not_live(row)
        assert "does not demodulate" in row["note"]
    xm = cite["rf_bands"]["xm_sdars"]
    relay = cite["satellite_relay"]
    assert xm["hardware"] == "siriusxm-tuner"
    assert xm["enabled"] is False
    assert xm["held"] is True
    assert xm["state"] == "HELD"
    assert xm["code"] is None
    assert xm["purchased"] is False
    _assert_not_live(xm)
    assert relay["hardware"] == "starlink"
    assert relay["enabled"] is False
    assert relay["held"] is True
    assert relay["transmit"] is False
    assert relay["code"] is None
    assert relay["purchased"] is False
    assert "not a purchase" in relay["note"]
    _assert_not_live(relay)
    assert _node_cite(tmp_path) == _jsonable(cite)


def test_mesh_and_path_keep_flags_false_and_refuse_spend(monkeypatch) -> None:
    monkeypatch.setattr("azinterface.rf_bands.probe_sdr", lambda root=None: {"present": False, "kind": None})
    monkeypatch.setattr("azinterface.rf_bands.probe_siriusxm", lambda root=None: {"present": False, "kind": None})
    monkeypatch.setattr("azinterface.rf_bands.probe_satellite_terminal", lambda root=None: {"present": False, "kind": None})
    for ident in OPEN:
        tile = mesh_radios_tile({"carrier": ident, "confirm": True, "live": True, "hardware_live": True, "packet_live": True, "spend": True})
        assert tile["ok"] is False
        assert tile["code"] == RADIO_ABSENT
        assert tile["live"] is False
        assert tile["hardware_live"] is False
        assert tile["packet_live"] is False
        assert tile["carrier_live"] is False
        assert tile["mock"] is False
        assert tile["mesh_node_live"] is True
        assert tile["cap7_is_icann"] is False
        assert tile["public_icann"] is False
        assert tile["qnm_rf"]["rf_bands"][ident]["enabled"] is True
        assert tile["qnm_rf"]["rf_bands"][ident]["live"] is False
    hostile = {
        "carrier": "xm_sdars",
        "confirm": True,
        "enabled": True,
        "live": True,
        "hardware_live": True,
        "packet_live": True,
        "spend": True,
        "checkout": True,
        "skus": True,
        "plans": True,
        "purchased": True,
        "paid_ok": True,
    }
    xm = mesh_radios_tile(hostile)
    assert xm["ok"] is False
    assert xm["status"] == "REFUSED"
    assert xm["held"] is True
    assert xm["carrier_enabled"] is False
    assert xm["mutated"] is False
    assert xm["code"] == RADIO_ABSENT
    assert xm["live"] is False
    assert xm["hardware_live"] is False
    assert xm["packet_live"] is False
    assert xm["spend"] is False
    assert xm["checkout"] is False
    assert xm["skus"] is False
    assert xm["plans"] is False
    assert xm["purchased"] is False
    assert xm["paid_ok"] is False
    assert xm["mesh_node_live"] is True
    assert xm["packet_path_live"] is True
    assert xm["cap7_is_icann"] is False
    assert xm["qnm_rf"]["rf_bands"]["xm_sdars"]["enabled"] is False
    relay = mesh_radios_tile({"carrier": "satellite-relay", "confirm": True, "spend": True, "live": True})
    assert relay["held"] is True
    assert relay["mutated"] is False
    assert relay["spend"] is False
    assert relay["live"] is False
    assert relay["hardware_live"] is False
    assert relay["packet_live"] is False
    assert relay["qnm_rf"]["satellite_relay"]["enabled"] is False
    assert relay["qnm_rf"]["satellite_relay"]["transmit"] is False
    asked = path_report({"carrier": "sat_rx", "live": True, "packet_live": True, "spend": True})
    assert asked["code"] == RADIO_ABSENT
    assert asked["live"] is False
    assert asked["hardware_live"] is False
    assert asked["packet_live"] is False
    assert asked["packet_path_live"] is True
    assert asked["alt_internet_live"] is True
    assert asked["mesh_node_live"] is True
    assert asked["carrier_order"] == ["lan", "wifi", "bluetooth", "rf", "photon"]
    assert asked["cap7_is_icann"] is False
    assert asked["public_icann"] is False
    held = path_report({"carrier": "xm", "confirm": True, "spend": True, "live": True, "enabled": True})
    assert held["ok"] is False
    assert held["held"] is True
    assert held["code"] == RADIO_ABSENT
    assert held["spend"] is False
    assert held["live"] is False
    assert held["hardware_live"] is False
    assert held["packet_live"] is False
    assert held["packet_path_live"] is True
    assert held["qnm_rf"]["cap7_is_icann"] is False
    cap7 = path_report({"carrier": "cap7", "live": True})
    assert cap7["ok"] is False
    assert cap7["code"] == "MG-NO-IP-EXIT"
    assert cap7["public_icann"] is False
    assert cap7["cap7_registrar_live"] is False
    assert cap7["qnm_rf"]["cap7_is_icann"] is False


def test_present_open_band_is_gated_like_the_other_carriers(monkeypatch) -> None:
    monkeypatch.setattr("azinterface.rf_bands.probe_sdr", lambda root=None: {"present": True, "kind": "sdr"})
    tile = mesh_radios_tile({"carrier": "fm", "confirm": True, "live": True, "packet_live": True, "hardware_live": True})
    assert tile["ok"] is True
    assert tile["carrier"] == "fm"
    assert tile["carrier_state"] == "HW-PRESENT"
    assert tile["live"] is False
    assert tile["hardware_live"] is False
    assert tile["packet_live"] is False
    assert tile["carrier_live"] is False
    assert tile["mock"] is False
    assert tile["qnm_rf"]["rf_bands"]["fm"]["enabled"] is True
    assert tile["qnm_rf"]["rf_bands"]["fm"]["state"] == "HW-PRESENT"
    assert tile["qnm_rf"]["rf_bands"]["fm"]["live"] is False
    report = path_report({"carrier": "am", "live": True, "hardware_live": True, "packet_live": True})
    assert report["code"] == "PACKET-NOT-CARRIED"
    assert report["carrier_state"] == "HW-PRESENT"
    assert report["live"] is False
    assert report["hardware_live"] is False
    assert report["packet_live"] is False
    assert report["packet_path_live"] is True
    assert report["carrier_order"] == ["lan", "wifi", "bluetooth", "rf", "photon"]
    assert report["qnm_rf"]["rf_bands"]["am"]["hardware"] == "sdr"
    paid = mesh_radios_tile({"carrier": "xm_sdars", "confirm": True, "enabled": True, "live": True, "spend": True})
    assert paid["ok"] is False
    assert paid["held"] is True
    assert paid["mutated"] is False
    assert paid["live"] is False
    assert paid["hardware_live"] is False
    assert paid["packet_live"] is False
    assert paid["spend"] is False
    assert paid["qnm_rf"]["rf_bands"]["xm_sdars"]["enabled"] is False


def test_worker_cite_matches_this_machine_without_a_network_call() -> None:
    cite = rf_band_cite()
    assert _node_cite(None) == _jsonable(cite)
    for ident in OPEN:
        row = cite["rf_bands"][ident]
        _assert_not_live(row)
        if row["hardware"] is False:
            assert row["code"] == RADIO_ABSENT
            assert row["live"] is False
    for ident in ("xm_sdars",):
        row = cite["rf_bands"][ident]
        assert row["held"] is True
        assert row["enabled"] is False
        _assert_not_live(row)
    relay = cite["satellite_relay"]
    assert relay["held"] is True
    assert relay["enabled"] is False
    assert relay["transmit"] is False
    _assert_not_live(relay)
