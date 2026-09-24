/**
 * Worker custody app screens keep one primary action per tool.
 */
import assert from "node:assert/strict";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

const html = homeHtml({ views: 3, downloads: 4, github: { stars: 1 } });

function slice(src, start, end) {
  const i = src.indexOf(start);
  assert.ok(i >= 0, start);
  const j = src.indexOf(end, i + start.length);
  assert.ok(j > i, end);
  return src.slice(i + start.length, j);
}

assert.match(html, /id="app-view"/);
assert.match(html, /id="app-screen"/);
assert.match(html, /value="integrity" selected/);
assert.match(html, /Check integrity/);
assert.match(html, /id="integrity-btn"/);
const css = slice(html, 'id="app-screen"', "</style>");
assert.match(css, /prefers-color-scheme: light/);
assert.match(css, /focus-visible/);
assert.match(css, /#c9a227/);
const cycle = slice(html, 'id="cycle-more"', "</details>");
assert.match(cycle, /data-state="ON"/);
assert.match(cycle, /data-state="OFF"/);
assert.match(cycle, /data-state="FULL_SHUTDOWN"/);
assert.match(cycle, /data-state="MEMORIAL"/);
assert.match(slice(html, ">Key status<", "</details>"), /genesis-status-btn/);
assert.match(slice(html, ">Withdraw or list witnesses<", "</details>"), /withdraw-btn/);
assert.match(slice(html, ">Withdraw or list witnesses<", "</details>"), /witness-btn/);
const pair = slice(html, ">Accept, seal, cut, or status<", "</details>");
assert.match(pair, /pair-accept-btn/);
assert.match(pair, /pair-seal-btn/);
assert.match(pair, /pair-cut-btn/);
assert.match(pair, /pair-status-btn/);
assert.match(slice(html, ">Remote wipe<", "</details>"), /scorch-remote-btn/);
assert.match(slice(html, ">Pipeline cite</summary>", "</details>"), /pipeline-btn/);
assert.match(html, /pair-offer-btn/);
assert.match(html, /QNS-CD-1.0/);
assert.match(html, /qnsd/);
assert.match(html, /OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL/);
assert.match(html, /PRE-LOCKED/);
assert.match(html, /Views/);
assert.match(html, /Downloads/);
assert.match(html, /Live Nodes/);
assert.match(html, /syncCyclePrimary/);
assert.match(html, /applyAppView/);

console.log("worker app screen ok");
