/**
 * MASTER-33 pipeline cite — Interface cites; aziel-runtime owns fabric.
 *
 * Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
 * Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
 * DecisionGATE → AZPIPE → Internal Domain Layer (33 / 11; isolation labels) →
 * optional ASE → RoseClock (forward-only) → TemporalLock → ChainLock-OUT →
 * ForgeReceipts → Return.
 *
 * Product name is aziel-runtime. FragGate is THE SINGLE DOOR — not mashed
 * into the runtime name. SUITE-PIPE-1.6.15 is historical.
 * Author: Aziel Eliab only.
 */

export const AP_WP = "AP-WP-0.2";
export const SG_WP = "SG-WP-0.1";
export const CL_WP = "CL-WP-0.4";
export const DM_WP = "4DM-WP-1.0";
export const FG_WP = "FG-0.1";
export const SUITE_PIPE = "SUITE-PIPE-1.6.15";
export const MASTER_33 = "MASTER-33";
export const MASTER_ARCH = "MASTER-ARCHITECTURE-2.0";
export const PIPELINE_OWNER = "aziel-runtime";
export const RUNTIME_LOCK = "1.7.0";
export const MASTER_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-33-SOFTWARE.md";
export const MASTER_ARCH_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-ARCHITECTURE-2.0.md";
export const SUITE_PAPER = "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SUITE-PIPE-1.6.15.md";

export const SUITE_PIPE_PATH =
  "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → " +
  "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → " +
  "StaticClock → ChainLock-OUT → Response/Receipt";

export const FOURDMAP_FRAME =
  "inspection frame — not an extra door (domains_are_doors:false)";

export const PIPELINE_PATH =
  "Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → " +
  "Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → " +
  "DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; " +
  "4DMap inspection frame) → optional ASE → RoseClock (forward-only; StaticClock / " +
  "VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return";

export const PIPELINE_HOPS = Object.freeze([
  Object.freeze({ id: "human", label: "Human", kind: "surface", owner: "azinterface", software_tab: false }),
  Object.freeze({ id: "azinterface", label: "AZInterface", kind: "surface", owner: "azinterface", software_tab: true, placement: "human-ui", note: "This product. Human-facing UI before FragGate. Not a second door. Not one of the 33 domain slugs." }),
  Object.freeze({ id: "public", label: "PUBLIC/UI/AGENT/API", kind: "surface", owner: "azinterface", software_tab: false }),
  Object.freeze({ id: "fraggate", label: "FragGate", kind: "door", spec: FG_WP, owner: PIPELINE_OWNER, software_tab: false, highlight: true, single_door: true, badge: "THE SINGLE DOOR" }),
  Object.freeze({ id: "lamb_lens", label: "Lamb Lens", kind: "ethics", owner: PIPELINE_OWNER, software_tab: false, decisions: Object.freeze(["PASS", "REFUSE", "HOLD-UNCERTAIN"]), bases: Object.freeze(["Peace", "Clarity", "Service"]), note: "Fabric ethics after FragGate. Not Softwares-tab. Not LambGate. Not a second door." }),
  Object.freeze({ id: "sweepgate", label: "SweepGate", kind: "fabric", spec: SG_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "sentinel", label: "Sentinel", kind: "fabric", owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "provenance", label: "Provenance/Input Packet", kind: "fabric", owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "chainlock_in", label: "ChainLock-IN", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false, append_only: true }),
  Object.freeze({ id: "decisiongate", label: "DecisionGATE", kind: "gate", spec: "DecisionGATE", owner: PIPELINE_OWNER, software_tab: true, placement: "fabric-product" }),
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
    isolation_labels: true,
    inspection: Object.freeze({
      name: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
      domain: "Research",
      domain_id: "06",
      note: "4DMap is a Research-domain inspection frame T/Δ/Γ/Π after AZPIPE. Not a sequential gate. Not an extra door (domains_are_doors:false).",
    }),
  }),
  Object.freeze({ id: "ase", label: "optional ASE", kind: "analytical", owner: PIPELINE_OWNER, software_tab: false, optional: true, note: "Cite only. Not Softwares-tab unless already a product." }),
  Object.freeze({ id: "roseclock", label: "RoseClock", kind: "action_time", owner: PIPELINE_OWNER, software_tab: false, forward_only: true, rollback: false, note: "Forward-only. StaticClock / VECTOR as needed. No rollback." }),
  Object.freeze({ id: "temporallock", label: "TemporalLock", kind: "neighbor", owner: PIPELINE_OWNER, software_tab: true, append_only: true }),
  Object.freeze({ id: "chainlock_out", label: "ChainLock-OUT", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false, append_only: true }),
  Object.freeze({ id: "forgereceipts", label: "ForgeReceipts", kind: "receipt", owner: PIPELINE_OWNER, software_tab: true, placement: "fabric-product" }),
  Object.freeze({ id: "return", label: "Return", kind: "surface", owner: "azinterface", software_tab: false }),
]);

