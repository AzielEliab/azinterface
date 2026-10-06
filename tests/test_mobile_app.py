"""The human app shows the worker sentences and does not call a refused door live."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "mobile" / "lib"

_NEGATION = re.compile(r"\b(not|never|without|absent|refused|cannot|can't)\b", re.I)
_TOPICS = (
    ("public mail send", re.compile(r"public mail send|mail send", re.I), re.compile(r"\b(is live|are live|runs|is running|does run|live)\b", re.I)),
    ("packet path", re.compile(r"packet path", re.I), re.compile(r"\b(is live|are live|runs|is running|does run|live)\b", re.I)),
    ("alternative internet", re.compile(r"alternative internet", re.I), re.compile(r"\b(is live|are live|runs|is running|does run|live)\b", re.I)),
    ("kernel", re.compile(r"\bkernel\b", re.I), re.compile(r"\b(is live|are live|runs|is running|does run|live)\b", re.I)),
    ("boot", re.compile(r"\bboot(?:ed|s|ing)?\b", re.I), re.compile(r"\b(is live|are live|runs|is running|does run|has booted|boots|live)\b", re.I)),
    ("second device", re.compile(r"second device|another device", re.I), re.compile(r"\b(is live|are live|runs|is running|wipes?|live)\b", re.I)),
)


def live_claims(text: str) -> list[str]:
    found: list[str] = []
    for sentence in re.split(r"[.!?\n;]", text):
        for name, topic, live in _TOPICS:
            if topic.search(sentence) and live.search(sentence) and not _NEGATION.search(sentence):
                found.append(name)
    return found


def _library() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(LIB.glob("*.dart"))
        if path.name != "claims.dart"
    )


def test_live_claim_checker_flags_each_refused_door() -> None:
    samples = {
        "public mail send": "Public mail send is live.",
        "packet path": "The packet path is live.",
        "alternative internet": "An alternative internet is live.",
        "kernel": "The kernel is live.",
        "boot": "Boot is live.",
        "second device": "A second device is live.",
    }
    for name, sentence in samples.items():
        assert name in live_claims(sentence)
    assert "kernel" in live_claims("The public worker runs a kernel.")
    assert "boot" in live_claims("Boot has booted.")
    assert "second device" in live_claims("This wipes a second device.")
    assert "second device" in live_claims("This wipes another device.")
    honest = [
        "Mail send does not run on the public worker.",
        "The packet path does not run.",
        "An alternative internet does not run.",
        "An alternative internet is not live (alt_internet_live is false).",
        "A packet path is not live (packet_path_live is false).",
        "Public mail send, the kernel, and boot stay not live.",
        "The public door stays FG-STUB.",
        "A second device stays false while both ends share that id.",
        "The public worker does not run a kernel.",
        "Boot does not run on the public worker.",
        "This does not wipe another device.",
        "It does not wipe a second device.",
        "There is no kernel.",
        "This has not booted.",
    ]
    for sentence in honest:
        assert live_claims(sentence) == []


def test_app_keeps_the_worker_facts_and_refuses_live_claims() -> None:
    source = _library()
    assert live_claims(source) == []
    assert "const int softwareCount = 33;" in source
    assert "const String siteState = 'OFF';" in source
    for sentence in (
        "The domain count stays 33.",
        "software_count stays 33.",
        "An alternative internet is not live (alt_internet_live is false).",
        "A packet path is not live (packet_path_live is false).",
        "This isolate cannot see host hardware (worker_hardware is false).",
        "A second device stays false while both ends share that id.",
        "A same-machine mesh frame does not count.",
        "Public mail send, the kernel, and boot stay not live.",
        "The public door stays FG-STUB.",
        "Isolation is single-node security-awareness.",
        "Phoenix is a local wait and re-seal.",
        "That is not a loopback fence.",
        "Mail send does not run on the public worker.",
        "The public worker does not run a kernel.",
        "Boot does not run on the public worker.",
        "The host operating system stays the host operating system.",
        "AZNews can stand alone.",
        "4DMap can stand alone.",
        "This does not wipe another device.",
        "It does not wipe a second device.",
        "There is no kernel.",
        "This has not booted.",
        "The page is OFF.",
    ):
        assert sentence in source
    assert "42" not in source
    assert "alt_internet_live is true" not in source
    assert "packet_path_live is true" not in source
    lowered = source.lower()
    assert "internet is not live." not in lowered
    assert "installed" not in lowered
    assert "one-click" not in lowered
    assert "play store" not in lowered
    assert "app store" not in lowered


def test_phone_and_desktop_projects_exist_without_a_store_listing() -> None:
    mobile = ROOT / "mobile"
    assert (mobile / "android/app/src/main/AndroidManifest.xml").is_file()
    assert 'applicationId = "com.azieeliab.azinterface"' in (mobile / "android/app/build.gradle.kts").read_text(encoding="utf-8")
    assert (mobile / "ios/Runner.xcodeproj/project.pbxproj").is_file()
    assert (mobile / "ios/Runner/Info.plist").is_file()
    assert "PRODUCT_BUNDLE_IDENTIFIER = com.azieeliab.azinterface;" in (mobile / "ios/Runner.xcodeproj/project.pbxproj").read_text(encoding="utf-8")
    assert (mobile / "linux/CMakeLists.txt").is_file()
    assert 'APPLICATION_ID "com.azieeliab.azinterface"' in (mobile / "linux/CMakeLists.txt").read_text(encoding="utf-8")
    assert (mobile / "macos/Runner.xcodeproj/project.pbxproj").is_file()
    assert (mobile / "windows/CMakeLists.txt").is_file()
    assert not (mobile / "fastlane").exists()
    assert not any(path.name.lower() == "store_listing.txt" for path in mobile.rglob("*") if ".dart_tool" not in path.parts and "build" not in path.parts)
