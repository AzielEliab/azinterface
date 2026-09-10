import assert from "node:assert/strict";
import { dispatch, genesisHashKey, LIVE_OPS, PAGE_CYCLES, resetEngine, STUB_OPS } from "../workers/download-tracker/src/engine.js";

assert.ok(LIVE_OPS.includes("pair_offer") && LIVE_OPS.includes("pair_status"));
assert.ok(STUB_OPS.includes("pair_wipe"));

resetEngine();

assert.ok(LIVE_OPS.includes("page_cycle_status") && LIVE_OPS.includes("integrity_check"));
assert.ok(STUB_OPS.includes("scorch_remote") && STUB_OPS.includes("vault_read"));
assert.ok(STUB_OPS.includes("skip_cycle") && STUB_OPS.includes("invent_cycle"));
assert.deepEqual(PAGE_CYCLES, ["OFF", "integrity", "ON", "FULL SHUTDOWN", "MEMORIAL"]);

const cycle = await dispatch("page_cycle_status", {});
assert.equal(cycle.site_state, "OFF");
assert.equal(cycle.current, "OFF");
assert.equal(cycle.living_presence, false);
assert.equal(cycle.cloud_asleep, false);
assert.equal(cycle.modules.azhome.served, false);
assert.equal(cycle.page_cycle.skip_forbidden, true);

const skip = await dispatch("site_state_set", { state: "ON" });
assert.equal(skip.code, "AIH-CYCLE-LOCKED");

const memorialSkip = await dispatch("site_state_set", { state: "MEMORIAL" });
assert.equal(memorialSkip.code, "AIH-CYCLE-LOCKED");

const integ = await dispatch("integrity_check", {});
assert.equal(integ.ok, true);
assert.equal(integ.living_presence, false);
assert.equal(integ.current, "integrity");

const lockedPair = await dispatch("pair_offer", { via: "local" });
assert.equal(lockedPair.code, "PRE_LOCKED");

const on = await dispatch("site_state_set", { state: "ON" });
assert.equal(on.ok, true);
assert.equal(on.living_presence, true);
assert.equal(on.cycle.modules.azhome.served, true);

const boot = await dispatch("genesis_boot", { username: "operator-seed-example" });
assert.equal(boot.ok, true);
assert.equal(boot.genesis_hash, await genesisHashKey("operator-seed-example"));
assert.equal(boot.username_stored, false);
assert.equal(JSON.stringify(boot).includes("operator-seed-example"), false);

const again = await dispatch("genesis_boot", { username: "another-name" });
assert.equal(again.code, "GENESIS_ALREADY_KEYED");

const hold = await dispatch("hold", { label: "secret-box" });
assert.equal(hold.ok, true);
assert.equal(hold.vault_contents, false);

const offer = await dispatch("pair_offer", { via: "lan", photon_id: "qns1-cite" });
assert.equal(offer.ok, true);
assert.equal(offer.handshake, "OFFER");
assert.equal(offer.pair.via_runs_in, "qnsd");
assert.equal(offer.pair.untraceable_origin, false);
const accept = await dispatch("pair_accept", { pair_id: offer.pair.pair_id });
assert.equal(accept.handshake, "ACCEPT");
const skipAccept = await dispatch("pair_accept", { pair_id: offer.pair.pair_id });
assert.equal(skipAccept.code, "QNS-HANDSHAKE-LOCKED");
const seal = await dispatch("pair_seal", { pair_id: offer.pair.pair_id });
assert.equal(seal.handshake, "SEAL");
const citedHold = await dispatch("hold", { label: "paired", pair_id: offer.pair.pair_id, photon_id: "qns1-cite" });
assert.equal(citedHold.hold.pair_id, offer.pair.pair_id);
assert.equal(JSON.stringify(citedHold).includes("paired"), false);
const listed = await dispatch("witness_list", {});
assert.equal(JSON.stringify(listed).includes("secret-box"), false);
assert.equal(listed.vault_contents, false);

const stub = await dispatch("scorch_remote", {});
assert.equal(stub.code, "STUB");
assert.equal(stub.remote_wipe, false);

const skipOp = await dispatch("skip_cycle", {});
assert.equal(skipOp.code, "STUB");

const unlock = await dispatch("site_state_set", { cycle: "FULL SHUTDOWN", auto_unlock: true });
assert.equal(unlock.code, "AIH-AUTO-UNLOCK-REFUSE");

const shut = await dispatch("site_state_set", { state: "FULL_SHUTDOWN" });
assert.equal(shut.ok, true);
assert.equal(shut.current, "FULL SHUTDOWN");
const shutPair = await dispatch("pair_cut", {});
assert.equal(shutPair.code, "QNS-CYCLE-REFUSE");
const mem = await dispatch("site_state_set", { state: "MEMORIAL" });
assert.equal(mem.ok, true);
const leave = await dispatch("site_state_set", { state: "ON" });
assert.equal(leave.code, "AIH-CYCLE-TERMINAL");
const memPair = await dispatch("pair_offer", { via: "local" });
assert.equal(memPair.code, "AIH-CYCLE-TERMINAL");
const memorialRead = await dispatch("pair_status", {});
assert.equal(memorialRead.ok, true);
assert.equal(memorialRead.count >= 1, true);

const wipe = await dispatch("pair_wipe", {});
assert.equal(wipe.code, "STUB");
assert.equal(wipe.remote_wipe, false);

const bad = await dispatch("not_real", {});
assert.equal(bad.code, "FG-HALLUC-TOOL");

resetEngine();
console.log("worker engine smoke ok", LIVE_OPS.length, "live ops");
