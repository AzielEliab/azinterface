"""Device-to-device packet path on the existing AZNet door.

The human sentence is the one aziel-runtime computes. Carrier order is LAN,
then Wi-Fi, then Bluetooth, then RF, then photon. alt_internet_live and
packet_path_live stay false. A same-machine frame is not a second device.
Cap-7 and .aziel stay names.
"""

from __future__ import annotations

import os
import socket
import struct
import threading
from pathlib import Path
from typing import Any

ORDER = ("lan", "wifi", "bluetooth", "rf", "photon")
NAMES = {"lan": "LAN", "wifi": "Wi-Fi", "bluetooth": "Bluetooth", "rf": "RF", "photon": "Photon"}
RADIO_ABSENT = "QNM-RADIO-ABSENT"
NAME_ONLY = "MG-NO-IP-EXIT"

WARN5 = "STANDS-until-demonstrated"
HEAD = (
    "An alternative internet is not live (alt_internet_live is false). "
    "A packet path is not live (packet_path_live is false)."
)
TAIL = " ".join((
    "Still missing: a packet that leaves this machine and arrives on a different machine id.",
    "A same-machine mesh frame does not count.",
    "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP.",
    "WireGuard, OpenVPN, an L3 exit pool, kernel UDP, and TUN/TAP stay SLOT.",
    "Public mail send, the kernel, and boot stay not live.",
    "The public door stays FG-STUB.",
    "Isolation is single-node security-awareness.",
    "Phoenix is a local wait and re-seal.",
    "That is not a loopback fence.",
))

_NET = Path("/sys/class/net")
_LOCK = threading.Lock()
_CACHE: dict[str, Any] | None = None


def second_device(local_host: object, remote_host: object) -> bool:
    return (
        isinstance(local_host, str)
        and isinstance(remote_host, str)
        and len(local_host) > 0
        and len(remote_host) > 0
        and local_host != remote_host
    )


def host_hardware_visible() -> bool:
    return _NET.is_dir()


def not_live_sentence() -> str:
    """The sentence aziel-runtime currentAltInternetFact computes. No caller watch."""
    if not host_hardware_visible():
        return f"{HEAD} This isolate cannot see host hardware (worker_hardware is false). {TAIL}"
    carriers = {row["id"]: row for row in _probe_carriers()}
    clauses = [_carrier_clause(ident, carriers.get(ident)) for ident in ORDER]
    return f"{HEAD} {' '.join(clauses)} {_machine_clause(_host_id())} {TAIL}"


def path_sentence(refresh: bool = False) -> str:
    del refresh
    return not_live_sentence()


def path_report(payload: dict[str, Any] | None = None, *, refresh: bool = False) -> dict[str, Any]:
    asked = _asked_bearer(payload)
    if asked:
        return _assemble(_probe_carriers(), None, name_only_refuse=asked)
    explicit = _explicit_carrier(payload)
    global _CACHE
    with _LOCK:
        if explicit is None and _CACHE is not None and not refresh:
            return dict(_CACHE)
        carriers = _probe_carriers()
        if explicit:
            chosen = next(row for row in carriers if row["id"] == explicit)
            if chosen.get("state") != "HW-PRESENT":
                return _assemble(carriers, {"ok": False, "code": RADIO_ABSENT, "mock": False, "carrier": explicit}, name_only_refuse=None)
            return _assemble(carriers, _carry(carriers, only=explicit), name_only_refuse=None)
        report = _assemble(carriers, _carry(carriers), name_only_refuse=None)
        _CACHE = report
        return dict(report)


def _carrier_text(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("carrier") or payload.get("bearer") or "").strip().lower()


def _asked_bearer(payload: dict[str, Any] | None) -> str | None:
    raw = _carrier_text(payload)
    if not raw:
        return None
    compact = raw.replace("_", "-")
    if compact in {"cap7", "cap-7", "icann", "cap7-egress"} or raw.endswith(".aziel"):
        return raw
    return None


def _explicit_carrier(payload: dict[str, Any] | None) -> str | None:
    raw = _carrier_text(payload).replace("-", "")
    aliases = {"lan": "lan", "wifi": "wifi", "wi-fi": "wifi", "bluetooth": "bluetooth", "bt": "bluetooth", "rf": "rf", "photon": "photon"}
    return aliases.get(_carrier_text(payload), aliases.get(raw))


