# AZBot Node Collaborative Forensic Design 1.0 — AZInterface tether

Author: Aziel Eliab. October 2026. Apache-2.0.

This file is the AZInterface side of Design 1.0. AZBot owns the azbot repository. A Softwares OVERRIDE is a separate change. This tether does not rewrite the public FragGate contract.

## Role

AZInterface is the local control surface and the pre-locked page cycles.

`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`

One step only. No skip. Living presence is ON after integrity. The handoff to AZBot is admitted only then. FULL SHUTDOWN refuses a new handoff. MEMORIAL is terminal. Tip read stays available. The cycle is not advanced by this tether.

## Local handoff

AZBot runs at `127.0.0.1`. Interface does not open that socket and does not open a public port. On the loopback desk (`http://127.0.0.1:8880`):

- `GET /v1/forensic/handoff` reports whether the sealed cycle admits a handoff.
- `POST /v1/forensic/handoff` with `{slug, op, payload}` returns a FragGate package. `executed` stays false. The package names `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`. AZBot sends it. Interface does not.

A host other than `127.0.0.1` / `localhost` is `AZBOT-BIND-LOOPBACK`.

## Multi-party tips

`GET /v1/forensic/tip` and `GET /v1/forensic/session` share the tip hash, `prev`, `seq`, and party labels.

`POST /v1/forensic/session` appends a tip only at ON after integrity. The first tip links to 64 zeroes. The next tip's `prev` must be the current tip. A different tip with another `prev`, or `rewrite: true`, is `TIP-REWRITE-REFUSED`. Payloads and usernames are not stored.

The public worker stores no session. Its GET returns an empty tip list. Its POST returns `LOCAL-DESK-ONLY`.

## AzielTether under bearer

`GET` or `POST /v1/azieltether` without an operator bearer returns `MESH-NEED-BEARER` and `exposed: false`. With a bearer it cites AzielTether (`slug=azieltether`, door `fraggate`) plus the existing `AZRT-AZOS-TETHER-1.0` name and external anchors as cites. The bearer is not stored and not returned. `mesh_enabled` stays false. `GET /v1/mesh` is unchanged and still never enables.

## Single door

These paths are not FragGate door prefixes and not catalog LIVE ops. Agents still use one call:

`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with `slug=azinterface`.

## Remain-OFF

Mesh auto-enable, AZ-OS public exec, vault destructive ops, deanonymize, invent_mark, backdate, and public rollback stay refused. Cap-7 and `.aziel` stay names (`MG-NO-IP-EXIT`). They are not ICANN or BGP.

## Code

- Local desk: `azinterface/forensic_session.py`, routes in `azinterface/ui.py`
- Public cite: `workers/download-tracker/src/forensic-tether.js`, wired from `src/entry.js`
