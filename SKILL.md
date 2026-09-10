---
name: AZInterface
description: >-
  Use when operating AZInterface (AIH-WP-1.0) custody — hold / withdraw /
  witness, pre-locked page cycles, genesis keying, integrity, AZHome,
  QNS-CD-1.0 pair memorial (offer/accept/seal/cut). Interface is CUSTODY.
  Never collapse into Hub. Author Aziel Eliab.
---

# AZInterface

Custodial operating environment (AIH-WP-1.0). Hold / withdraw / witness.
AZHome bunker browser surface. Genesis one-time keying. Integrity loop.
Witness list (no vault contents). Scorched Earth is a **local stub/advisory
only** on the hosted Worker — never a remote wipe of user devices.

Author: **Aziel Eliab** only.

**THIS IS:** Interface custody. Five pre-locked page cycles
(`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`). One step only.
No skip. No invented cycle. No auto-unlock.

**THIS IS NOT:** AZHub (separate software — Blank Key / spatial container —
https://github.com/AzielEliab/azhub). Never collapse Interface into Hub.
Never a combined hub+interface product. Not a vault dump. Not a remote wipe
service. Not a separate FragGate door.

Always send `User-Agent: Mozilla/5.0`.

**Agent path is the one FragGate door.** MCP / agents call aziel-runtime —
not a second Interface MCP brand. AZHub and AZInterface are separate
software under that door.

```
POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call
{"slug":"azinterface","op":"<op>","payload":{}}
```

Same door as MCP `fraggate_call` (`slug=azinterface`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog is live. Human chrome uses
this Worker `/v1/{op}` (single-segment local ops only). `/v1/fraggate/*`,
`/v1/runtime/*`, and `/v1/mesh/*` PROXY to aziel-runtime (`AZIEL_RUNTIME`
or HTTPS). Suite mesh is QNM-BUILD-1.0 rollup (live|locked|isolated);
default OFF until runtime enable. `GET /v1/mesh` never enables.
QNS-CD-1.0 photon vias run in local `qnm-node/` **qnsd** (127.0.0.1).
Interface holds pair memorial cites only — not a Softwares-tab QNS
product. AIH-WP-1.3 spiderweb is local `qnm-node/` — not a public
Node Gate. No auto-heal. Not anonymity. Anon-broadcast is not a
publish path. `GET|POST /mcp` here is a pointer, not a second MCP.

**Human UI stays on this Worker.** AI path is FragGate + this OpenAPI.

## Catalog LIVE ops (FragGate)

| op | What |
|----|------|
| `health` | Liveness. Does not increment downloads. |
| `skill` | This markdown. |
| `genesis_status` | Cycle seal + optional one-time hash. Username never stored. |
| `site_state_get` | Current cycle: OFF / integrity / ON / FULL SHUTDOWN / MEMORIAL. |
| `site_state_set` | Advance one sealed step only. ON requires integrity. |
| `integrity_check` | Records integrity. Advances OFF → integrity. Does not auto-unlock ON. |
| `witness_list` | Witness metadata. Never vault contents. Never a ranking. |
| `page_cycle_status` | Pre-locked cycle. Living presence only at ON. Includes LOCKED pipeline cite. |

## LOCKED suite pipeline (cite)

Runtime owns fabric hops. Interface cites the frozen list — not a Softwares-tab
product. No LambGate.

`PUBLIC/UI/Agents → FragGate → SweepGate → ChainLock-IN → DecisionGATE → AZPIPE → Domain Doors (incl. 4DMap inspection) → TemporalLock → StaticClock → ChainLock-OUT → Response/Receipt`

4DMap (`slug=4dmap`, 4DM-WP-1.0) is Domain Door inspection after AZPIPE —
not a sequential gate. Papers live on aziel-runtime (AP-WP-0.2 / SG-WP-0.1 /
CL-WP-0.4 / 4DM-WP-1.0). Local op `pipeline_arch` returns the same cite.

## Local Worker extras (human UI `/v1`)

`genesis_boot` · `hold` · `withdraw` · `scorch_local` · `pipeline_arch` ·
`pair_offer` · `pair_accept` · `pair_seal` · `pair_cut` · `pair_status`

## QNS-CD-1.0 cross-map

Canonical qnsd: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
(bind `127.0.0.1`). Design summary: `docs/QNS-CD-1.0.md`.

| Plane | Who | What |
|-------|-----|------|
| CUSTODY | AZInterface | Pair memorial (`pair_id` + `photon_id` cites) |
| VIA | local qnsd | QNS1 packet on lan/plc/bt/rf/light/qns/operator/local |
| CATALOG | aziel-runtime | `slug=azinterface` + QNM-BUILD-1.0 mesh rollup |

Handshake is AIH-WP-1.3: `OFFER → ACCEPT → SEAL`. Walker restriction
applies. Pair mutate only at ON after integrity. `pair_status` reads
memorial in any cycle. `pair_cut` is a dissolve — not a remote wipe.
Do not invent a Softwares-tab QNS product. Do not claim untraceable
origin. `GET /v1/mesh` never enables. No Node Gate.

`hold` / `witness_list` may record `pair_id` + `photon_id` cites.
Vault contents are never stored.

## Stub (refuse)

`scorch_remote` / `scorch` / `pair_wipe` / `auto_unlock` / `unlock` /
`ranking` / `rank` / `completeness_detect` / `complete` / `completeness` /
`skip_cycle` / `invent_cycle` / `deanonymize` / `vault_read`

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants — **through FragGate only**.

Agents display `display.title`, `display.summary`, and
`display.fields` in chat, then take the next input.

## How to call

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azinterface","op":"page_cycle_status","payload":{}}'
curl -s -A 'Mozilla/5.0' -X POST https://azinterface-download-tracker.vibelock.workers.dev/v1/integrity_check \
  -H 'content-type: application/json' -d '{}'
curl -s -A 'Mozilla/5.0' https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list
```

Apache-2.0. Forks are welcome and always allowed.