def _assemble(carriers: list[dict[str, Any]], carry: dict[str, Any] | None, *, name_only_refuse: str | None) -> dict[str, Any]:
    witnessed = _off_machine(carry)
    shown = []
    for row in carriers:
        shown.append({
            **row,
            "packet_live": False,
            "packet_counted": False,
            "peer_exchange_demonstrated": False,
            "alt_internet_live": False,
            "mock": False,
            "public_door": "FG-STUB",
        })
    quiet = None if carry is None else {
        **carry,
        "packet_live": False,
        "alt_internet_live": False,
        "peer_exchange_demonstrated": False,
        "mock": False,
        "public_door": "FG-STUB",
        "second_device": False,
        "cap7_name_only": True,
    }
    same_machine = bool(
        quiet
        and quiet.get("bytes_match")
        and quiet.get("local_host")
        and quiet.get("remote_host")
        and not second_device(quiet.get("local_host"), quiet.get("remote_host"))
    )
    status = not_live_sentence()
    return {
        "ok": name_only_refuse is None,
        "packet_path": False,
        "alt_internet": False,
        "packet_path_live": False,
        "alt_internet_live": False,
        "alt_internet_earned": False,
        "packet_path_earned": False,
        "second_device": False,
        "public_icann": False,
        "bgp": False,
        "cap7_name_only": True,
        "dot_aziel_name_only": True,
        "public_door": "FG-STUB",
        "d2d_status": "NOT-READY",
        "warn_5": WARN5,
        "warn5": WARN5,
        "carrier_order": [row["id"] for row in shown],
        "carriers": shown,
        "carry": quiet,
        "same_machine": same_machine,
        "off_machine": witnessed,
        "code": NAME_ONLY if name_only_refuse else (quiet or {}).get("code"),
        "field_1_0": False,
        "line": status,
        "packet_line": "A packet path is not live (packet_path_live is false).",
        "alt_line": "An alternative internet is not live (alt_internet_live is false).",
        "status": status,
    }


def _carrier_clause(ident: str, row: dict[str, Any] | None) -> str:
    code = (row or {}).get("code") or RADIO_ABSENT
    if not row or row.get("state") == "REFUSE":
        if ident == "lan" and row and row.get("up") is False and row.get("hardware"):
            return f"LAN interface {row['hardware']} is down ({code})."
        if ident == "lan":
            return f"LAN hardware is absent ({code})."
        if ident == "wifi":
            return f"Wi-Fi hardware is absent ({code})."
        if ident == "bluetooth":
            return f"Bluetooth hardware is absent ({code})."
        if ident == "rf":
            return f"RF hardware is absent ({code})."
        return f"Photon camera or flash is absent ({code})."
    if ident == "lan":
        where = f" at {row['address']}" if row.get("address") else ""
        name = row.get("hardware") or "unnamed"
        return f"LAN interface {name}{where} is present on this machine and is not a second device."
    hardware = f" {row['hardware']}" if row.get("hardware") else ""
    if ident == "wifi":
        return f"Wi-Fi hardware{hardware} is present on this machine and is not a second device."
    if ident == "bluetooth":
        return f"Bluetooth hardware{hardware} is present on this machine and is not a second device."
    if ident == "rf":
        return f"RF hardware{hardware} is present on this machine and is not a second device."
    return f"Photon camera or flash hardware{hardware} is present on this machine and is not a second device."


def _machine_clause(machine_id: str | None) -> str:
    if machine_id:
        return f"This machine id is {machine_id}. A second device stays false while both ends share that id."
    return "This machine id is absent (MESH-HOST-ABSENT). A second device stays false without two different ids."


def _off_machine(carry: dict[str, Any] | None) -> bool:
    if not carry or carry.get("mock") is True or carry.get("bytes_match") is not True:
        return False
    if not second_device(carry.get("local_host"), carry.get("remote_host")):
        return False
    remote = str(carry.get("remote_addr") or "")
    sent_to = str(carry.get("sent_to") or "")
    local = set(carry.get("local_addrs") or [])
    if not remote or remote in local or remote.startswith("127."):
        return False
    if not sent_to or sent_to in local or sent_to.startswith("127."):
        return False
    return True


