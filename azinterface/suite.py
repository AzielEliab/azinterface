"""Softwares suite launcher for the local AZInterface page.

Boots a product only when its own local ui is installed or can be installed
from that card's download_url. Otherwise the pane is an honest FragGate session.
GET paths do not install or start anything.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import threading
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .meta import FRAGGATE_CALL, IDENTITY, LOOPBACK
from .shadow_links import add_link, links_path, list_links, remove_link, shadow_desk_html, shadow_map_html
from .trajectory_review import accept_product_imagery, review_event, review_html

SNAPSHOT = Path(__file__).resolve().parent / "data" / "softwares.json"
CATALOG_URL = "https://aziel-runtime.vibelock.workers.dev/v1/software"
# The live catalog leaves AZVPN download_url empty. This is the standalone project archive.
AZVPN_SOURCE = "https://github.com/AzielEliab/azvpn/archive/refs/heads/main.tar.gz"
MAX_DOWNLOAD = 80_000_000
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,48}$")
OP_RE = re.compile(r"^[a-z0-9_]{1,64}$")
URL_RE = re.compile(r"https?://(?:127\.0\.0\.1|localhost):(\d+)")

LABELS = {
    "ready": "Ready",
    "installing": "Installing",
    "needs-install": "Needs install",
    "local-only": "Local only",
    "fraggate-only": "FragGate only",
    "failed": "Could not open",
    "repair": "Repair",
    "running": "Running",
    "quiet": "Quiet",
    "review": "Review",
    "link": "Link",
    "map": "Map",
}


def default_vendor() -> Path:
    return Path.home() / ".azinterface" / "suite"


def bundled_software() -> list[dict[str, Any]]:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows = data.get("software") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [normalize_card(row) for row in rows if isinstance(row, dict) and row.get("slug")]


def normalize_card(raw: dict[str, Any], hint: dict[str, Any] | None = None) -> dict[str, Any]:
    hint = hint or {}
    slug = str(raw.get("slug") or hint.get("slug") or "").strip()
    port = raw.get("ui_port", hint.get("ui_port"))
    if not isinstance(port, int):
        port = None
    status = str(raw.get("status") or hint.get("status") or "")
    fraggate_status = str(raw.get("fraggate_status") or hint.get("fraggate_status") or "")
    local_only = bool(raw.get("local_only") or hint.get("local_only")) or status == "local_only" or fraggate_status == "local_only"
    ui_cmd = hint.get("ui_cmd") if "ui_cmd" in hint else raw.get("ui_cmd")
    if ui_cmd is not None:
        ui_cmd = str(ui_cmd).strip() or None
    download = raw.get("download_url")
    if download is None and "download_url" not in raw:
        download = hint.get("download_url")
    bucket = raw.get("bucket", hint.get("bucket"))
    if bucket not in {"plain", "gate", "lock"}:
        bucket = None
    return {
        "name": str(raw.get("name") or hint.get("name") or slug),
        "slug": slug,
        "download_url": str(download).strip() if download else None,
        "worker_home": raw.get("worker_home") or raw.get("homepage") or hint.get("worker_home"),
        "github": raw.get("github") or hint.get("github"),
        "door": str(raw.get("door") or hint.get("door") or ""),
        "fraggate_status": fraggate_status,
        "status": status,
        "local_only": local_only,
        "ui_port": port,
        "ui_cmd": ui_cmd,
        "bucket": bucket,
    }


def _url_allowed(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "https" and host:
        return True
    return parsed.scheme == "http" and host in {LOOPBACK, "localhost"}


def _fraggate_live(card: dict[str, Any]) -> bool:
    if card.get("local_only"):
        return False
    if str(card.get("door") or "").lower() == "none":
        return False
    return str(card.get("fraggate_status") or "").lower() == "live" or str(card.get("door") or "").lower() == "fraggate"


class Suite:
    def __init__(
        self,
        *,
        catalog: list[dict[str, Any]] | None = None,
        vendor: Path | None = None,
        refresh: bool = True,
        suite_port: int = 8880,
    ) -> None:
        self.vendor = Path(vendor) if vendor is not None else default_vendor()
        self.refresh = refresh
        self.suite_port = suite_port
        self.source = "bundled snapshot"
        self._fixed = [normalize_card(row) for row in catalog] if catalog is not None else None
        self._cards: list[dict[str, Any]] | None = None
        self._state: dict[str, dict[str, Any]] = {}
        self._procs: dict[str, subprocess.Popen[str]] = {}
        self._installed: set[str] = set()
        self._lock = threading.Lock()
        self._job = False
        self._ports_before: set[int] | None = None
        self._vpn_listen: str | None = None
        self._traj_listen: str | None = None

    def cards(self) -> list[dict[str, Any]]:
        with self._lock:
            if self._cards is None:
                self._cards = self._load_cards()
            return list(self._cards)

    def _load_cards(self) -> list[dict[str, Any]]:
        bundled = bundled_software() if self._fixed is None else list(self._fixed)
        hints = {row["slug"]: row for row in bundled_software()}
        if self._fixed is not None:
            self.source = "test catalog"
            return bundled
        if not self.refresh:
            self.source = "bundled snapshot"
            return bundled
        live = _fetch_live()
        if not live:
            self.source = "bundled snapshot"
            return bundled
        merged: list[dict[str, Any]] = []
        for item in live:
            slug = str(item.get("slug") or "")
            hint = hints.get(slug, {})
            card = normalize_card(item, hint)
            card["ui_cmd"] = hint.get("ui_cmd")
            card["ui_port"] = hint.get("ui_port") if isinstance(hint.get("ui_port"), int) else None
            if hint.get("local_only"):
                card["local_only"] = True
            merged.append(card)
        self.source = "GET /v1/software"
        return merged

    def document(self) -> dict[str, Any]:
        rows = [self._public_row(card) for card in self.cards()]
        rows.sort(key=lambda row: 0 if row["slug"] == "azvpn" else 1)
        counts: dict[str, int] = {}
        outcomes: dict[str, int] = {}
        for row in rows:
            counts[row["posture"]] = counts.get(row["posture"], 0) + 1
            if row.get("outcome"):
                outcomes[row["outcome"]] = outcomes.get(row["outcome"], 0) + 1
        return {
            "ok": True,
            "count": len(rows),
            "source": self.source,
            "author": IDENTITY,
            "running": self._job,
            "vendor": str(self.vendor),
            "counts": counts,
            "outcomes": outcomes,
            "software": rows,
        }

    def _public_row(self, card: dict[str, Any]) -> dict[str, Any]:
        slug = card["slug"]
        with self._lock:
            saved = dict(self._state.get(slug) or {})
        if saved.get("posture"):
            posture = str(saved["posture"])
            reason = str(saved.get("reason") or "")
            nxt = str(saved.get("next") or "")
            url = saved.get("url")
            mode = saved.get("mode")
            outcome = saved.get("outcome")
        else:
            posture, reason, nxt = self._idle(card)
            if slug == "azvpn":
                url = "/suite/azvpn"
                mode = "vpn"
            elif slug == "azinterface":
                url = "/custody"
                mode = "suite"
            elif slug == "azcoherence":
                url = None
                mode = "background"
            elif slug == "trajectorylock":
                url = "/suite/trajectorylock"
                mode = "review"
            elif slug == "shadowlock":
                url = "/suite/shadowlock"
                mode = "link"
            elif slug == "4dmap":
                url = "/suite/4dmap"
                mode = "map"
            else:
                url = None
                mode = None
            outcome = None
        return {
            "name": card["name"],
            "slug": slug,
            "posture": posture,
            "label": LABELS.get(posture, posture),
            "reason": reason,
            "next": nxt,
            "url": url,
            "mode": mode,
            "outcome": outcome,
            "ui_cmd": card.get("ui_cmd"),
            "ui_port": card.get("ui_port"),
            "download_url": card.get("download_url"),
            "github": card.get("github"),
            "local_only": bool(card.get("local_only")),
            "fraggate": _fraggate_live(card),
            "always_on": slug == "azvpn",
            "background": slug == "azcoherence",
            "review": slug == "trajectorylock",
            "link": slug == "shadowlock",
            "map": slug == "4dmap",
            "bucket": card.get("bucket"),
        }

    def _idle(self, card: dict[str, Any]) -> tuple[str, str, str]:
        slug = card["slug"]
        if slug == "azinterface":
            return (
                "ready",
                "AZInterface is this suite, already running on this computer.",
                "Press Start suite. Custody opens in the pane.",
            )
        if slug == "azvpn":
            if self._azvpn_up(card):
                return (
                    "ready",
                    "AZVPN is on. It starts with the suite and is not optional.",
                    "Rotate IP and settings are in the pane.",
                )
            exe = self._find_exe(card)
            if exe:
                return (
                    "ready",
                    "AZVPN is installed. It starts with the suite and is not optional.",
                    "Press Start suite. Rotate IP and settings are in the pane.",
                )
            return (
                "repair",
                "AZVPN is required and is not installed on this computer.",
                "Press Start suite. The suite installs the project archive and starts AZVPN. There is no opt-out.",
            )
        if slug == "azcoherence":
            if self._coherence_health(card):
                return (
                    "running",
                    "AZCoherence is running in the background.",
                    "This tile is status only. It does not open a review page.",
                )
            return (
                "quiet",
                "AZCoherence is quiet. It is a background service, not a page to open.",
                "Press Start suite. It starts in the background. This tile stays status only.",
            )
        if slug == "trajectorylock":
            extra = ""
            if not self._find_exe(card):
                cmd = card.get("ui_cmd") or "trajectorylock ui"
                extra = f" {cmd} is not installed yet. Start suite will try to install it. The review workbench on this desk still pulls imagery."
            return (
                "review",
                "TrajectoryLock opens a review workbench. It pulls satellite imagery for an event place and time, then traces what it knows."
                + extra,
                "Press Review. Enter a place and a time. The pane shows a real frame or names the gap.",
            )
        if slug == "shadowlock":
            return (
                "link",
                "ShadowLock opens a link desk. Drop a Software, or press Link, to record it and an input under a business label.",
                "Press Link. Plain, gate, and lock each have a column. Nothing is linked until you drop or press Link.",
            )
        if slug == "4dmap":
            return (
                "map",
                "4DMap shows ShadowLock links on a Softwares · Shadow layer.",
                "Press Map. If nothing is linked, the layer says so.",
            )
        if self._port_is_ours(card):
            return (
                "ready",
                f"Something is already listening on {LOOPBACK}:{card['ui_port']}.",
                "Press Start suite to show that page. This check does not start a second copy.",
            )
        exe = self._find_exe(card)
        if exe and card.get("ui_cmd"):
            return (
                "ready",
                f"{card['ui_cmd']} is installed.",
                "Press Start suite to open its local page.",
            )
        if not card.get("ui_cmd"):
            if _fraggate_live(card):
                return (
                    "fraggate-only",
                    "No local ui command is listed for this Software.",
                    "Open the FragGate session. This suite will not invent a local page.",
                )
            if card.get("download_url"):
                return (
                    "needs-install",
                    "No local ui command is listed, so a download cannot be opened as a page.",
                    "Use the project's own install notes on its download page.",
                )
            return (
                "failed",
                "No local page and no FragGate door are listed.",
                "This suite cannot open it.",
            )
        if card.get("local_only") and not exe:
            return (
                "local-only",
                f"{card['name']} is local only and is not installed on this computer.",
                "Press Start suite to install it from its download, then open its local page.",
            )
        if card.get("download_url"):
            return (
                "needs-install",
                f"{card['ui_cmd']} is not installed on this computer.",
                "Press Start suite to install it from its download, then open its local page.",
            )
        if _fraggate_live(card):
            return (
                "fraggate-only",
                f"{card['ui_cmd']} is not installed, and the catalog has no download.",
                "Open the FragGate session for this slug.",
            )
        return (
            "failed",
            f"{card['ui_cmd']} is not installed, and there is no download to fetch.",
            "Install that product yourself, then press Start suite again.",
        )

    def _port_is_ours(self, card: dict[str, Any]) -> bool:
        port = card.get("ui_port")
        if not isinstance(port, int) or port == self.suite_port:
            return False
        if not _port_open(port):
            return False
        # During Start suite, a port that opened mid-run belongs to whichever
        # product just bound it. Only a port that was already open counts.
        if self._ports_before is not None:
            return port in self._ports_before
        return True

    def _find_exe(self, card: dict[str, Any]) -> str | None:
        cmd = card.get("ui_cmd")
        if not cmd:
            return None
        name = cmd.split()[0]
        found = shutil.which(name)
        if found:
            return found
        candidate = self.vendor / card["slug"] / ".venv" / "bin" / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        wrapper = self.vendor / card["slug"] / "bin" / name
        if wrapper.is_file() and os.access(wrapper, os.X_OK):
            return str(wrapper)
        bundled = self.vendor / card["slug"] / "src"
        if bundled.is_dir():
            for path in bundled.rglob(name):
                if path.is_file() and os.access(path, os.X_OK) and "bin" in path.parts:
                    return str(path)
        return None

    def start(self) -> dict[str, Any]:
        with self._lock:
            if self._job:
                return {"ok": True, "running": True, "already": True}
            self._job = True
        thread = threading.Thread(target=self._start_all, name="azinterface-suite", daemon=True)
        thread.start()
        return {"ok": True, "running": True}

    def _start_all(self) -> None:
        try:
            cards = self.cards()
            before: set[int] = set()
            for card in cards:
                port = card.get("ui_port")
                if isinstance(port, int) and port != self.suite_port and _port_open(port):
                    before.add(port)
            self._ports_before = before
            vpn = next((card for card in cards if card["slug"] == "azvpn"), None)
            if vpn is not None:
                try:
                    self.boot("azvpn", allow_install=True)
                except Exception as exc:  # noqa: BLE001
                    self._azvpn_repair(vpn, f"Could not start AZVPN. {exc}")
            for card in cards:
                if card["slug"] == "azvpn":
                    continue
                try:
                    self.boot(card["slug"], allow_install=False)
                except Exception as exc:  # noqa: BLE001 — one Software must not stop the rest
                    self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                               reason=f"Could not open {card['name']}. {exc}",
                               nxt="Press Start suite again. The other Softwares still open.")
            queue = []
            for card in cards:
                if card["slug"] == "azvpn":
                    continue
                row = self._public_row(card)
                if row["posture"] in {"needs-install", "local-only"} and card.get("download_url") and card.get("ui_cmd"):
                    queue.append(card)
            if queue:
                workers = min(3, len(queue))
                def _install_one(card: dict[str, Any]) -> None:
                    try:
                        self.boot(card["slug"], allow_install=True)
                    except Exception as exc:  # noqa: BLE001 — one Software must not stop the rest
                        self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                                   reason=f"Could not open {card['name']}. {exc}",
                                   nxt="Press Start suite again. The other Softwares still open.")

                with ThreadPoolExecutor(max_workers=workers) as pool:
                    list(pool.map(_install_one, queue))
        finally:
            self._ports_before = None
            with self._lock:
                self._job = False

    def boot(self, slug: str, *, allow_install: bool = True) -> dict[str, Any]:
        row = self._boot_impl(slug, allow_install=allow_install)
        if slug == "azcoherence":
            return self._as_background(row)
        if slug == "trajectorylock":
            return self._as_review(row)
        if slug == "shadowlock":
            return self._as_desk(
                row,
                slug="shadowlock",
                posture="link",
                mode="link",
                url="/suite/shadowlock",
                desk_reason="The link desk records a Software and an optional input. It does not read file contents.",
                nxt="Press Link. Drop a Software onto its kind, or press Link on that Software.",
            )
        if slug == "4dmap":
            return self._as_desk(
                row,
                slug="4dmap",
                posture="map",
                mode="map",
                url="/suite/4dmap",
                desk_reason="The map pane shows the ShadowLock link record on the Softwares · Shadow layer.",
                nxt="Press Map. The layer lists only links that were saved.",
            )
        return row

    def _boot_impl(self, slug: str, *, allow_install: bool = True) -> dict[str, Any]:
        card = self._card(slug)
        if card is None:
            return {
                "ok": False,
                "slug": slug,
                "posture": "failed",
                "label": LABELS["failed"],
                "reason": f"No Software named {slug} is in the catalog.",
                "next": "Refresh the suite. The name has to match the catalog.",
                "outcome": "failed",
            }
        if slug == "azinterface":
            return self._save(card, posture="ready", mode="suite", url="/custody", outcome="booted",
                              reason="AZInterface is this suite. Custody is open in the pane.",
                              nxt="Use Integrity and the page cycle inside the pane.")
        if slug == "azvpn":
            return self._boot_azvpn(card, allow_install=allow_install)
        if self._our_proc_alive(slug):
            saved = self._public_row(card)
            saved["ok"] = True
            return saved
        if not card.get("ui_cmd"):
            if _fraggate_live(card):
                return self._fraggate(card, "No local ui command is listed, so this suite did not start a local page.")
            return self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                              reason="No local ui command is listed, and FragGate is not the door for this Software.",
                              nxt="This suite cannot open it.")
        if self._port_is_ours(card):
            url = f"http://{LOOPBACK}:{card['ui_port']}/"
            return self._save(card, posture="ready", mode="local", url=url, outcome="booted",
                              reason=f"Already listening at {url}. The suite did not start a second copy.",
                              nxt="Use the page in the pane. If the frame is empty, open the address itself.")
        exe = self._find_exe(card)
        installed_now = False
        if not exe:
            if not allow_install:
                posture, reason, nxt = self._idle(card)
                if posture == "fraggate-only":
                    return self._fraggate(card, reason)
                return self._save(card, posture=posture, mode=None, url=None, outcome=None, reason=reason, nxt=nxt)
            if not card.get("download_url"):
                if _fraggate_live(card):
                    return self._fraggate(card, f"{card['ui_cmd']} is not installed, and the catalog has no download.")
                return self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                                  reason=f"{card['ui_cmd']} is not installed, and there is no download to fetch.",
                                  nxt="Install that product yourself, then press Start suite again.")
            self._save(card, posture="installing", mode=None, url=None, outcome=None,
                       reason=f"Installing {card['name']} from its download.",
                       nxt="Wait for this tile. The suite does not open a page until the install finishes.")
            try:
                self._install(card)
                installed_now = True
            except Exception as exc:  # noqa: BLE001 — show the failure, do not pretend it opened
                message = str(exc).strip() or "Install failed."
                if _fraggate_live(card) and not card.get("local_only"):
                    return self._fraggate(card, f"Install failed. {message}")
                posture = "local-only" if card.get("local_only") else "failed"
                return self._save(card, posture=posture, mode=None, url=None, outcome="failed",
                                  reason=f"Install failed. {message}",
                                  nxt="Try Start suite again, or install from the project's page, then open it here.")
            exe = self._find_exe(card)
            if not exe:
                return self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                                  reason="The download unpacked, but the ui command was not found afterward.",
                                  nxt=f"Look in {self.vendor / card['slug']} and run {card['ui_cmd']} yourself.")
        return self._spawn(card, exe, installed_now=installed_now)

    def _as_background(self, row: dict[str, Any]) -> dict[str, Any]:
        card = self._card("azcoherence")
        if card is None:
            return row
        ours = self._our_proc_alive("azcoherence")
        health = self._coherence_health(card)
        if ours or health:
            outcome = row.get("outcome") if row.get("outcome") in {"booted", "install-then-boot"} else "booted"
            return self._save(
                card,
                posture="running",
                mode="background",
                url=None,
                outcome=outcome,
                reason="AZCoherence is running in the background.",
                nxt="This tile is status only. It does not open a review page.",
            )
        reason = str(row.get("reason") or "AZCoherence is quiet.").strip()
        if "quiet" not in reason.lower() and "background" not in reason.lower():
            reason = f"AZCoherence is quiet. {reason}"
        return self._save(
            card,
            posture="quiet",
            mode="background",
            url=None,
            outcome=row.get("outcome"),
            reason=reason,
            nxt="Press Start suite. AZCoherence starts in the background. This tile is status only. It does not open a review page.",
        )

    def _coherence_health(self, card: dict[str, Any]) -> bool:
        port = card.get("ui_port")
        if not isinstance(port, int) or port == self.suite_port:
            return False
        if not _port_open(port):
            return False
        url = f"http://{LOOPBACK}:{port}/v1/health"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                body = resp.read(4000).decode("utf-8", "replace").lower()
        except (urllib.error.URLError, TimeoutError, OSError):
            return False
        return "azcoherence" in body

    def _as_review(self, row: dict[str, Any]) -> dict[str, Any]:
        card = self._card("trajectorylock")
        if card is None:
            return row
        product_url = row.get("url") if isinstance(row.get("url"), str) else None
        ours = self._our_proc_alive("trajectorylock")
        if product_url and product_url.startswith("http") and (ours or self._trajectory_page(product_url)):
            self._traj_listen = product_url
        else:
            if product_url and product_url.startswith("http"):
                prior = str(row.get("reason") or "")
                row = dict(row)
                row["reason"] = (
                    f"Port {card.get('ui_port')} answered, but the page is not TrajectoryLock. {prior}"
                ).strip()
                if row.get("outcome") in {"booted", "install-then-boot"}:
                    row["outcome"] = "failed"
            product_url = None
        outcome = row.get("outcome")
        if outcome == "fraggate":
            outcome = None
        running = bool(product_url) and outcome in {"booted", "install-then-boot"}
        workbench = (
            "The review workbench pulls NASA GIBS imagery for the event place and time and traces what it measured. "
            "It does not invent pixels."
        )
        prior = str(row.get("reason") or "").strip()
        if running and product_url:
            reason = f"trajectorylock ui is open at {product_url}. {workbench}"
        else:
            reason = f"{prior} {workbench}".strip()
        return self._save(
            card,
            posture="review",
            mode="review",
            url="/suite/trajectorylock",
            outcome=outcome,
            reason=reason,
            nxt="Press Review. Enter the event place and time. The pane shows a real frame or names the gap.",
        )

    def _trajectory_page(self, url: str) -> bool:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                body = resp.read(5000).decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, OSError):
            return False
        lowered = body.lower()
        return "trajectorylock" in lowered

    def _as_desk(
        self,
        row: dict[str, Any],
        *,
        slug: str,
        posture: str,
        mode: str,
        url: str,
        desk_reason: str,
        nxt: str,
    ) -> dict[str, Any]:
        card = self._card(slug)
        if card is None:
            return row
        outcome = row.get("outcome")
        if outcome == "fraggate":
            outcome = None
        product_url = row.get("url") if isinstance(row.get("url"), str) else None
        if not (isinstance(product_url, str) and product_url.startswith("http")):
            product_url = None
        running = bool(product_url) and outcome in {"booted", "install-then-boot"}
        prior = str(row.get("reason") or "").strip()
        if running and product_url:
            reason = f"{card.get('ui_cmd') or slug} is open at {product_url}. {desk_reason}"
        else:
            reason = f"{prior} {desk_reason}".strip()
        return self._save(card, posture=posture, mode=mode, url=url, outcome=outcome, reason=reason, nxt=nxt)

    def trajectory_html(self) -> str:
        return review_html()

    def shadow_html(self) -> str:
        return shadow_desk_html()

    def map_html(self) -> str:
        return shadow_map_html()

    def shadow_links(self) -> dict[str, Any]:
        return list_links(links_path(self.vendor))

    def shadow_link(self, payload: dict[str, Any]) -> dict[str, Any]:
        return add_link(links_path(self.vendor), payload, self.cards())

    def shadow_unlink(self, payload: dict[str, Any]) -> dict[str, Any]:
        return remove_link(links_path(self.vendor), str(payload.get("id") or ""))

    def review_trajectory(self, payload: dict[str, Any]) -> dict[str, Any]:
        place = str(payload.get("place") or "").strip()
        when = str(payload.get("time") or payload.get("when") or "").strip()
        proxied = self._proxy_imagery(payload)
        if proxied is not None and proxied.get("image_jpeg_b64"):
            note = "Imagery came from the running trajectorylock ui."
            proxied["note"] = note
            trace = str(proxied.get("trace") or "").strip()
            proxied["trace"] = f"{note}\n{trace}".strip()
            return proxied
        result = review_event(place=place, lat=payload.get("lat"), lon=payload.get("lon"), when=when)
        note = "This pane fetched NASA GIBS. It shows a JPEG only when the source returned one."
        if proxied is not None and proxied.get("gaps"):
            note = "The running trajectorylock ui did not return a JPEG. " + note
        elif self._traj_listen:
            note = "The installed trajectorylock ui did not return imagery. " + note
        result["imagery_via"] = "NASA GIBS"
        result["note"] = note
        result["trace"] = f"{note}\n{result.get('trace') or ''}".strip()
        return result

    def _proxy_imagery(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        base = self._traj_listen
        if not base:
            return None
        body = json.dumps(
            {
                "place": payload.get("place"),
                "lat": payload.get("lat"),
                "lon": payload.get("lon"),
                "time": payload.get("time") or payload.get("when"),
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            base.rstrip("/") + "/api/imagery",
            data=body,
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read(3_000_000)
        except (urllib.error.URLError, TimeoutError, OSError):
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict):
            return None
        return accept_product_imagery(data)

    def _fraggate(self, card: dict[str, Any], reason: str) -> dict[str, Any]:
        return self._save(
            card,
            posture="fraggate-only",
            mode="fraggate",
            url=f"/suite/fraggate/{card['slug']}",
            outcome="fraggate",
            reason=reason,
            nxt="Use the FragGate session in the pane. It calls the real door for this slug.",
        )

    def _spawn(self, card: dict[str, Any], exe: str, *, installed_now: bool) -> dict[str, Any]:
        name, args = _split_cmd(str(card.get("ui_cmd") or ""))
        argv = [exe, *args]
        env = os.environ.copy()
        bin_dir = str(Path(exe).parent)
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONUNBUFFERED"] = "1"
        cwd = Path(exe).parent
        if cwd.name == "bin" and cwd.parent.name == ".venv":
            project = _find_project(self.vendor / card["slug"] / "src")
            if project is not None:
                cwd = project
        try:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                cwd=str(cwd),
                start_new_session=True,
            )
        except OSError as exc:
            return self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                              reason=f"Could not start {name}: {exc}",
                              nxt=f"Run {card['ui_cmd']} in a terminal and read the error.")
        with self._lock:
            self._procs[card["slug"]] = proc
        lines: list[str] = []
        reader = threading.Thread(target=_read_output, args=(proc, lines), daemon=True)
        reader.start()
        url = _wait_url(proc, lines, card.get("ui_port"), skip_port=self.suite_port)
        if not url:
            tail = " ".join(line.strip() for line in lines[-4:] if line.strip())
            if proc.poll() is not None:
                reason = f"{card['ui_cmd']} exited before it opened a page."
            else:
                reason = f"{card['ui_cmd']} is running, but it did not announce a loopback page."
            if tail:
                reason = f"{reason} {tail}"
            self._stop_proc(card["slug"])
            return self._save(card, posture="failed", mode=None, url=None, outcome="failed",
                              reason=reason,
                              nxt=f"Run {card['ui_cmd']} in a terminal. This suite will not show a blank page as if it opened.")
        outcome = "install-then-boot" if installed_now else "booted"
        if installed_now:
            with self._lock:
                self._installed.add(card["slug"])
        if card["slug"] == "azvpn":
            self._remember_vpn(url)
            return self._save(
                card,
                posture="ready",
                mode="vpn",
                url="/suite/azvpn",
                outcome=outcome,
                reason=f"AZVPN is on at {url}. It started with the suite.",
                nxt="Use Rotate IP. That opens a new in-process path. It does not change this computer's public address, and there is no opt-out.",
            )
        return self._save(card, posture="ready", mode="local", url=url, outcome=outcome,
                          reason=f"Open at {url}.",
                          nxt="Use it in the pane. If the frame is empty, open that address. The product refused embedding, or it is still painting.")

    def _card(self, slug: str) -> dict[str, Any] | None:
        if not SLUG_RE.fullmatch(slug or ""):
            return None
        for card in self.cards():
            if card["slug"] == slug:
                return card
        return None

    def _save(self, card: dict[str, Any], *, posture: str, mode: str | None, url: str | None,
              outcome: str | None, reason: str, nxt: str) -> dict[str, Any]:
        saved = {
            "posture": posture,
            "mode": mode,
            "url": url,
            "outcome": outcome,
            "reason": reason,
            "next": nxt,
        }
        with self._lock:
            self._state[card["slug"]] = saved
        row = self._public_row(card)
        if posture == "running" and outcome in {"booted", "install-then-boot"}:
            row["ok"] = True
        elif posture in {"review", "link", "map"}:
            row["ok"] = True
        else:
            row["ok"] = posture in {"ready", "fraggate-only"} and outcome in {"booted", "install-then-boot", "fraggate"}
        return row

    def _our_proc_alive(self, slug: str) -> bool:
        with self._lock:
            proc = self._procs.get(slug)
        return bool(proc and proc.poll() is None)

    def _stop_proc(self, slug: str) -> None:
        with self._lock:
            proc = self._procs.pop(slug, None)
        if proc and proc.poll() is None:
            _terminate(proc)

    def stop(self) -> None:
        with self._lock:
            procs = list(self._procs.items())
            self._procs.clear()
        for _slug, proc in procs:
            if proc.poll() is None:
                _terminate(proc)

    def _install(self, card: dict[str, Any]) -> None:
        url = str(card.get("download_url") or "")
        if not _url_allowed(url):
            raise RuntimeError("The download address is not one this suite will fetch.")
        root = self.vendor / card["slug"]
        root.mkdir(parents=True, exist_ok=True)
        blob = root / "download.bin"
        data = _download(url)
        if data.lstrip()[:1] in {b"<", b"{"} and not data.startswith(b"\x1f\x8b") and not data.startswith(b"PK"):
            raise RuntimeError("The download address returned a page, not a package.")
        blob.write_bytes(data)
        src = root / "src"
        if src.exists():
            _remove_tree(src)
        src.mkdir()
        _extract(blob, src)
        for path in src.rglob("*"):
            if path.is_file() and "bin" in path.parts:
                path.chmod(path.stat().st_mode | 0o755)
        project = _find_project(src)
        if project is None:
            node_root = _find_node_project(src)
            if node_root is not None:
                _install_node(node_root, root, card["slug"])
                return
            if self._find_exe(card):
                return
            raise RuntimeError("The package unpacked, but it has no project this suite can install.")
        venv = root / ".venv"
        pip = venv / "bin" / "pip"
        if not pip.is_file():
            if venv.exists():
                _remove_tree(venv)
            made = subprocess.run(
                [sys.executable, "-m", "venv", str(venv)],
                capture_output=True,
                text=True,
                timeout=90,
            )
            if made.returncode != 0 or not pip.is_file():
                detail = (made.stderr or made.stdout or "").strip().splitlines()
                line = detail[-1] if detail else f"venv exited {made.returncode}"
                if "ensurepip" in (made.stderr or "") or "python3-venv" in (made.stderr or ""):
                    line = "This computer cannot create a Python environment. Install the python3-venv package, then press Start suite again."
                raise RuntimeError(line)
        pip = venv / "bin" / "pip"
        proc = subprocess.run(
            [str(pip), "install", "-e", str(project)],
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"},
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            detail = tail[-1] if tail else f"pip exited {proc.returncode}"
            raise RuntimeError(detail)

    def _boot_azvpn(self, card: dict[str, Any], *, allow_install: bool) -> dict[str, Any]:
        if self._our_proc_alive("azvpn") or self._azvpn_up(card):
            port = self._vpn_port(card)
            self._remember_vpn(self._vpn_listen or f"http://{LOOPBACK}:{port}/")
            return self._save(
                card,
                posture="ready",
                mode="vpn",
                url="/suite/azvpn",
                outcome="booted",
                reason="AZVPN is on. It started with the suite and is not optional.",
                nxt="Use Rotate IP and settings. There is no opt-out.",
            )
        exe = self._find_exe(card)
        if not exe:
            if not allow_install:
                return self._azvpn_repair(card, "AZVPN is required and is not installed yet.", outcome=None)
            install_card = dict(card)
            note = ""
            if not install_card.get("download_url"):
                install_card["download_url"] = AZVPN_SOURCE
                note = " The catalog has no download, so this suite uses the AZVPN project archive."
            self._save(
                card,
                posture="installing",
                mode="vpn",
                url="/suite/azvpn",
                outcome=None,
                reason="Installing AZVPN." + note,
                nxt="Wait. AZVPN starts when the install finishes. There is no opt-out.",
            )
            try:
                self._install(install_card)
            except Exception as exc:  # noqa: BLE001 — show the failure, do not pretend it opened
                return self._azvpn_repair(card, f"Install failed. {exc}")
            exe = self._find_exe(card)
            if not exe:
                return self._azvpn_repair(card, "The AZVPN archive unpacked, but azvpn ui was not found afterward.")
            return self._spawn(self._azvpn_command(card), exe, installed_now=True)
        return self._spawn(self._azvpn_command(card), exe, installed_now=False)

    def _azvpn_command(self, card: dict[str, Any]) -> dict[str, Any]:
        """Use the catalog port unless another program is already bound there."""
        port = card.get("ui_port") if isinstance(card.get("ui_port"), int) else 8787
        if not _port_open(port) or self._azvpn_up(card):
            return card
        for candidate in range(port + 1, port + 30):
            if candidate != self.suite_port and not _port_open(candidate):
                shifted = dict(card)
                shifted["ui_cmd"] = f"{card.get('ui_cmd') or 'azvpn ui'} --port {candidate}"
                shifted["ui_port"] = candidate
                return shifted
        return card

    def _azvpn_repair(self, card: dict[str, Any], reason: str, outcome: str | None = "repair") -> dict[str, Any]:
        return self._save(
            card,
            posture="repair",
            mode="vpn",
            url="/suite/azvpn",
            outcome=outcome,
            reason=reason,
            nxt="Press Start suite again. AZVPN stays required. There is no opt-out.",
        )

    def _remember_vpn(self, url: str) -> None:
        self._vpn_listen = url
        path = self.vendor / "azvpn" / "listen.url"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(url + "\n", encoding="utf-8")

    def _vpn_port(self, card: dict[str, Any]) -> int:
        if self._vpn_listen:
            match = URL_RE.search(self._vpn_listen)
            if match:
                return int(match.group(1))
        saved = self.vendor / "azvpn" / "listen.url"
        if saved.is_file():
            match = URL_RE.search(saved.read_text(encoding="utf-8"))
            if match:
                return int(match.group(1))
        port = card.get("ui_port")
        return port if isinstance(port, int) else 8787

    def _azvpn_up(self, card: dict[str, Any]) -> bool:
        ports = [self._vpn_port(card)]
        catalog = card.get("ui_port")
        if isinstance(catalog, int) and catalog not in ports:
            ports.append(catalog)
        for port in ports:
            if port == self.suite_port or not _port_open(port):
                continue
            req = urllib.request.Request(
                f"http://{LOOPBACK}:{port}/",
                headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
            )
            try:
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    body = resp.read(4000).decode("utf-8", "replace")
            except (urllib.error.URLError, TimeoutError, OSError):
                continue
            if "AZVPN" in body:
                self._vpn_listen = f"http://{LOOPBACK}:{port}/"
                return True
        return False

    def azvpn_html(self) -> str:
        card = self._card("azvpn")
        port = 8787
        reason = "AZVPN is required. Press Start suite."
        if card is not None:
            if isinstance(card.get("ui_port"), int):
                port = card["ui_port"]
            reason = self._public_row(card)["reason"]
        up = card is not None and (self._our_proc_alive("azvpn") or self._azvpn_up(card))
        status = "ON" if up else "Repair"
        listen = escape(self._vpn_listen or f"http://{LOOPBACK}:{port}/")
        safe_reason = escape(reason)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZVPN</title>
<style>
:root {{ color-scheme: light dark; --bg:#f4f0e6; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#100f0c; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }}
}}
body {{ margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
main {{ padding:1rem 1.1rem 2rem; max-width:40rem; }}
button {{ font:inherit; min-height:44px; border-radius:10px; background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.55rem 0.9rem; }}
:focus-visible {{ outline:2px solid #c9a227; outline-offset:3px; }}
pre {{ white-space:pre-wrap; overflow-wrap:anywhere; }}
p, summary {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>AZVPN</h1>
  <p id="status">Status: {status}. AZVPN starts with the suite. It is not optional.</p>
  <p>{safe_reason}</p>
  <p><button id="rotate" type="button">Rotate IP</button></p>
  <pre id="out">Rotate IP opens a new in-process path. It does not change this computer's public address.</pre>
  <details>
    <summary>Settings</summary>
    <p>Listening address the suite uses: {listen}. The Softwares catalog has no AZVPN download, so a missing install uses the project archive.</p>
    <p>Public address rotation is SLOT. WireGuard, public Tor, and origin-hiding are SLOT. Rotate IP opens a new in-process onion path only.</p>
  </details>
</main>
<script>
document.getElementById("rotate").addEventListener("click", async function () {{
  var out = document.getElementById("out");
  out.textContent = "Rotating…";
  try {{
    var res = await fetch("/suite/azvpn/rotate", {{ method: "POST", headers: {{ "content-type": "application/json" }}, body: "{{}}" }});
    var data = await res.json();
    out.textContent = data.note || data.error || JSON.stringify(data, null, 2);
    if (data.next) out.textContent += " Next: " + data.next;
  }} catch (e) {{
    out.textContent = "Rotate IP could not reach AZVPN. Press Start suite again. There is no opt-out.";
  }}
}});
</script>
</body>
</html>
"""

    def rotate_azvpn(self) -> dict[str, Any]:
        card = self._card("azvpn")
        if card is None:
            return {
                "ok": False,
                "status": "Repair",
                "error": "AZVPN is not in the catalog.",
                "next": "Refresh the suite.",
            }
        port = self._vpn_port(card)
        if not (self._our_proc_alive("azvpn") or self._azvpn_up(card)):
            return {
                "ok": False,
                "status": "Repair",
                "error": "AZVPN is not listening.",
                "next": "Press Start suite. AZVPN starts with the suite. There is no opt-out.",
            }
        body = json.dumps({"peer": "suite", "mode": "onion"}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{LOOPBACK}:{port}/v1/open",
            data=body,
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                parsed = json.loads(resp.read(200_000).decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read(400).decode("utf-8", "replace")
            return {
                "ok": False,
                "status": "Repair",
                "error": f"AZVPN answered {exc.code}.",
                "detail": detail[:400],
                "next": "Press Start suite again. There is no opt-out.",
            }
        except urllib.error.URLError as exc:
            return {
                "ok": False,
                "status": "Repair",
                "error": f"Rotate IP could not reach AZVPN. {exc.reason}",
                "next": "Press Start suite again. There is no opt-out.",
            }
        except json.JSONDecodeError:
            return {
                "ok": False,
                "status": "Repair",
                "error": "AZVPN did not return JSON.",
                "next": "Press Rotate IP again.",
            }
        return {
            "ok": True,
            "status": "ON",
            "public_address": "unchanged",
            "note": "Opened a new in-process onion path. This computer's public address did not change. WireGuard, public Tor, and origin-hiding are SLOT.",
            "result": parsed if isinstance(parsed, dict) else {"result": parsed},
        }

    def fraggate_html(self, slug: str) -> str | None:
        card = self._card(slug)
        if card is None or not _fraggate_live(card):
            return None
        name = escape(card["name"])
        safe_slug = escape(card["slug"])
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — FragGate</title>
<style>
:root {{ color-scheme: light dark; --bg:#f4f0e6; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#100f0c; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }}
}}
body {{ margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
main {{ padding:1rem 1.1rem 2rem; max-width:40rem; }}
button, input {{ font:inherit; min-height:44px; border-radius:10px; }}
button {{ background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.55rem 0.9rem; }}
input {{ width:100%; box-sizing:border-box; background:transparent; color:inherit; border:1px solid var(--line); padding:0.5rem 0.6rem; }}
:focus-visible {{ outline:2px solid #c9a227; outline-offset:3px; }}
pre {{ white-space:pre-wrap; overflow-wrap:anywhere; }}
p {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>{name}</h1>
  <p>This is a FragGate session for slug <code>{safe_slug}</code>. It is not a local page. The call goes to the aziel-runtime door.</p>
  <label for="op">Operation</label>
  <input id="op" value="health">
  <p><button id="call" type="button">Call</button></p>
  <pre id="out">No call yet.</pre>
</main>
<script>
document.getElementById("call").addEventListener("click", async function () {{
  var out = document.getElementById("out");
  out.textContent = "Calling…";
  try {{
    var res = await fetch("/suite/fraggate", {{
      method: "POST",
      headers: {{ "content-type": "application/json" }},
      body: JSON.stringify({{ slug: "{safe_slug}", op: document.getElementById("op").value, payload: {{}} }})
    }});
    var data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  }} catch (e) {{
    out.textContent = "The session could not reach the door. Stay on this computer and try Call again.";
  }}
}});
</script>
</body>
</html>
"""

    def fraggate_call(self, slug: str, op: str, payload: dict[str, Any]) -> dict[str, Any]:
        card = self._card(slug)
        if card is None:
            return {"ok": False, "error": "Unknown Software.", "next": "Choose a name from the suite."}
        if not _fraggate_live(card):
            return {
                "ok": False,
                "error": f"{card['name']} is not on FragGate.",
                "next": "Open its local page from the suite when it is installed.",
            }
        if not OP_RE.fullmatch(op or ""):
            return {"ok": False, "error": "The operation name is not usable.", "next": "Use a short name such as health."}
        body = json.dumps({"slug": slug, "op": op, "payload": payload or {}}).encode("utf-8")
        req = urllib.request.Request(
            FRAGGATE_CALL,
            data=body,
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read(1_000_000)
        except urllib.error.HTTPError as exc:
            detail = exc.read(400).decode("utf-8", "replace")
            return {"ok": False, "error": f"The door answered {exc.code}.", "detail": detail[:400], "next": "Try health, or read the door reply."}
        except urllib.error.URLError as exc:
            return {"ok": False, "error": f"The door could not be reached. {exc.reason}", "next": "Check this computer's network and try Call again."}
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {"ok": False, "error": "The door did not return JSON.", "next": "Try Call again."}
        if isinstance(parsed, dict):
            return parsed
        return {"ok": True, "result": parsed}


def _fetch_live() -> list[dict[str, Any]] | None:
    req = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read(2_000_000).decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None
    rows = data.get("software") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return None
    return [row for row in rows if isinstance(row, dict) and row.get("slug")]


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read(MAX_DOWNLOAD + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"The download answered {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"The download could not be reached. {exc.reason}") from exc
    if len(data) > MAX_DOWNLOAD:
        raise RuntimeError("The download is larger than this suite will store.")
    if not data:
        raise RuntimeError("The download was empty.")
    return data


def _reject_escape(dest: Path, name: str) -> None:
    cleaned = name.replace("\\", "/").lstrip("/")
    if not cleaned or ".." in Path(cleaned).parts:
        raise RuntimeError("The package tried to write outside its folder.")
    target = (dest / cleaned).resolve()
    root = dest.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("The package tried to write outside its folder.")


def _remove_tree(path: Path) -> None:
    if path.is_symlink() or not path.is_dir():
        path.unlink()
        return
    for child in list(path.iterdir()):
        _remove_tree(child)
    path.rmdir()


def _extract(blob: Path, dest: Path) -> None:
    raw = blob.read_bytes()[:4]
    if raw.startswith(b"PK"):
        with zipfile.ZipFile(blob) as zf:
            for info in zf.infolist():
                _reject_escape(dest, info.filename)
            zf.extractall(dest)
        return
    try:
        with tarfile.open(blob, mode="r:*") as tar:
            for member in tar.getmembers():
                _reject_escape(dest, member.name)
            try:
                tar.extractall(dest, filter="data")
            except TypeError:
                tar.extractall(dest)
    except tarfile.TarError as exc:
        raise RuntimeError("The download is not a package this suite can unpack.") from exc


def _find_project(src: Path) -> Path | None:
    found: list[Path] = []
    for name in ("pyproject.toml", "setup.py"):
        found.extend(src.rglob(name))
    if not found:
        return None
    found.sort(key=lambda path: len(path.parts))
    return found[0].parent


def _find_node_project(src: Path) -> Path | None:
    found = [path for path in src.rglob("package.json") if "node_modules" not in path.parts]
    if not found:
        return None
    found.sort(key=lambda path: len(path.parts))
    return found[0].parent


def _install_node(project: Path, root: Path, slug: str) -> None:
    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node or not npm:
        raise RuntimeError("Node.js 20 or newer is required. Install Node.js, then press Start suite again.")
    env = {**os.environ, "npm_config_fund": "false", "npm_config_audit": "false"}
    proc = subprocess.run(
        [npm, "install"],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(tail[-1] if tail else f"npm install exited {proc.returncode}")
    pkg = json.loads((project / "package.json").read_text(encoding="utf-8"))
    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    if "build" in scripts and not (project / "dist" / "cli.js").is_file():
        built = subprocess.run(
            [npm, "run", "build"],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        if built.returncode != 0:
            tail = (built.stderr or built.stdout or "").strip().splitlines()
            raise RuntimeError(tail[-1] if tail else f"npm run build exited {built.returncode}")
    bins = pkg.get("bin") or {}
    if isinstance(bins, str):
        bins = {slug: bins}
    if not isinstance(bins, dict) or not bins:
        raise RuntimeError("The package has no program this suite can start.")
    bindir = root / "bin"
    bindir.mkdir(exist_ok=True)
    for bin_name, rel in bins.items():
        target = (project / str(rel)).resolve()
        if not target.is_file():
            raise RuntimeError(f"{bin_name} was not built ({target.name} is missing).")
        wrapper = bindir / str(bin_name)
        wrapper.write_text(f"#!/bin/sh\nexec {shlex.quote(node)} {shlex.quote(str(target))} \"$@\"\n")
        wrapper.chmod(0o755)


def _split_cmd(ui_cmd: str) -> tuple[str, list[str]]:
    parts = ui_cmd.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def _loopback_addr(ip_hex: str) -> bool:
    if ip_hex == "0100007F":
        return True
    return ip_hex == "00000000000000000000000001000000"


def _proc_listen_ports(proc: subprocess.Popen[str]) -> list[int]:
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        return []
    pids: list[int] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if os.getpgid(int(entry.name)) == pgid:
                pids.append(int(entry.name))
        except OSError:
            continue
    inodes: set[str] = set()
    for pid in pids:
        fd_dir = Path(f"/proc/{pid}/fd")
        if not fd_dir.is_dir():
            continue
        try:
            names = list(fd_dir.iterdir())
        except OSError:
            continue
        for fd in names:
            try:
                target = os.readlink(fd)
            except OSError:
                continue
            if target.startswith("socket:[") and target.endswith("]"):
                inodes.add(target[8:-1])
    if not inodes:
        return []
    ports: list[int] = []
    for table in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            rows = Path(table).read_text(encoding="utf-8").splitlines()[1:]
        except OSError:
            continue
        for row in rows:
            parts = row.split()
            if len(parts) < 10 or parts[3] != "0A":
                continue
            if parts[9] not in inodes:
                continue
            ip_hex, port_hex = parts[1].split(":")
            if _loopback_addr(ip_hex):
                ports.append(int(port_hex, 16))
    return ports


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection((LOOPBACK, port), timeout=0.2):
            return True
    except OSError:
        return False


def _read_output(proc: subprocess.Popen[str], lines: list[str]) -> None:
    if proc.stdout is None:
        return
    for line in proc.stdout:
        if len(lines) < 80:
            lines.append(line)


def _wait_url(proc: subprocess.Popen[str], lines: list[str], known_port: int | None, *, skip_port: int) -> str | None:
    import time

    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        owned = [port for port in _proc_listen_ports(proc) if port != skip_port and _port_open(port)]
        for line in lines:
            match = URL_RE.search(line)
            if match:
                port = int(match.group(1))
                if port in owned:
                    return f"http://{LOOPBACK}:{port}/"
        heard = owned
        if heard:
            if isinstance(known_port, int) and known_port in heard:
                return f"http://{LOOPBACK}:{known_port}/"
            return f"http://{LOOPBACK}:{heard[0]}/"
        if proc.poll() is not None:
            return None
        time.sleep(0.2)
    return None


def _terminate(proc: subprocess.Popen[str]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        proc.terminate()
