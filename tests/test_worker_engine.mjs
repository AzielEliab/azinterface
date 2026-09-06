import assert from "node:assert/strict";
import { dispatch, genesisHashKey, LIVE_OPS, resetEngine, STUB_OPS } from "../workers/download-tracker/src/engine.js";

resetEngine();

assert.ok(LIVE_OPS.includes("page_cycle_status") && LIVE_OPS.includes("integrity_check"));
assert.ok(STUB_OPS.includes("scorch_remote") && STUB_OPS.includes("vault_read"));

const cycle = await dispatch("page_cycle_status", {});
assert.equal(cycle.site_state, "OFF");
assert.equal(cycle.living_presence, false);
assert.equal(cycle.cloud_asleep, false);
assert.equal(cycle.modules.azhome.served, false);

const refused = await dispatch("site_state_set", { state: "ON" });
assert.equal(refused.code, "NEED_INTEGRITY");

const integ = await dispatch("integrity_check", {});
assert.equal(integ.ok, true);
assert.equal(integ.living_presence, false);

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
const listed = await dispatch("witness_list", {});
assert.equal(JSON.stringify(listed).includes("secret-box"), false);
assert.equal(listed.vault_contents, false);

const stub = await dispatch("scorch_remote", {});
assert.equal(stub.code, "STUB");
assert.equal(stub.remote_wipe, false);

const bad = await dispatch("not_real", {});
assert.equal(bad.code, "FG-HALLUC-TOOL");

resetEngine();
console.log("worker engine smoke ok", LIVE_OPS.length, "live ops");
