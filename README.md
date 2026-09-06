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
`/v1/fraggate/*` and `/v1/runtime/*` **PROXY** to aziel-runtime.
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

Prove locally (after `pip install -e ".[dev]"`):

```bash
azinterface doctor
azinterface call integrity_check
azinterface call site_state_set --payload '{"state":"ON"}'
azinterface call genesis_boot --payload '{"username":"seed"}'
azinterface call witness_list
azinterface call page_cycle_status
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
azinterface witness
azinterface withdraw
```

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
node tests/test_worker_engine.mjs
node tests/test_worker_door.mjs
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
docs/                 AIH-WP-1.0 notes
workers/download-tracker/   Cloudflare Worker azinterface-download-tracker
mobile/               Flutter scaffold
SKILL.md              agent skill (also GET /v1/skill)
```

## Cross-links (optional, not required)

- Runtime: https://github.com/AzielEliab/aziel-runtime · https://aziel-runtime.vibelock.workers.dev/
- FragGate: https://github.com/AzielEliab/fraggate
- Digital Library: https://www.azielcorpuslibrary.net/
- AZHub (separate software — Blank Key): https://github.com/AzielEliab/azhub
- godlock.uk
- https://www.azieleliab.com

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
