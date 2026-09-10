/**
 * Worker cite.json names AZCoherence and Plain A–Z peers.
 */
import assert from "node:assert/strict";
import { citeDocument } from "../workers/download-tracker/src/cite.js";
import { SKILL_MD } from "../workers/download-tracker/src/engine.js";

const cite = citeDocument();
assert.equal(cite.author, "Aziel Eliab");
assert.equal(cite.identity, "Aziel Eliab only");
assert.equal(cite.azcoherence_slug, "azcoherence");
assert.match(cite.azcoherence, /AZCoherence/i);
assert.match(cite.azcoherence_worker, /azcoherence-download-tracker/);
assert.match(cite.azcoherence_download, /\/download$/);
assert.match(cite.note, /azcoherence/);
assert.match(cite.note, /FragGate is THE single door/);
assert.deepEqual(cite.peers.map((p) => p.name), ["AZ-CLCE", "AZCoherence", "AZHub"]);
assert.ok(cite.peers.every((p) => p.bucket === "plain"));
const coherence = cite.peers.find((p) => p.slug === "azcoherence");
assert.equal(coherence.spec, "AZC-WP-0.1");
assert.equal(coherence.not, "AKM-TRIAD");
assert.match(coherence.fraggate_describe, /fraggate\/describe\?slug=azcoherence/);
assert.match(coherence.fraggate_call, /fraggate\/call/);
assert.match(cite.sort_law, /plain A–Z/);
assert.match(cite.catalog_software, /\/v1\/software$/);
assert.match(SKILL_MD, /azcoherence-download-tracker/);

console.log("worker cite.json azcoherence peers ok");
