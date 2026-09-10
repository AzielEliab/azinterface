"""MASTER-33 pipeline cite — Interface cites; aziel-runtime owns fabric.

Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains;
isolation labels, not additional doors; 4DMap inspection frame) →
optional ASE → RoseClock (forward-only; StaticClock / VECTOR as needed) →
TemporalLock → ChainLock-OUT → ForgeReceipts → Return.

Live lock is MASTER-33 on aziel-runtime (introduced 1.7.0). The product
name is aziel-runtime. FragGate is THE SINGLE DOOR — not mashed into the
runtime name. SUITE-PIPE-1.6.15 is historical (kept, not rolled back).

AZInterface is the human-facing UI before the door. It is not a second
door and is not one of the 33 domain-layer slugs. Lamb Lens is fabric
ethics after FragGate. LambGate is not a hop.

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
MASTER_33 = "MASTER-33"
MASTER_ARCH = "MASTER-ARCHITECTURE-2.0"

PIPELINE_OWNER = "aziel-runtime"
RUNTIME_LOCK = "1.7.0"
MASTER_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-33-SOFTWARE.md"
MASTER_ARCH_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-ARCHITECTURE-2.0.md"
SUITE_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SUITE-PIPE-1.6.15.md"

SUITE_PIPE_PATH = (
    "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → "
    "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → "
    "StaticClock → ChainLock-OUT → Response/Receipt"
)

FOURDMAP_FRAME = "inspection frame — not an extra door (domains_are_doors:false)"

PIPELINE_PATH = (
    "Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → "
    "Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → "
    "DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; "
    "4DMap inspection frame) → optional ASE → RoseClock (forward-only; StaticClock / "
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
        "placement": "human-ui",
        "note": "This product. Human-facing UI before FragGate. Not a second door. Not one of the 33 domain slugs.",
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
        "note": "Fabric ethics after FragGate. Not Softwares-tab. Not LambGate. Not a second door.",
    },
    {"id": "sweepgate", "label": "SweepGate", "kind": "fabric", "spec": SG_WP, "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "sentinel", "label": "Sentinel", "kind": "fabric", "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "provenance", "label": "Provenance/Input Packet", "kind": "fabric", "owner": PIPELINE_OWNER, "software_tab": False},
    {"id": "chainlock_in", "label": "ChainLock-IN", "kind": "fabric", "spec": CL_WP, "owner": PIPELINE_OWNER, "software_tab": False, "append_only": True},
    {"id": "decisiongate", "label": "DecisionGATE", "kind": "gate", "spec": "DecisionGATE", "owner": PIPELINE_OWNER, "software_tab": True, "placement": "fabric-product"},
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
        "isolation_labels": True,
        "inspection": {
            "name": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
            "domain": "Research",
            "domain_id": "06",
            "note": "4DMap is a Research-domain inspection frame T/Δ/Γ/Π after AZPIPE. Not a sequential gate. Not an extra door (domains_are_doors:false).",
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
    {"id": "forgereceipts", "label": "ForgeReceipts", "kind": "receipt", "owner": PIPELINE_OWNER, "software_tab": True, "placement": "fabric-product"},
    {"id": "return", "label": "Return", "kind": "surface", "owner": "azinterface", "software_tab": False},
)

# Live MASTER-33 map from aziel-runtime GET /v1/software. Isolation labels — not doors.
# AZInterface is human UI before the door (not in this 33). AZChat is stub / not hosted yet.
DOMAIN_MAP: tuple[dict[str, Any], ...] = (
    {
        "id": "01",
        "slug": "vault-custody",
        "name": "Vault/Custody",
        "softwares": (
            {"slug": "ark", "name": "ARK", "status": "live"},
            {"slug": "embryolock", "name": "EmbryoLock", "status": "stub / local-not-hosted"},
        ),
    },
    {
        "id": "02",
        "slug": "media",
        "name": "Media",
        "softwares": (
            {"slug": "vibelock", "name": "VibeLock", "status": "live"},
            {"slug": "veillock", "name": "VeilLock", "status": "live"},
            {"slug": "spectrallock", "name": "SpectralLock", "status": "live"},
            {"slug": "trajectorylock", "name": "TrajectoryLock", "status": "live"},
        ),
    },
    {
        "id": "03",
        "slug": "evidence",
        "name": "Evidence",
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
        "id": "04",
        "slug": "language",
        "name": "Language",
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
        "id": "05",
        "slug": "ai",
        "name": "AI",
        "softwares": (
            {"slug": "azai", "name": "AZAI", "status": "live"},
            {"slug": "azbot", "name": "AZBot", "status": "live"},
            {"slug": "azhub", "name": "AZHub", "status": "live"},
        ),
    },
    {
        "id": "06",
        "slug": "research",
        "name": "Research",
        "softwares": (
            {"slug": "azbrowser", "name": "AZBrowser", "status": "live"},
            {"slug": "aziel-corpus", "name": "Aziel Corpus", "status": "live"},
            {"slug": "4dmap", "name": "4DMap", "status": "live"},
        ),
    },
    {
        "id": "07",
        "slug": "comms",
        "name": "Comms",
        "softwares": (
            {"slug": "azmail", "name": "AZMail", "status": "live"},
            {"slug": "azchat", "name": "AZChat", "status": "stub / not hosted yet"},
        ),
    },
    {
        "id": "08",
        "slug": "network",
        "name": "Network",
        "softwares": (
            {"slug": "aznet", "name": "AZNet", "status": "live"},
            {"slug": "miragegrid", "name": "MirageGrid", "status": "live"},
            {"slug": "azieltether", "name": "AzielTether", "status": "live"},
        ),
    },
    {
        "id": "09",
        "slug": "system",
        "name": "System",
        "softwares": ({"slug": "azos", "name": "AZ-OS", "status": "live"},),
    },
    {
        "id": "10",
        "slug": "simulation",
        "name": "Simulation",
        "softwares": ({"slug": "postking", "name": "Post-King Chess", "status": "live"},),
    },
    {
        "id": "11",
        "slug": "core-time",
        "name": "Core Time",
        "softwares": (
            {"slug": "staticclock", "name": "StaticClock", "status": "live"},
            {"slug": "temporallock", "name": "TemporalLock", "status": "live"},
        ),
    },
)

PLACEMENTS = (
    {
        "slug": "azinterface",
        "placement": "human-ui",
        "note": "AZInterface is the human UI before FragGate. Catalog software. Not an extra door. Not one of the 33.",
    },
    {
        "slug": "decisiongate",
        "placement": "fabric-product",
        "note": "DecisionGATE is the policy hop. Catalog engine. Not an extra door.",
    },
    {
        "slug": "forgereceipts",
        "placement": "fabric-product",
        "note": "ForgeReceipts packages Return. Catalog engine. Not an extra door.",
    },
    {
        "slug": "azcoherence",
        "name": "AZCoherence",
        "placement": "scoring-review",
        "bucket": "plain",
        "note": (
            "AZCoherence is the second-pass coherence reviewer for triad scores. "
            "Scoring-adjacent to AZ-CLCE (Language isolation). Catalog software. "
            "Not an extra door. Not one of the 33. Not AKM-TRIAD fabric."
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
    "master_33": MASTER_PAPER,
    "master": MASTER_ARCH_PAPER,
    "suite_pipe": SUITE_PAPER,
    "azpipe": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
    "sweepgate": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
    "chainlock": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
    "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
}

PIPELINE_NOTE = (
    "MASTER-33 locked path on aziel-runtime (lock introduced 1.7.0). "
    "The fabric owner is aziel-runtime — not a version+FragGate mash. "
    "FragGate is THE SINGLE DOOR. AZInterface is the human-facing UI before "
    "that door — not a second door and not one of the 33 domain slugs. "
    "Internal Domain Layer is 33 softwares in 11 domains (isolation labels, "
    "not additional doors). 4DMap is a Research-domain inspection frame "
    "(T/Δ/Γ/Π), not an extra door (domains_are_doors:false). "
    "AZChat is stub / not hosted yet (Comms). RoseClock is forward-only. "
    "ChainLock / TemporalLock are append-only evidence. Lamb Lens is fabric "
    "ethics after FragGate (Peace / Clarity / Service → PASS / REFUSE / "
    "HOLD-UNCERTAIN), not Softwares-tab. LambGate is not a hop. "
    "SUITE-PIPE-1.6.15 is historical (kept, not rolled back). MASTER-ARCHITECTURE-2.0 "
    "is the companion spec; MASTER-33 overrides §4.2. ZD30, rollback, and "
    "generic truth score are absent from the core."
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
            "slug": domain["slug"],
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
    """Frozen MASTER-33 cite. Same hop list the Worker UI strip paints."""
    slugs = domain_slugs()
    return {
        "locked": True,
        "lambgate": False,
        "second_door": False,
        "owner": PIPELINE_OWNER,
        "owner_note": "aziel-runtime owns fabric hops. FragGate is the door hop, not part of the product name.",
        "software_tab": False,
        "fabric_hops_software_tab": False,
        "cite": "aziel-runtime fabric. Interface cites; runtime owns hops. Not a second door.",
        "controlling_design": MASTER_33,
        "companion_design": MASTER_ARCH,
        "runtime_lock": RUNTIME_LOCK,
        "suite_pipe": SUITE_PIPE,
        "suite_pipe_status": "historical",
        "suite_pipe_path": SUITE_PIPE_PATH,
        "migration": "SUITE-PIPE-1.6.15 historical; MASTER-33 live on aziel-runtime",
        "path": PIPELINE_PATH,
        "hops": [_clone_hop(h) for h in PIPELINE_HOPS],
        "single_door": "fraggate",
        "domains_are_doors": False,
        "domain_doors": {
            "inspection": "4DMap",
            "slug": "4dmap",
            "spec": DM_WP,
            "sequential_gate": False,
            "axes": "T/Δ/Γ/Π",
            "additional_doors": False,
            "domains_are_doors": False,
            "role": "inspection_frame",
            "layer": "Internal Domain Layer",
            "domain": "Research",
            "domain_id": "06",
            "note": "4DMap is an inspection frame after AZPIPE, not an extra door (domains_are_doors:false).",
        },
        "domain_map": domain_map(),
        "domain_count": 11,
        "software_count": len(slugs),
        "softwares": slugs,
        "placements": [dict(x) for x in PLACEMENTS],
        "azchat": {"slug": "azchat", "status": "stub / not hosted yet", "domain": "Comms", "domain_id": "07"},
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
            "master_33": MASTER_33,
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
            badge = '<em class="inspect">4DMap inspection frame</em>'
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
        '<p class="pipe-note">FragGate is THE SINGLE DOOR. Fabric owner is aziel-runtime '
        "(not a version+FragGate mash). AZInterface is the human UI before the door — not a second door. "
        "Internal Domain Layer = 33 softwares / 11 domains (isolation labels, not extra doors). "
        "RoseClock is forward-only. Lamb Lens is fabric ethics after FragGate. MASTER-33 is live; "
        "SUITE-PIPE-1.6.15 is historical. No LambGate. No ZD30. No rollback.</p>"
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
            f'<section class="domain" data-domain="{domain["slug"]}">'
            f"<h3>{domain['id']} {domain['name']}</h3>"
            f'<ul>{"".join(items)}</ul></section>'
        )
    analytical = " · ".join(f'{x["name"]} ({x["note"]})' for x in OPTIONAL_ANALYTICAL)
    return (
        '<div id="domains">'
        "<strong>Internal Domain Layer</strong>"
        "<p class=\"pipe-note\">MASTER-33: 33 softwares in 11 domains after AZPIPE. Isolation labels — "
        "not additional FragGate doors. 4DMap is a Research-domain inspection frame (T/Δ/Γ/Π), "
        "not an extra door (domains_are_doors:false). AZChat is stub / not hosted yet. "
        "AZInterface is the human UI before the door, not one of the 33. "
        "Softwares-tab placements (not the 33): AZCoherence (plain, scoring-review; peer of AZ-CLCE; not AKM-TRIAD), "
        "AZInterface (human-ui), DecisionGATE, ForgeReceipts. Live catalog sort: plain A–Z → gate A–Z → lock A–Z "
        "at GET /v1/software. Owner: aziel-runtime. "
        "Author: Aziel Eliab only.</p>"
        f'<div class="domain-grid">{"".join(cards)}</div>'
        f'<p class="pipe-note">Optional analytical (cite only): {analytical}. '
        "Absent from core: ZD30, rollback, generic truth score.</p>"
        "</div>"
    )
