/**
 * Worker homepage keeps custody chrome and adds the suite Live Nodes strip.
 */
import assert from "node:assert/strict";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import { MESH_OFF_COPY, QNS_CD, QNM_BUILD } from "../workers/download-tracker/src/mesh.js";

const html = homeHtml({ views: 1, downloads: 2, github: { stars: 0 } });

assert.match(html, /id="nodes"/);
assert.match(html, /Live Nodes/);
assert.match(html, /Mesh OFF/);
assert.match(html, /QNM-BUILD-1.0/);
assert.match(html, /QNS-CD-1.0/);
assert.match(html, /live\|locked\|isolated/);
assert.match(html, /AIH-WP-1.3 spiderweb is local qnm-node/);
assert.match(html, /not a public Node Gate/);
assert.match(html, /GET never enables/);
assert.match(html, /qnsd/);
assert.equal(QNS_CD, "QNS-CD-1.0");
assert.equal(QNM_BUILD, "QNM-BUILD-1.0");
assert.match(MESH_OFF_COPY, /QNS-CD-1.0/);
assert.match(MESH_OFF_COPY, /QNM-BUILD-1.0/);
assert.match(html, /pair-offer-btn/);
assert.match(html, /pair_offer/);
assert.match(html, /not anonymity/);
assert.match(html, /not a publish path/);
assert.match(html, /\/v1\/mesh\/status/);
assert.match(html, /no auto-heal/);
assert.match(html, /product: MESH_PRODUCT/);
assert.match(html, /azinterface/);

assert.match(html, /data-state="ON"/);
assert.match(html, /data-state="OFF"/);
assert.match(html, /data-state="FULL_SHUTDOWN"/);
assert.match(html, /data-state="MEMORIAL"/);
assert.match(html, /genesis-btn/);
assert.match(html, /integrity-btn/);
assert.match(html, /witness-btn/);
assert.match(html, /withdraw-btn/);
assert.match(html, /PRE-LOCKED/);
assert.match(html, /AZHome bunker/);
assert.match(html, /Scorched Earth/);
assert.match(html, /page_cycle_status/);
assert.match(html, /LOCKED pipeline/);
assert.match(html, /THE SINGLE DOOR/);
assert.match(html, /Internal Domain Layer/);
assert.match(html, /No LambGate/);
assert.match(html, /out-panel/);
assert.match(html, /collapsed by default/);
assert.match(html, /max-height:12rem/);
assert.match(html, /install-steps/);
assert.match(html, /install-advanced/);
assert.match(html, /Checksum note/);
assert.match(html, /custody UI only/);
assert.match(html, /Agents use aziel-runtime FragGate\/MCP/);
assert.match(html, /install\.sh -o install-azinterface\.sh/);
assert.match(html, /toastMemorial/);
assert.match(html, /AIH-CYCLE-TERMINAL/);
assert.match(html, /MEMORIAL is terminal/);
assert.equal(html.includes("curl -fsSL") && html.includes("| bash"), true);
const installCmd = (html.match(/id="install-cmd">([\s\S]*?)<\/pre>/) || [])[1] || "";
assert.match(installCmd, /install\.sh -o install-azinterface\.sh/);
assert.equal(installCmd.includes("| bash"), false);

console.log("worker ui mesh strip ok");
