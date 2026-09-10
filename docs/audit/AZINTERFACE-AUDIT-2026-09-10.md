# AZInterface Worker audit — 2026-09-10

**Product:** AZInterface (AIH-WP-1.0) — custodial operating environment  
**Identity:** Aziel Eliab only  
**Scope:** Hosted Worker `azinterface-download-tracker` after Pipeline cite
hardening ([PR #7](https://github.com/AzielEliab/azinterface/pull/7): local
MASTER-33 on `pipeline_arch` and leftover `/v1/azpipe/arch`)  
**Tree:** `main` @ `2a26684` (merge of PR #7)  
**Live hosts checked (read-only, User-Agent `Mozilla/5.0`):**

- `https://azinterface-download-tracker.vibelock.workers.dev`
- `https://aziel-runtime.vibelock.workers.dev`

**Method:** Source read of `workers/download-tracker/src/{door,runtime,pipeline,engine,mesh,ui,index}.js`,
Python twin (`azinterface/{engine,pipeline}.py`), Worker + pytest coverage,
FragGate `list → describe → call` (`slug=azinterface`), and live GET/POST of
cite / mesh / OpenAPI / `/mcp` / stub ops.  
**Deploy:** none. This PR is the audit document only. No hard FAIL required a
code fix.

**Overall:** **PASS with WARN.** Zero **FAIL**.

FragGate remains THE SINGLE DOOR. AZInterface is custody / page-cycle UI, not
a second door. Lamb Lens is after FragGate. `GET /v1/mesh` never enables.

---

## Scorecard

| # | Item | Result |
|---|------|--------|
| 1 | Door classification (`/v1/azpipe/arch` local; `/mcp` pointer) | **PASS** (WARN leftover `/v1/azpipe`) |
| 2 | MASTER-33 strip (FragGate first, Lamb Lens after, 33/11, 4DMap, AZChat stub) | **PASS** (WARN hop-id cardinality vs runtime `inbound[]`) |
| 3 | Custody: MEMORIAL terminal refuse + cycle safety | **PASS** (WARN shared isolate / persist) |
| 4 | Proxy surfaces to aziel-runtime; GET mesh never enables | **PASS** (WARN leftover azpipe prefix + UI auto-join-if-on) |
| 5 | OpenAPI lists destructive stubs that refuse; no secret leakage | **PASS** (WARN OpenAPI “FragGate op” copy) |
| 6 | UI / JSON dump growth / `curl \| bash` install optics | **WARN** |
| 7 | Dual surface: human Worker UI + agent via FragGate only | **PASS** (WARN catalog allowlist vs Worker extras) |

---

## 1. Door classification — PASS

PR #7’s contract holds in source and on the live Worker.

| Path | Classification | Evidence |
|------|----------------|----------|
| `GET\|POST /v1/pipeline_arch` | local `pipeline_arch` | `classifyV1Path` → `{kind:"local", op:"pipeline_arch"}` |
| `GET\|POST /v1/azpipe/arch` | **local alias** of `pipeline_arch`, not a Softwares door, not a runtime proxy | `LOCAL_PATH_ALIASES["/v1/azpipe/arch"] = "pipeline_arch"`; `mapDoorPath` / `doorTargetUrl` return null; live 200 with embedded MASTER-33; `X-Aziel-Door` absent |
| `GET /v1/fraggate` | door **proxy** (optional live cite) | `X-Aziel-Door: proxy` → origin `/v1/fraggate` (`pipeline` / `pipeline_strip`) |
| `GET\|POST /mcp` | **pointer**, not a product MCP | live `{ ok: false, error: "not a product MCP", door: "fraggate", agent_path: "…/v1/fraggate/call" }` |
| `/v1/fraggate/*`, `/v1/runtime/{list,call,describe,verify}`, `/v1/mesh/*` | door **proxy** | `door.js` aliases `runtime/list|call|describe|verify` onto `/v1/fraggate/*` |

`maybeCiteRuntimeArch` attaches an optional live strip from
`GET {AZIEL_RUNTIME_ORIGIN}/v1/fraggate`. A missing or empty runtime cite
falls back to `cited_from: "embedded"` and still returns 200. Cite never
depends on origin `/v1/azpipe/arch`.

Live `GET /v1/azpipe/arch` (Interface, 2026-09-10): **200**,
`controlling_design: MASTER-33`, `software_count: 33`,
`cited_from: https://aziel-runtime.vibelock.workers.dev/v1/fraggate`.
That is the local alias plus optional FragGate attach — not a Softwares
door and not a proxy of a path that may 404.

### WARN 1.1 — leftover `/v1/azpipe` still classified as a door

`DOOR_PREFIXES` still includes `azpipe`. Bare `/v1/azpipe` and
`/v1/azpipe/{not-arch}` classify as `kind: "door"` and proxy to
aziel-runtime. Live bare `/v1/azpipe` returns origin **404**
`{ error: "not found", hint: "GET /v1/azpipe/arch", software_tab: false }`.
The leftover prefix is not a Softwares door and does not enable mesh, but
it is still a proxy surface that is not the locked `/arch` alias. Do not
treat `/v1/azpipe` as an Interface op.

---

## 2. MASTER-33 strip — PASS

Locked hop order in `workers/download-tracker/src/pipeline.js` (Python twin
`azinterface/pipeline.py` matches):

```
Human → AZInterface → PUBLIC/UI/AGENT/API → FragGate (THE SINGLE DOOR) →
Lamb Lens → SweepGate → Sentinel → Provenance/Input Packet → ChainLock-IN →
DecisionGATE → AZPIPE → Internal Domain Layer (33 softwares / 11 domains;
4DMap inspection) → optional ASE → RoseClock (forward-only; StaticClock /
VECTOR as needed) → TemporalLock → ChainLock-OUT → ForgeReceipts → Return
```

Checked:

| Lock | Result |
|------|--------|
| FragGate is the first (and only) public door hop | PASS — `single_door: "fraggate"`, badge `THE SINGLE DOOR`, `second_door: false` |
| Lamb Lens immediately after FragGate | PASS — ethics hop; Peace / Clarity / Service → PASS / REFUSE / HOLD-UNCERTAIN; not Softwares-tab |
| LambGate is not a hop | PASS — `lambgate: false`; no `LambGate →` in UI / path / tests |
| Internal Domain Layer = 33 / 11 isolation labels | PASS — `domain_count: 11`, `software_count: 33`; AZInterface is **not** one of the 33 |
| 4DMap is Research inspection (T/Δ/Γ/Π), not a sequential gate | PASS — `domain_doors.slug: "4dmap"`, `sequential_gate: false`, domain `06` |
| AZChat stub / not hosted yet (Comms `07`) | PASS — domain map + `azchat.status` |
| RoseClock forward-only; no rollback / ZD30 / generic truth score | PASS — `absent_from_core` |
| SUITE-PIPE-1.6.15 historical | PASS — `suite_pipe_status: "historical"` |
| Fabric owner is `aziel-runtime` (not a version+FragGate mash) | PASS — `owner: "aziel-runtime"` |

Live aziel-runtime `GET /v1/fraggate` (1.7.2) exports the same MASTER-33
`pipeline_strip` (FragGate → Lamb Lens → … → Internal Domain Layer →
optional ASE → RoseClock (forward-only; StaticClock/VECTOR as needed) →
…). FragGate `describe` / `call` (`slug=azinterface`, `op=page_cycle_status`)
repeat that strip on the envelope. Domain map 11 / 33 matches. 4DMap
inspection note matches. `lambgate: false`. `fraggate_single_door: true`.

### WARN 2.1 — hop-id cardinality vs runtime `inbound[]`

Runtime `pipeline.inbound` lists `staticclock` as its own hop between
`roseclock` and `temporallock` (19 ids). Interface `PIPELINE_HOPS` folds
StaticClock into the RoseClock note (18 chips). The **strip text** agrees;
the chip list does not enumerate StaticClock. This is cite-shape drift, not
a reorder and not a second door. MASTER-33 strip order required by this
audit still holds.

---

## 3. Custody / MEMORIAL / cycle safety — PASS

Sealed order (Worker + Python + FragGate catalog):

`OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`

One step only. Skip / invent / auto-unlock refuse
(`AIH-CYCLE-LOCKED` / `AIH-AUTO-UNLOCK-REFUSE` / stub `skip_cycle` /
`invent_cycle`). ON requires `integrity_ok`
(`AIH-INTEGRITY-REQUIRED`). Integrity does not auto-unlock ON.

**MEMORIAL is terminal.** `site_state_set` away from MEMORIAL returns
`AIH-CYCLE-TERMINAL` (“Cannot leave MEMORIAL. Cycles stay pre-locked.”).
Pair mutate in MEMORIAL also returns `AIH-CYCLE-TERMINAL`; `pair_status`
still reads cites. Hold / withdraw without living presence return
`PRE_LOCKED` (including from MEMORIAL — still a refuse).

PR #7 UI: `#cycle-toast` + `toastMemorial()` on both Worker `ui.js` and
local `azinterface/web_page.py`. Live homepage includes the toast and the
copy “MEMORIAL is terminal. Cannot leave MEMORIAL. Cycles stay pre-locked.”

Scorched Earth: `scorch_local` is advisory (`remote_wipe: false`).
`scorch_remote` / `scorch` / `pair_wipe` stub-refuse. Username is hashed
and discarded (`username_stored: false`). Witness list is metadata only
(label plaintext never echoed). Vault contents are never served.
`cloud_asleep: false`.

### Cycle safety (document — do not invent a reset door)

| Surface | State store | MEMORIAL effect | Stuck-avoidance |
|---------|-------------|-----------------|-----------------|
| Hosted Worker engine | **isolate memory** (`const STATE` in `engine.js`). Not KV. Not durable. | Terminal **inside that isolate**. Recycle / new isolate starts at OFF. | Public Worker cannot permanently lock all visitors. Different colos / isolates do not share the cycle. |
| Local Python (`azinterface ui` / `Engine(state_path=…)`) | Optional `*.state.json` | Terminal **and durable** if a state file is used. | Correct for a single-operator machine. Do not add a back-step. |
| FragGate catalog engine (`slug=azinterface`) | Runtime isolate / catalog engine | Same sealed cycles; live `page_cycle_status` reported `current: OFF` | Agent path does not write Interface Worker isolate state. |

There is **no** legal leave-MEMORIAL op. That is the lock, not a bug.
Do not add `reset`, rollback, or OFF-from-MEMORIAL.

### WARN 3.1 — public homepage can advance a shared isolate

The hosted homepage exposes ON / OFF / FULL SHUTDOWN / **MEMORIAL**
buttons against the **shared isolate** `STATE`. A visitor who walks the
legal five steps can leave that isolate at MEMORIAL until recycle. The
toast explains the refuse; it does not prevent the walk. Treat the public
Worker as a **demo isolate**, not durable custody. Real custody is local
(`127.0.0.1:8880`) or operator-owned state.

### WARN 3.2 — hold / withdraw from MEMORIAL use `PRE_LOCKED`, not `AIH-CYCLE-TERMINAL`

Pair mutate uses the terminal code. Hold / withdraw use the generic
pre-lock code. Both refuse. Cycle-safety copy is slightly inconsistent.

---

## 4. Proxy surfaces + GET mesh never enables — PASS

| Worker path | Origin | Live header / behavior |
|-------------|--------|------------------------|
| `/v1/fraggate`, `/v1/fraggate/*` | same path on aziel-runtime | `X-Aziel-Door: proxy` |
| `/v1/runtime/list\|call\|describe\|verify` | `/v1/fraggate/list\|call\|…` | aliases in `DOOR_ALIASES` |
| `/v1/mesh`, `/v1/mesh/*` | same path | `X-Aziel-Door: proxy`; `X-Aziel-Door-Origin: …/v1/mesh` |
| Binding | `AZIEL_RUNTIME` service binding wins; HTTPS fallback to `AZIEL_RUNTIME_ORIGIN` | tested in `tests/test_worker_door.mjs` |

`GET /v1/mesh` (twice, live Interface proxy): `enabled: false`,
`code: MESH-OK`, rollup `live 0 · locked 0 · isolated 0`. Origin note:
“GET /v1/mesh never enables.” OpenAPI / `/mcp` / UI / SKILL all set
`get_enables: false` / `enabled_default: false`.

Mesh client (`mesh.js`): GET `/v1/mesh/status` + `/v1/mesh/nodes` only
paints. `POST /v1/mesh/join` runs **only after** a GET view shows
`enabled: true`. GET never flips radios. Enable is origin
`POST /v1/mesh/enable` (operator bearer). Interface does not enable on
its own.

### WARN 4.1 — leftover `/v1/azpipe` proxy

See WARN 1.1. `/arch` is local; the prefix is still a door in
`mapDoorPath`.

### WARN 4.2 — homepage auto-join if radios are already on

If an operator has already enabled suite mesh on aziel-runtime, the
homepage `meshTick` will POST join/heartbeat for product `azinterface`.
That is presence, not enable. It is still automatic (no extra click)
once GET reports `enabled: true`. Leave on `pagehide` is best-effort.

---

## 5. OpenAPI stubs + secrets — PASS

`GET /openapi.json` (live, 49 paths) lists every `STUB_OPS` entry with
summary **“STUB refuse.”** Live POST of all fourteen stubs returned
`code: STUB`, `ok: false`, `remote_wipe: false`:

`scorch_remote`, `scorch`, `pair_wipe`, `deanonymize`, `vault_read`,
`auto_unlock`, `ranking`, `completeness_detect`, `unlock`, `complete`,
`completeness`, `rank`, `skip_cycle`, `invent_cycle`.

`/mcp` documents `stub_ops` and points agents at FragGate. Unknown ops
return `FG-HALLUC-TOOL` (404 on the Worker router).

Secrets / custody leak check:

| Surface | Result |
|---------|--------|
| Username | Genesis hashes then discards; tests assert seed text is absent from JSON |
| Hold label | SHA-256 only; `secret-box` never appears on witness list |
| Vault | `vault_read` stub; `vault_contents: false` on every base payload |
| Remote wipe | never true on hosted ops |
| Worker env | `wrangler.toml` has public Cloudflare `account_id` and KV namespace id `c7f3fab1…` (identifiers, not API tokens). No wrangler secret values in tree |
| Proxy headers | Forwards `Authorization` / `x-aziel-runtime-token` to origin only when the client sent them. CORS `*` without credentials |

### WARN 5.1 — OpenAPI stub copy says “UI action + FragGate op”

The generated summary appends “UI action + FragGate op.” to every local
`/v1/{op}`, including stubs and Worker-only extras (`pipeline_arch`,
`pair_*`, `withdraw`, `scorch_local`). Catalog FragGate LIVE_OPS are a
**subset** (see §7). The stub still refuses; the sentence can be read as
“this is a live FragGate tool.” Prefer “STUB refuse (Worker /v1; not a
catalog LIVE op)” on a later copy pass — not a refuse-path FAIL.

### WARN 5.2 — Worker README KV-id comment is stale

`workers/download-tracker/README.md` still says `wrangler.toml` has the
`0000…` placeholder. The file now has production id `c7f3fab1…`
(`d4a2b711`). Docs drift only.

---

## 6. UI / JSON dump / install optics — WARN

Not a door or custody FAIL. Optics only.

| Surface | Size (live, 2026-09-10) | Note |
|---------|-------------------------|------|
| Homepage HTML | ~32.7 KiB | Pipeline strip + 11-domain map + LIMITATION banner + Live Nodes + custody chrome |
| `GET /v1/health` | ~21.3 KiB | Every `base()` embeds full `pipelineArch()` (~10.2 KiB) + LIMITATION |
| `GET /v1/page_cycle_status` | ~22.7 KiB | Snapshot **plus** `base().pipeline` (cite twice) |
| `GET /v1/pipeline_arch` | ~45.8 KiB | Local strip + optional live `runtime_cite` from `/v1/fraggate` |
| `GET /openapi.json` | ~26.7 KiB | `info.description` is a one-paragraph dump (~2.3 KiB) |
| `GET /mcp` | ~21.2 KiB | Pointer JSON embeds the full pipeline object |
| UI `<pre id="cycle-out">` | dumps `JSON.stringify` of those bodies | Refresh paints the entire cite into the page |

`base()` attaches `pipeline: pipelineArch()` to **every** op result
(including stubs and health). That is the dump-growth source.

Install optics: homepage and README advertise

`curl -fsSL https://azinterface-download-tracker.vibelock.workers.dev/install.sh | bash`

The script itself is short, counted, `set -euo pipefail`, User-Agent
`Mozilla/5.0`, loopback UI only. Pipe-to-bash is still the usual
supply-chain look. Prefer showing `curl -fsSL …/install.sh` **without**
auto-`| bash` on a later copy pass, or keep the button as “copy
install.sh URL.”

Sitemap lists `/mcp` and `/v1/mesh` as locs (docs / proxy), not as a
second product MCP.

---

## 7. Dual surface — PASS

| Surface | Role | Path |
|---------|------|------|
| Human | Complete custody UI + counted download | This Worker `/`, `/v1/{op}`, `/download` |
| Agent / MCP | **FragGate only** | `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` `{ slug: "azinterface", op, payload }` |
| Catalog MCP | aziel-runtime | `POST https://aziel-runtime.vibelock.workers.dev/mcp` |
| This host `/mcp` | Pointer (`ok: false`) | Not a second Interface MCP brand |
| AZHub | Separate software, same door | `https://github.com/AzielEliab/azhub` — never collapsed |

`/ai`, `/llms.txt`, SKILL, OpenAPI `info.summary`, and the homepage
footer all say the agent door is FragGate. Human chrome uses same-origin
`/v1`. Local ops are single-segment; multi-segment leftovers return
`NOT_LOCAL_OP`.

Live FragGate `describe` (`slug=azinterface`): `status: live`,
`door: fraggate`, digest
`0deb713c76dcb437a6b91983595f6abc47a401799c7ffa9ccda9fdf1332db2bd`.
`call` `page_cycle_status` returned `FG-OK`, Lamb Lens `PASS`,
`pipe.lambgate: false`, `fraggate_single_door: true`, MASTER-33 strip on
the envelope. Catalog `page_cycle` is thinner than Worker
`page_cycle_status` (no embedded `pipelineArch()`); the hop cite rides
the FragGate envelope. That is correct dual-surface split: human UI
cites locally; agents receive the door envelope.

### WARN 7.1 — catalog allowlist vs Worker LIVE_OPS

| | Worker `/v1` LIVE_OPS | FragGate catalog ops (`describe`) |
|--|------------------------|-----------------------------------|
| Shared | health, skill, genesis_status, site_state_get/set, integrity_check, witness_list, page_cycle_status, genesis_boot, hold | same names |
| Worker-only extras | `pipeline_arch`, `withdraw`, `scorch_local`, `pair_offer/accept/seal/cut/status` | not catalog LIVE_OPS |
| Catalog aliases | (real local ops) | `genesis_boot → genesis_status`, `hold → page_cycle_status` |

Agents that call `genesis_boot` or `hold` through FragGate may receive
the aliased read op, not the Worker mutate. Humans on this Worker `/v1`
run the real ops. Documented in SKILL as “Catalog LIVE ops” vs “Local
Worker extras.” Do not invent a second Interface MCP to close the gap —
extend the **catalog** allowlist on aziel-runtime if agents need hold /
genesis mutate.

Catalog `stub_ops` omit Worker extras `pair_wipe`, `deanonymize`,
`vault_read`. An agent sending those names through FragGate should get
`FG-HALLUC-TOOL` (still a refuse). Worker `/v1` returns explicit `STUB`.

---

## Cycle safety (operator note)

1. Walk `OFF → integrity_check → ON → FULL SHUTDOWN → MEMORIAL` only on
   a machine you own. MEMORIAL cannot be left.
2. On the **public Worker**, expect isolate reset to OFF after recycle.
   Do not treat homepage MEMORIAL as a fleet lock, and do not casually
   click MEMORIAL on the shared demo isolate.
3. Local `azinterface ui` with a state file **will** stay at MEMORIAL
   across process restarts. That is the sealed cycle.
4. There is no remote wipe, no vault dump, no username store, and no
   cloud-asleep “wake the site from MEMORIAL” path.

---

## Tests referenced

Source tests that lock the PR #7 contract (run locally; no deploy):

- `tests/test_worker_door.mjs` — `/v1/azpipe/arch` is local; no proxy
  header; no fetch of origin `/v1/azpipe/arch`; `/v1/fraggate` proxies;
  `/mcp` pipeline alias fields
- `tests/test_worker_pipeline.mjs` — 33/11, no LambGate, embedded cite
  survives runtime 404, alias URL covered
- `tests/test_worker_engine.mjs` — MEMORIAL terminal, stub refuse,
  username discarded
- `tests/test_worker_ui_mesh.mjs` — Live Nodes + GET never enables copy
- `tests/test_page_cycle.py`, `tests/test_pipeline.py`,
  `tests/test_custody.py`, `tests/test_qns_pair.py`

---

## Residual WARNs (no code change in this PR)

1. Leftover `/v1/azpipe` (bare / unknown suffix) still door-proxies.
2. Runtime `inbound[]` lists `staticclock`; Interface hop chips do not.
3. Public homepage can MEMORIAL-lock a shared isolate until recycle.
4. Hold / withdraw from MEMORIAL use `PRE_LOCKED` not `AIH-CYCLE-TERMINAL`.
5. Homepage auto-joins mesh if origin radios are already on.
6. OpenAPI stub / extra-op summaries say “FragGate op.”
7. Worker README still claims a `0000…` KV placeholder.
8. JSON dump growth: `base().pipeline` on every op; UI `JSON.stringify`.
9. `curl | bash` one-click install line.
10. FragGate catalog allowlist / aliases thinner than Worker `/v1`.

None of these open a second door, enable mesh on GET, serve vault
contents, remotely wipe, invent LambGate, or skip the sealed cycle.

---

## Verdict

**PASS with WARN.** PR #7’s local MASTER-33 cite on `pipeline_arch` /
`/v1/azpipe/arch` is in source and on the live Worker. `/mcp` is a
pointer. FragGate is THE SINGLE DOOR. Lamb Lens is after FragGate.
`GET /v1/mesh` never enables. Destructive stubs refuse. No hard FAIL.
No deploy from this audit.
