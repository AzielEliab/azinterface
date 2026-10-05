/**
 * Public banner and page-cycle JSON keep the standing facts false.
 */
import assert from "node:assert/strict";
import { dispatch, resetEngine } from "../workers/download-tracker/src/engine.js";
import { installScript } from "../workers/download-tracker/src/index.js";
import { htmlHeaders, PUBLIC_CSP } from "../workers/download-tracker/src/headers.js";
import {
  COUNTED_TARBALL_SHA256,
  STANDING_SENTENCES,
  standingFacts,
} from "../workers/download-tracker/src/honesty.js";
import { notLiveSentence } from "../workers/download-tracker/src/alt-internet-fact.js";
import { domainMapHtml, pipelineArch } from "../workers/download-tracker/src/pipeline.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

const TAIL = [
  "WireGuard, OpenVPN, an L3 exit pool, kernel UDP, and TUN/TAP stay SLOT.",
  "The public door stays FG-STUB.",
  "Isolation is single-node security-awareness.",
  "Phoenix is a local wait and re-seal.",
];

function assertFacts(facts) {
  assert.equal(facts.alt_internet_live, false);
  assert.equal(facts.packet_path_live, false);
  assert.equal(facts.second_device, false);
  assert.equal(facts.mail_send, false);
  assert.equal(facts.kernel, false);
  assert.equal(facts.kernel_base, false);
  assert.equal(facts.booted, false);
  assert.equal(facts.installed, false);
  assert.equal(facts.os_yet, false);
  assert.equal(facts.internet_base.present, true);
  assert.equal(facts.internet_base.live, false);
  assert.equal(facts.internet_base.installed, false);
  assert.equal(facts.veillock, "local_only");
  assert.equal(facts.veillock_public_door, false);
  assert.equal(facts.whitestone_worker_only, true);
  assert.equal(facts.whitestone_public_door, false);
  assert.equal(facts.public_door, "FG-STUB");
  for (const line of STANDING_SENTENCES) assert.equal(facts.text.includes(line), true);
  assert.equal(facts.text.includes("is true"), false);
}

const html = homeHtml({ views: 0, downloads: 0, github: {} });
const sentence = notLiveSentence();
assert.equal(html.includes(sentence), true);
for (const line of STANDING_SENTENCES) assert.equal(html.includes(line), true);
for (const line of TAIL) {
  assert.equal(html.includes(line), true);
  assert.equal(sentence.includes(line), true);
}
assert.equal(html.includes("Internet is not live."), false);
assert.equal(html.includes("Softwares 42 is the runtime catalog."), true);
assert.equal(html.includes("The domain count stays 33."), true);
assert.equal(html.includes(COUNTED_TARBALL_SHA256), true);

resetEngine();
const caller = {
  alt_internet_live: true,
  packet_path_live: true,
  second_device: true,
  mail_send: true,
  kernel: true,
  kernel_base: true,
  booted: true,
  installed: true,
  os_yet: true,
  site_state: "ON",
  veillock: "live",
  whitestone_public_door: true,
  internet_base: { present: false, live: true, installed: true },
};
const cycle = await dispatch("page_cycle_status", caller);
assert.equal(cycle.site_state, "OFF");
assert.equal(cycle.booted, false);
assert.equal(cycle.installed, false);
assert.equal(cycle.mail_send, false);
assert.equal(cycle.kernel_base, false);
assert.equal(cycle.os_yet, false);
assert.equal(cycle.alt_internet_live, false);
assert.equal(cycle.packet_path_live, false);
assert.equal(cycle.second_device, false);
assert.equal(String(cycle.kernel).includes("github.com/AzielEliab/fraggate"), true);
assert.equal(cycle.kernel === true, false);
assert.equal(cycle.pipeline.software_count, 33);
assertFacts(cycle.honesty);
assertFacts(standingFacts(caller));

const pipe = pipelineArch();
const cited = Object.fromEntries(pipe.domain_map.flatMap((domain) => domain.softwares.map((row) => [row.slug, row.status])));
assert.equal(Object.keys(cited).length, 33);
assert.equal(pipe.software_count, 33);
assert.equal(cited.veillock.includes("local_only"), true);
assert.equal(cited.veillock.includes("no public FragGate door"), true);
assert.equal(cited.veillock === "live", false);
const map = domainMapHtml();
const veil = (map.match(/data-slug="veillock"[\s\S]*?<\/li>/) || [])[0] || "";
assert.equal(veil.includes("listed on aziel-runtime"), false);
assert.equal(veil.includes("local_only"), true);
const vibe = (map.match(/data-slug="vibelock"[\s\S]*?<\/li>/) || [])[0] || "";
assert.equal(vibe.includes("listed on aziel-runtime"), true);
assert.equal(cited.whitestone, undefined);

const script = installScript();
assert.equal(script.includes(COUNTED_TARBALL_SHA256), true);
assert.equal(script.includes("Refusing to install. The counted tarball digest does not match."), true);
assert.equal(script.includes("tar -xzf"), true);
const headers = htmlHeaders();
assert.equal(headers["Content-Security-Policy"], PUBLIC_CSP);
assert.equal(headers["Access-Control-Allow-Origin"], "*");
assert.equal(PUBLIC_CSP.includes("default-src 'self'"), true);
assert.equal(PUBLIC_CSP.includes("https://www.azielcorpuslibrary.net"), true);
assert.equal(PUBLIC_CSP.includes("frame-ancestors 'none'"), true);

console.log("worker honesty ok");
