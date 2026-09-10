/**
 * FragGate / runtime / suite-mesh door — classify Worker /v1 paths.
 *
 * `/v1/fraggate/*`, `/v1/runtime/*`, and `/v1/mesh/*` PROXY to aziel-runtime
 * via AZIEL_RUNTIME or HTTPS fallback. Leftover `/v1/azpipe` and
 * `/v1/azpipe/arch` alias GET `/v1/fraggate` (MASTER-33 `pipeline` /
 * `pipeline_strip` — fabric cite, not a Softwares door). Local engine ops
 * are single-segment `/v1/{op}` only. Multi-segment leftovers are never
 * swallowed as op names.
 *
 * Suite mesh is QNM-BUILD-1.0 rollup only (live|locked|isolated). Default OFF.
 * GET never enables. QNS-CD-1.0 vias run in local qnsd (127.0.0.1).
 * AIH-WP-1.3 spiderweb is local qnm-node — not a public Node Gate.
 *
 * Author: Aziel Eliab only.
 */

export const DEFAULT_RUNTIME_ORIGIN = "https://aziel-runtime.vibelock.workers.dev";

/** Live aziel-runtime surface that returns MASTER-33 pipeline / pipeline_strip. */
export const RUNTIME_ARCH_PATH = "/v1/fraggate";

export const DOOR_PREFIXES = Object.freeze(["fraggate", "runtime", "mesh", "azpipe"]);

/** UI / leftover aliases → correct origin FragGate paths. */
export const DOOR_ALIASES = Object.freeze({
  "/v1/runtime/list": "/v1/fraggate/list",
  "/v1/runtime/call": "/v1/fraggate/call",
  "/v1/runtime/describe": "/v1/fraggate/describe",
  "/v1/runtime/verify": "/v1/fraggate/verify",
  "/v1/azpipe": RUNTIME_ARCH_PATH,
  "/v1/azpipe/arch": RUNTIME_ARCH_PATH,
});

export function normalizeV1Path(pathname) {
  const raw = String(pathname || "");
  const path = raw.replace(/\/+$/, "") || "/";
  return path.startsWith("/") ? path : "/" + path;
}

export function runtimeOrigin(env) {
  const fromEnv = env && (env.AZIEL_RUNTIME_ORIGIN || env.RUNTIME_ORIGIN);
  if (typeof fromEnv === "string" && /^https:\/\//i.test(fromEnv)) {
    return fromEnv.replace(/\/+$/, "");
  }
  return DEFAULT_RUNTIME_ORIGIN;
}

export function runtimeArchUrl(env) {
  return runtimeOrigin(env) + RUNTIME_ARCH_PATH;
}

export function mapDoorPath(pathname) {
  const path = normalizeV1Path(pathname);
  if (DOOR_ALIASES[path]) return DOOR_ALIASES[path];
  if (path === "/v1/fraggate" || path.startsWith("/v1/fraggate/")) return path;
  if (path === "/v1/runtime" || path.startsWith("/v1/runtime/")) return path;
  if (path === "/v1/mesh" || path.startsWith("/v1/mesh/")) return path;
  if (path === "/v1/azpipe" || path.startsWith("/v1/azpipe/")) return path;
  return null;
}

export function isDoorPath(pathname) {
  return mapDoorPath(pathname) != null;
}

export function localOpFromPath(pathname) {
  const path = normalizeV1Path(pathname);
  if (!path.startsWith("/v1/")) return null;
  const rest = path.slice("/v1/".length);
  if (!rest || rest.includes("/")) return null;
  if (DOOR_PREFIXES.includes(rest)) return null;
  return rest;
}

/**
 * Classify a Worker pathname.
 * @returns {{ kind: "door"|"local"|"multi"|"none", path: string, originPath?: string, op?: string }}
 */
export function classifyV1Path(pathname) {
  const path = normalizeV1Path(pathname);
  const originPath = mapDoorPath(path);
  if (originPath) return { kind: "door", path, originPath };
  const op = localOpFromPath(path);
  if (op) return { kind: "local", path, op };
  if (path === "/v1" || path === "/v1/") return { kind: "none", path: "/v1" };
  if (path.startsWith("/v1/")) return { kind: "multi", path };
  return { kind: "none", path };
}

export function doorTargetUrl(pathname, requestUrl, env) {
  const mapped = mapDoorPath(pathname);
  if (!mapped) return null;
  const origin = runtimeOrigin(env);
  let search = "";
  try {
    search = new URL(requestUrl).search || "";
  } catch {
    search = "";
  }
  return origin + mapped + search;
}
