/**
 * AZInterface /cite.json — cross-map for agents and humans.
 * Identity is Aziel Eliab only. FragGate is THE single door.
 */
import {
  AZCLCE,
  AZCLCE_WORKER,
  AZCOHERENCE,
  AZCOHERENCE_DOWNLOAD,
  AZCOHERENCE_WORKER,
  AZHUB,
  AZHUB_WORKER,
  FRAGGATE,
  FRAGGATE_CALL,
  GITHUB,
  HOST,
  IDENTITY,
  NAME,
  RUNTIME,
  SOFTWARE_CATALOG,
  SORT_LAW,
  SPEC,
  VERSION,
} from "./engine.js";

export function citeDocument() {
  return {
    author: IDENTITY,
    identity: "Aziel Eliab only",
    title: NAME,
    version: VERSION,
    spec: SPEC,
    github: GITHUB,
    homepage: HOST + "/",
    download: HOST + "/download",
    skill: HOST + "/v1/skill",
    llms: HOST + "/llms.txt",
    license: "Apache-2.0",
    catalog: RUNTIME + "/",
    catalog_software: SOFTWARE_CATALOG,
    fraggate: FRAGGATE,
    fraggate_call: FRAGGATE_CALL,
    fraggate_describe: RUNTIME + "/v1/fraggate/describe?slug=azinterface",
    door: "fraggate",
    sort_law: SORT_LAW,
    sibling: AZHUB,
    azcoherence: AZCOHERENCE,
    azcoherence_worker: AZCOHERENCE_WORKER + "/",
    azcoherence_download: AZCOHERENCE_DOWNLOAD,
    azcoherence_slug: "azcoherence",
    peers: [
      {
        name: "AZ-CLCE",
        slug: "azclce",
        bucket: "plain",
        github: AZCLCE,
        worker: AZCLCE_WORKER + "/",
        note: "Language-domain isolation. AZCoherence is the scoring-adjacent peer — do not merge.",
      },
      {
        name: "AZCoherence",
        slug: "azcoherence",
        bucket: "plain",
        spec: "AZC-WP-0.1",
        placement: "scoring-review",
        github: AZCOHERENCE,
        worker: AZCOHERENCE_WORKER + "/",
        download: AZCOHERENCE_DOWNLOAD,
        fraggate_describe: RUNTIME + "/v1/fraggate/describe?slug=azcoherence",
        fraggate_call: FRAGGATE_CALL,
        one_line:
          "Second-pass triad coherence review (primary vs alternate → PASS/FLAG/NEUTRALIZE/REFUSE). Peer of AZ-CLCE. Not AKM-TRIAD.",
        not: "AKM-TRIAD",
        human: AZCOHERENCE_WORKER + "/ + /download",
        agent: "fraggate_describe then fraggate_call slug=azcoherence via aziel-runtime",
      },
      {
        name: "AZHub",
        slug: "azhub",
        bucket: "plain",
        github: AZHUB,
        worker: AZHUB_WORKER + "/",
        note: "Blank Key / spatial container. Separate software — never collapse Interface into Hub.",
      },
    ],
    note:
      "Do not invent a DOI. Interface is CUSTODY — never collapse into Hub. " +
      "AZCoherence is separate Softwares on the same FragGate door (slug=azcoherence). " +
      "FragGate is THE single door. Agents use aziel-runtime MCP/FragGate; humans use this Worker UI + /download.",
  };
}
