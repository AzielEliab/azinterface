"""LOCKED suite pipeline cite — Interface cites; aziel-runtime owns fabric hops.

PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE →
AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock →
StaticClock → ChainLock-OUT → Response/Receipt

No LambGate. Fabric hops are not Softwares-tab products.
4DMap (slug 4dmap) is Domain Door inspection, not a sequential gate.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .meta import IDENTITY, RUNTIME

AP_WP = "AP-WP-0.2"
SG_WP = "SG-WP-0.1"
CL_WP = "CL-WP-0.4"
DM_WP = "4DM-WP-1.0"
FG_WP = "FG-0.1"

PIPELINE_OWNER = "aziel-runtime"
PIPELINE_PATH = (
    "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → "
    "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → "
    "StaticClock → ChainLock-OUT → Response/Receipt"
)

# Frozen hop ids. Order is sealed. LambGate is not on this list.
PIPELINE_HOPS: tuple[dict[str, Any], ...] = (
    {"id": "public", "label": "PUBLIC/UI/Agents", "kind": "surface", "owner": "azinterface", "software_tab": False},
    {"id": "fraggate", "label": "FragGate", "kind": "door", "spec": FG_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "sweepgate", "label": "SweepGate", "kind": "fabric", "spec": SG_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "chainlock_in", "label": "ChainLock-IN", "kind": "fabric", "spec": CL_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "decisiongate", "label": "DecisionGATE", "kind": "gate", "spec": "DecisionGATE", "owner": PIPELINE_OWNER, "software_tab": True},
    {"id": "azpipe", "label": "AZPIPE", "kind": "fabric", "spec": AP_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {
        "id": "domain_doors",
        "label": "Domain Doors",
        "kind": "inspection",
        "highlight": True,
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "inspection": {
            "name": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
            "note": "Domain Door inspection after AZPIPE. Not a sequential gate.",
        },
    },
    {"id": "temporallock", "label": "TemporalLock", "kind": "neighbor", "owner": PIPELINE_OWNER, "software_tab": True},
    {"id": "staticclock", "label": "StaticClock", "kind": "neighbor", "owner": PIPELINE_OWNER, "software_tab": True},
    {"id": "chainlock_out", "label": "ChainLock-OUT", "kind": "fabric", "spec": CL_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "response", "label": "Response/Receipt", "kind": "surface", "owner": "azinterface", "software_tab": False},
)

PIPELINE_PAPERS = {
    "azpipe": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
    "sweepgate": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
    "chainlock": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
    "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
}

PIPELINE_NOTE = (
    "LOCKED suite pipeline. Interface cites this hop list. "
    "aziel-runtime owns fabric hops (SweepGate / ChainLock / AZPIPE). "
    "Those hops are not Softwares-tab products. "
    "4DMap (slug 4dmap, 4DM-WP-1.0) is Domain Door inspection after AZPIPE — "
    "not a sequential gate. LambGate is not on this list."
)


def pipeline_arch() -> dict[str, Any]:
    """Frozen pipeline cite. Same hop list the Worker UI strip paints."""
    hops = [dict(h) for h in PIPELINE_HOPS]
    for hop in hops:
        if hop.get("inspection"):
            hop["inspection"] = dict(hop["inspection"])
    return {
        "locked": True,
        "lambgate": False,
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "fabric_hops_software_tab": False,
        "cite": "aziel-runtime fabric. Interface cites; runtime owns hops.",
        "path": PIPELINE_PATH,
        "hops": hops,
        "domain_doors": {
            "inspection": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
        },
        "papers": dict(PIPELINE_PAPERS),
        "specs": {"azpipe": AP_WP, "sweepgate": SG_WP, "chainlock": CL_WP, "4dmap": DM_WP, "fraggate": FG_WP},
        "identity": IDENTITY,
        "author": IDENTITY,
        "runtime": RUNTIME,
        "note": PIPELINE_NOTE,
    }


def pipeline_strip_html() -> str:
    chips = []
    for hop in PIPELINE_HOPS:
        extra = " door" if hop.get("highlight") else ""
        kind = hop.get("kind") or ""
        inspect = ""
        if hop.get("inspection"):
            inspect = '<em class="inspect">4DMap inspection</em>'
        chips.append(
            f'<li class="hop{extra}" data-hop="{hop["id"]}" data-kind="{kind}">'
            f'<span>{hop["label"]}</span>{inspect}</li>'
        )
    hops = "".join(chips)
    return (
        '<div id="pipeline">'
        "<strong>LOCKED pipeline</strong>"
        f'<p class="pipe-path">{PIPELINE_PATH}</p>'
        f'<ol class="hops">{hops}</ol>'
        '<p class="pipe-note">Runtime owns fabric hops (SweepGate / ChainLock / AZPIPE) — '
        "not Softwares-tab. Domain Doors highlight 4DMap as inspection. No LambGate.</p>"
        "</div>"
    )
