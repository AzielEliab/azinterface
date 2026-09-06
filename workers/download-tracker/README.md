# AZInterface download tracker

Cloudflare Worker `azinterface-download-tracker`.

URL pattern after deploy (workers.dev + account subdomain, same as sibling products):

`https://azinterface-download-tracker.vibelock.workers.dev`

- `GET /` — complete pre-locked custody UI (site state / genesis / integrity / witness / AZHome) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /v1/*` — custody ops (does **not** increment downloads)

KV binding `DOWNLOADS` (create `AZINTERFACE_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`. Placeholder KV id is OK until first deploy.

Human UI is this Worker. Agent / MCP path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with
`{"slug":"azinterface","op":"…","payload":{}}`. There is no separate Interface MCP
on this host (`POST /mcp` returns a pointer).

Interface is CUSTODY. AZHub is separate software under the one FragGate
door — never collapse them.
Scorched Earth is a local stub/advisory only. Never a remote wipe.

Author: Aziel Eliab. Apache-2.0.