export const DOMAIN_MAP = Object.freeze([
  Object.freeze({ id: "01", slug: "vault-custody", name: "Vault/Custody", softwares: Object.freeze([
    Object.freeze({ slug: "ark", name: "ARK", status: "live" }),
    Object.freeze({ slug: "embryolock", name: "EmbryoLock", status: "stub / local-not-hosted" }),
  ]) }),
  Object.freeze({ id: "02", slug: "media", name: "Media", softwares: Object.freeze([
    Object.freeze({ slug: "vibelock", name: "VibeLock", status: "live" }),
    Object.freeze({ slug: "veillock", name: "VeilLock", status: "live" }),
    Object.freeze({ slug: "spectrallock", name: "SpectralLock", status: "live" }),
    Object.freeze({ slug: "trajectorylock", name: "TrajectoryLock", status: "live" }),
  ]) }),
  Object.freeze({ id: "03", slug: "evidence", name: "Evidence", softwares: Object.freeze([
    Object.freeze({ slug: "employeelock", name: "EmployeeLock", status: "live" }),
    Object.freeze({ slug: "whistlelock", name: "WhistleLock", status: "live" }),
    Object.freeze({ slug: "peacelock", name: "PeaceLock", status: "live" }),
    Object.freeze({ slug: "shadowlock", name: "ShadowLock", status: "live" }),
    Object.freeze({ slug: "mialock", name: "M.I.A.Lock", status: "live" }),
    Object.freeze({ slug: "chronolock", name: "ChronoLock", status: "live" }),
  ]) }),
  Object.freeze({ id: "04", slug: "language", name: "Language", softwares: Object.freeze([
    Object.freeze({ slug: "codelock", name: "CodeLock", status: "live" }),
    Object.freeze({ slug: "foldlock", name: "FoldLock", status: "live" }),
    Object.freeze({ slug: "glossafilter", name: "GlossaFilter", status: "live" }),
    Object.freeze({ slug: "zsolver", name: "Zion Pattern Solver", status: "live" }),
    Object.freeze({ slug: "godlock", name: "GodLock", status: "live" }),
    Object.freeze({ slug: "azclce", name: "AZ-CLCE", status: "live" }),
  ]) }),
  Object.freeze({ id: "05", slug: "ai", name: "AI", softwares: Object.freeze([
    Object.freeze({ slug: "azai", name: "AZAI", status: "live" }),
    Object.freeze({ slug: "azbot", name: "AZBot", status: "live" }),
    Object.freeze({ slug: "azhub", name: "AZHub", status: "live" }),
  ]) }),
  Object.freeze({ id: "06", slug: "research", name: "Research", softwares: Object.freeze([
    Object.freeze({ slug: "azbrowser", name: "AZBrowser", status: "live" }),
    Object.freeze({ slug: "aziel-corpus", name: "Aziel Corpus", status: "live" }),
    Object.freeze({ slug: "4dmap", name: "4DMap", status: "live" }),
  ]) }),
  Object.freeze({ id: "07", slug: "comms", name: "Comms", softwares: Object.freeze([
    Object.freeze({ slug: "azmail", name: "AZMail", status: "live" }),
    Object.freeze({ slug: "azchat", name: "AZChat", status: "stub / not hosted yet" }),
  ]) }),
  Object.freeze({ id: "08", slug: "network", name: "Network", softwares: Object.freeze([
    Object.freeze({ slug: "aznet", name: "AZNet", status: "live" }),
    Object.freeze({ slug: "miragegrid", name: "MirageGrid", status: "live" }),
    Object.freeze({ slug: "azieltether", name: "AzielTether", status: "live" }),
  ]) }),
  Object.freeze({ id: "09", slug: "system", name: "System", softwares: Object.freeze([
    Object.freeze({ slug: "azos", name: "AZ-OS", status: "live" }),
  ]) }),
  Object.freeze({ id: "10", slug: "simulation", name: "Simulation", softwares: Object.freeze([
    Object.freeze({ slug: "postking", name: "Post-King Chess", status: "live" }),
  ]) }),
  Object.freeze({ id: "11", slug: "core-time", name: "Core Time", softwares: Object.freeze([
    Object.freeze({ slug: "staticclock", name: "StaticClock", status: "live" }),
    Object.freeze({ slug: "temporallock", name: "TemporalLock", status: "live" }),
  ]) }),
]);

