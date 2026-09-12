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
    assert "4DMap inspection frame" in html
    assert "domains_are_doors:false" in html
    assert "Domain Door" not in html
    assert "azchat" in html
    assert "stub / not hosted yet" in html
    assert "pipeline-btn" in html
    assert "cycle-toast" in html
    assert "toastMemorial" in html
    assert "MEMORIAL is terminal" in html
    assert "out-panel" in html
    assert "out-pre" in html
    assert "collapsed by default" in html
    assert "max-height:12rem" in html
    assert "install-steps" in html
    assert "install-advanced" in html
    assert "Checksum note" in html
    assert "custody UI only" in html
    assert "Agents use aziel-runtime FragGate/MCP" in html
    assert "curl -fsSL" in html
    assert html.split('id="install-advanced"', 1)[1].count("| bash") >= 1
    assert 'id="install-cmd">curl -fsSL' in html.replace("\n", "") or "install.sh -o install-azinterface.sh" in html
    assert "| bash" not in html.split('id="install-steps"', 1)[0]
    assert "No LambGate" in html
    assert "LambGate →" not in html
    assert "separate software" in html
    assert "AZCoherence" in html
    assert "slug=azcoherence" in html
    assert "AZ-CLCE" in html
    assert "cite.json" in html
    assert "azcoherence-download-tracker" in html
    assert "GET /v1/software" in html
    assert "plain A–Z" in html
    assert "AKM-TRIAD" in html
    assert "azielcorpuslibrary.net/sigil.png" in html
    assert "Live Nodes" in html
    assert "Mesh ON" in html
    assert "Mesh OFF" not in html
    assert "mesh/disable" not in html
    assert "Default off" not in html
    assert "mesh default OFF" not in html
    assert "/v1/mesh/status" in html
    assert "/v1/mesh/nodes" in html
    local = home_html(local=True)
    assert "azinterface-download-tracker.vibelock.workers.dev/download" in local
    assert "azinterface-download-tracker.vibelock.workers.dev/count" in local
    assert "slug\":\"azinterface\"" in html or "slug=azinterface" in html or '"azinterface"' in html