def _probe_carriers() -> list[dict[str, Any]]:
    wifi = "ieee80211" if _dir_has("/sys/class/ieee80211") or _wireless_nic() else None
    bluetooth = "bluetooth" if _dir_has("/sys/class/bluetooth") else None
    found = {
        "lan": _probe_lan(),
        "wifi": _kind_probe(wifi),
        "bluetooth": _kind_probe(bluetooth),
        "rf": _kind_probe(_probe_rf()),
        "photon": _kind_probe(_probe_photon()),
    }
    rows = []
    for index, ident in enumerate(ORDER, start=1):
        probe = found[ident]
        down = probe["present"] is True and probe["up"] is False
        if probe["present"] and not down:
            state, hardware, up, code = "HW-PRESENT", probe["kind"], True, None
        elif down:
            state, hardware, up, code = "REFUSE", probe["kind"], False, RADIO_ABSENT
        else:
            state, hardware, up, code = "REFUSE", False, False, RADIO_ABSENT
        rows.append({
            "order": index,
            "id": ident,
            "name": NAMES[ident],
            "state": state,
            "hardware": hardware,
            "address": probe["address"] if probe["present"] else None,
            "up": up,
            "code": code,
            "mock": False,
        })
    return rows


def _kind_probe(kind: str | None) -> dict[str, Any]:
    if kind:
        return {"present": True, "kind": kind, "address": None, "up": True}
    return {"present": False, "kind": None, "address": None, "up": False}


def _probe_lan() -> dict[str, Any]:
    empty = {"present": False, "kind": None, "address": None, "up": False}
    if not _NET.is_dir():
        return empty
    names = _nic_names()
    preferred = _default_iface()
    if preferred and preferred in names and _iface_up(preferred):
        address = _ipv4(preferred)
        if address:
            return {"present": True, "kind": preferred, "address": address, "up": True}
    for name in names:
        if not _iface_up(name):
            continue
        address = _ipv4(name)
        if address:
            return {"present": True, "kind": name, "address": address, "up": True}
    if names:
        name = names[0]
        return {"present": True, "kind": name, "address": _ipv4(name), "up": False}
    return empty


def _probe_rf() -> str | None:
    if Path("/dev/swradio0").exists() or _dir_has("/sys/class/sdr") or _dir_has("/sys/bus/usb/drivers/dvb_usb_rtl28xxu"):
        return "sdr"
    if _dir_has("/sys/class/wwan") or Path("/dev/cdc-wdm0").exists():
        return "modem"
    for name in _nic_names():
        if name.startswith(("wwan", "rmnet")) or name.startswith("cdc-wdm"):
            return name
    return None


def _probe_photon() -> str | None:
    if Path("/dev/video0").exists():
        return "camera"
    leds = Path("/sys/class/leds")
    if not leds.is_dir():
        return None
    try:
        for name in leds.iterdir():
            if "flash" in name.name.lower() or "torch" in name.name.lower():
                return name.name
    except OSError:
        return None
    return None


def _carry(carriers: list[dict[str, Any]], only: str | None = None) -> dict[str, Any]:
    by_id = {row["id"]: row for row in carriers}
    lan = by_id.get("lan")
    refused: list[dict[str, Any]] = []
    skip_lan = only not in {None, "lan"}
    if skip_lan:
        lan_hit = None
    elif not lan or lan.get("state") != "HW-PRESENT" or lan.get("mock") is True:
        lan_hit: dict[str, Any] | None = {
            "ok": False,
            "code": RADIO_ABSENT,
            "packet_live": False,
            "mock": False,
            "alt_internet_live": False,
            "second_device": False,
        }
    else:
        lan_hit = None
        for address, name in _lan_candidates(str(lan.get("hardware") or "")):
            trip = _exchange_mesh(address)
            trip["interface"] = name
            if trip.get("bytes_match") is True and trip.get("mock") is not True:
                lan_hit = trip
                break
            lan_hit = trip
        if not lan_hit or lan_hit.get("bytes_match") is not True:
            lan_hit = {
                "ok": False,
                "code": (lan_hit or {}).get("code") or RADIO_ABSENT,
                "mock": False,
                "packet_live": False,
                "alt_internet_live": False,
                "second_device": False,
                "public_icann": False,
                "bgp": False,
                "interface": lan.get("hardware"),
            }
        else:
            distinct = second_device(lan_hit.get("local_host"), lan_hit.get("remote_host"))
            off = _off_machine(lan_hit)
            lan_hit = {
                **lan_hit,
                "ok": True,
                "code": "PACKET-CARRIED",
                "carrier": "lan",
                "mock": False,
                "packet_live": False,
                "peer_exchange_demonstrated": False,
                "second_device": bool(lan_hit.get("second_device") is True and distinct and off),
                "alt_internet_live": False,
                "public_door": "FG-STUB",
                "public_icann": False,
                "bgp": False,
                "cap7_name_only": True,
                "note": (
                    "A node-mesh frame moved on this machine. It is not the public packet path and not an alternative internet."
                    if not off
                    else "A packet left this machine and the reply came from a different machine id."
                ),
            }
    for ident in ORDER:
        if ident == "lan":
            continue
        row = by_id.get(ident) or {}
        if row.get("state") != "HW-PRESENT":
            refused.append({"id": ident, "code": RADIO_ABSENT, "packet_live": False, "mock": False})
            continue
        refused.append({
            "id": ident,
            "code": "PACKET-NOT-CARRIED",
            "packet_live": False,
            "mock": False,
            "note": "The hardware is present. This process has no round trip on that hardware.",
        })
    if lan_hit and lan_hit.get("ok") is True:
        return {**lan_hit, "refused": refused}
    asked = next((row for row in refused if row["id"] == only), None) if only and only != "lan" else None
    return {
        "ok": False,
        "code": (asked or lan_hit or {}).get("code") or RADIO_ABSENT,
        "mock": False,
        "packet_live": False,
        "peer_exchange_demonstrated": False,
        "second_device": False,
        "alt_internet_live": False,
        "public_icann": False,
        "bgp": False,
        "cap7_name_only": True,
        "refused": refused,
    }


