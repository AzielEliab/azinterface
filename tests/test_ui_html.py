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
    assert "PRE-LOCKED" in html
    assert "Never collapse Interface into Hub" in html
    assert "azielcorpuslibrary.net/sigil.png" in html
    assert "slug\":\"azinterface\"" in html or "slug=azinterface" in html or '"azinterface"' in html
