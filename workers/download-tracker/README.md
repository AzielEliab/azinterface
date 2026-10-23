# AZInterface download tracker

Cloudflare Worker `azinterface-download-tracker`.

URL pattern after deploy (workers.dev + account subdomain, same as sibling products):

`https://azinterface-download-tracker.vibelock.workers.dev`

- `GET /` — complete pre-locked custody UI (site state / genesis / integrity / witness / AZHome) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /v1/*` — custody ops (does **not** increment downloads)
- `GET|POST /v1/mesh/*` — PROXY to aziel-runtime QNM-BUILD-1.0 rollup (node mesh ON). Cites SPLIT THE WIRES + COLD-COPY SURVIVAL.
- `GET /v1/fraggate` — PROXY to aziel-runtime FragGate door (MASTER-33 `pipeline` / `pipeline_strip`)
- `GET|POST /v1/azpipe/arch` — local alias of `pipeline_arch` (embedded MASTER-33; not a Softwares door)
- `GET|POST /v1/pipeline_arch` — local frozen LOCKED hop-list cite; optional runtime FragGate strip when live

KV binding `DOWNLOADS` (create `AZINTERFACE_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.
**Parent-deploy note:** `wrangler.toml` still has the `0000…` placeholder KV id.
A real production id was not in comments/README. Parent must create the
namespace and replace the id before deploy. Do not invent an id.

Human UI includes a **LOCKED pipeline** strip (MASTER-33 on aziel-runtime;
FragGate is THE SINGLE DOOR; Internal Domain Layer 33/11 isolation labels
with 4DMap inspection frame, not an extra door (`domains_are_doors:false`); no LambGate) plus the 11-domain
map, and a **Live Nodes** strip (QNM-BUILD-1.0)
live|locked|isolated + QNS-CD-1.0 cite + SPLIT THE WIRES + COLD-COPY
SURVIVAL + REHEAL refuse). Node mesh is ON (MESH_RADIOS=on). `GET /v1/mesh` never enables. QNS-CD-1.0 photon vias run in local
`qnm-node/` qnsd (127.0.0.1); this Worker holds pair memorial cites only.
AIH-WP-1.3 spiderweb is local `qnm-node/` — this Worker does not invent a
public Node Gate. Tip tick is presence+tip hash only; payload is pull-only
on a second plane; 1s loop and 777s gate never share a socket. Multiply
cold copies; refuse live body sync; server pull cannot wipe cold replicas.
No auto-heal. Not anonymity. Anon-broadcast is not a publish path. Not a Softwares-tab QNS product.

Human UI is this Worker. Agent / MCP path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with
`{"slug":"azinterface","op":"…","payload":{}}`. There is no separate Interface MCP
on this host (`GET|POST /mcp` returns `ok: false` — agents use
aziel-runtime FragGate/MCP; this host is custody UI only).

Interface is CUSTODY. AZHub is separate software under the one FragGate
door — never collapse them. AZCoherence (AZC-WP-0.1, `slug=azcoherence`)
is separate Plain Softwares on that same door (peer of AZ-CLCE; not
AKM-TRIAD). Humans: https://azcoherence-download-tracker.vibelock.workers.dev/
+ `/download`. Agents: FragGate `describe` then `call` via aziel-runtime.
`GET /cite.json` and `GET /llms.txt` cite those peer links. Softwares
tabs: `GET /v1/software` (plain A–Z).
Scorched Earth is a local stub/advisory only. Never a remote wipe.

Author: Aziel Eliab. Apache-2.0.

## Human / bot schema (`/stats` and `/count`)

Additive dual-count (Whitestone canary). Classification lives in `src/classify.js`
and response shaping in `src/stats-shape.js`.

Invariant: `views === views_human + views_bot` and
`downloads === downloads_human + downloads_bot`.

Legacy strategy (b): existing KV totals are never reset. Pre-split remainder
is shown as bot on read (`views_bot = views - views_human`). Author: Aziel Eliab only.


## AZ-LOCKSTEP-1.0 (shared design + contract with aziel-runtime)

This leg is independent and optional. `vendor/lockstep/` is a byte-for-byte copy of aziel-runtime's
design tokens, contract, and consumer check, pinned by SHA-256 in `LOCKSTEP.pin.json`.

- `GET /v1/lockstep`: `agree` / `drift` / `absent` against the runtime over the `AZIEL_RUNTIME` binding. When the runtime is absent this leg keeps running standalone and shows every flag as false.
- `GET /design/tokens.css`, `/design/tokens.json`: the shared design source, the same bytes as the runtime's.
- `npm test` fails if a vendored file changed, a lock moved, `mesh_node_live`, `alt_internet_live`, or `packet_path_live` is not true, any other contract flag is true, the tether key, chains, or mesh differ from the contract, or a feature this leg claims in the contract's union stops answering. `npm run lockstep:remote` also compares the pin with runtime `main`.
- To re-vendor after a runtime contract change, run `node scripts/lockstep-vendor.mjs <this checkout>` from an aziel-runtime checkout.
- Softwares tip `6f27394fbcafb640a1ede7017b599a6f66c68769` is aziel-runtime `main`, the squash of [aziel-runtime #365](https://github.com/AzielEliab/aziel-runtime/pull/365). `LOCKSTEP.pin.json` `runtime_commit` pins that tip. The vendored contract is `c24c368f5fa4df71ef7e43afeab21486e160876036a5572c272d87034e1ff492`. `hints_sha256` is `31d107ef0b113a5e5807128558a46a1d40afcc0da424e9ec34c6d94ddc12d679`. Tokens and CSS hashes are unchanged. Locks stay 42/36. Cap-7 and `.aziel` stay names. `public_icann` and `cap7_registrar_live` stay false. `GET /v1/mesh` never enables.
- There is no GitHub workflow here. Adding one that runs `npm test` needs a token with `workflow` scope.
