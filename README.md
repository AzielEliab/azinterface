# AZInterface

AZInterface is the suite shell for this computer (AIH-WP-1.0). It opens the Softwares that can run here, and it keeps custody through five sealed page cycles.

Author: Aziel Eliab · September 2026 · v0.1.0 · [Apache-2.0](LICENSE)

## Start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .
azinterface
azinterface ui
```

Open http://127.0.0.1:8880/ on this computer and press **Start suite**. AZVPN starts with the suite. AZCoherence stays in the background (Running or Quiet). TrajectoryLock opens a review that pulls satellite imagery for an event place and time. Custody (integrity and the page cycle) is under Advanced.

Forks are welcome and always allowed. How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

## Notes

v0.1.0 is a custodial shell. The page cycle is sealed. One step only:

`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`

Content does not serve as living presence until the page is ON after integrity. Integrity does not move the page to ON by itself. MEMORIAL stays in place.

Scorched Earth in this package is a local advisory. It does not wipe other devices.

Genesis takes a one-time username seed and shows a Genesis Hash Key. The username is not stored.

The witness list is metadata. Vault contents are not served.

AZHub is separate software (Blank Key) under the same FragGate door: https://github.com/AzielEliab/azhub

## LOCKED suite pipeline (cite)

Controlling design: **MASTER-33** on **aziel-runtime** (lock introduced
1.7.0). The product name is `aziel-runtime` — not a version+FragGate mash.
**FragGate is THE SINGLE DOOR.** AZInterface is the human-facing UI before
that door — not a second door and not one of the 33 domain slugs.
SUITE-PIPE-1.6.15 is historical (kept, not rolled back). No LambGate.

`Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) → Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN → DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains; 4DMap inspection frame) → optional ASE → RoseClock (forward-only; StaticClock / VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return`

Internal Domain Layer is **33 softwares in 11 domains** after AZPIPE —
isolation labels, not additional doors. Live map: Vault/Custody, Media,
Evidence, Language, AI, Research (`4dmap`), Comms (`azchat` stub / not
hosted yet), Network, System, Simulation, Core Time. 4DMap is a
Research-domain inspection frame (T/Δ/Γ/Π), not an extra door
(`domains_are_doors:false`). RoseClock is forward-only. Lamb Lens is fabric ethics
after FragGate (Peace / Clarity / Service → PASS / REFUSE / HOLD-UNCERTAIN).
Optional ASE / VECTOR / Oracle / Constellation are cite only. ZD30,
rollback, and generic truth score are absent from the core.

Worker UI paints the hop strip plus the 11-domain map. Engine / MCP:
`page_cycle_status` includes the cite; local `GET|POST /v1/pipeline_arch`
and leftover `GET|POST /v1/azpipe/arch` return the same embedded
MASTER-33 strip. Optional runtime cite is `GET /v1/fraggate` (`pipeline` /
`pipeline_strip`). Cite never depends on a missing runtime path. FragGate
is THE SINGLE DOOR — not a Softwares door. Papers: [MASTER-33](https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-33-SOFTWARE.md)
· [MASTER-ARCHITECTURE-2.0](https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/MASTER-ARCHITECTURE-2.0.md)
· [SUITE-PIPE-1.6.15](https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/SUITE-PIPE-1.6.15.md).

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
SPLIT THE WIRES (0.5–1s tip tick vs 777s pull-only gate; never share a
socket) and COLD-COPY SURVIVAL (multiply cold copies; refuse live body
sync; server pull cannot wipe cold replicas). REHEAL refuse:
isolate+local phoenix; no neighbor vote-to-fix; allowed
live/locked/isolated/tip-hash only. See
[docs/SPLIT-THE-WIRES.md](docs/SPLIT-THE-WIRES.md).
No auto-heal. Not anonymity. Anon-broadcast is not a publish path.
`GET|POST /mcp` and `/openapi.json` document those ops and **point at
FragGate** — they are not a second agent brand. `/mcp` keeps `ok: false`
/ not a product MCP. Agents use aziel-runtime FragGate/MCP; this host is
custody UI only.

Agents display `display.title`, `display.summary`, and `display.fields`
in chat, then take the next input.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants.

## Quick start

See [Start](#start). For the test tools as well: `pip install -e ".[dev]"`, then `azinterface doctor`, then `azinterface ui`.

## Install (counted tarball)

Prefer the counted tarball, then local steps. This host is custody UI only.
Agents use aziel-runtime FragGate/MCP — not a second Interface MCP.

1. Download and unpack [azinterface-0.1.0.tar.gz](https://azinterface-download-tracker.vibelock.workers.dev/download?asset=azinterface-0.1.0.tar.gz) (`tar -xzf azinterface-0.1.0.tar.gz`).
2. `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
3. `azinterface ui`, open http://127.0.0.1:8880/, and press Start suite.

After download, run `sha256sum azinterface-0.1.0.tar.gz` (or `shasum -a 256`)
and compare with a hash you trust.

### Advanced / optional: scripted installer

Review [`/install.sh`](https://azinterface-download-tracker.vibelock.workers.dev/install.sh)
before running it. Prefer writing the script to disk (not pipe-to-bash):

```bash
curl -fsSL https://azinterface-download-tracker.vibelock.workers.dev/install.sh -o install-azinterface.sh
# review install-azinterface.sh, then:
bash install-azinterface.sh
```

Pipe-to-bash (`curl … | bash`) remains available and is optional, not the
recommended path. One-click on the Worker homepage copies the tarball steps.

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
| `/mcp` | Pointer only (`ok: false`). Agents use aziel-runtime FragGate/MCP; this host is custody UI only |
| `/v1/{op}` | Human UI backend — single-segment local ops only |
| `/v1/fraggate/*` | PROXY to aziel-runtime |
| `/v1/runtime/*` | PROXY aliases (`list`/`call` → `/v1/fraggate/list`/`call`) |
| `/v1/mesh/*` | PROXY to aziel-runtime QNM-BUILD-1.0 rollup (default OFF). SPLIT THE WIRES + COLD-COPY SURVIVAL cite |
| `/v1/azpipe/arch` | Local alias of `/v1/pipeline_arch` (embedded MASTER-33; never a runtime 404) |
| `/v1/pipeline_arch` | Local frozen LOCKED hop-list cite |

- Homepage: [https://azinterface-download-tracker.vibelock.workers.dev/](https://azinterface-download-tracker.vibelock.workers.dev/)
- Direct tarball: [azinterface-0.1.0.tar.gz](https://azinterface-download-tracker.vibelock.workers.dev/download?asset=azinterface-0.1.0.tar.gz)
- Sigil: [https://www.azielcorpuslibrary.net/sigil.png](https://www.azielcorpuslibrary.net/sigil.png)
- Cite: [cite.json](https://azinterface-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). AZInterface 0.1.0 [Software]. Apache-2.0. Plain peers A–Z: AZ-CLCE, AZCoherence (`slug=azcoherence`), AZHub. Do not invent a DOI.

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
| Pipeline cite | `POST /v1/pipeline_arch` | `pipeline_arch` (embedded hop list; alias `/v1/azpipe/arch`; optional `GET /v1/fraggate`) |
| Scorched Earth local | `POST /v1/scorch_local` | `scorch_local` (advisory) |
| Remote wipe | `POST /v1/scorch_remote` | stub refuse |
| Live Nodes strip | `GET /v1/mesh/status` (proxy) | QNM-BUILD-1.0 + QNS-CD-1.0 + SPLIT THE WIRES + COLD-COPY SURVIVAL; default OFF; GET never enables |
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
azinterface call pipeline_arch
azinterface call pair_offer --payload '{"via":"local"}'
azinterface call pair_status
```

## CLI

`azinterface` with no command prints a short welcome. `azinterface --help` lists commands. Add `--json` when you want the machine JSON. The same engine objects are what agents already read.

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
azinterface pipeline
```

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
node tests/test_worker_engine.mjs
node tests/test_worker_door.mjs
node tests/test_worker_ui_mesh.mjs
node tests/test_worker_mesh_law.mjs
node tests/test_worker_pipeline.mjs
node tests/test_worker_cite.mjs
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
azinterface/          library (engine, genesis, cycle, pipeline cite, receipts, cli)
tests/                pytest + worker smoke
docs/                 AIH-WP-1.0 notes + QNS-CD-1.0 + SPLIT THE WIRES / COLD-COPY SURVIVAL
workers/download-tracker/   Cloudflare Worker azinterface-download-tracker
mobile/               Flutter scaffold
SKILL.md              agent skill (also GET /v1/skill)
```

## Cross-map (AZInterface ↔ qnm-node qnsd ↔ catalog)

| Plane | Who | Role |
|-------|-----|------|
| CUSTODY | this product (`slug=azinterface`) | Pair memorial, cycle gate, witness cites |
| VIA | local [`qnm-node/`](https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node) **qnsd** on `127.0.0.1` | QNS1 packet on lan/plc/bt/rf/light/qns/operator/local |
| CATALOG | [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) | AZInterface + QNM-BUILD-1.0 mesh rollup — not a Softwares-tab QNS card |
| FABRIC | local `qnm-node` | [SPLIT THE WIRES](docs/SPLIT-THE-WIRES.md) + COLD-COPY SURVIVAL |

Design: [docs/QNS-CD-1.0.md](docs/QNS-CD-1.0.md). Handshake is AIH-WP-1.3
(`OFFER → ACCEPT → SEAL`). Walker restriction applies. `pair_cut` is not
a remote wipe. `GET /v1/mesh` never enables. No Node Gate. No untraceable
origin claim. Fabric law: [docs/SPLIT-THE-WIRES.md](docs/SPLIT-THE-WIRES.md).

## Cross-links (optional, not required)

- Runtime: https://github.com/AzielEliab/aziel-runtime · https://aziel-runtime.vibelock.workers.dev/
- Local qnsd: https://github.com/AzielEliab/aziel-runtime/tree/main/qnm-node
- FragGate: https://github.com/AzielEliab/fraggate
- Digital Library: https://www.azielcorpuslibrary.net/
- AZ-CLCE (Plain peer of AZCoherence — Language isolation; do not merge): https://github.com/AzielEliab/az-clce
- AZCoherence (separate Softwares — AZC-WP-0.1; same FragGate door, `slug=azcoherence`; peer of AZ-CLCE; not AKM-TRIAD): https://github.com/AzielEliab/AZCoherence · Worker https://azcoherence-download-tracker.vibelock.workers.dev/ · [download](https://azcoherence-download-tracker.vibelock.workers.dev/download) · agents `fraggate_describe` / `fraggate_call`
- AZHub (separate software — Blank Key): https://github.com/AzielEliab/azhub
- godlock.uk
- https://www.azieleliab.com

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
