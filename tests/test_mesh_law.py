"""SPLIT THE WIRES + COLD-COPY SURVIVAL copy and cross-map."""

from azinterface.engine import Engine, qns_cross_map
from azinterface.mesh_radios import mesh_radios_tile
from azinterface.meta import COLD_COPY_SURVIVAL, REHEAL, SPLIT_THE_WIRES, STW_DOC
from azinterface.receipts import Ledger
from azinterface.suite import Suite
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
    assert m["mesh_default"] == "on"
    assert m["node_mesh_enabled"] is True
    assert m["mesh_node_live"] is True
    assert m["alt_internet_live"] is True
    assert m["packet_path_live"] is True
    assert m["qnm_membership"] is True
    assert m["qns_cite_plane"] is True
    assert m["qns_is_membership"] is False
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
    assert "mesh_node_live is true" in html


def test_mesh_radios_status_is_on_and_names_stay_names() -> None:
    tile = mesh_radios_tile({})
    assert tile["ok"] is True
    assert tile["status"] == "OK"
    assert tile["radios"] == "on"
    assert tile["enabled"] is True
    assert tile["action"] == "status"
    assert tile["mesh_node_live"] is True
    assert tile["alt_internet_live"] is True
    assert tile["packet_path_live"] is True
    assert tile["qns_cite_plane"] is False
    assert tile["qns_is_membership"] is False
    assert tile["hardware_live"] is False
    assert tile["public_icann"] is False
    assert tile["cap7_name_only"] is True
    assert tile["cap7_registrar_live"] is False
    assert tile["locks"] == {"softwares": 42, "mcp_tools": 36}
    enabled = mesh_radios_tile({"confirm": True})
    assert enabled["ok"] is True
    assert enabled["code"] == "AZI-MESH-RADIOS"
    assert enabled["radios"] == "on"
    assert enabled["hardware_live"] is False
    forced = mesh_radios_tile({"confirm": True}, {"MESH_RADIOS": "off"})
    assert forced["ok"] is False
    assert forced["code"] == "MESH-OFF"
    assert forced["radios"] == "off"
    assert forced["enabled"] is False
    assert forced["mesh_node_live"] is True
    assert forced["alt_internet_live"] is True
    assert forced["packet_path_live"] is True
    cap7 = mesh_radios_tile({"carrier": "node.aziel", "confirm": True})
    assert cap7["ok"] is False
    assert cap7["code"] == "MG-NO-IP-EXIT"
    assert cap7["public_icann"] is False
    assert cap7["cap7_registrar_live"] is False
    assert cap7["mesh_node_live"] is True
    photon = mesh_radios_tile({"carrier": "photon"})
    assert photon["mock"] is False
    assert photon["hardware_live"] is False
    if photon["ok"] is False:
        assert photon["code"] == "QNM-RADIO-ABSENT"
    else:
        assert photon["carrier_state"] == "HW-PRESENT"
        assert photon["carrier_live"] is False
    op = Engine(Ledger()).mesh_radios({})
    assert op["status"] == "OK"
    assert op["mesh_node_live"] is True
    assert op["qns"]["qns_cite_plane"] is True
    assert op["qns"]["qns_is_membership"] is False


def test_every_software_tile_defaults_mesh_on() -> None:
    rows = Suite(refresh=False).document()["software"]
    assert rows
    for row in rows:
        assert row["node_mesh"]["enabled"] is True
        assert row["node_mesh"]["radios"] == "on"
        assert row["node_mesh"]["qns_cite_plane"] is False
        assert row["mesh_radios"]["status"] == "OK"
        assert row["mesh_radios"]["radios"] == "on"
        assert row["mesh_radios"]["hardware_live"] is False
        assert row["mesh_radios"]["public_icann"] is False
        assert row["mesh_radios"]["cap7_registrar_live"] is False
        assert row["mesh_node_live"] is True
        assert row["alt_internet_live"] is True
        assert row["packet_path_live"] is True
