"""MASTER-ARCHITECTURE-2.0 pipeline cite — Interface cites; runtime owns fabric.

Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains;
4DMap inspection; NOT additional doors) → optional ASE → RoseClock
(forward-only; StaticClock / VECTOR as needed) → TemporalLock →
ChainLock-OUT → ForgeReceipts → Return.

SUITE-PIPE-1.6.15 remains the current runtime public strip (not dropped).
This Interface cite extends toward MASTER-ARCHITECTURE-2.0 / runtime 1.6.15+.

AZInterface is the human-facing UI. It is not a second FragGate door.
Lamb Lens is fabric ethics (Peace / Clarity / Service → PASS / REFUSE /
HOLD-UNCERTAIN), not a Softwares-tab product. LambGate is not a hop.

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
SUITE_PIPE = "SUITE-PIPE-1.6.15"
MASTER_ARCH = "MASTER-ARCHITECTURE-2.0"

PIPELINE_OWNER = "aziel-runtime"
MASTER_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-ARCHITECTURE-2.0.md"
SUITE_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SUITE-PIPE-1.6.15.md"

SUITE_PIPE_PATH = (
    "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → "
    "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → "
    "StaticClock → ChainLock-OUT → Response/Receipt"
)

PIPELINE_PATH = (
    "Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → "
    "Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → "
    "DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; "
    "4DMap inspection) → optional ASE → RoseClock (forward-only; StaticClock / "
    "VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return"
)

# Frozen hop ids. FragGate is the only public door. LambGate is not a hop.
PIPELINE_HOPS: tuple[dict[str, Any], ...] = (
    {"id": "human", "label": "Human", "kind": "surface", "owner": "azinterface", "software_tab": False},
    {
        "id": "azinterface",
        "label": "AZInterface",
        "kind": "surface",
        "owner": "azinterface",
        "software_tab": True,
        "note": "This product. Human-facing UI. Not a second FragGate door.",
    },
    {"id": "public", "label": "PUBLIC/UI/AGENT/API", "kind": "surface", "owner": "azinterface", "software_tab": False},
    {
        "id": "fraggate",
        "label": "FragGate",
        "kind": "door",
        "spec": FG_WP,
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "highlight": True,
        "single_door": True,
        "badge": "THE SINGLE DOOR",
    },
    {
        "id": "lamb_lens",
        "label": "Lamb Lens",
        "kind": "ethics",
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "decisions": ("PASS", "REFUSE", "HOLD-UNCERTAIN"),
        "bases": ("Peace", "Clarity", "Service"),
        "note": "Fabric ethics. Not Softwares-tab. Not LambGate.",
    },
    {"id": "sweepgate", "label": "SweepGate", "kind": "fabric", "spec": SG_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "sentinel", "label": "Sentinel", "kind": "fabric", "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "provenance", "label": "Provenance/Input Packet", "kind": "fabric", "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "chainlock_in", "label": "ChainLock-IN", "kind": "fabric", "spec": CL_WP, "owner": PIPELINE_OWNER, "software_tab": False, "append_only": True},
    {"id": "decisiongate", "label": "DecisionGATE", "kind": "gate", "spec": "DecisionGATE", "owner": PIPELINE_OWNER, "software_tab": True},
    {"id": "azpipe", "label": "AZPIPE", "kind": "fabric", "spec": AP_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {
        "id": "domain_layer",
        "label": "Internal Domain Layer",
        "kind": "inspection",
        "highlight": True,
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "additional_doors": False,
        "softwares": 33,
        "domains": 11,
        "inspection": {
            "name": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
            "note": "Inspection of the 11-domain layer after AZPIPE. Not a sequential gate. Not additional doors.",
        },
    },
    {
        "id": "ase",
        "label": "optional ASE",
        "kind": "analytical",
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "optional": True,
        "note": "Cite only. Not Softwares-tab unless already a product.",
    },
    {
        "id": "roseclock",
        "label": "RoseClock",
        "kind": "action_time",
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "forward_only": True,
        "rollback": False,
        "note": "Forward-only. StaticClock / VECTOR as needed. No rollback.",
    },
    {"id": "temporallock", "label": "TemporalLock", "kind": "neighbor", "owner": PIPELINE_OWNER, "software_tab": True, "append_only": True},
    {"id": "chainlock_out", "label": "ChainLock-OUT", "kind": "fabric", "spec": CL_WP, "owner": PIPELINE_OWNER, "software_tab": False, "append_only": True},
    {"id": "forgereceipts", "label": "ForgeReceipts", "kind": "receipt", "owner": PIPELINE_OWNER, "software_tab": True},
    {"id": "return", "label": "Return", "kind": "surface", "owner": "azinterface", "software_tab": False},
)

# 11 domains / 33 softwares. Internal layer — not additional FragGate doors.
# AZChat is listed stub / not hosted yet. EmbryoLock is stub / local-not-hosted.
DOMAIN_MAP: tuple[dict[str, Any], ...] = (
    {
        "id": "vault",
        "name": "Vault / Custody",
        "softwares": (
            {"slug": "ark", "name": "ARK", "status": "live"},
            {"slug": "embryolock", "name": "EmbryoLock", "status": "stub / local-not-hosted"},
        ),
    },
    {
        "id": "media",
        "name": "Media / Authenticity / Physics",
        "softwares": (
            {"slug": "vibelock", "name": "VibeLock", "status": "live"},
            {"slug": "veillock", "name": "VeilLock", "status": "live"},
            {"slug": "spectrallock", "name": "SpectralLock", "status": "live"},
            {"slug": "trajectorylock", "name": "TrajectoryLock", "status": "live"},
        ),
    },
    {
        "id": "evidence",
        "name": "Evidence / Provenance",
        "softwares": (
            {"slug": "employeelock", "name": "EmployeeLock", "status": "live"},
            {"slug": "whistlelock", "name": "WhistleLock", "status": "live"},
            {"slug": "peacelock", "name": "PeaceLock", "status": "live"},
            {"slug": "shadowlock", "name": "ShadowLock", "status": "live"},
            {"slug": "mialock", "name": "M.I.A.Lock", "status": "live"},
            {"slug": "chronolock", "name": "ChronoLock", "status": "live"},
        ),
    },
    {
        "id": "language",
        "name": "Language / Structure / Pattern",
        "softwares": (
            {"slug": "codelock", "name": "CodeLock", "status": "live"},
            {"slug": "foldlock", "name": "FoldLock", "status": "live"},
            {"slug": "glossafilter", "name": "GlossaFilter", "status": "live"},
            {"slug": "zsolver", "name": "Zion Pattern Solver", "status": "live"},
            {"slug": "godlock", "name": "GodLock", "status": "live"},
            {"slug": "azclce", "name": "AZ-CLCE", "status": "live"},
        ),
    },
    {
        "id": "cognition",
        "name": "AI / Agent Cognition",
        "softwares": (
            {"slug": "azai", "name": "AZAI", "status": "live"},
            {"slug": "azbot", "name": "AZBot", "status": "live"},
            {"slug": "azhub", "name": "AZHub", "status": "live"},
            {"slug": "azinterface", "name": "AZInterface", "status": "live"},
            {"slug": "azchat", "name": "AZChat", "status": "stub / not hosted yet"},
        ),
    },
    {
        "id": "research",
        "name": "Research / Knowledge",
        "softwares": (
            {"slug": "azbrowser", "name": "AZBrowser", "status": "live"},
            {"slug": "aziel-corpus", "name": "Aziel Corpus", "status": "live"},
        ),
    },
    {
        "id": "communications",
        "name": "Communications",
        "softwares": ({"slug": "azmail", "name": "AZMail", "status": "live"},),
    },
    {
        "id": "network",
        "name": "Network / Connectivity",
        "softwares": (
            {"slug": "aznet", "name": "AZNet", "status": "live"},
            {"slug": "miragegrid", "name": "MirageGrid", "status": "live"},
            {"slug": "azieltether", "name": "AzielTether", "status": "live"},
        ),
    },
    {
        "id": "system",
        "name": "System / Local Execution",
        "softwares": ({"slug": "azos", "name": "AZ-OS", "status": "live"},),
    },
    {
        "id": "simulation",
        "name": "Simulation / Game",
        "softwares": ({"slug": "postking", "name": "Post-King Chess", "status": "live"},),
    },
    {
        "id": "core_fabric",
        "name": "Core Fabric",
        "softwares": (
            {"slug": "staticclock", "name": "StaticClock", "status": "live"},
            {"slug": "temporallock", "name": "TemporalLock", "status": "live"},
        ),
    },
)

OPTIONAL_ANALYTICAL = (
    {"id": "ase", "name": "ASE", "note": "perspective integrity — cite only"},
    {"id": "vector", "name": "VECTOR", "note": "directional selection — cite only"},
    {"id": "oracle", "name": "Oracle", "note": "append-only learning — cite only"},
    {"id": "constellation", "name": "Constellation", "note": "independent multi-node comparison — cite only"},
)

ABSENT_FROM_CORE = ("ZD30", "rollback", "generic truth score")

PIPELINE_PAPERS = {
    "master": MASTER_PAPER,
    "suite_pipe": SUITE_PAPER,
    "azpipe": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
    "sweepgate": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
    "chainlock": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
    "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
}

PIPELINE_NOTE = (
    "MASTER-ARCHITECTURE-2.0 locked path. Interface cites; aziel-runtime owns fabric hops. "
    "AZInterface is the human-facing UI — not a second FragGate door. "
    "FragGate is THE SINGLE DOOR. Internal Domain Layer is 33 softwares in 11 domains "
    "(not additional doors). 4DMap inspects that layer. RoseClock is forward-only. "
    "ChainLock / TemporalLock are append-only evidence. Lamb Lens is fabric ethics "
    "(Peace / Clarity / Service → PASS / REFUSE / HOLD-UNCERTAIN), not Softwares-tab. "
    "LambGate is not a hop. SUITE-PIPE-1.6.15 is the current runtime public strip and is "
    "not dropped — this cite is the 1.6.15+ migration toward MASTER-ARCHITECTURE-2.0. "
    "ZD30, rollback, and generic truth score are absent from the core."
)


def _clone_hop(hop: dict[str, Any]) -> dict[str, Any]:
    row = dict(hop)
    if hop.get("inspection"):
        row["inspection"] = dict(hop["inspection"])
    if hop.get("decisions"):
        row["decisions"] = list(hop["decisions"])
    if hop.get("bases"):
        row["bases"] = list(hop["bases"])
    return row


def domain_map() -> list[dict[str, Any]]:
    out = []
    for domain in DOMAIN_MAP:
        row = {
            "id": domain["id"],
            "name": domain["name"],
            "softwares": [dict(s) for s in domain["softwares"]],
        }
        out.append(row)
    return out


def domain_slugs() -> list[str]:
    slugs: list[str] = []
    for domain in DOMAIN_MAP:
        for row in domain["softwares"]:
            slugs.append(row["slug"])
    return slugs


def pipeline_arch() -> dict[str, Any]:
    """Frozen master pipeline cite. Same hop list the Worker UI strip paints."""
    slugs = domain_slugs()
    return {
        "locked": True,
        "lambgate": False,
        "second_door": False,
        "owner": PIPELINE_OWNER,
        "software_tab": False,
        "fabric_hops_software_tab": False,
        "cite": "aziel-runtime fabric. Interface cites; runtime owns hops. Not a second door.",
        "controlling_design": MASTER_ARCH,
        "suite_pipe": SUITE_PIPE,
        "suite_pipe_path": SUITE_PIPE_PATH,
        "migration": "runtime 1.6.15+ toward MASTER-ARCHITECTURE-2.0",
        "path": PIPELINE_PATH,
        "hops": [_clone_hop(h) for h in PIPELINE_HOPS],
        "single_door": "fraggate",
        "domain_doors": {
            "inspection": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
            "additional_doors": False,
            "layer": "Internal Domain Layer",
        },
        "domain_map": domain_map(),
        "domain_count": 11,
        "software_count": len(slugs),
        "softwares": slugs,
        "azchat": {"slug": "azchat", "status": "stub / not hosted yet"},
        "roseclock": {"forward_only": True, "rollback": False},
        "optional_analytical": [dict(x) for x in OPTIONAL_ANALYTICAL],
        "absent_from_core": list(ABSENT_FROM_CORE),
        "papers": dict(PIPELINE_PAPERS),
        "specs": {
            "azpipe": AP_WP,
            "sweepgate": SG_WP,
            "chainlock": CL_WP,
            "4dmap": DM_WP,
            "fraggate": FG_WP,
            "suite_pipe": SUITE_PIPE,
            "master": MASTER_ARCH,
        },
        "identity": IDENTITY,
        "author": IDENTITY,
        "runtime": RUNTIME,
        "note": PIPELINE_NOTE,
    }


def pipeline_strip_html() -> str:
    chips = []
    for hop in PIPELINE_HOPS:
        classes = ["hop"]
        if hop.get("highlight"):
            classes.append("door")
        if hop.get("single_door"):
            classes.append("single")
        if hop.get("optional"):
            classes.append("optional")
        badge = ""
        if hop.get("badge"):
            badge = f'<em class="inspect">{hop["badge"]}</em>'
        elif hop.get("inspection"):
            badge = '<em class="inspect">4DMap inspection</em>'
        elif hop.get("forward_only"):
            badge = '<em class="inspect">forward-only</em>'
        chips.append(
            f'<li class="{" ".join(classes)}" data-hop="{hop["id"]}" data-kind="{hop.get("kind") or ""}">'
            f'<span>{hop["label"]}</span>{badge}</li>'
        )
    hops = "".join(chips)
    return (
        '<div id="pipeline">'
        "<strong>LOCKED pipeline</strong>"
        f'<p class="pipe-path">{PIPELINE_PATH}</p>'
        f'<ol class="hops">{hops}</ol>'
        '<p class="pipe-note">FragGate is THE SINGLE DOOR. AZInterface is the human UI — not a second door. '
        "Runtime owns fabric hops. Internal Domain Layer = 33 softwares / 11 domains (not extra doors). "
        "RoseClock is forward-only. Lamb Lens is fabric ethics. SUITE-PIPE-1.6.15 is kept; this strip is the "
        "MASTER-ARCHITECTURE-2.0 / runtime 1.6.15+ cite. No LambGate. No ZD30. No rollback.</p>"
        "</div>"
    )


def domain_map_html() -> str:
    cards = []
    for domain in DOMAIN_MAP:
        items = []
        for row in domain["softwares"]:
            stub = " stub" if "stub" in row["status"] else ""
            items.append(
                f'<li class="sw{stub}" data-slug="{row["slug"]}">'
                f'<code>{row["slug"]}</code> {row["name"]}'
                f'<span class="st">{row["status"]}</span></li>'
            )
        cards.append(
            f'<section class="domain" data-domain="{domain["id"]}">'
            f"<h3>{domain['name']}</h3>"
            f'<ul>{"".join(items)}</ul></section>'
        )
    analytical = " · ".join(f'{x["name"]} ({x["note"]})' for x in OPTIONAL_ANALYTICAL)
    return (
        '<div id="domains">'
        "<strong>Internal Domain Layer</strong>"
        "<p class=\"pipe-note\">33 softwares in 11 domains after AZPIPE. Not additional FragGate doors. "
        "4DMap inspects this layer. AZChat is stub / not hosted yet. Author: Aziel Eliab only.</p>"
        f'<div class="domain-grid">{"".join(cards)}</div>'
        f'<p class="pipe-note">Optional analytical (cite only): {analytical}. '
        "Absent from core: ZD30, rollback, generic truth score.</p>"
        "</div>"
    )