def _lan_candidates(preferred: str) -> list[tuple[str, str]]:
    ranked: list[tuple[int, str, str]] = []
    default = _default_iface()
    for name in _nic_names():
        address = _ipv4(name)
        if not address:
            continue
        if name == preferred and _oper_up(name):
            rank = 0
        elif name == default and _oper_up(name):
            rank = 1
        elif _oper_up(name):
            rank = 2
        else:
            rank = 3
        ranked.append((rank, name, address))
    ranked.sort()
    return [(address, name) for _rank, name, address in ranked]


def _exchange_mesh(address: str) -> dict[str, Any]:
    local_host = _host_id()
    local_addrs = _local_addrs()
    if not local_host:
        return {
            "ok": False,
            "code": "MESH-HOST-ABSENT",
            "packet_live": False,
            "mock": False,
            "alt_internet_live": False,
            "second_device": False,
            "local_addrs": sorted(local_addrs),
        }
    payload = os.urandom(16)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((address, 0))
        port = int(server.getsockname()[1])
        seen: dict[str, Any] = {}

        def serve() -> None:
            server.settimeout(1.2)
            try:
                msg, rinfo = server.recvfrom(4096)
            except OSError as exc:
                seen["error"] = str(exc)
                return
            parsed = _parse_mesh(msg)
            seen["request_from"] = rinfo[0]
            if not parsed or parsed["dst"] != "az-node-b" or parsed["src"] != "az-node-a":
                seen["bad"] = True
                return
            reply = _encode_mesh(src="az-node-b", dst="az-node-a", host=local_host, payload=parsed["payload"])
            try:
                server.sendto(reply, rinfo)
            except OSError as exc:
                seen["error"] = str(exc)
                return
            seen["request"] = parsed

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        client.bind((address, 0))
        client.settimeout(1.2)
        request = _encode_mesh(src="az-node-a", dst="az-node-b", host=local_host, payload=payload)
        client.sendto(request, (address, port))
        reply, rinfo = client.recvfrom(4096)
        thread.join(timeout=1.2)
        parsed = _parse_mesh(reply)
        match = bool(
            parsed
            and parsed["src"] == "az-node-b"
            and parsed["dst"] == "az-node-a"
            and parsed["payload"] == payload
        )
        remote_host = parsed["host"] if parsed else None
        distinct = second_device(local_host, remote_host)
        remote_addr = str(rinfo[0])
        return {
            "ok": match,
            "code": "PACKET-CARRIED" if match else "PACKET-NOT-CARRIED",
            "mesh": match,
            "bytes_match": match,
            "address": address,
            "sent_to": address,
            "remote_addr": remote_addr,
            "request_from": seen.get("request_from"),
            "bytes": len(payload),
            "local_host": local_host,
            "remote_host": remote_host,
            "local_addrs": sorted(local_addrs),
            "second_device": match and distinct and remote_addr not in local_addrs,
            "alt_internet_live": False,
            "packet_live": False,
            "mock": False,
            "public_icann": False,
            "bgp": False,
            "watched": True,
        }
    except OSError as exc:
        return {
            "ok": False,
            "code": "PACKET-NOT-CARRIED",
            "mock": False,
            "packet_live": False,
            "alt_internet_live": False,
            "second_device": False,
            "error": str(exc),
            "local_host": local_host,
            "local_addrs": sorted(local_addrs),
            "sent_to": address,
            "watched": False,
        }
    finally:
        client.close()
        server.close()


