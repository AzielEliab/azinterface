# Contributing to AZInterface

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
node tests/test_worker_engine.mjs
node tests/test_worker_door.mjs
node tests/test_worker_pipeline.mjs
node tests/test_worker_ui_mesh.mjs
```

Python 3.10+. Engine is stdlib only. pytest is the dev extra.
No network. No ML. Not a remote wipe service.

## Ground rules

1. **Interface is CUSTODY.** Do not collapse this product into AZHub
   (Blank Key / spatial container). Hub is separate software under the
   one FragGate door — never a second FragGate engine.
2. **Pre-locked page cycles.** Sealed order:
   `OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL`. One step only.
   Default OFF. ON requires integrity. MEMORIAL is terminal. Do not
   invent cloud-asleep availability.
3. **Genesis is one-time.** Display the Genesis Hash Key only. Never
   persist a username.
4. **Witness list is metadata.** Never serve vault contents. `vault_read`
   stays stub.
5. **Scorched Earth is local advisory only** on the hosted Worker.
   `scorch_remote` / `pair_wipe` must refuse. Never remotely wipe user
   devices. `pair_cut` is a local dissolve of memorial cites.
6. **QNS-CD-1.0 pair custody.** Handshake is AIH-WP-1.3
   (OFFER → ACCEPT → SEAL). Pair mutate only at ON after integrity.
   Vias run in local qnsd (127.0.0.1). Do not invent a Softwares-tab QNS
   product, enable mesh from GET, add a Node Gate, or claim untraceable
   origin.
7. **UI binds loopback only** (`127.0.0.1:8880`). Do not listen on
   `0.0.0.0`. No telemetry. No CDN.
8. **Do not mix the download tracker** with any other product's Worker
   or KV. Namespace `AZINTERFACE_DOWNLOADS` only.
9. **Public identity is Aziel Eliab only.** Do not add GodLock.AZ or any
   other public name.
10. New behavior needs a test that fails without the change.

## Where to change things

- Engine / cycle / genesis / witness: `azinterface/engine.py`
- CLI / doctor / UI: `azinterface/cli.py`, `azinterface/doctor.py`, `azinterface/ui.py`, `azinterface/web_page.py`
- Spec: `docs/whitepaper.md`, `docs/QNS-CD-1.0.md`
- Skill: `SKILL.md` (same text at Worker `GET /v1/skill`)
- Flutter: `mobile/`
- Isolated counter: `workers/download-tracker/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.
