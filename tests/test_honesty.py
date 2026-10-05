"""Standing facts stay false, and a caller cannot flip them."""

from __future__ import annotations

import re
from pathlib import Path

from azinterface.engine import Engine
from azinterface.honesty import STANDING_SENTENCES, VEILLOCK_STATUS, standing_facts
from azinterface.overlay_kernel import boot_session
from azinterface.packet_path import not_live_sentence, path_report
from azinterface.pipeline import domain_map_html, pipeline_arch
from azinterface.plain import human_lines
from azinterface.receipts import Ledger
from azinterface.suite_page import suite_html
from azinterface.web_page import home_html

ROOT = Path(__file__).resolve().parents[1]
TAIL = (
    "WireGuard, OpenVPN, an L3 exit pool, kernel UDP, and TUN/TAP stay SLOT.",
    "The public door stays FG-STUB.",
    "Isolation is single-node security-awareness.",
    "Phoenix is a local wait and re-seal.",
)
CALLER = {
    "alt_internet_live": True,
    "packet_path_live": True,
    "second_device": True,
    "mail_send": True,
    "public_smtp_send": True,
    "kernel": True,
    "kernel_base": True,
    "booted": True,
    "installed": True,
    "os_yet": True,
    "site_state": "ON",
    "veillock": "live",
    "whitestone_public_door": True,
    "internet_base": {"present": False, "live": True, "installed": True},
}


def _assert_facts(facts: dict) -> None:
    assert facts["alt_internet_live"] is False
    assert facts["packet_path_live"] is False
    assert facts["second_device"] is False
    assert facts["mail_send"] is False
    assert facts["public_smtp_send"] is False
    assert facts["kernel"] is False
    assert facts["kernel_base"] is False
    assert facts["booted"] is False
    assert facts["installed"] is False
    assert facts["os_yet"] is False
    assert facts["is_os"] is False
    assert facts["public_worker_boot"] is False
    assert facts["public_worker_kernel"] is False
    assert facts["public_worker_mail_send"] is False
    assert facts["host_os_booted"] is False
    assert facts["internet_base"]["present"] is True
    assert facts["internet_base"]["live"] is False
    assert facts["internet_base"]["installed"] is False
    assert facts["veillock"] == "local_only"
    assert facts["veillock_public_door"] is False
    assert facts["whitestone_worker_only"] is True
    assert facts["whitestone_public_door"] is False
    assert facts["public_door"] == "FG-STUB"
    assert facts["smtp_send"] == "FG-STUB"
    for line in STANDING_SENTENCES:
        assert line in facts["text"]
    assert "is true" not in facts["text"]


def test_banner_and_status_keep_the_standing_facts() -> None:
    html = home_html(views=0, downloads=0)
    suite = suite_html(port=8880, vendor="/tmp/azinterface-suite")
    sentence = not_live_sentence()
    assert sentence in html
    for line in STANDING_SENTENCES:
        assert line in html
        assert line in suite
    for line in TAIL:
        assert line in html
        assert line in sentence
    assert "Internet is not live." not in html
    assert "Softwares 42 is the runtime catalog." in html
    assert "The domain count stays 33." in html
    eng = Engine(Ledger())
    cycle = eng.page_cycle_status(CALLER)
    assert cycle["site_state"] == "OFF"
    assert cycle["current"] == "OFF"
    assert cycle["booted"] is False
    assert cycle["installed"] is False
    assert cycle["mail_send"] is False
    assert cycle["kernel_base"] is False
    assert cycle["os_yet"] is False
    assert cycle["alt_internet_live"] is False
    assert cycle["packet_path_live"] is False
    assert cycle["second_device"] is False
    assert "github.com/AzielEliab/fraggate" in str(cycle["kernel"])
    assert cycle["kernel"] is not True
    _assert_facts(cycle["honesty"])
    assert cycle["pipeline"]["software_count"] == 33
    walked = Engine(Ledger())
    walked.integrity_check({})
    stayed = walked.page_cycle_status({"site_state": "ON", "alt_internet_live": True})
    assert stayed["site_state"] == "integrity"
    assert stayed["alt_internet_live"] is False
    report = path_report(CALLER, refresh=True)
    assert report["alt_internet_live"] is False
    assert report["packet_path_live"] is False
    assert report["second_device"] is False
    assert report["booted"] is False
    assert report["installed"] is False
    assert report["mail_send"] is False
    assert report["status"] == sentence
    _assert_facts(report["honesty"])
    _assert_facts(standing_facts(CALLER))


def test_veillock_is_not_painted_as_a_public_door() -> None:
    html = domain_map_html()
    cited = {
        row["slug"]: row["status"]
        for domain in pipeline_arch()["domain_map"]
        for row in domain["softwares"]
    }
    assert pipeline_arch()["software_count"] == 33
    assert len(cited) == 33
    assert cited["veillock"] == VEILLOCK_STATUS
    assert cited["veillock"] != "live"
    assert "local_only" in cited["veillock"]
    assert "no public FragGate door" in cited["veillock"]
    assert "not a public-door live" in cited["veillock"]
    row = re.search(r'data-slug="veillock".*?</li>', html)
    assert row is not None
    assert "listed on aziel-runtime" not in row.group(0)
    assert "local_only" in row.group(0)
    vibe = re.search(r'data-slug="vibelock".*?</li>', html)
    assert vibe is not None
    assert "listed on aziel-runtime" in vibe.group(0)
    assert "whitestone" not in cited


def test_folder_session_copy_cannot_be_read_as_a_host_boot(tmp_path: Path) -> None:
    opened = boot_session(tmp_path)
    assert opened["booted"] is True
    assert opened["folder_session"] is True
    assert opened["host_os_booted"] is False
    assert opened["public_worker_boot"] is False
    assert opened["public_worker_kernel"] is False
    assert opened["host_kernel"] is False
    text = opened["status"]
    assert "folder session" in text
    assert "The host operating system did not boot." in text
    assert "The public worker did not boot." in text
    assert "the host operating system booted" not in text.lower()
    lines = human_lines({"ok": True, "display": {"title": "Session", "summary": text, "fields": [{"label": "booted", "value": True}]}})
    spoken = " ".join(lines)
    assert "The host operating system did not boot." in spoken
    assert "The booted is on." not in spoken
    assert "host operating system booted" not in spoken.lower()
