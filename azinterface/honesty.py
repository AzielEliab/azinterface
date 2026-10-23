"""Standing facts for AZInterface.

AZIEL OVERRIDE 2026-10-23: the stay-false hold on the three QNM flags is
cancelled. mesh_node_live, alt_internet_live, and packet_path_live stay on.
A caller cannot turn them off, and cannot turn kernel, mail, boot, or
second_device on. software_count stays 33. Cap-7 and .aziel stay names.
The runtime Softwares catalog stays a different list (locks 42 / 36).
"""

from __future__ import annotations

from typing import Any

# SHA-256 of workers/download-tracker/public/azinterface-0.1.0.tar.gz
COUNTED_TARBALL_SHA256 = "0282a37a5edbdd8b8a15e0b148ebd5aabd0ffe8eaf78b10bc94c1e012c457a5b"

VEILLOCK_STATUS = (
    "VeilLock stays local_only. It is not a public-door live and has no public FragGate door."
)

STANDING_SENTENCES = (
    "Internet base is present. Not live.",
    "Not an OS yet.",
    "The kernel base is present. It has not booted a machine.",
    "Public mail send is not live.",
    "VeilLock stays local_only. It is not a public-door live and has no public FragGate door.",
    "Whitestone is worker-only and has no public FragGate door.",
)

_FALSE_FLAGS = (
    "second_device",
    "mail_send",
    "public_smtp_send",
    "public_worker_mail_send",
    "kernel_base",
    "booted",
    "installed",
    "os_yet",
    "public_worker_boot",
    "public_worker_kernel",
    "host_os_booted",
)


def standing_text() -> str:
    return " ".join(STANDING_SENTENCES)


def standing_facts(caller: dict[str, Any] | None = None) -> dict[str, Any]:
    """Facts a posted payload cannot flip. `caller` is ignored on purpose."""
    del caller
    return {
        "mesh_node_live": True,
        "alt_internet_live": True,
        "packet_path_live": True,
        "qnm_membership": True,
        "qns_cite_plane": False,
        "second_device": False,
        "mail_send": False,
        "public_smtp_send": False,
        "public_worker_mail_send": False,
        "kernel": False,
        "kernel_base": False,
        "booted": False,
        "installed": False,
        "os_yet": False,
        "is_os": False,
        "public_worker_boot": False,
        "public_worker_kernel": False,
        "host_kernel": False,
        "host_os_booted": False,
        "internet_base": {"present": True, "live": False, "installed": False},
        "veillock": "local_only",
        "veillock_public_door": False,
        "whitestone_worker_only": True,
        "whitestone_public_door": False,
        "public_door": "FG-STUB",
        "smtp_send": "FG-STUB",
        "wireguard": "SLOT",
        "openvpn": "SLOT",
        "l3": "SLOT",
        "kernel_udp": "SLOT",
        "tun_tap": "SLOT",
        "isolation": "single-node security-awareness",
        "phoenix": "local wait and re-seal",
        "lines": {
            "internet": STANDING_SENTENCES[0],
            "os": STANDING_SENTENCES[1],
            "kernel_note": STANDING_SENTENCES[2],
            "mail": STANDING_SENTENCES[3],
            "veillock": STANDING_SENTENCES[4],
            "whitestone": STANDING_SENTENCES[5],
        },
        "text": standing_text(),
    }


_ON_FLAGS = (
    "mesh_node_live",
    "alt_internet_live",
    "packet_path_live",
    "qnm_membership",
)


def seal_standing(body: dict[str, Any], caller: dict[str, Any] | None = None) -> dict[str, Any]:
    """Write the standing facts onto a status object. Caller flags are not copied."""
    facts = standing_facts(caller)
    body["honesty"] = facts
    for key in _FALSE_FLAGS:
        body[key] = False
    for key in _ON_FLAGS:
        body[key] = True
    body["qns_cite_plane"] = False
    return body
