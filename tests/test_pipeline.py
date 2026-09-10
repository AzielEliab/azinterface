"""LOCKED suite pipeline cite — frozen hops, 4DMap at Domain Doors, no LambGate."""

from azinterface.engine import Engine, LIVE_OPS
from azinterface.pipeline import PIPELINE_HOPS, PIPELINE_PATH, pipeline_arch, pipeline_strip_html
from azinterface.receipts import Ledger


def test_frozen_path_and_owner() -> None:
    pipe = pipeline_arch()
    assert pipe["locked"] is True
    assert pipe["lambgate"] is False
    assert pipe["owner"] == "aziel-runtime"
    assert pipe["software_tab"] is False
    assert pipe["identity"] == "Aziel Eliab"
    assert pipe["author"] == "Aziel Eliab"
    assert "LambGate" not in pipe["path"]
    assert pipe["path"] == PIPELINE_PATH
    assert "Domain Doors (incl. 4DMap inspection)" in pipe["path"]
    assert pipe["hops"][0]["label"] == "PUBLIC/UI/Agents"
    assert pipe["hops"][-1]["label"] == "Response/Receipt"


def test_domain_doors_are_4dmap_inspection() -> None:
    doors = next(h for h in PIPELINE_HOPS if h["id"] == "domain_doors")
    assert doors["kind"] == "inspection"
    assert doors["highlight"] is True
    assert doors["inspection"]["name"] == "4DMap"
    assert doors["inspection"]["slug"] == "4dmap"
    assert doors["inspection"]["sequential_gate"] is False
    cite = pipeline_arch()
    assert cite["domain_doors"]["slug"] == "4dmap"
    assert cite["domain_doors"]["sequential_gate"] is False


def test_fabric_hops_not_softwares_tab() -> None:
    fabric = {h["id"] for h in PIPELINE_HOPS if h.get("kind") == "fabric"}
    assert fabric == {"sweepgate", "chainlock_in", "azpipe", "chainlock_out"}
    for hop in PIPELINE_HOPS:
        if hop["kind"] == "fabric":
            assert hop["software_tab"] is False
            assert hop["owner"] == "aziel-runtime"


def test_engine_op_and_page_cycle_cite() -> None:
    assert "pipeline_arch" in LIVE_OPS
    eng = Engine(Ledger())
    out = eng.pipeline_arch({})
    assert out["ok"] is True
    assert out["lambgate"] is False
    assert out["owner"] == "aziel-runtime"
    assert out["display"]["title"] == "LOCKED pipeline"
    cycle = eng.page_cycle_status()
    assert cycle["pipeline_path"] == PIPELINE_PATH
    assert cycle["pipeline"]["domain_doors"]["slug"] == "4dmap"
    assert cycle["pipeline"]["lambgate"] is False
    alias = eng.dispatch("pipeline", {})
    assert alias["ok"] is True
    assert alias["path"] == PIPELINE_PATH


def test_strip_highlights_domain_doors() -> None:
    html = pipeline_strip_html()
    assert 'id="pipeline"' in html
    assert "LOCKED pipeline" in html
    assert "data-hop=\"domain_doors\"" in html
    assert "hop door" in html
    assert "4DMap inspection" in html
    assert "No LambGate" in html
    assert "LambGate →" not in html
