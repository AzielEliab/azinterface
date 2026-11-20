/**
 * Boot self-measure for the public worker.
 * verified is set only when a complete file hash matches a signed release manifest.
 * A dropped hash does not fall through to verified or mismatch. The isolate has no
 * install tree, so startup stays unknown. The published runtime pin does not vouch
 * for azinterface. This module does not write, deploy, or change the QNM flags.
 * Author: Aziel Eliab. SPDX-License-Identifier: Apache-2.0
 */
import { canonicalize } from "./tether.js";

export const SPEC = "AZINTERFACE-BOOT-MEASURE-1.0";
export const PRODUCT = "azinterface";
/** Published aziel-runtime pin. It does not vouch for this product. */
export const RELEASE_PUBLIC_KEY = "_3mc9CfQWexUWcyqDadNoQLjb6fFFPRv_XfWirwuH9s";

const HEX64 = /^[a-f0-9]{64}$/;

function pathOk(path) {
  if (typeof path !== "string" || !path || path.length > 240) return false;
  if (path.startsWith("/") || path.includes("\\") || path.endsWith("/")) return false;
  return path.split("/").every((part) => part !== "" && part !== "." && part !== "..");
}

function shapeCode(manifest) {
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) return "BOOT-MEASURE-SHAPE";
  if (Object.keys(manifest).sort().join(",") !== "files,product,spec") return "BOOT-MEASURE-SHAPE";
  if (manifest.spec !== SPEC) return "BOOT-MEASURE-SHAPE";
  if (manifest.product !== PRODUCT) return "BOOT-MEASURE-PRODUCT";
  if (!Array.isArray(manifest.files) || manifest.files.length === 0) return "BOOT-MEASURE-SHAPE";
  const seen = new Set();
  for (const row of manifest.files) {
    if (!row || typeof row !== "object" || Array.isArray(row)) return "BOOT-MEASURE-SHAPE";
    if (Object.keys(row).sort().join(",") !== "path,sha256,size") return "BOOT-MEASURE-SHAPE";
    if (!pathOk(row.path) || seen.has(row.path)) return "BOOT-MEASURE-SHAPE";
    const base = row.path.split("/").pop();
    if (base === "boot-manifest.json" || base === "boot-manifest.sig" || base === "boot-measure.pub") return "BOOT-MEASURE-SHAPE";
    seen.add(row.path);
    if (typeof row.sha256 !== "string" || !HEX64.test(row.sha256)) return "BOOT-MEASURE-SHAPE";
    if (!Number.isSafeInteger(row.size) || row.size < 0) return "BOOT-MEASURE-SHAPE";
  }
  return null;
}

function keyClass(publicKey) {
  if (typeof publicKey !== "string" || !publicKey.trim()) return "absent";
  if (publicKey.trim() === RELEASE_PUBLIC_KEY) return "runtime-pin";
  return "present";
}

function records(files) {
  if (!Array.isArray(files)) return null;
  const rows = [];
  const seen = new Set();
  for (const row of files) {
    if (!row || !pathOk(row.path) || typeof row.sha256 !== "string" || !HEX64.test(row.sha256)) return null;
    if (!Number.isSafeInteger(row.size) || row.size < 0 || seen.has(row.path)) return null;
    seen.add(row.path);
    rows.push({ path: row.path, sha256: row.sha256, size: row.size });
  }
  rows.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  return rows;
}

function same(left, right) {
  if (!left || !right || left.length !== right.length || left.length === 0) return false;
  return left.every((row, i) => row.path === right[i].path && row.sha256 === right[i].sha256 && row.size === right[i].size);
}

function b64urlBytes(text) {
  const s = String(text || "").replace(/-/g, "+").replace(/_/g, "/");
  const pad = s.length % 4 ? "=".repeat(4 - (s.length % 4)) : "";
  try {
    const bin = atob(s + pad);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  } catch {
    return null;
  }
}

async function signatureOk(publicKey, manifest, signature) {
  const raw = b64urlBytes(publicKey);
  const sig = b64urlBytes(signature);
  if (!raw || raw.length !== 32 || !sig || sig.length !== 64) return false;
  try {
    const key = await crypto.subtle.importKey("raw", raw, { name: "Ed25519" }, false, ["verify"]);
    return await crypto.subtle.verify("Ed25519", key, sig, new TextEncoder().encode(canonicalize(manifest)));
  } catch {
    return false;
  }
}

export function sentence(report) {
  const row = report || {};
  const verified = row.status === "verified" && row.verified === true && row.signature_ok === true && row.hashed === true && row.manifest_present === true && row.hash_dropped !== true;
  if (verified) return "Boot measure: verified. The installed files match the signed release manifest.";
  if (row.status === "mismatch" && row.verified === false && row.signature_ok === true && row.hash_dropped !== true) {
    return "Boot measure: mismatch. The signed release manifest does not match the installed files.";
  }
  if (row.hashed === true && row.hash_dropped !== true) {
    return "Boot measure: unknown. The installed files were hashed. There is no signed release manifest to compare.";
  }
  return "Boot measure: unknown. The file hash was not completed. This measure is not verified.";
}

