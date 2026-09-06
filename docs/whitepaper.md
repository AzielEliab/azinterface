# AZInterface — AIH-WP-1.0 (Interface custody)

**Author:** Aziel Eliab only
**Software:** AZInterface 0.1.0
**License:** Apache-2.0
**Date:** September 2026
**Authority:** Aziel Hub & Interface Combined Final — Interface sections 5–6

## Abstract

AZInterface is the **custodial operating environment**. It holds,
withdraws, and witnesses. It is not AZHub.

AZHub is **separate software** (Blank Key / spatial container) under the
one FragGate door. Interface is CUSTODY. The two products share a visual
schema (black background, gold trim, white text, everblooming sigil)
and must never be collapsed into one product.

## Site states (sections 5–6)

Apps load in **five pre-locked page cycles**. Order is sealed at genesis.
One step only. No skip. No invented cycle. No auto-unlock.

```
OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL
```

- **OFF** — default locked posture
- **integrity** — check recorded; does not auto-unlock ON
- **ON** — living presence; requires a passing integrity check
- **FULL SHUTDOWN** — living presence off; next sealed step after ON
- **MEMORIAL** — commemorative lock; terminal

**Pre-locked** means content does not serve or render as living
presence until the operator explicitly enables ON after integrity.
Hosted v0.1 does **not** invent cloud-asleep availability.

AZHome is the bunker browser surface. It is a module of Interface, not
a Hub room, and it does not render as living presence while the cycle
is locked.

## Genesis

Genesis seals the five page cycles. A one-time username seed may also
compute a **Genesis Hash Key** (hash only). The username is discarded
and never stored. A second boot is refused (`GENESIS_ALREADY_KEYED`).

## Integrity loop

`integrity_check` from OFF advances to **integrity**. It does not
auto-unlock ON. `site_state_set` to ON from integrity requires
`integrity_ok`. Skip / invent / auto-unlock refuse
(`AIH-CYCLE-LOCKED` / `AIH-AUTO-UNLOCK-REFUSE`).

## Witness

The witness list is metadata: kind, hold id, hash, timestamp. It never
includes vault contents and is not a ranking. `vault_read` is stub.

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
2. Agent / MCP — one FragGate door on aziel-runtime:
   `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
   with `{ slug: "azinterface", op, payload }`.

Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama,
Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence,
Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable
assistants.

Public identity is **Aziel Eliab** only.
