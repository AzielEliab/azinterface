"""Softwares mesh_radios tile.

Status is OK by default. Membership is MESH_RADIOS=on unless the env is
explicitly off. QNM mesh_node_live, alt_internet_live, and packet_path_live
are on with that membership. The QNS cite plane is separate. Cap-7 and
.aziel stay names, not a public registrar and not ICANN. A named carrier
refuses only when QNM says the hardware is absent. GET never enables.
Author: Aziel Eliab.
"""

from __future__ import annotations

import os
from typing import Any

from .packet_path import RADIO_ABSENT, path_report

MESH_DEFAULT = "on"
MESH_DEFAULT_ENABLED = True
NODE_MESH_ENABLED = True
SUITE_PRESENCE = "on"
QNM_LIVE = {
    "mesh_node_live": True,
    "alt_internet_live": True,
    "packet_path_live": True,
}
CARRIERS = {"lan": "lan", "wifi": "wifi", "wi-fi": "wifi", "bluetooth": "bluetooth", "bt": "bluetooth", "rf": "rf", "photon": "photon"}
STAY_OFF = (
    "public_egress_ip",
    "residential",
    "cf_geo_exit",
    "cf_geo_exit_pool",
    "sticky_public_ip",
    "packet_forward",
    "packet_forwarding",
    "packet_egress",
    "hosted_vpn",
    "vpn_hop",
    "wireguard",
    "openvpn",
    "l3_exit",
    "payload_host",
    "origin_hiding",
    "public_icann",
    "icann_tld_az",
    "standard_internet_reaches_cap7",
    "resolves_to_hub",
    "dns_publish",
    "register",
    "forced_loopback",
    "loopback_isolation",
    "loopback_fence",
    "cap7_registrar_live",
    "public_registrar",
)
NOTE = (
    "Softwares membership is MESH_RADIOS=on. QNM mesh_node_live, alt_internet_live, "
    "and packet_path_live are on. That membership is not the QNS cite plane. "
    "Cap-7 and .aziel stay names, not a public registrar and not ICANN. "
    "A named carrier refuses only when QNM says the hardware is absent. GET never enables."
)


def read_mesh_radio_env(env: Any | None = None) -> bool | None:
    source = os.environ if env is None else env
    if not hasattr(source, "get"):
        return None
    raw = source.get("MESH_RADIOS")
    if raw is None or raw == "":
        raw = source.get("QNM_RADIOS")
    if raw is None or raw == "":
        return None
    text = str(raw).strip().lower()
    if text in {"off", "0", "false", "disabled"}:
        return False
    if text in {"on", "1", "true", "enabled"}:
        return True
    return None


def _stay_off(src: dict[str, Any]) -> str | None:
    if src.get("not_a_second_internet") is False or src.get("aznet_replaces_internet") is True:
        return "not_a_second_internet"
    bearer = str(src.get("carrier") or src.get("bearer") or src.get("name") or "").strip().lower()
    if bearer in {"cap7", "cap-7", "icann"} or bearer.endswith(".aziel"):
        return "cap7-name"
    for key in STAY_OFF:
        if src.get(key) is True:
            return key
    return None


def _named_carrier(src: dict[str, Any]) -> str | None:
    raw = str(src.get("carrier") or "").strip().lower()
    return CARRIERS.get(raw)


def _flags(on: bool) -> dict[str, bool]:
    del on
    return dict(QNM_LIVE)


def mesh_radios_tile(payload: dict[str, Any] | None = None, env: Any | None = None) -> dict[str, Any]:
    src = payload if isinstance(payload, dict) else {}
    env_radios = read_mesh_radio_env(env)
    radios_on = env_radios is not False
    tile: dict[str, Any] = {
        "ok": True,
        "status": "OK",
        "product": "azinterface",
        "op": "mesh_radios",
        "radios": "on" if radios_on else "off",
        "enabled": radios_on,
        "node_mesh": radios_on,
        "node_mesh_enabled": radios_on,
        "suite_presence": "on" if radios_on else "off",
        "mesh_default": MESH_DEFAULT,
        **_flags(radios_on),
        "qnm_membership": True,
        "qns_cite_plane": False,
        "qns_is_membership": False,
        "softwares_membership": radios_on,
        "hardware_live": False,
        "worker_hardware": False,
        "mock": False,
        "carrier_live": False,
        "second_device": False,
        "get_never_enables": True,
        "public_icann": False,
        "cap7_is_icann": False,
        "cap7_name_only": True,
        "dot_aziel_name_only": True,
        "cap7_registrar_live": False,
        "not_a_second_internet": True,
        "bearers": ["suite-presence"] if radios_on else [],
        "env_radios": env_radios,
        "locks": {"softwares": 42, "mcp_tools": 36},
        "note": NOTE,
    }
    stayed = _stay_off(src)
    if stayed:
        tile.update({
            "ok": False,
            "status": "REFUSED",
            "code": "MG-NO-IP-EXIT" if stayed == "cap7-name" else "MESH-STAY-OFF",
            "stayed": stayed,
            "mutated": False,
            "public_icann": False,
            "cap7_registrar_live": False,
            "message": (
                "Cap-7 and .aziel stay names. They are not ICANN and not a public registrar. "
                "Mesh radios do not arm Cap-7 egress, a public registrar, or a loopback fence."
            ),
        })
        return tile
    carrier = _named_carrier(src)
    if carrier:
        report = path_report({"carrier": carrier})
        row = next((item for item in report.get("carriers") or [] if item.get("id") == carrier), {})
        absent = row.get("state") != "HW-PRESENT"
        if absent:
            tile.update({
                "ok": False,
                "status": "REFUSED",
                "code": row.get("code") or RADIO_ABSENT,
                "carrier": carrier,
                "mock": False,
                "hardware_live": False,
                "carrier_live": False,
                "worker_hardware": "worker_hardware is false" not in str(report.get("status") or ""),
                "message": "That carrier is refused. QNM says the hardware is absent. This does not invent a live radio.",
            })
            return tile
        tile["worker_hardware"] = True
        tile["carrier"] = carrier
        tile["carrier_state"] = "HW-PRESENT"
        tile["hardware_live"] = False
        tile["note"] = tile["note"] + " The named carrier is present on this machine and is not a second device."
    if src.get("confirm") is not True or src.get("dry_run") is True:
        tile.update({
            "action": "status",
            "mutated": False,
            "needs_confirm": True,
            "dry_run": src.get("dry_run") is True,
            "message": (
                "Status only. Softwares mesh radios are ON. confirm true keeps MESH_RADIOS=on. Hardware is not claimed live. GET never enables."
                if radios_on
                else "Status only. MESH_RADIOS=off keeps transmission radios off."
            ),
        })
        return tile
    if env_radios is False:
        tile.update({
            "ok": False,
            "status": "REFUSED",
            "code": "MESH-OFF",
            "action": "enable",
            "mutated": False,
            "radios": "off",
            "enabled": False,
            "message": "MESH_RADIOS=off keeps transmission radios off. Confirm does not override that env.",
        })
        return tile
    tile.update({
        "ok": True,
        "status": "OK",
        "code": "AZI-MESH-RADIOS",
        "action": "enable",
        "mutated": True,
        "confirm": True,
        "radios": "on",
        "enabled": True,
        **QNM_LIVE,
        "hardware_live": False,
        "message": (
            "MESH_RADIOS=on. Suite-presence membership is on. QNM mesh_node_live, "
            "alt_internet_live, and packet_path_live are true. That is not the QNS cite "
            "plane and not a Cap-7 registrar. GET still never enables."
        ),
    })
    return tile
