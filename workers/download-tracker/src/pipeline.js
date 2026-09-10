/**
 * MASTER-ARCHITECTURE-2.0 pipeline cite — Interface cites; runtime owns fabric.
 *
 * Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
 * Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
 * DecisionGATE → AZPIPE → Internal Domain Layer (33 / 11; 4DMap inspection) →
 * optional ASE → RoseClock (forward-only) → TemporalLock → ChainLock-OUT →
 * ForgeReceipts → Return.
 *
 * SUITE-PIPE-1.6.15 is kept. AZInterface is not a second door.
 * Author: Aziel Eliab only.
 */

export const AP_WP = "AP-WP-0.2";
export const SG_WP = "SG-WP-0.1";
export const CL_WP = "CL-WP-0.4";
export const DM_WP = "4DM-WP-1.0";
export const FG_WP = "FG-0.1";
export const SUITE_PIPE = "SUITE-PIPE-1.6.15";
export const MASTER_ARCH = "MASTER-ARCHITECTURE-2.0";
export const PIPELINE_OWNER = "aziel-runtime";
export const MASTER_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-ARCHITECTURE-2.0.md";
export const SUITE_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SUITE-PIPE-1.6.15.md";

export const SUITE_PIPE_PATH =
  "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → " +
  "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → " +
  "StaticClock → ChainLock-OUT → Response/Receipt";

export const PIPELINE_PATH =
  "Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → " +
  "Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → " +
  "DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; " +
  "4DMap inspection) → optional ASE → RoseClock (forward-only; StaticClock / " +
  "VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return";

