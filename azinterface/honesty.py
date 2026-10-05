"""Standing facts shared with aziel-runtime and AZ-OS.

A caller who posts a live flag does not change these facts.
software_count stays 33. The runtime Softwares catalog stays a different list.
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
    "alt_internet_live",
    "packet_path_live",
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
        "alt_internet_live": False,
        "packet_path_live": False,
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
            "kernel": STANDING_SENTENCES[2],
            "mail": STANDING_SENTENCES[3],
            "veillock": STANDING_SENTENCES[4],
            "whitestone": STANDING_SENTENCES[5],
        },
        "text": standing_text(),
    }


def seal_standing(body: dict[str, Any], caller: dict[str, Any] | None = None) -> dict[str, Any]:
    """Write the standing facts onto a status object. Caller flags are not copied."""
    facts = standing_facts(caller)
    body["honesty"] = facts
    for key in _FALSE_FLAGS:
        body[key] = False
    return body