export const PLACEMENTS = Object.freeze([
  Object.freeze({ slug: "azinterface", placement: "human-ui", note: "AZInterface is the human UI before FragGate. Catalog software. Not an extra door. Not one of the 33." }),
  Object.freeze({ slug: "decisiongate", placement: "fabric-product", note: "DecisionGATE is the policy hop. Catalog engine. Not an extra door." }),
  Object.freeze({ slug: "forgereceipts", placement: "fabric-product", note: "ForgeReceipts packages Return. Catalog engine. Not an extra door." }),
]);

export const OPTIONAL_ANALYTICAL = Object.freeze([
  Object.freeze({ id: "ase", name: "ASE", note: "perspective integrity — cite only" }),
  Object.freeze({ id: "vector", name: "VECTOR", note: "directional selection — cite only" }),
  Object.freeze({ id: "oracle", name: "Oracle", note: "append-only learning — cite only" }),
  Object.freeze({ id: "constellation", name: "Constellation", note: "independent multi-node comparison — cite only" }),
]);

export const ABSENT_FROM_CORE = Object.freeze(["ZD30", "rollback", "generic truth score"]);

export const PIPELINE_PAPERS = Object.freeze({
  master_33: MASTER_PAPER,
  master: MASTER_ARCH_PAPER,
  suite_pipe: SUITE_PAPER,
  azpipe: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
  sweepgate: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
  chainlock: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
  "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
});

