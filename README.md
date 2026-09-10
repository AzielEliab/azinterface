# AZInterface

Open-source **custodial operating environment** — AIH-WP-1.0.
Hold / withdraw / witness. Pre-locked page cycles. Not AZHub.

**Author:** Aziel Eliab only
**Date:** September 2026 · v0.1.0
**License:** [Apache-2.0](LICENSE)
**Spec:** Aziel Hub & Interface Combined Final — Interface sections 5–6

> Interface is CUSTODY. Never collapse into Hub.

How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

AZHub is **separate software** (Blank Key / spatial container) under the
one FragGate door. Do not rebuild it here: https://github.com/AzielEliab/azhub

## Honest scope (read this)

v0.1 is a **custodial shell**. Apps load in **five pre-locked page
cycles**. Order is sealed. One step only. No skip. No invented cycle:

`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`

Pre-locked means content does not serve or render as living presence
until the operator explicitly enables ON after integrity. Integrity
does **not** auto-unlock ON. MEMORIAL is terminal. This Worker does
**not** invent cloud-asleep availability.

Scorched Earth on the hosted Worker is a **local stub/advisory only**.
It never remotely wipes user devices.

Genesis boot takes a one-time username seed and displays a **Genesis
Hash Key** (hash only). The username is never stored.

Witness list is metadata only. Vault contents are never served.

## Dual surface (mandatory)

1. **Human UI** — Worker homepage is complete software: site-state
   buttons, genesis boot, integrity, witness list, withdraw, AZHome
   bunker (locked until ON), counted download. Black / gold / white.
   Humans stay here.