function seal({ code, hashed, files, manifestPresent, signatureOk: signed, matched, hashDropped, surface }) {
  const complete = hashed === true && hashDropped !== true && Array.isArray(files) && files.length > 0;
  let verified = matched === true && signed === true && manifestPresent === true && complete;
  let status = "unknown";
  let nextCode = code;
  if (verified) {
    status = "verified";
    nextCode = "BOOT-MEASURE-VERIFIED";
  } else if (signed === true && complete && manifestPresent === true && matched === false) {
    status = "mismatch";
    nextCode = "BOOT-MEASURE-MISMATCH";
    verified = false;
  } else {
    verified = false;
    if (nextCode === "BOOT-MEASURE-VERIFIED" || nextCode === "BOOT-MEASURE-MISMATCH") {
      nextCode = complete ? "BOOT-MEASURE-UNSIGNED" : "BOOT-MEASURE-UNREADABLE";
    }
  }
  const dropped = hashDropped === true || !Array.isArray(files);
  const keep = !dropped && hashed === true;
  const text = sentence({
    status,
    verified,
    signature_ok: signed === true && !dropped && (status === "verified" || status === "mismatch"),
    hashed: keep,
    manifest_present: manifestPresent === true,
    hash_dropped: dropped,
  });
  return {
    ok: true,
    spec: SPEC,
    product: PRODUCT,
    surface,
    status,
    verified,
    code: nextCode,
    hashed: keep,
    hash_dropped: dropped,
    file_count: keep ? files.length : 0,
    manifest_present: manifestPresent === true,
    manifest_hash: null,
    signature_ok: signed === true && !dropped && (status === "verified" || status === "mismatch"),
    read_only: true,
    writes: false,
    live: false,
    booted: false,
    installed: false,
    os_yet: false,
    kernel: false,
    mesh_node_live: true,
    alt_internet_live: true,
    packet_path_live: true,
    qnm_membership: true,
    qns_cite_plane: false,
    cap7_registrar_live: false,
    public_icann: false,
    cap7_is_icann: false,
    satellite_relay: "HELD",
    paid_satellite: "HELD",
    remain_off: true,
    dns_publish: false,
    api: "/v1/boot_measure",
    sentence: text,
    display: { title: "Boot measure", summary: text, fields: [{ label: "status", value: status }] },
  };
}

export async function compareSigned(files, manifest, signature, publicKey, { hashed = true, readCode = null, surface = "worker", manifestPresent = manifest != null } = {}) {
  if (readCode || hashed !== true || files == null) {
    return seal({
      code: readCode || "BOOT-MEASURE-UNREADABLE",
      hashed: false,
      files: null,
      manifestPresent: false,
      signatureOk: false,
      matched: false,
      hashDropped: true,
      surface,
    });
  }
  const rows = records(files);
  if (!rows) {
    return seal({ code: "BOOT-MEASURE-UNREADABLE", hashed: false, files: null, manifestPresent: false, signatureOk: false, matched: false, hashDropped: true, surface });
  }
  if (!manifestPresent || manifest == null) {
    return seal({ code: "BOOT-MEASURE-NO-MANIFEST", hashed: true, files: rows, manifestPresent: false, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  if (keyClass(publicKey) === "runtime-pin") {
    return seal({ code: "BOOT-MEASURE-KEY-SCOPE", hashed: true, files: rows, manifestPresent: true, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  const shape = shapeCode(manifest);
  if (shape) {
    return seal({ code: shape, hashed: true, files: rows, manifestPresent: true, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  if (typeof signature !== "string" || !signature.trim()) {
    return seal({ code: "BOOT-MEASURE-UNSIGNED", hashed: true, files: rows, manifestPresent: true, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  if (keyClass(publicKey) !== "present") {
    return seal({ code: "BOOT-MEASURE-NO-KEY", hashed: true, files: rows, manifestPresent: true, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  const signed = await signatureOk(String(publicKey).trim(), manifest, signature.trim());
  if (!signed) {
    return seal({ code: "BOOT-MEASURE-UNSIGNED", hashed: true, files: rows, manifestPresent: true, signatureOk: false, matched: false, hashDropped: false, surface });
  }
  const claimed = records(manifest.files);
  const matched = same(claimed, rows);
  const report = seal({
    code: matched ? "BOOT-MEASURE-VERIFIED" : "BOOT-MEASURE-MISMATCH",
    hashed: true,
    files: rows,
    manifestPresent: true,
    signatureOk: true,
    matched,
    hashDropped: false,
    surface,
  });
  if (report.signature_ok) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonicalize(manifest)));
    report.manifest_hash = [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  return report;
}

/** Startup on this isolate. There is no install tree, so the hash is not completed. */
export function isolateReport() {
  return seal({
    code: "BOOT-MEASURE-NO-MANIFEST",
    hashed: false,
    files: null,
    manifestPresent: false,
    signatureOk: false,
    matched: false,
    hashDropped: true,
    surface: "worker",
  });
}

export const STARTUP = Object.freeze(isolateReport());

function shownStatus(report) {
  const row = report || {};
  if (row.status === "verified" && row.verified === true && row.signature_ok === true && row.hashed === true && row.manifest_present === true && row.hash_dropped !== true) return "verified";
  if (row.status === "mismatch" && row.verified === false && row.signature_ok === true && row.hash_dropped !== true) return "mismatch";
  return "unknown";
}

export function markup(report) {
  const shown = shownStatus(report);
  const text = sentence({ ...report, status: shown, verified: shown === "verified" });
  return `<p class="banner" id="boot-measure" data-status="${shown}" role="status">${text}</p>`;
}
