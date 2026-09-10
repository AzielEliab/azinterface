"""Human UI must wire the custody buttons and stay black / gold."""

from azinterface.web_page import home_html


def test_home_html_wires_buttons() -> None:
    html = home_html(views=1, downloads=2, github={"stars": 0})
    assert "background:var(--bg)" in html or "#0b0b0b" in html
    assert "#c9a227" in html
    assert "data-state=\"ON\"" in html
    assert "data-state=\"OFF\"" in html
    assert "data-state=\"FULL_SHUTDOWN\"" in html
    assert "data-state=\"MEMORIAL\"" in html
    assert "genesis-btn" in html
    assert "integrity-btn" in html
    assert "witness-btn" in html
    assert "withdraw-btn" in html
    assert "pair-offer-btn" in html
    assert "pair-accept-btn" in html
    assert "pair-seal-btn" in html
    assert "pair-cut-btn" in html
    assert "QNS-CD-1.0" in html
    assert "qnsd" in html
    assert "PRE-LOCKED" in html
    assert "Never collapse Interface into Hub" in html
    assert "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL" in html
    assert "LOCKED pipeline" in html
    assert "THE SINGLE DOOR" in html
    assert "Internal Domain Layer" in html
    assert "azchat" in html
    assert "stub / not hosted yet" in html
    assert "pipeline-btn" in html
    assert "No LambGate" in html
    assert "LambGate →" not in html
    assert "separate software" in html
    assert "azielcorpuslibrary.net/sigil.png" in html
    local = home_html(local=True)
    assert "azinterface-download-tracker.vibelock.workers.dev/download" in local
    assert "azinterface-download-tracker.vibelock.workers.dev/count" in local
    assert "slug\":\"azinterface\"" in html or "slug=azinterface" in html or '"azinterface"' in html
