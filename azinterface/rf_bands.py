"""QNM-RF-BANDS-1.0 cite for AZInterface.

AM, FM, and SDR satellite receive (`sat_rx`) are enabled and absent-hardware
gated the same way LAN, Wi-Fi, Bluetooth, RF, and photon are. The switch is
on. Missing hardware refuses QNM-RADIO-ABSENT. `live`, `hardware_live`, and
`packet_live` stay false when that hardware is absent. A present SDR is not
a demodulator and does not mark those flags live.

XM SDARS and `satellite_relay` stay HELD. No spend, no SKU, no plan, and no
checkout. A caller cannot lift that hold. Cap-7 is not ICANN.

This cite reads local device nodes only. It does not open a socket, transmit,
or buy a plan. The failover walk stays LAN, Wi-Fi, Bluetooth, RF, photon.
Author: Aziel Eliab.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

RF_BAND_SPEC = "QNM-RF-BANDS-1.0"
TRAFFIC_SPEC = "QNM-TRAFFIC-PATHS-1.0"
RADIO_ABSENT = "QNM-RADIO-ABSENT"
AUTHOR = "Aziel Eliab"

OPEN_PATHS = ("lan", "wifi", "bluetooth", "rf", "photon", "am", "fm", "sat_rx")
HELD_PATHS = ("xm_sdars", "satellite_relay")
OPEN_BANDS = ("am", "fm", "sat_rx")

_OPEN_ALIASES = {
    "am": "am",
    "fm": "fm",
    "sat_rx": "sat_rx",
    "sat-rx": "sat_rx",
    "satrx": "sat_rx",
}
_HELD_ALIASES = {
    "xm_sdars": "xm_sdars",
    "xm-sdars": "xm_sdars",
    "xm": "xm_sdars",
    "siriusxm": "xm_sdars",
    "satellite_relay": "satellite_relay",
    "satellite-relay": "satellite_relay",
    "satrelay": "satellite_relay",
}

_SWITCH_PHY = {
    "lan": "absent-until-interface",
    "wifi": "absent-until-hardware",
    "bluetooth": "absent-until-hardware",
    "rf": "absent-until-sdr",
    "photon": "absent-until-light",
    "am": "absent-until-sdr",
    "fm": "absent-until-sdr",
    "sat_rx": "absent-until-sdr",
    "xm_sdars": "absent-until-siriusxm-tuner",
    "satellite_relay": "absent",
}


def classify_carrier(raw: str) -> tuple[str, str] | None:
    """Return ('open', id) or ('held', id) for an RF-band cite name."""
    text = str(raw or "").strip().lower()
    if text in _HELD_ALIASES:
        return ("held", _HELD_ALIASES[text])
    if text in _OPEN_ALIASES:
        return ("open", _OPEN_ALIASES[text])
    return None


def _base(root: Path | str | None) -> Path | None:
    if root is None or root == "":
        return None
    return Path(root)


def _at(root: Path | None, rel: str) -> Path:
    if root is None:
        return Path("/") / rel
    return root / rel


def _dir_has(path: Path) -> bool:
    if not path.is_dir():
        return False
    try:
        return any(child.name not in {".", ".."} for child in path.iterdir())
    except OSError:
        return False


def probe_sdr(root: Path | str | None = None) -> dict[str, Any]:
    base = _base(root)
    if (
        _at(base, "dev/swradio0").exists()
        or _dir_has(_at(base, "sys/class/sdr"))
        or _dir_has(_at(base, "sys/bus/usb/drivers/dvb_usb_rtl28xxu"))
    ):
        return {"present": True, "kind": "sdr"}
    return {"present": False, "kind": None}


def probe_siriusxm(root: Path | str | None = None) -> dict[str, Any]:
    base = _base(root)
    if _at(base, "dev/siriusxm0").exists() or _dir_has(_at(base, "sys/class/siriusxm")):
        return {"present": True, "kind": "siriusxm-tuner"}
    return {"present": False, "kind": None}


def probe_satellite_terminal(root: Path | str | None = None) -> dict[str, Any]:
    base = _base(root)
    candidates = (
        ("dev/starlink0", "starlink", "file"),
        ("dev/iridium0", "iridium", "file"),
        ("sys/class/starlink", "starlink", "dir"),
        ("sys/class/iridium", "iridium", "dir"),
    )
    for rel, kind, mode in candidates:
        path = _at(base, rel)
        if path.exists() if mode == "file" else _dir_has(path):
            return {"present": True, "kind": kind}
    return {"present": False, "kind": None}


def _flags(enabled: bool, held: bool) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "live": False,
        "held": held,
        "hardware_live": False,
        "packet_live": False,
        "transmit": False,
        "checkout": False,
        "skus": False,
        "plans": False,
        "spend": False,
        "purchased": False,
        "paid_ok": False,
        "paid_terminal": False,
        "worker_hardware": False,
        "mock": False,
    }


def _open_band(ident: str, band: str, probe: dict[str, Any], absent: str, present: str) -> dict[str, Any]:
    seen = probe.get("present") is True and bool(probe.get("kind"))
    kind = str(probe.get("kind") or "")
    row = {
        "id": ident,
        "parent": "rf",
        "spec": RF_BAND_SPEC,
        "band": band,
        "receive_only": True,
        "device": "sdr",
        "hardware": kind if seen else False,
        "state": "HW-PRESENT" if seen else "REFUSE",
        "code": None if seen else RADIO_ABSENT,
        "mesh_traffic": False,
        "note": present.format(kind=kind) if seen else absent,
        **_flags(True, False),
    }
    return row


def _held_band(ident: str, band: str, device: str, probe: dict[str, Any], absent: str, present: str, **extra: Any) -> dict[str, Any]:
    seen = probe.get("present") is True and bool(probe.get("kind"))
    kind = str(probe.get("kind") or "")
    row = {
        "id": ident,
        "parent": "rf",
        "spec": RF_BAND_SPEC,
        "band": band,
        "receive_only": True,
        "device": device,
        "hardware": kind if seen else False,
        "state": "HELD",
        "code": None if seen else RADIO_ABSENT,
        "subscription_held": False,
        "mesh_traffic": False,
        "note": present.format(kind=kind) if seen else absent,
        **_flags(False, True),
        **extra,
    }
    return row


def _relay(probe: dict[str, Any]) -> dict[str, Any]:
    seen = probe.get("present") is True and bool(probe.get("kind"))
    kind = str(probe.get("kind") or "")
    absent = (
        "Satellite relay stays HELD. Transmit is off. No spend, no SKU, no plan, no checkout. "
        "Without a terminal the relay refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false."
    )
    present = (
        "Satellite relay terminal {kind} is present. The switch stays HELD. Transmit stays off. "
        "live, hardware_live, and packet_live stay false. Presence is not a purchase and not a checkout."
    )
    return {
        "id": "satellite_relay",
        "spec": RF_BAND_SPEC,
        "device": "amateur-or-commercial-terminal",
        "hardware": kind if seen else False,
        "state": "HELD",
        "code": None if seen else RADIO_ABSENT,
        "software_path": False,
        "encryption_allowed": False,
        "envelope_spec": "FED-MESH-1.0",
        "envelope_kind": "store-and-forward",
        "note": present.format(kind=kind) if seen else absent,
        **_flags(False, True),
    }


def _bands(root: Path | str | None) -> dict[str, Any]:
    sdr = probe_sdr(root)
    tuner = probe_siriusxm(root)
    am = _open_band(
        "am",
        "530-1700 kHz",
        sdr,
        "AM receive needs an SDR. The mesh does not transmit on AM. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
        "AM device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
    )
    fm = _open_band(
        "fm",
        "88-108 MHz",
        sdr,
        "FM receive needs an SDR. The mesh does not transmit on FM. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
        "FM device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
    )
    sat = _open_band(
        "sat_rx",
        "satellite-downlink",
        sdr,
        "Satellite receive (weather, GNSS, amateur downlinks) needs an SDR. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
        "Satellite receive device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
    )
    sat["kinds"] = ["weather", "gnss", "amateur-downlink"]
    xm = _held_band(
        "xm_sdars",
        "2320-2345 MHz",
        "siriusxm-tuner",
        tuner,
        "XM SDARS stays HELD. It needs a licensed SiriusXM tuner and a paid plan. No SKU, no checkout, no spend. Without the tuner the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
        "XM SDARS device {kind} is present. The switch stays HELD. live, hardware_live, and packet_live stay false. No spend, no SKU, no plan, no checkout.",
        encrypted=True,
        subscription=True,
        one_way=True,
    )
    return {"am": am, "fm": fm, "xm_sdars": xm, "sat_rx": sat}


def _path_row(row: dict[str, Any]) -> dict[str, Any]:
    ident = str(row["id"])
    body = {
        "id": ident,
        "enabled": row["enabled"] is True,
        "live": False,
        "hardware_live": False,
        "packet_live": False,
        "held": row["held"] is True,
        "spend": False,
        "checkout": False,
        "mock": False,
        "phy": _SWITCH_PHY[ident],
    }
    if ident in OPEN_BANDS or ident in HELD_PATHS:
        body["state"] = row["state"]
        body["code"] = row["code"]
    return body


def rf_band_cite(root: Path | str | None = None) -> dict[str, Any]:
    """Honest RF-band cite. Caller payloads are not accepted and cannot flip a hold."""
    bands = _bands(root)
    relay = _relay(probe_satellite_terminal(root))
    switches = {
        "lan": {"id": "lan", "enabled": True, "live": False, "hardware_live": False, "packet_live": False, "held": False, "spend": False, "checkout": False, "mock": False, "phy": _SWITCH_PHY["lan"]},
        "wifi": {"id": "wifi", "enabled": True, "live": False, "hardware_live": False, "packet_live": False, "held": False, "spend": False, "checkout": False, "mock": False, "phy": _SWITCH_PHY["wifi"]},
        "bluetooth": {"id": "bluetooth", "enabled": True, "live": False, "hardware_live": False, "packet_live": False, "held": False, "spend": False, "checkout": False, "mock": False, "phy": _SWITCH_PHY["bluetooth"]},
        "rf": {"id": "rf", "enabled": True, "live": False, "hardware_live": False, "packet_live": False, "held": False, "spend": False, "checkout": False, "mock": False, "phy": _SWITCH_PHY["rf"]},
        "photon": {"id": "photon", "enabled": True, "live": False, "hardware_live": False, "packet_live": False, "held": False, "spend": False, "checkout": False, "mock": False, "phy": _SWITCH_PHY["photon"]},
    }
    for ident in ("am", "fm", "sat_rx", "xm_sdars"):
        switches[ident] = _path_row(bands[ident])
    switches["satellite_relay"] = _path_row(relay)
    return {
        "spec": RF_BAND_SPEC,
        "author": AUTHOR,
        "traffic_paths_spec": TRAFFIC_SPEC,
        "traffic_paths_enabled": True,
        "traffic_paths_live": False,
        "traffic_paths_open": list(OPEN_PATHS),
        "traffic_paths_held": list(HELD_PATHS),
        "paid_satellite_held": True,
        "paid_satellite_checkout": False,
        "paid_satellite_skus": False,
        "paid_satellite_plans": False,
        "paid_satellite_spend": False,
        "cap7_is_icann": False,
        "public_icann": False,
        "cap7_public_icann": False,
        "cap7_name_only": True,
        "cap7_registrar_live": False,
        "get_never_enables": True,
        "radio_phy": False,
        "mock": False,
        "paths": switches,
        "rf_bands": bands,
        "satellite_relay": relay,
    }


def band_row(cite: dict[str, Any], ident: str) -> dict[str, Any]:
    if ident == "satellite_relay":
        row = cite.get("satellite_relay")
        return row if isinstance(row, dict) else {}
    bands = cite.get("rf_bands")
    if isinstance(bands, dict) and isinstance(bands.get(ident), dict):
        return bands[ident]
    return {}
