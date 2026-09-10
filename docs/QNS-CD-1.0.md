# QNS-CD-1.0 — Interface pair custody

**Author:** Aziel Eliab only
**Software:** AZInterface 0.1.0 (AIH-WP-1.0)
**Companion:** QNS-CD-1.0 coding design · AIH-WP-1.3 pair handshake
**License:** Apache-2.0
**Date:** September 2026

Interface is CUSTODY. This page is the Interface-side summary of QNS-CD-1.0.
It is not a Softwares-tab QNS product. Photon vias do not run on this Worker.

## Canonical process

Local **qnsd** lives in runtime `qnm-node/` and binds **127.0.0.1** only.

- Canonical tree: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
- Suite rollup (not the node): [QNM-BUILD-1.0](https://github.com/AzielEliab/aziel-runtime/blob/main/docs/NODE_MESH.md)
- Fabric concept: [QNM-WP-1.0](https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/QNM-WP-1.0.md)

AZInterface holds **pair memorial** (pair_id + photon_id cites). Local qnsd
moves **QNS1** packets. aziel-runtime catalogs AZInterface (`slug=azinterface`)
and the suite mesh rollup (`slug=mesh`). It does not invent a QNS catalog card.

## What this is / is not

| This is | This is not |
| --- | --- |
| Pair custody aligned with QNS-CD §19 | A Softwares-tab QNS product |
| AIH-WP-1.3 handshake: OFFER → ACCEPT → SEAL | A skippable or invented handshake |
| Memorial cites (`pair_id`, `photon_id`) | Vault contents, usernames, or packet bytes |
| Walker-restricted via cite | Interface-run lan/plc/bt/rf/light/qns hops |
| Living-presence ops at ON after integrity | Pair mutate in OFF / FULL SHUTDOWN / MEMORIAL |
| `pair_cut` as a clean dissolve | Remote wipe / Scorched Earth |
| Default mesh OFF (QNM-BUILD-1.0) | Node Gate, GET-enable, untraceable origin |

## Photon QNS1 (via plane)

QNS1 packets transfer across sealed vias:

`lan · plc · bt · rf · light · qns · operator · local`

**Walker restriction:** a walker may not invent a via, hop off the sealed
list, or skip handshake steps. Via execution is **local qnsd** (127.0.0.1).
Interface records the via name as a cite. It does not claim the packet
moved, hide origin, or serve payload bytes.

Default via is `local` (loopback qnsd). Unknown via names refuse
`QNS-VIA-UNKNOWN`. A via change mid-handshake refuses `QNS-WALKER-RESTRICT`.

## Pair handshake (AIH-WP-1.3)

Sealed order, one step only:

```
OFFER → ACCEPT → SEAL
```

`CUT` dissolves a living pair (OFFER / ACCEPT / SEAL). It is not a remote
wipe and never stores vault contents. Handshake skip refuses
`QNS-HANDSHAKE-LOCKED`.

## §19 pair custody ops (this product)

Names match existing Interface style (`hold`, `site_state_set`, …):

| op | Handshake | Cycle gate |
|----|-----------|------------|
| `pair_offer` | create OFFER | living presence only (ON after integrity) |
| `pair_accept` | OFFER → ACCEPT | living presence only |
| `pair_seal` | ACCEPT → SEAL | living presence only |
| `pair_cut` | dissolve → CUT | living presence only |
| `pair_status` | read memorial | always (metadata only) |

`hold` / `witness_list` may attach `pair_id` + `photon_id` cites. Witness
rows never include vault contents.

Site cycles stay sealed and unchanged:

```
OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL
```

- **OFF / integrity** — pair mutate refuses `PRE_LOCKED`
- **ON** (after integrity) — living pair ops
- **FULL SHUTDOWN** — pair mutate refuses `QNS-CYCLE-REFUSE`
- **MEMORIAL** — pair mutate refuses `AIH-CYCLE-TERMINAL`; memorial cites remain readable

`pair_wipe` / remote scorch stay stub. `scorch_local` remains advisory only.

## Cross-map

| Plane | Who | What |
|-------|-----|------|
| CUSTODY | AZInterface (`slug=azinterface`) | Pair memorial, cycle gate, witness cites |
| VIA | local `qnm-node/` **qnsd** on 127.0.0.1 | QNS1 packet transfer on sealed vias |
| CATALOG | aziel-runtime | AZInterface + QNM-BUILD-1.0 mesh rollup |

```
AZInterface pair_*  ←memorial cites→  qnm-node qnsd (127.0.0.1)
        ↑
        FragGate slug=azinterface
        (not a second MCP; not a QNS Softwares-tab card)
```

`GET /v1/mesh` never enables radios. Live Nodes strip cites QNS-CD-1.0 and
QNM-BUILD-1.0. No Node Gate. No untraceable-origin claim.

## Agent path

Same door as every other Interface op:

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azinterface","op":"pair_status","payload":{}}'
```

Human chrome uses this Worker `/v1/pair_*`. Display `display.title`,
`display.summary`, and `display.fields`, then take the next input.

Public identity is **Aziel Eliab** only.
