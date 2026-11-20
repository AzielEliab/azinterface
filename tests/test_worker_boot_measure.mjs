/**
 * Worker boot measure: match, mismatch, missing manifest, and a dropped hash.
 * The isolate startup report stays unknown. A posted verified flag is ignored.
 */
import assert from "node:assert/strict";
import { createHash, generateKeyPairSync, sign } from "node:crypto";
import { canonicalize } from "../workers/download-tracker/src/tether.js";
import { RELEASE_PUBLIC_KEY, STARTUP, compareSigned, markup } from "../workers/download-tracker/src/boot-measure.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import worker from "../workers/download-tracker/src/entry.js";

const hello = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824";
assert.equal(createHash("sha256").update("hello").digest("hex"), hello);

function keys() {
  const pair = generateKeyPairSync("ed25519");
  const der = pair.publicKey.export({ format: "der", type: "spki" });
  return { publicKey: der.subarray(der.length - 32).toString("base64url"), privateKey: pair.privateKey };
}

function signManifest(privateKey, manifest) {
  return sign(null, Buffer.from(canonicalize(manifest)), privateKey).toString("base64url");
}

const files = [{ path: "app.txt", sha256: hello, size: 5 }];
const manifest = { spec: "AZINTERFACE-BOOT-MEASURE-1.0", product: "azinterface", files };
const canon = '{"files":[{"path":"app.txt","sha256":"2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824","size":5}],"product":"azinterface","spec":"AZINTERFACE-BOOT-MEASURE-1.0"}';
assert.equal(canonicalize(manifest), canon);

const { publicKey, privateKey } = keys();
const signature = signManifest(privateKey, manifest);

const match = await compareSigned(files, manifest, signature, publicKey);
assert.equal(match.status, "verified");
assert.equal(match.verified, true);
assert.equal(match.signature_ok, true);
assert.equal(match.hashed, true);
assert.equal(match.hash_dropped, false);
assert.equal(match.code, "BOOT-MEASURE-VERIFIED");
assert.equal(match.mesh_node_live, true);
assert.equal(match.alt_internet_live, true);
assert.equal(match.packet_path_live, true);
assert.equal(match.cap7_registrar_live, false);
assert.equal(match.public_icann, false);
assert.equal(match.satellite_relay, "HELD");
assert.equal(match.paid_satellite, "HELD");
assert.equal(match.remain_off, true);
assert.equal(match.installed, false);
assert.equal(match.booted, false);
assert.match(match.sentence, /^Boot measure: verified\./);

const mismatch = await compareSigned([{ path: "app.txt", sha256: hello, size: 6 }], manifest, signature, publicKey);
assert.equal(mismatch.status, "mismatch");
assert.equal(mismatch.verified, false);
assert.equal(mismatch.signature_ok, true);
assert.equal(mismatch.hash_dropped, false);
assert.equal(mismatch.code, "BOOT-MEASURE-MISMATCH");
assert.match(mismatch.sentence, /^Boot measure: mismatch\./);
assert.equal(mismatch.sentence.includes("Boot measure: verified"), false);

const missing = await compareSigned(files, null, null, publicKey);
assert.equal(missing.status, "unknown");
assert.equal(missing.verified, false);
assert.equal(missing.manifest_present, false);
assert.equal(missing.hash_dropped, false);
assert.equal(missing.code, "BOOT-MEASURE-NO-MANIFEST");
assert.equal(missing.sentence.includes("Boot measure: verified"), false);

const dropped = await compareSigned(files, manifest, signature, publicKey, { hashed: false, readCode: "BOOT-MEASURE-UNREADABLE" });
assert.equal(dropped.status, "unknown");
assert.equal(dropped.verified, false);
assert.equal(dropped.hash_dropped, true);
assert.equal(dropped.hashed, false);
assert.equal(dropped.file_count, 0);
assert.equal(dropped.code, "BOOT-MEASURE-UNREADABLE");
assert.notEqual(dropped.code, "BOOT-MEASURE-VERIFIED");
assert.notEqual(dropped.code, "BOOT-MEASURE-MISMATCH");

const unsigned = await compareSigned(files, manifest, signature.slice(0, -4) + "AAAA", publicKey);
assert.equal(unsigned.status, "unknown");
assert.equal(unsigned.verified, false);
assert.equal(unsigned.code, "BOOT-MEASURE-UNSIGNED");

const pinned = await compareSigned(files, manifest, signature, RELEASE_PUBLIC_KEY);
assert.equal(pinned.status, "unknown");
assert.equal(pinned.verified, false);
assert.equal(pinned.code, "BOOT-MEASURE-KEY-SCOPE");

assert.equal(STARTUP.status, "unknown");
assert.equal(STARTUP.verified, false);
assert.equal(STARTUP.hashed, false);
assert.equal(STARTUP.hash_dropped, true);
assert.equal(STARTUP.mesh_node_live, true);
assert.equal(STARTUP.alt_internet_live, true);
assert.equal(STARTUP.packet_path_live, true);

const html = homeHtml({ views: 1, downloads: 0, github: {} });
assert.match(html, /id="boot-measure"/);
assert.match(html, /data-status="unknown"/);
assert.equal(html.includes("Boot measure: verified"), false);
const forged = markup({ status: "verified", verified: true, signature_ok: false, hashed: false, hash_dropped: true, manifest_present: true });
assert.equal(forged.includes("data-status=\"verified\""), false);
assert.equal(forged.includes("Boot measure: verified"), false);

const env = { DOWNLOADS: { get: async () => null, put: async () => {}, list: async () => ({ keys: [] }) } };
const ctx = { waitUntil() {} };
const got = await (await worker.fetch(new Request("https://h.example/v1/boot_measure"), env, ctx)).json();
assert.equal(got.status, "unknown");
assert.equal(got.verified, false);
assert.equal(got.hash_dropped, true);
assert.equal(got.mesh_node_live, true);
assert.equal(got.alt_internet_live, true);
assert.equal(got.packet_path_live, true);
assert.equal(got.cap7_registrar_live, false);
assert.equal(got.satellite_relay, "HELD");
assert.equal(got.remain_off, true);
const posted = await (await worker.fetch(new Request("https://h.example/v1/boot_measure", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ status: "verified", verified: true }),
}), env, ctx)).json();
assert.equal(posted.status, "unknown");
assert.equal(posted.verified, false);
assert.deepEqual(posted, got);

console.log("test_worker_boot_measure: passed");