export const PIPELINE_NOTE =
  "MASTER-33 locked path on aziel-runtime (lock introduced 1.7.0). " +
  "The fabric owner is aziel-runtime — not a version+FragGate mash. " +
  "FragGate is THE SINGLE DOOR. AZInterface is the human-facing UI before " +
  "that door — not a second door and not one of the 33 domain slugs. " +
  "Internal Domain Layer is 33 softwares in 11 domains (isolation labels, " +
  "not additional doors). 4DMap is a Research-domain inspection frame " +
  "(T/Δ/Γ/Π), not an extra door (domains_are_doors:false). " +
  "AZChat is stub / not hosted yet (Comms). RoseClock is forward-only. " +
  "ChainLock / TemporalLock are append-only evidence. Lamb Lens is fabric " +
  "ethics after FragGate (Peace / Clarity / Service → PASS / REFUSE / " +
  "HOLD-UNCERTAIN), not Softwares-tab. LambGate is not a hop. " +
  "SUITE-PIPE-1.6.15 is historical (kept, not rolled back). MASTER-ARCHITECTURE-2.0 " +
  "is the companion spec; MASTER-33 overrides §4.2. ZD30, rollback, and " +
  "generic truth score are absent from the core.";

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
    slug: domain.slug,
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
    owner_note: "aziel-runtime owns fabric hops. FragGate is the door hop, not part of the product name.",
    software_tab: false,
    fabric_hops_software_tab: false,
    cite: "aziel-runtime fabric. Interface cites; runtime owns hops. Not a second door.",
    controlling_design: MASTER_33,
    companion_design: MASTER_ARCH,
    runtime_lock: RUNTIME_LOCK,
    suite_pipe: SUITE_PIPE,
    suite_pipe_status: "historical",
    suite_pipe_path: SUITE_PIPE_PATH,
    migration: "SUITE-PIPE-1.6.15 historical; MASTER-33 live on aziel-runtime",
    path: PIPELINE_PATH,
    hops: PIPELINE_HOPS.map(cloneHop),
    single_door: "fraggate",
    domains_are_doors: false,
    domain_doors: {
      inspection: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
      additional_doors: false,
      domains_are_doors: false,
      role: "inspection_frame",
      layer: "Internal Domain Layer",
      domain: "Research",
      domain_id: "06",
      note: "4DMap is an inspection frame after AZPIPE, not an extra door (domains_are_doors:false).",
    },
    domain_map: domainMap(),
    domain_count: 11,
    software_count: slugs.length,
    softwares: slugs,
    placements: PLACEMENTS.map((x) => ({ ...x })),
    azchat: { slug: "azchat", status: "stub / not hosted yet", domain: "Comms", domain_id: "07" },
    roseclock: { forward_only: true, rollback: false },
    optional_analytical: OPTIONAL_ANALYTICAL.map((x) => ({ ...x })),
    absent_from_core: [...ABSENT_FROM_CORE],
    papers: { ...PIPELINE_PAPERS },
    specs: { azpipe: AP_WP, sweepgate: SG_WP, chainlock: CL_WP, "4dmap": DM_WP, fraggate: FG_WP, suite_pipe: SUITE_PIPE, master_33: MASTER_33, master: MASTER_ARCH },
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
    else if (hop.inspection) badge = '<em class="inspect">4DMap inspection frame</em>';
    else if (hop.forward_only) badge = '<em class="inspect">forward-only</em>';
    return `<li class="${classes.join(" ")}" data-hop="${hop.id}" data-kind="${hop.kind || ""}"><span>${hop.label}</span>${badge}</li>`;
  }).join("");
  return `<div id="pipeline">
  <strong>LOCKED pipeline</strong>
  <p class="pipe-path">${PIPELINE_PATH}</p>
  <ol class="hops">${chips}</ol>
  <p class="pipe-note">FragGate is THE SINGLE DOOR. Fabric owner is aziel-runtime (not a version+FragGate mash). AZInterface is the human UI before the door — not a second door. Internal Domain Layer = 33 softwares / 11 domains (isolation labels, not extra doors). RoseClock is forward-only. Lamb Lens is fabric ethics after FragGate. MASTER-33 is live; SUITE-PIPE-1.6.15 is historical. No LambGate. No ZD30. No rollback.</p>
</div>`;
}

export function domainMapHtml() {
  const cards = DOMAIN_MAP.map((domain) => {
    const items = domain.softwares.map((row) => {
      const stub = String(row.status).includes("stub") ? " stub" : "";
      return `<li class="sw${stub}" data-slug="${row.slug}"><code>${row.slug}</code> ${row.name}<span class="st">${row.status}</span></li>`;
    }).join("");
    return `<section class="domain" data-domain="${domain.slug}"><h3>${domain.id} ${domain.name}</h3><ul>${items}</ul></section>`;
  }).join("");
  const analytical = OPTIONAL_ANALYTICAL.map((x) => `${x.name} (${x.note})`).join(" · ");
  return `<div id="domains">
  <strong>Internal Domain Layer</strong>
  <p class="pipe-note">MASTER-33: 33 softwares in 11 domains after AZPIPE. Isolation labels — not additional FragGate doors. 4DMap is a Research-domain inspection frame (T/Δ/Γ/Π), not an extra door (domains_are_doors:false). AZChat is stub / not hosted yet. AZInterface is the human UI before the door, not one of the 33. Owner: aziel-runtime. Author: Aziel Eliab only.</p>
  <div class="domain-grid">${cards}</div>
  <p class="pipe-note">Optional analytical (cite only): ${analytical}. Absent from core: ZD30, rollback, generic truth score.</p>
</div>`;
}
