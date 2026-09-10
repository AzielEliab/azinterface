# AZInterface download tracker

Cloudflare Worker `azinterface-download-tracker`.

URL pattern after deploy (workers.dev + account subdomain, same as sibling products):

`https://azinterface-download-tracker.vibelock.workers.dev`

- `GET /` — complete pre-locked custody UI (site state / genesis / integrity / witness / AZHome) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /v1/*` — custody ops (does **not** increment downloads)
- `GET|POST /v1/mesh/*` — PROXY to aziel-runtime QNM-BUILD-1.0 rollup (default OFF)
- `GET /v1/fraggate` — PROXY to aziel-runtime FragGate door (MASTER-33 `pipeline` / `pipeline_strip`)
- `GET|POST /v1/azpipe/arch` — local alias of `pipeline_arch` (embedded MASTER-33; not a Softwares door)
- `GET|POST /v1/pipeline_arch` — local frozen LOCKED hop-list cite; optional runtime FragGate strip when live

KV binding `DOWNLOADS` (create `AZINTERFACE_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.
**Parent-deploy note:** `wrangler.toml` still has the `0000…` placeholder KV id.
A real production id was not in comments/README. Parent must create the
namespace and replace the id before deploy. Do not invent an id.

Human UI includes a **LOCKED pipeline** strip (MASTER-33 on aziel-runtime;
FragGate is THE SINGLE DOOR; Internal Domain Layer 33/11 isolation labels
with 4DMap inspection; no LambGate) plus the 11-domain
map, and a **Live Nodes** strip (QNM-BUILD-1.0)
live|locked|isolated + QNS-CD-1.0 cite). Radios stay off until runtime
enable. `GET /v1/mesh` never enables. QNS-CD-1.0 photon vias run in local
`qnm-node/` qnsd (127.0.0.1); this Worker holds pair memorial cites only.
AIH-WP-1.3 spiderweb is local `qnm-node/` — this Worker does not invent a
public Node Gate. No auto-heal. Not anonymity. Anon-broadcast is not a
publish path. Not a Softwares-tab QNS product.

Human UI is this Worker. Agent / MCP path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with
`{"slug":"azinterface","op":"…","payload":{}}`. There is no separate Interface MCP
on this host (`POST /mcp` returns a pointer).

Interface is CUSTODY. AZHub is separate software under the one FragGate
door — never collapse them.
Scorched Earth is a local stub/advisory only. Never a remote wipe.

Author: Aziel Eliab. Apache-2.0.
