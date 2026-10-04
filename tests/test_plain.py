"""People see sentences. The engine object stays JSON when asked."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from azinterface.cli import main
from azinterface.engine import Engine
from azinterface.plain import HUMAN_JS, human_lines
from azinterface.receipts import Ledger

ROOT = Path(__file__).resolve().parents[1]


def test_browser_source_matches_the_worker() -> None:
    worker = (ROOT / "workers/download-tracker/src/human.js").read_text(encoding="utf-8")
    assert HUMAN_JS.strip() in worker
    assert "export const HUMAN_LINES_SOURCE" in worker


def test_python_matches_browser_sentences() -> None:
    cases = [
        {
            "ok": True,
            "display": {
                "title": "Integrity passed",
                "summary": "Integrity recorded. Does not auto-unlock to ON.",
                "fields": [
                    {"label": "integrity_ok", "value": True},
                    {"label": "current", "value": "integrity"},
                    {"label": "digest", "value": "abc"},
                ],
            },
        },
        {
            "ok": False,
            "code": "AIH-CYCLE-TERMINAL",
            "refused": True,
            "error": "MEMORIAL is terminal. Page cycles stay pre-locked.",
            "display": {
                "title": "Memorial is terminal",
                "summary": "Cannot leave MEMORIAL. Cycles stay pre-locked.",
                "fields": [],
            },
        },
        {
            "ok": False,
            "code": "STUB",
            "error": "Hosted Scorched Earth never remotely wipes user devices.",
            "display": {
                "title": "Stub refused",
                "summary": "Hosted Scorched Earth never remotely wipes user devices.",
                "fields": [{"label": "op", "value": "scorch_remote"}, {"label": "code", "value": "STUB"}],
            },
        },
        {
            "ok": False,
            "code": "AIH-CYCLE-UNKNOWN",
            "error": "Only the five pre-locked cycles are accepted.",
        },
        {
            "ok": True,
            "code": "SCORCH_LOCAL_ADVISORY",
            "note": "Local advisory only.",
            "display": {
                "title": "Scorched Earth (local advisory)",
                "summary": "Hosted Worker will not remotely wipe devices.",
                "fields": [
                    {"label": "remote_wipe", "value": False},
                    {"label": "code", "value": "SCORCH_LOCAL_ADVISORY"},
                ],
            },
        },
        {"ok": True, "note": "Opened a new in-process onion path.", "next": "Use Rotate IP."},
    ]
    script = HUMAN_JS + "\nconst cases = " + json.dumps(cases) + ";\nfor (const row of cases) console.log(JSON.stringify(humanLines(row)));\n"
    proc = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=True)
    browser = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    python_rows = [human_lines(row) for row in cases]
    assert browser == python_rows


def test_refusal_stays_a_refusal() -> None:
    eng = Engine(Ledger())
    out = eng.site_state_set({"state": "ON"})
    lines = human_lines(out)
    text = " ".join(lines)
    assert out["ok"] is False
    assert "refus" in text.lower() or "Cannot" in text or "locked" in text.lower()
    assert not text.lstrip().startswith("{")
    assert "AIH-CYCLE-LOCKED" not in text or "refused" in text.lower()


def test_integrity_human_is_sentences(tmp_path, capsys) -> None:
    ledger = str(tmp_path / "receipts.jsonl")
    assert main(["--ledger", ledger, "integrity"]) == 0
    human = capsys.readouterr().out
    assert "Integrity passed" in human
    assert "The page is integrity." in human
    assert "Integrity has passed." in human
    assert "integrity_ok:" not in human
    assert not human.lstrip().startswith("{")
    assert main(["--json", "--ledger", ledger, "state"]) == 0
    raw = capsys.readouterr().out
    data = json.loads(raw)
    assert data["site_state"] == "integrity"
    assert "display" in data


def test_stub_refusal_names_the_refusal(capsys) -> None:
    assert main(["call", "scorch_remote"]) == 2
    human = capsys.readouterr().out
    assert "refused" in human.lower() or "never" in human.lower()
    assert not human.lstrip().startswith("{")
    assert "wipe" in human.lower()
