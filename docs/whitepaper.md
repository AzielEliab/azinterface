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

## QNS-CD-1.0 pair custody

Photon QNS1 vias (`lan/plc/bt/rf/light/qns/operator/local`) run in local
`qnm-node/` **qnsd** on 127.0.0.1. Interface does not transfer packets
and does not invent a Softwares-tab QNS product.

Pair handshake is AIH-WP-1.3: `OFFER → ACCEPT → SEAL`. Ops
`pair_offer` / `pair_accept` / `pair_seal` / `pair_cut` require living
presence (ON after integrity). They refuse in OFF (`PRE_LOCKED`),
FULL SHUTDOWN (`QNS-CYCLE-REFUSE`), and MEMORIAL (`AIH-CYCLE-TERMINAL`).
`pair_status` reads memorial cites in any cycle.

Witness / hold may record `pair_id` + `photon_id` cites. Vault contents
are never stored. `pair_cut` and `pair_wipe` never remotely wipe devices.
Walker restriction: unknown vias and mid-handshake via changes refuse.
Canonical: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
— summary in [QNS-CD-1.0.md](QNS-CD-1.0.md).

## LOCKED suite pipeline

Controlling design is MASTER-ARCHITECTURE-2.0. SUITE-PIPE-1.6.15 remains
the current runtime public strip and is not dropped. aziel-runtime owns
fabric hops. AZInterface is the human-facing UI — not a second FragGate
door. FragGate is THE SINGLE DOOR. LambGate is not a hop.

```
Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains;
4DMap inspection) → optional ASE → RoseClock (forward-only; StaticClock /
VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return
```

The Internal Domain Layer is 33 softwares in 11 domains after AZPIPE —
not additional doors. 4DMap inspects that layer. AZChat is stub / not
hosted yet. RoseClock is forward-only. Lamb Lens is fabric ethics.
`page_cycle_status` and `pipeline_arch` carry the cite.

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
