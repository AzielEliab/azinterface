# AZInterface — AIH-WP-1.0 (Interface custody)

**Author:** Aziel Eliab only
**Software:** AZInterface 0.1.0
**License:** Apache-2.0
**Date:** September 2026
**Authority:** Aziel Hub & Interface Combined Final — Interface sections 5–6

## Abstract

AZInterface is the **custodial operating environment**. It holds,
withdraws, and witnesses. It is not AZHub.

AZHub (sibling) is the Blank Key / spatial container. Interface is
CUSTODY. The two products share a visual schema (black background, gold
trim, white text, everblooming sigil) and must never be collapsed.

## Site states (sections 5–6)

Apps load in **pre-locked page cycles**. Interface app and module
surfaces enter through explicit locked site-state cycles before any ON
serve.

```
OFF → [integrity check] → ON
```

Additional locked postures:

- **FULL SHUTDOWN** — living presence off; cycle closed
- **MEMORIAL** — commemorative lock; living apps not served

**Pre-locked** means content does not serve or render as living
presence until the operator explicitly enables ON after integrity.
Hosted v0.1 does **not** invent cloud-asleep availability.

AZHome is the bunker browser surface. It is a module of Interface, not
a Hub room, and it does not render as living presence while the cycle
is locked.

## Genesis

One-time username seed. The Worker / engine computes a **Genesis Hash
Key** and displays the hash only. The username is discarded and never
stored. A second boot is refused (`GENESIS_ALREADY_KEYED`).

## Integrity loop

Integrity must pass in the current cycle before ON. Failure keeps the
surface pre-locked. Leaving ON closes the living cycle; ON again
requires a fresh integrity check.

## Witness

The witness list is metadata: kind, hold id, hash, timestamp. It never
includes vault contents. `vault_read` is stub.

## Hold / withdraw

These are living-presence acts. They refuse with `PRE_LOCKED` until ON
after integrity. Hosted v0.1 stores label hashes, not vault bytes.

## Scorched Earth

On the hosted Worker this is a **local stub/advisory only**.
`scorch_local` explains that no remote wipe occurs.
`scorch_remote` / `scorch` refuse. User devices are never remotely
wiped from this surface.

## Dual surface

1. Human software — Worker homepage, Flutter `mobile/`, local
   `azinterface ui`, counted `/download`.
2. Agent / MCP — FragGate only on aziel-runtime:
   `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
   with `{ slug: "azinterface", op, payload }`.

Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama,
Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence,
Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable
assistants.

Public identity is **Aziel Eliab** only.
