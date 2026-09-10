/**
 * LOCKED suite pipeline cite — Interface cites; aziel-runtime owns fabric hops.
 *
 * PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE →
 * AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock →
 * StaticClock → ChainLock-OUT → Response/Receipt
 *
 * No LambGate. Fabric hops are not Softwares-tab products.
 * 4DMap (slug 4dmap) is Domain Door inspection, not a sequential gate.
 *
 * Author: Aziel Eliab only.
 */

export const AP_WP = "AP-WP-0.2";
export const SG_WP = "SG-WP-0.1";
export const CL_WP = "CL-WP-0.4";
export const DM_WP = "4DM-WP-1.0";
export const FG_WP = "FG-0.1";
export const PIPELINE_OWNER = "aziel-runtime";
export const PIPELINE_PATH =
  "PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → " +
  "AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → " +
  "StaticClock → ChainLock-OUT → Response/Receipt";

export const PIPELINE_HOPS = Object.freeze([
  Object.freeze({ id: "public", label: "PUBLIC/UI/Agents", kind: "surface", owner: "azinterface", software_tab: false }),
  Object.freeze({ id: "fraggate", label: "FragGate", kind: "door", spec: FG_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "sweepgate", label: "SweepGate", kind: "fabric", spec: SG_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "chainlock_in", label: "ChainLock-IN", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "decisiongate", label: "DecisionGATE", kind: "gate", spec: "DecisionGATE", owner: PIPELINE_OWNER, software_tab: true }),
  Object.freeze({ id: "azpipe", label: "AZPIPE", kind: "fabric", spec: AP_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({
    id: "domain_doors",
    label: "Domain Doors",
    kind: "inspection",
    highlight: true,
    owner: PIPELINE_OWNER,
    software_tab: false,
    inspection: Object.freeze({
      name: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
      note: "Domain Door inspection after AZPIPE. Not a sequential gate.",
    }),
  }),
  Object.freeze({ id: "temporallock", label: "TemporalLock", kind: "neighbor", owner: PIPELINE_OWNER, software_tab: true }),
  Object.freeze({ id: "staticclock", label: "StaticClock", kind: "neighbor", owner: PIPELINE_OWNER, software_tab: true }),
  Object.freeze({ id: "chainlock_out", label: "ChainLock-OUT", kind: "fabric", spec: CL_WP, owner: PIPELINE_OWNER, software_tab: false }),
  Object.freeze({ id: "response", label: "Response/Receipt", kind: "surface", owner: "azinterface", software_tab: false }),
]);

export const PIPELINE_PAPERS = Object.freeze({
  azpipe: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/AP-WP-0.2.md",
  sweepgate: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SG-WP-0.1.md",
  chainlock: "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/CL-WP-0.4.md",
  "4dmap": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/4DM-WP-1.0.md",
});

export const PIPELINE_NOTE =
  "LOCKED suite pipeline. Interface cites this hop list. " +
  "aziel-runtime owns fabric hops (SweepGate / ChainLock / AZPIPE). " +
  "Those hops are not Softwares-tab products. " +
  "4DMap (slug 4dmap, 4DM-WP-1.0) is Domain Door inspection after AZPIPE — " +
  "not a sequential gate. LambGate is not on this list.";

function cloneHop(hop) {
  const row = { ...hop };
  if (hop.inspection) row.inspection = { ...hop.inspection };
  return row;
}

export function pipelineArch() {
  return {
    locked: true,
    lambgate: false,
    owner: PIPELINE_OWNER,
    software_tab: false,
    fabric_hops_software_tab: false,
    cite: "aziel-runtime fabric. Interface cites; runtime owns hops.",
    path: PIPELINE_PATH,
    hops: PIPELINE_HOPS.map(cloneHop),
    domain_doors: {
      inspection: "4DMap",
      slug: "4dmap",
      spec: DM_WP,
      sequential_gate: false,
      axes: "T/Δ/Γ/Π",
    },
    papers: { ...PIPELINE_PAPERS },
    specs: { azpipe: AP_WP, sweepgate: SG_WP, chainlock: CL_WP, "4dmap": DM_WP, fraggate: FG_WP },
    identity: "Aziel Eliab",
    author: "Aziel Eliab",
    runtime: "https://aziel-runtime.vibelock.workers.dev",
    note: PIPELINE_NOTE,
  };
}

export function pipelineStripHtml() {
  const chips = PIPELINE_HOPS.map((hop) => {
    const extra = hop.highlight ? " door" : "";
    const inspect = hop.inspection ? '<em class="inspect">4DMap inspection</em>' : "";
    return `<li class="hop${extra}" data-hop="${hop.id}" data-kind="${hop.kind || ""}"><span>${hop.label}</span>${inspect}</li>`;
  }).join("");
  return `<div id="pipeline">
  <strong>LOCKED pipeline</strong>
  <p class="pipe-path">${PIPELINE_PATH}</p>
  <ol class="hops">${chips}</ol>
  <p class="pipe-note">Runtime owns fabric hops (SweepGate / ChainLock / AZPIPE) — not Softwares-tab. Domain Doors highlight 4DMap as inspection. No LambGate.</p>
</div>`;
}