export const PIPELINE_HOPS = Object.freeze([
  Object.freeze({ id: "human", label: "Human", kind: "surface", owner: "azinterface", software_tab: false }),
  Object.freeze({ id: "azinterface", label: "AZInterface", kind: "surface", owner: "azinterface", software_tab: true, note: "This product. Human-facing UI. Not a second FragGate door." }),
  Object.freeze({ id: "public", label: "PUBLIC/UI/AGENT/API", kind: "surface", owner: "azinterface", software_tab: false }),
  Object.freeze({ id: "fraggate", label: "FragGate", kind: "door", spec: FG_WP, owner: PIPELINE_OWNER, software_tab: false, highlight: true, single_door: true, badge: "THE SINGLE DOOR" }),
  Object.freeze({ id: "lamb_lens", label: "Lamb Lens", kind: "ethics", owner: PIPELINE_OWNER, software_tab: false, decisions: Object.freeze(["PASS", "REFUSE", "HOLD-UNCERTAIN"]), bases: Object.freeze(["Peace", "Clarity", "Service"]), note: "Fabric ethics. Not Softwares-tab. Not LambGate." }),
  Object.freeze({ id: "sweepgate", label: "SweepGate", kind: "fabric", spec: SG_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "sentinel", label: "Sentinel", kind: "fabric", owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "provenance", label: "Provenance/Input Packet", kind: "fabric", owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "chainlock_in", label: "ChainLock-IN", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false, append_only: true }),
  Object.freeze({ id: "decisiongate", label: "DecisionGATE", kind: "gate", spec: "DecisionGATE", owner: PIPELINE_OWNER, software_tab: true }),
  Object.freeze({ id: "azpipe", label: "AZPIPE", kind: "fabric", spec: AP_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({
    id: "domain_layer",
    label: "Internal Domain Layer",
    kind: "inspection",
    highlight: true,
    owner: PIPELINE_OWNER,
    software_tab: false,
    additional_doors: false,
    softwares: 33,
    domains: 11,
    inspection: Object.freeze({
      name: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
      note: "Inspection of the 11-domain layer after AZPIPE. Not a sequential gate. Not additional doors.",
    }),
  }),
  Object.freeze({ id: "ase", label: "optional ASE", kind: "analytical", owner: PIPELINE_OWNER, software_tab: false, optional: true, note: "Cite only. Not Softwares-tab unless already a product." }),
  Object.freeze({ id: "roseclock", label: "RoseClock", kind: "action_time", owner: PIPELINE_OWNER, software_tab: false, forward_only: true, rollback: false, note: "Forward-only. StaticClock / VECTOR as needed. No rollback." }),
  Object.freeze({ id: "temporallock", label: "TemporalLock", kind: "neighbor", owner: PIPELINE_OWNER, software_tab: true, append_only: true }),
  Object.freeze({ id: "chainlock_out", label: "ChainLock-OUT", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false, append_only: true }),
  Object.freeze({ id: "forgereceipts", label: "ForgeReceipts", kind: "receipt", owner: PIPELINE_OWNER, software_tab: true }),
  Object.freeze({ id: "return", label: "Return", kind: "surface", owner: "azinterface", software_tab: false }),
]);

export const DOMAIN_MAP = Object.freeze([
  Object.freeze({ id: "vault", name: "Vault / Custody", softwares: Object.freeze([
    Object.freeze({ slug: "ark", name: "ARK", status: "live" }),
    Object.freeze({ slug: "embryolock", name: "EmbryoLock", status: "stub / local-not-hosted" }),
  ]) }),
  Object.freeze({ id: "media", name: "Media / Authenticity / Physics", softwares: Object.freeze([
    Object.freeze({ slug: "vibelock", name: "VibeLock", status: "live" }),
    Object.freeze({ slug: "veillock", name: "VeilLock", status: "live" }),
    Object.freeze({ slug: "spectrallock", name: "SpectralLock", status: "live" }),
    Object.freeze({ slug: "trajectorylock", name: "TrajectoryLock", status: "live" }),
  ]) }),
  Object.freeze({ id: "evidence", name: "Evidence / Provenance", softwares: Object.freeze([
    Object.freeze({ slug: "employeelock", name: "EmployeeLock", status: "live" }),
    Object.freeze({ slug: "whistlelock", name: "WhistleLock", status: "live" }),
    Object.freeze({ slug: "peacelock", name: "PeaceLock", status: "live" }),
    Object.freeze({ slug: "shadowlock", name: "ShadowLock", status: "live" }),
    Object.freeze({ slug: "mialock", name: "M.I.A.Lock", status: "live" }),
    Object.freeze({ slug: "chronolock", name: "ChronoLock", status: "live" }),
  ]) }),
  Object.freeze({ id: "language", name: "Language / Structure / Pattern", softwares: Object.freeze([
    Object.freeze({ slug: "codelock", name: "CodeLock", status: "live" }),
    Object.freeze({ slug: "foldlock", name: "FoldLock", status: "live" }),
    Object.freeze({ slug: "glossafilter", name: "GlossaFilter", status: "live" }),
    Object.freeze({ slug: "zsolver", name: "Zion Pattern Solver", status: "live" }),
    Object.freeze({ slug: "godlock", name: "GodLock", status: "live" }),
    Object.freeze({ slug: "azclce", name: "AZ-CLCE", status: "live" }),
  ]) }),
  Object.freeze({ id: "cognition", name: "AI / Agent Cognition", softwares: Object.freeze([
    Object.freeze({ slug: "azai", name: "AZAI", status: "live" }),
    Object.freeze({ slug: "azbot", name: "AZBot", status: "live" }),
    Object.freeze({ slug: "azhub", name: "AZHub", status: "live" }),
    Object.freeze({ slug: "azinterface", name: "AZInterface", status: "live" }),
    Object.freeze({ slug: "azchat", name: "AZChat", status: "stub / not hosted yet" }),
  ]) }),
  Object.freeze({ id: "research", name: "Research / Knowledge", softwares: Object.freeze([
    Object.freeze({ slug: "azbrowser", name: "AZBrowser", status: "live" }),
    Object.freeze({ slug: "aziel-corpus", name: "Aziel Corpus", status: "live" }),
  ]) }),
  Object.freeze({ id: "communications", name: "Communications", softwares: Object.freeze([
    Object.freeze({ slug: "azmail", name: "AZMail", status: "live" }),
  ]) }),
  Object.freeze({ id: "network", name: "Network / Connectivity", softwares: Object.freeze([
    Object.freeze({ slug: "aznet", name: "AZNet", status: "live" }),
    Object.freeze({ slug: "miragegrid", name: "MirageGrid", status: "live" }),
    Object.freeze({ slug: "azieltether", name: "AzielTether", status: "live" }),
  ]) }),
  Object.freeze({ id: "system", name: "System / Local Execution", softwares: Object.freeze([
    Object.freeze({ slug: "azos", name: "AZ-OS", status: "live" }),
  ]) }),
  Object.freeze({ id: "simulation", name: "Simulation / Game", softwares: Object.freeze([
    Object.freeze({ slug: "postking", name: "Post-King Chess", status: "live" }),
  ]) }),
  Object.freeze({ id: "core_fabric", name: "Core Fabric", softwares: Object.freeze([
    Object.freeze({ slug: "staticclock", name: "StaticClock", status: "live" }),
    Object.freeze({ slug: "temporallock", name: "TemporalLock", status: "live" }),
  ]) }),
]);

export const OPTIONAL_ANALYTICAL = Object.freeze([
  Object.freeze({ id: "ase", name: "ASE", note: "perspective integrity — cite only" }),
  Object.freeze({ id: "vector", name: "VECTOR", note: "directional selection — cite only" }),
  Object.freeze({ id: "oracle", name: "Oracle", note: "append-only learning — cite only" }),
  Object.freeze({ id: "constellation", name: "Constellation", note: "independent multi-node comparison — cite only" }),
]);

export const ABSENT_FROM_CORE = Object.freeze(["ZD30", "rollback", "generic truth score"]);

export const PIPELINE_PAPERS = Object.freeze({
  master: MASTER_PAPER,
  suite_pipe: SUITE_PAPER,
  azpipe: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
  sweepgate: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
  chainlock: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
  "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
});

export const PIPELINE_NOTE =
  "MASTER-ARCHITECTURE-2.0 locked path. Interface cites; aziel-runtime owns fabric hops. " +
  "AZInterface is the human-facing UI — not a second FragGate door. " +
  "FragGate is THE SINGLE DOOR. Internal Domain Layer is 33 softwares in 11 domains " +
  "(not additional doors). 4DMap inspects that layer. RoseClock is forward-only. " +
  "ChainLock / TemporalLock are append-only evidence. Lamb Lens is fabric ethics " +
  "(Peace / Clarity / Service → PASS / REFUSE / HOLD-UNCERTAIN), not Softwares-tab. " +
  "LambGate is not a hop. SUITE-PIPE-1.6.15 is the current runtime public strip and is " +
  "not dropped — this cite is the 1.6.15+ migration toward MASTER-ARCHITECTURE-2.0. " +
  "ZD30, rollback, and generic truth score are absent from the core.";

function cloneHop(hop) {
  const row = { ...hop };
  if (hop.inspection) row.inspection = { ...hop.inspection };
  if (hop.decisions) row.decisions = [...hop.decisions];
  if (hop.bases) row.bases = [...hop.bases];
  return row;
}

export function domainMap() {
  return DOMAIN_MAP.map((domain) => ({
    id: domain.id,
    name: domain.name,
    softwares: domain.softwares.map((s) => ({ ...s })),
  }));
}

export function domainSlugs() {
  const slugs = [];
  for (const domain of DOMAIN_MAP) {
    for (const row of domain.softwares) slugs.push(row.slug);
  }
  return slugs;
}

export function pipelineArch() {
  const slugs = domainSlugs();
  return {
    locked: true,
    lambgate: false,
    second_door: false,
    owner: PIPELINE_OWNER,
    software_tab: false,
    fabric_hops_software_tab: false,
    cite: "aziel-runtime fabric. Interface cites; runtime owns hops. Not a second door.",
    controlling_design: MASTER_ARCH,
    suite_pipe: SUITE_PIPE,
    suite_pipe_path: SUITE_PIPE_PATH,
    migration: "runtime 1.6.15+ toward MASTER-ARCHITECTURE-2.0",
    path: PIPELINE_PATH,
    hops: PIPELINE_HOPS.map(cloneHop),
    single_door: "fraggate",
    domain_doors: {
      inspection: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
      additional_doors: false,
      layer: "Internal Domain Layer",
    },
    domain_map: domainMap(),
    domain_count: 11,
    software_count: slugs.length,
    softwares: slugs,
    azchat: { slug: "azchat", status: "stub / not hosted yet" },
    roseclock: { forward_only: true, rollback: false },
    optional_analytical: OPTIONAL_ANALYTICAL.map((x) => ({ ...x })),
    absent_from_core: [...ABSENT_FROM_CORE],
    papers: { ...PIPELINE_PAPERS },
    specs: { azpipe: AP_WP, sweepgate: SG_WP, chainlock: CL_WP, "4dmap": DM_WP, fraggate: FG_WP, suite_pipe: SUITE_PIPE, master: MASTER_ARCH },
    identity: "Aziel Eliab",
    author: "Aziel Eliab",
    runtime: "https://aziel-runtime.vibelock.workers.dev",
    note: PIPELINE_NOTE,
  };
}

export function pipelineStripHtml() {
  const chips = PIPELINE_HOPS.map((hop) => {
    const classes = ["hop"];
    if (hop.highlight) classes.push("door");
    if (hop.single_door) classes.push("single");
    if (hop.optional) classes.push("optional");
    let badge = "";
    if (hop.badge) badge = `<em class="inspect">${hop.badge}</em>`;
    else if (hop.inspection) badge = '<em class="inspect">4DMap inspection</em>';
    else if (hop.forward_only) badge = '<em class="inspect">forward-only</em>';
    return `<li class="${classes.join(" ")}" data-hop="${hop.id}" data-kind="${hop.kind || ""}"><span>${hop.label}</span>${badge}</li>`;
  }).join("");
  return `<div id="pipeline">
  <strong>LOCKED pipeline</strong>
  <p class="pipe-path">${PIPELINE_PATH}</p>
  <ol class="hops">${chips}</ol>
  <p class="pipe-note">FragGate is THE SINGLE DOOR. AZInterface is the human UI — not a second door. Runtime owns fabric hops. Internal Domain Layer = 33 softwares / 11 domains (not extra doors). RoseClock is forward-only. Lamb Lens is fabric ethics. SUITE-PIPE-1.6.15 is kept; this strip is the MASTER-ARCHITECTURE-2.0 / runtime 1.6.15+ cite. No LambGate. No ZD30. No rollback.</p>
</div>`;
}

export function domainMapHtml() {
  const cards = DOMAIN_MAP.map((domain) => {
    const items = domain.softwares.map((row) => {
      const stub = String(row.status).includes("stub") ? " stub" : "";
      return `<li class="sw${stub}" data-slug="${row.slug}"><code>${row.slug}</code> ${row.name}<span class="st">${row.status}</span></li>`;
    }).join("");
    return `<section class="domain" data-domain="${domain.id}"><h3>${domain.name}</h3><ul>${items}</ul></section>`;
  }).join("");
  const analytical = OPTIONAL_ANALYTICAL.map((x) => `${x.name} (${x.note})`).join(" · ");
  return `<div id="domains">
  <strong>Internal Domain Layer</strong>
  <p class="pipe-note">33 softwares in 11 domains after AZPIPE. Not additional FragGate doors. 4DMap inspects this layer. AZChat is stub / not hosted yet. Author: Aziel Eliab only.</p>
  <div class="domain-grid">${cards}</div>
  <p class="pipe-note">Optional analytical (cite only): ${analytical}. Absent from core: ZD30, rollback, generic truth score.</p>
</div>`;
}