def _host_id() -> str | None:
    try:
        text = Path("/etc/machine-id").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if len(text) == 32 and all(ch in "0123456789abcdef" for ch in text):
        return text
    return None


def _nic_names() -> list[str]:
    if not _NET.is_dir():
        return []
    names = []
    try:
        for entry in _NET.iterdir():
            if entry.name and entry.name != "lo":
                names.append(entry.name)
    except OSError:
        return []
    return names


def _oper_up(name: str) -> bool:
    try:
        return (_NET / name / "operstate").read_text(encoding="utf-8").strip() == "up"
    except OSError:
        return False


def _iface_up(name: str) -> bool:
    if not _oper_up(name):
        return False
    carrier = _NET / name / "carrier"
    if not carrier.exists():
        return True
    try:
        text = carrier.read_text(encoding="utf-8").strip()
    except OSError:
        return True
    return text in {"1", ""}


def _default_iface() -> str | None:
    try:
        lines = Path("/proc/net/route").read_text(encoding="utf-8").splitlines()[1:]
    except OSError:
        return None
    fallback = None
    for line in lines:
        cols = line.split()
        if len(cols) < 4 or cols[1] != "00000000" or not cols[0] or cols[0] == "lo":
            continue
        try:
            flags = int(cols[3], 16)
        except ValueError:
            continue
        if flags & 1 == 0:
            continue
        if cols[2] not in {"", "00000000"}:
            return cols[0]
        if fallback is None:
            fallback = cols[0]
    return fallback


def _ipv4(name: str) -> str | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        packed = struct.pack("256s", name.encode("utf-8")[:15])
        res = fcntl_ioctl(sock, packed)
        return socket.inet_ntoa(res[20:24])
    except OSError:
        return None
    finally:
        sock.close()


def fcntl_ioctl(sock: socket.socket, packed: bytes) -> bytes:
    import fcntl

    return fcntl.ioctl(sock.fileno(), 0x8915, packed)


def _local_addrs() -> set[str]:
    found = set()
    for name in _nic_names() + ["lo"]:
        address = _ipv4(name)
        if address:
            found.add(address)
    return found


def _dir_has(path: str) -> bool:
    folder = Path(path)
    if not folder.is_dir():
        return False
    try:
        return any(entry.name not in {".", ".."} for entry in folder.iterdir())
    except OSError:
        return False


def _wireless_nic() -> bool:
    for name in _nic_names():
        if (_NET / name / "wireless").exists():
            return True
    return False


def _crc32(body: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in body:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _pad(text: str, size: int) -> bytes:
    raw = text.encode("utf-8")[:size]
    return raw + bytes(size - len(raw))


def _encode_mesh(*, src: str, dst: str, host: str, payload: bytes) -> bytes:
    raw = bytearray(74 + len(payload))
    raw[0:7] = b"AZMESH1"
    raw[7] = 1
    raw[8:24] = _pad(src, 16)
    raw[24:40] = _pad(dst, 16)
    raw[40:72] = _pad(host, 32)
    raw[72] = (len(payload) >> 8) & 0xFF
    raw[73] = len(payload) & 0xFF
    raw[74:] = payload
    body = bytes(raw)
    crc = _crc32(body)
    return body + struct.pack(">I", crc)


def _parse_mesh(frame: bytes) -> dict[str, Any] | None:
    if len(frame) < 78 or frame[:7] != b"AZMESH1" or frame[7] != 1:
        return None
    body, crc_bytes = frame[:-4], frame[-4:]
    if struct.pack(">I", _crc32(body)) != crc_bytes:
        return None
    length = (body[72] << 8) | body[73]
    if 74 + length != len(body):
        return None
    return {
        "src": body[8:24].split(b"\x00", 1)[0].decode("utf-8", "replace"),
        "dst": body[24:40].split(b"\x00", 1)[0].decode("utf-8", "replace"),
        "host": body[40:72].split(b"\x00", 1)[0].decode("utf-8", "replace"),
        "payload": bytes(body[74:74 + length]),
        "mock": False,
    }
