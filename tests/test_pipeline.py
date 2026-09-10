"""MASTER-ARCHITECTURE-2.0 pipeline cite — 33/11, FragGate single door."""

from azinterface.engine import Engine, LIVE_OPS
from azinterface.pipeline import (
    DOMAIN_MAP,
    FOURDMAP_FRAME,
    PIPELINE_HOPS,
    PIPELINE_PATH,
    SUITE_PIPE_PATH,
    domain_map_html,
    domain_slugs,
    pipeline_arch,
    pipeline_strip_html,
)
from azinterface.receipts import Ledger


def test_frozen_path_and_owner() -> None:
    pipe = pipeline_arch()
    assert pipe["locked"] is True
    assert pipe["lambgate"] is False
    assert pipe["second_door"] is False
    assert pipe["owner"] == "aziel-runtime"
    assert pipe["identity"] == "Aziel Eliab"
    assert pipe["author"] == "Aziel Eliab"
    assert "LambGate" not in pipe["path"]
    assert pipe["path"] == PIPELINE_PATH
    assert "FragGate (THE SINGLE DOOR)" in pipe["path"]
    assert "Internal Domain Layer" in pipe["path"]
    assert pipe["hops"][0]["label"] == "Human"
    assert pipe["hops"][-1]["label"] == "Return"
    assert pipe["controlling_design"] == "MASTER-33"
    assert pipe["companion_design"] == "MASTER-ARCHITECTURE-2.0"
    assert pipe["owner"] == "aziel-runtime"
    assert "fraggate" not in pipe["owner"]
    assert pipe["runtime_lock"] == "1.7.0"
    assert pipe["suite_pipe"] == "SUITE-PIPE-1.6.15"
    assert pipe["suite_pipe_status"] == "historical"
    assert pipe["suite_pipe_path"] == SUITE_PIPE_PATH
    assert "Domain Doors" in SUITE_PIPE_PATH  # historical 1.6.15 quote only
    assert pipe["single_door"] == "fraggate"


def test_domain_layer_is_4dmap_inspection() -> None:
    layer = next(h for h in PIPELINE_HOPS if h["id"] == "domain_layer")
    assert layer["kind"] == "inspection"
    assert layer["additional_doors"] is False
    assert layer["inspection"]["slug"] == "4dmap"
    assert layer["inspection"]["sequential_gate"] is False
    cite = pipeline_arch()
    assert cite["domain_doors"]["slug"] == "4dmap"
    assert cite["domain_doors"]["additional_doors"] is False
    assert cite["domains_are_doors"] is False
    assert cite["domain_doors"]["domains_are_doors"] is False
    assert cite["domain_doors"]["role"] == "inspection_frame"
    assert "inspection frame" in cite["note"]
    assert "domains_are_doors:false" in cite["note"]
    assert "Domain Door" not in cite["note"]
    assert "Domain Door" not in PIPELINE_PATH
    assert "inspection frame" in PIPELINE_PATH
    out = Engine(Ledger()).pipeline_arch({})
    labels = {row["label"]: row["value"] for row in out["display"]["fields"]}
    assert labels["4dmap"] == FOURDMAP_FRAME
    cycle = Engine(Ledger()).page_cycle_status()
    cycle_labels = {row["label"]: row["value"] for row in cycle["display"]["fields"]}
    assert cycle_labels["4dmap"] == FOURDMAP_FRAME


def test_eleven_domains_thirty_three_softwares() -> None:
    slugs = domain_slugs()
    assert len(DOMAIN_MAP) == 11
    assert len(slugs) == 33
    assert slugs[0] == "ark"
    assert slugs[-1] == "temporallock"
    assert "azchat" in slugs
    assert "4dmap" in slugs
    assert "azinterface" not in slugs
    assert "azcoherence" not in slugs
    azchat = next(s for d in DOMAIN_MAP for s in d["softwares"] if s["slug"] == "azchat")
    assert azchat["status"] == "stub / not hosted yet"
    comms = next(d for d in DOMAIN_MAP if d["slug"] == "comms")
    assert "azchat" in [s["slug"] for s in comms["softwares"]]
    research = next(d for d in DOMAIN_MAP if d["slug"] == "research")
    assert "4dmap" in [s["slug"] for s in research["softwares"]]
    embryo = next(s for d in DOMAIN_MAP for s in d["softwares"] if s["slug"] == "embryolock")
    assert "stub" in embryo["status"]
    cite = pipeline_arch()
    assert cite["software_count"] == 33
    assert cite["domain_count"] == 11
    assert "ZD30" in cite["absent_from_core"]
    assert cite["roseclock"]["forward_only"] is True
    assert cite["roseclock"]["rollback"] is False


def test_fraggate_is_the_single_door() -> None:
    door = next(h for h in PIPELINE_HOPS if h.get("single_door"))
    assert door["id"] == "fraggate"
    assert door["badge"] == "THE SINGLE DOOR"
    lens = next(h for h in PIPELINE_HOPS if h["id"] == "lamb_lens")
    assert lens["software_tab"] is False
    assert "PASS" in lens["decisions"]


def test_engine_op_and_page_cycle_cite() -> None:
    assert "pipeline_arch" in LIVE_OPS
    eng = Engine(Ledger())
    out = eng.pipeline_arch({})
    assert out["ok"] is True
    assert out["lambgate"] is False
    assert out["second_door"] is False
    cycle = eng.page_cycle_status()
    assert cycle["pipeline_path"] == PIPELINE_PATH
    assert cycle["pipeline"]["domain_count"] == 11


def test_strip_and_domain_map_html() -> None:
    html = pipeline_strip_html() + domain_map_html()
    assert 'id="pipeline"' in html
    assert "THE SINGLE DOOR" in html
    assert "Internal Domain Layer" in html
    assert "4DMap inspection frame" in html
    assert "domains_are_doors:false" in html
    assert "Domain Door" not in html
    assert 'id="domains"' in html
    assert 'data-slug="azchat"' in html
    assert "stub / not hosted yet" in html
    assert "No LambGate" in html
    assert "LambGate →" not in html
    assert 'data-domain="vault-custody"' in html
    assert 'data-domain="core-time"' in html
    assert 'data-slug="4dmap"' in html
    assert "aziel-runtime" in html
