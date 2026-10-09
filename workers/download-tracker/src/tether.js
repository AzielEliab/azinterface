/**
 * Tether verification helpers for AZInterface's local copies (read-only crypto; no storage).
 * Same functions, byte for byte, as AZ-OS workers/download-tracker/src/tether.js, so both
 * hosts check the runtime's signed packets the same way. AZInterface keeps no KV tether.
 * Author: Aziel Eliab.
 */
export const GENESIS = "0".repeat(64);

export function canonicalize(value) {
  if (value === undefined) return undefined;
  if (value === null) return "null";
  const t = typeof value;
  if (t === "number") {
    if (!Number.isFinite(value)) throw new Error("cannot canonicalize non-finite number");
    return JSON.stringify(value);
  }
  if (t === "boolean") return value ? "true" : "false";
  if (t === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map((item) => canonicalize(item)).join(",") + "]";
  if (t === "object") {
    const keys = Object.keys(value).filter((k) => value[k] !== undefined).sort();
    return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalize(value[k])).join(",") + "}";
  }
  throw new Error("cannot canonicalize " + t);
}

export async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function primaryOf(documentHash, prev) {
  return sha256Hex(canonicalize({ document: documentHash, prev: prev || GENESIS }));
}

export async function offlineSecondaryOf(documentHash, username) {
  return sha256Hex(canonicalize({ primary: documentHash, username: String(username) }));
}

export async function onlineSecondaryOf(primary, prev) {
  return sha256Hex(canonicalize({ offline: false, prev: prev || GENESIS, primary }));
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

export async function verifySignature(publicKey, packet) {
  const raw = b64urlBytes(publicKey);
  const sig = b64urlBytes(packet && packet.sig);
  if (!raw || raw.length !== 32 || !sig || sig.length !== 64) return false;
  const { sig: _omit, ...unsigned } = packet;
  try {
    const key = await crypto.subtle.importKey("raw", raw, { name: "Ed25519" }, false, ["verify"]);
    return await crypto.subtle.verify("Ed25519", key, sig, new TextEncoder().encode(canonicalize(unsigned)));
  } catch {
    return false;
  }
}

export function pinnedKey(env) {
  const key = String((env && env.RUNTIME_TETHER_PUBKEY) || "").trim();
  return key || null;
}
