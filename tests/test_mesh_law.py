"""SPLIT THE WIRES + COLD-COPY SURVIVAL copy and cross-map."""

from azinterface.engine import qns_cross_map
from azinterface.meta import COLD_COPY_SURVIVAL, REHEAL, SPLIT_THE_WIRES, STW_DOC
from azinterface.web_page import home_html


def test_mesh_law_names() -> None:
    assert SPLIT_THE_WIRES == "SPLIT THE WIRES"
    assert COLD_COPY_SURVIVAL == "COLD-COPY SURVIVAL"
    assert REHEAL == "REHEAL"
    assert "SPLIT-THE-WIRES" in STW_DOC


def test_cross_map_cites_both_laws() -> None:
    m = qns_cross_map()
    assert m["split_the_wires"] == SPLIT_THE_WIRES
    assert m["cold_copy_survival"] == COLD_COPY_SURVIVAL
    assert m["reheal"] == REHEAL
    assert m["reheal_refuse"] is True
    assert m["neighbor_vote_to_fix"] is False
    assert m["get_enables_mesh"] is False
    assert m["live_body_sync"] is False
    assert m["server_pull_wipes_cold"] is False


def test_home_html_cites_mesh_law() -> None:
    html = home_html(views=1, downloads=2, github={"stars": 0})
    assert "SPLIT THE WIRES" in html
    assert "COLD-COPY SURVIVAL" in html
    assert "payload pull-only second plane" in html
    assert "never share a socket" in html
    assert "multiply cold copies" in html
    assert "refuse live body sync" in html
    assert "data outlives creators" in html
    assert "REHEAL refuse" in html
    assert "isolate+local phoenix" in html
    assert "no neighbor vote-to-fix" in html
    assert "live/locked/isolated/tip-hash only" in html
    assert "Mesh OFF" not in html
