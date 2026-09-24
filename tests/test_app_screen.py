"""Custody app screens: one tool, one primary action, disclosure for the rest."""

from azinterface.web_page import home_html


def _slice(html: str, start: str, end: str) -> str:
    return html.split(start, 1)[1].split(end, 1)[0]


def test_app_screen_keeps_one_primary_per_tool() -> None:
    html = home_html(views=3, downloads=4, github={"stars": 1})
    assert 'id="app-view"' in html
    assert 'id="app-screen"' in html
    assert 'value="integrity" selected' in html
    assert "Check integrity" in html
    assert 'id="integrity-btn"' in html
    assert "prefers-color-scheme: light" in _slice(html, 'id="app-screen"', "</style>")
    assert "focus-visible" in _slice(html, 'id="app-screen"', "</style>")
    assert "#c9a227" in _slice(html, 'id="app-screen"', "</style>")
    cycle = _slice(html, 'id="cycle-more"', "</details>")
    assert 'data-state="ON"' in cycle
    assert 'data-state="OFF"' in cycle
    assert 'data-state="FULL_SHUTDOWN"' in cycle
    assert 'data-state="MEMORIAL"' in cycle
    assert "genesis-status-btn" in _slice(html, ">Key status<", "</details>")
    assert "withdraw-btn" in _slice(html, ">Withdraw or list witnesses<", "</details>")
    assert "witness-btn" in _slice(html, ">Withdraw or list witnesses<", "</details>")
    pair = _slice(html, ">Accept, seal, cut, or status<", "</details>")
    assert "pair-accept-btn" in pair
    assert "pair-seal-btn" in pair
    assert "pair-cut-btn" in pair
    assert "pair-status-btn" in pair
    assert "scorch-remote-btn" in _slice(html, ">Remote wipe<", "</details>")
    assert "pipeline-btn" in _slice(html, ">Pipeline cite</summary>", "</details>")
    assert "pair-offer-btn" in html
    assert "QNS-CD-1.0" in html
    assert "qnsd" in html
    assert "OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL" in html
    assert "PRE-LOCKED" in html
    assert "Views" in html
    assert "Downloads" in html
    assert "Live Nodes" in html
    assert "syncCyclePrimary" in html
    assert "applyAppView" in html
