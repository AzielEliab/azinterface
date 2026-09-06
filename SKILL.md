---
name: AZInterface
description: >-
  Use when operating AZInterface (AIH-WP-1.0) custody — hold / withdraw /
  witness, pre-locked page cycles, genesis keying, integrity, AZHome.
  Interface is CUSTODY. Never collapse into Hub. Author Aziel Eliab.
---

# AZInterface

Custodial operating environment (AIH-WP-1.0). Hold / withdraw / witness.
AZHome bunker browser surface. Genesis one-time keying. Integrity loop.
Witness list (no vault contents). Scorched Earth is a **local stub/advisory
only** on the hosted Worker — never a remote wipe of user devices.

Author: **Aziel Eliab** only.

**THIS IS:** Interface custody. Pre-locked page cycles
(`OFF → [integrity check] → ON`, plus FULL SHUTDOWN and MEMORIAL).

**THIS IS NOT:** AZHub (Blank Key / spatial container — sibling
https://github.com/AzielEliab/azhub). Never collapse Interface into Hub.
Not a vault dump. Not a remote wipe service.

Always send `User-Agent: Mozilla/5.0`.

**Agent path is FragGate only.** MCP / agents call aziel-runtime — not a
separate Interface MCP brand.

```
POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call
{"slug":"azinterface","op":"<op>","payload":{}}
```

Same door as MCP `fraggate_call` (`slug=azinterface`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog listing lands in a
sibling aziel-runtime PR. Human chrome uses this Worker `/v1/{op}`
(single-segment local ops only). `/v1/fraggate/*` and `/v1/runtime/*`
PROXY to aziel-runtime. `GET|POST /mcp` here is a pointer, not a second MCP.

**Human UI stays on this Worker.** AI path is FragGate + this OpenAPI.

## Safe LIVE ops

| op | What |
|----|------|
| `health` | Liveness. Does not increment downloads. |
| `skill` | This markdown. |
| `genesis_status` | Whether one-time keying ran. Hash only. |
| `genesis_boot` | One-time username seed → Genesis Hash Key. Never stores username. |
| `site_state_get` | OFF / ON / FULL_SHUTDOWN / MEMORIAL. |
| `site_state_set` | Set site state. ON requires integrity. |
| `integrity_check` | Integrity loop. Required before ON. |
| `witness_list` | Witness metadata. Never vault contents. |
| `page_cycle_status` | Pre-locked cycle. Living presence only after ON. |
| `hold` / `withdraw` | Custody acts. Living presence only. |
| `scorch_local` | Local advisory. Not a remote wipe. |

## Stub (refuse)

`scorch_remote` / `scorch` / `deanonymize` / `vault_read`

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
