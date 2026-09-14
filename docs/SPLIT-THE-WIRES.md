# SPLIT THE WIRES + COLD-COPY SURVIVAL

**Author:** Aziel Eliab only
**Software:** AZInterface 0.1.0 (AIH-WP-1.0)
**Companion:** QNM-BUILD-1.0 rollup · QNS-CD-1.0 pair custody · NODE-OPS-1.0 phoenix
**License:** Apache-2.0
**Date:** September 2026

Interface is CUSTODY. This page is the Interface-side mesh fabric law.
The hosted Worker cites and encodes it. Local `qnm-node` executes it.
This is not a Softwares-tab product and not a public Node Gate.

## SPLIT THE WIRES

Two planes. Never one socket.

| Plane | Socket | Cadence | What moves |
| --- | --- | --- | --- |
| Tip | `tip-tick-1s` | Fast 0.5–1s | Presence + tip hash only, fixed-size |
| Payload | `gate-777` | 777s dwell after a valid cite | Pull-only. Never push. Never live-body sync |

Locked clauses:

- Fast **0.5–1s** tip tick is **presence + tip hash only**, **fixed-size**.
- Payload is a **pull-only second plane**.
- **Update = proof, not a timer.** Cite `prev` + lockset, **fail-closed**.
  **777s dwell** after a valid cite. **Clock desync ≠ yes.** **Ambiguous = isolate.**
- **Equivocation ends the peer.**
- **Emit last locally.**
- **Phoenix local only** (no controller hunt).
- **Partition: no auto-splice.**
- **Heartbeat loss ≠ poison ≠ apply last packet.**
- The **1s loop** and the **777s gate never share a socket.**

Refuse codes: `STW-SOCKET-SHARED`, `STW-TIP-PAYLOAD`, `STW-UPDATE-FAIL-CLOSED`,
`STW-CLOCK-DESYNC`, `STW-AMBIGUOUS-ISOLATE`, `STW-GATE-DWELL`,
`STW-EQUIVOCATION`, `STW-PHOENIX-HUNT-REFUSE`, `STW-NO-AUTO-SPLICE`.

The hosted Live Nodes strip paints suite rollup only. It does not run the
fabric 1s loop against the public proxy. Fabric sockets stay split.

## COLD-COPY SURVIVAL

Keep SPLIT THE WIRES. Survival is a second law on the same fabric.

- **Multiply cold copies.**
- **Refuse live body sync.**
- **Tip is expensive to erase** (not a cheap timer overwrite).
- **Server pull cannot wipe cold replicas.**
- **Hash-absolute poison refuse** (bad hash is not interpreted).
- **Data outlives creators.**

Refuse codes: `CCS-LIVE-BODY-SYNC-REFUSE`, `CCS-COLD-WIPE-REFUSE`,
`CCS-POISON-REFUSE`.

## REHEAL refuse

Keep SPLIT THE WIRES and COLD-COPY SURVIVAL. Reheal is refused.

- **Isolate + local phoenix** (no controller hunt, no remote phoenix).
- **No neighbor vote-to-fix.**
- Allowed surface tokens: **live / locked / isolated / tip-hash only.**

Refuse codes: `REHEAL-REFUSE`, `REHEAL-VOTE-REFUSE`, `REHEAL-SURFACE-REFUSE`.

A GET of `/v1/mesh` never enables radios and never wipes a cold replica.
Scorched Earth on this Worker stays a local stub/advisory only.

## Cross-map

| Plane | Who | What |
| --- | --- | --- |
| CUSTODY | AZInterface (`slug=azinterface`) | Pair memorial, Live Nodes cite, this law |
| VIA | local `qnm-node/` **qnsd** on 127.0.0.1 | QNS1 packet transfer |
| FABRIC | local `qnm-node` | Tip tick + 777s gate on split sockets |
| CATALOG | aziel-runtime | `slug=mesh` QNM-BUILD-1.0 rollup |

```
AZInterface Live Nodes  ←cite only→  qnm-node (127.0.0.1)
        ↑
        FragGate slug=azinterface
        (not a second MCP; not a Node Gate)
```

Public identity is **Aziel Eliab** only.
