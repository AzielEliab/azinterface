/**
 * Worker homepage keeps custody chrome and adds the suite Live Nodes strip.
 */
import assert from "node:assert/strict";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

const html = homeHtml({ views: 1, downloads: 2, github: { stars: 0 } });

assert.match(html, /id="nodes"/);
assert.match(html, /Live Nodes/);
assert.match(html, /Mesh OFF/);
assert.match(html, /QNM-BUILD-1.0/);
assert.match(html, /live\|locked\|isolated/);
assert.match(html, /AIH-WP-1.3 spiderweb is local qnm-node/);
assert.match(html, /not a public Node Gate/);
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

console.log("worker ui mesh strip ok");