2. **Agent / MCP — FragGate only.** There is no separate AZInterface MCP
   outside the door. Catalog door:

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azinterface","op":"page_cycle_status","payload":{}}'
```

MCP clients already on aziel-runtime call `fraggate_call` with
`slug=azinterface`. Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.
AZHub and AZInterface are separate software under that one door.

Worker `/v1/{op}` is the **human UI backend** (single-segment local ops).
`/v1/fraggate/*`, `/v1/runtime/*`, and `/v1/mesh/*` **PROXY** to
aziel-runtime (`AZIEL_RUNTIME` or HTTPS). Suite mesh is QNM-BUILD-1.0
rollup (live|locked|isolated); default OFF until runtime enable.
`GET /v1/mesh` never enables. QNS-CD-1.0 photon vias run in local
`qnm-node/` **qnsd** (127.0.0.1). Interface holds pair memorial cites —
not a Softwares-tab QNS product. AIH-WP-1.3 spiderweb is local
`qnm-node/` — not a public Node Gate.
No auto-heal. Not anonymity. Anon-broadcast is not a publish path.
`GET|POST /mcp` and `/openapi.json` document those ops and **point at
FragGate** — they are not a second agent brand.

Agents display `display.title`, `display.summary`, and `display.fields`
in chat, then take the next input.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
azinterface doctor
azinterface ui
```

Open http://127.0.0.1:8880 (loopback only).

## One-click install

```bash
curl -fsSL https://azinterface-download-tracker.vibelock.workers.dev/install.sh | bash
```

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

Worker name: `azinterface-download-tracker`

URL pattern (same as sibling Aziel Eliab products):

`https://azinterface-download-tracker.vibelock.workers.dev`

| Path | What |
|------|------|
| `/` | Complete pre-locked custody UI + views |
| `/download` | Counted tarball |
| `/count` | `{views, downloads, total}` |
| `/openapi.json` | OpenAPI 3.1 (docs; agents use FragGate) |
| `/mcp` | Pointer to FragGate (`slug=azinterface`) |
| `/v1/{op}` | Human UI backend — single-segment local ops only |
| `/v1/fraggate/*` | PROXY to aziel-runtime FragGate door |
| `/v1/runtime/*` | PROXY aliases (`list`/`call` → `/v1/fraggate/list`/`call`) |
| `/v1/mesh/*` | PROXY to aziel-runtime QNM-BUILD-1.0 rollup (default OFF) |

- Homepage: [https://azinterface-download-tracker.vibelock.workers.dev/](https://azinterface-download-tracker.vibelock.workers.dev/)
- Direct tarball: [azinterface-0.1.0.tar.gz](https://azinterface-download-tracker.vibelock.workers.dev/download?asset=azinterface-0.1.0.tar.gz)
- Sigil: [https://www.azielcorpuslibrary.net/sigil.png](https://www.azielcorpuslibrary.net/sigil.png)
- Cite: [cite.json](https://azinterface-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). AZInterface 0.1.0 [Software]. Apache-2.0. Do not invent a DOI.

Isolated counter: Worker `azinterface-download-tracker`, KV `AZINTERFACE_DOWNLOADS`. `/v1` and `/mcp` do not increment downloads.

## Chrome button checklist

Every control calls a real `/v1` handler (same op agents call). No dead buttons.

| Button | Handler | Op |
|--------|---------|-----|
| ON | `POST /v1/site_state_set` | `site_state_set` (next after integrity) |
| OFF | `POST /v1/site_state_set` | `site_state_set` (no-op at OFF; skip otherwise) |
| FULL SHUTDOWN | `POST /v1/site_state_set` | `site_state_set` (next after ON) |
| MEMORIAL | `POST /v1/site_state_set` | `site_state_set` (next after FULL SHUTDOWN; terminal) |
| Integrity | `POST /v1/integrity_check` | `integrity_check` |
| Genesis boot | `POST /v1/genesis_boot` | `genesis_boot` |
| Genesis status | `POST /v1/genesis_status` | `genesis_status` |
| Hold | `POST /v1/hold` | `hold` |
| Withdraw | `POST /v1/withdraw` | `withdraw` |
| Witness list | `POST /v1/witness_list` | `witness_list` |
| Cycle | `POST /v1/page_cycle_status` | `page_cycle_status` |
| Scorched Earth local | `POST /v1/scorch_local` | `scorch_local` (advisory) |
| Remote wipe | `POST /v1/scorch_remote` | stub refuse |
| Live Nodes strip | `GET /v1/mesh/status` (proxy) | QNM-BUILD-1.0 + QNS-CD-1.0 cite; default OFF; GET never enables |
| Offer | `POST /v1/pair_offer` | `pair_offer` (ON after integrity) |
| Accept | `POST /v1/pair_accept` | `pair_accept` |
| Seal | `POST /v1/pair_seal` | `pair_seal` |
| Cut | `POST /v1/pair_cut` | `pair_cut` (dissolve; not a remote wipe) |
| Pair status | `POST /v1/pair_status` | `pair_status` (memorial cites) |

Prove locally (after `pip install -e ".[dev]"`):

```bash
azinterface doctor
azinterface call integrity_check
azinterface call site_state_set --payload '{"state":"ON"}'
azinterface call genesis_boot --payload '{"username":"seed"}'
azinterface call witness_list
azinterface call page_cycle_status
azinterface call pair_offer --payload '{"via":"local"}'
azinterface call pair_status
```

## CLI

```bash
azinterface version
azinterface ui                 # 127.0.0.1:8880
azinterface doctor
azinterface genesis 'seed'
azinterface integrity
azinterface state-set ON
azinterface hold --label demo
azinterface pair-offer --via local
azinterface pair-accept
azinterface pair-seal
azinterface pair-status
azinterface pair-cut
azinterface witness
azinterface withdraw
```

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
node tests/test_worker_engine.mjs
node tests/test_worker_door.mjs
node tests/test_worker_ui_mesh.mjs
azinterface doctor
```

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.azinterface`.
Offline. No analytics. Dark matte / gold.

```bash
cd mobile
flutter create --org com.azieeliab --project-name azinterface .
flutter pub get
flutter run
```

## Layout

```
azinterface/          library (engine, genesis, cycle, receipts, cli)
tests/                pytest + worker smoke
docs/                 AIH-WP-1.0 notes + QNS-CD-1.0 Interface summary
workers/download-tracker/   Cloudflare Worker azinterface-download-tracker
mobile/               Flutter scaffold
SKILL.md              agent skill (also GET /v1/skill)
```

## Cross-map (AZInterface ↔ qnm-node qnsd ↔ catalog)

| Plane | Who | Role |
|-------|-----|------|
| CUSTODY | this product (`slug=azinterface`) | Pair memorial, cycle gate, witness cites |
| VIA | local [`qnm-node/`](https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node) **qnsd** on `127.0.0.1` | QNS1 packet on lan/plc/bt/rf/light/qns/operator/local |
| CATALOG | [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) FragGate | AZInterface + QNM-BUILD-1.0 mesh rollup — not a Softwares-tab QNS card |

Design: [docs/QNS-CD-1.0.md](docs/QNS-CD-1.0.md). Handshake is AIH-WP-1.3
(`OFFER → ACCEPT → SEAL`). Walker restriction applies. `pair_cut` is not
a remote wipe. `GET /v1/mesh` never enables. No Node Gate. No untraceable
origin claim.

## Cross-links (optional, not required)

- Runtime: https://github.com/AzielEliab/aziel-runtime · https://aziel-runtime.vibelock.workers.dev/
- Local qnsd: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
- FragGate: https://github.com/AzielEliab/fraggate
- Digital Library: https://www.azielcorpuslibrary.net/
- AZHub (separate software — Blank Key): https://github.com/AzielEliab/azhub
- godlock.uk
- https://www.azieleliab.com

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
