/**
 * SPLIT THE WIRES + COLD-COPY SURVIVAL — locked mesh law.
 * Author: Aziel Eliab only.
 */
import assert from "node:assert/strict";
import {
  COLD_COPY_LAW,
  COLD_COPY_SURVIVAL,
  GATE_DWELL_S,
  GATE_SOCKET,
  LIVE_NODES_COPY,
  SPLIT_THE_WIRES,
  SPLIT_THE_WIRES_LAW,
  TIP_SOCKET,
  TIP_TICK_FIXED_CHARS,
  TIP_TICK_MS_MAX,
  TIP_TICK_MS_MIN,
  dataOutlivesCreators,
  encodeTipTick,
  isTipTickInterval,
  judgeEmitLast,
  judgeEquivocation,
  judgeHeartbeatLoss,
  judgeLiveBodySync,
  judgePartition,
  judgePhoenix,
  judgePoison,
  judgeUpdate,
  mayPushPayload,
  meshClientScript,
  meshLaw,
  meshStripHtml,
  multiplyColdCopies,
  payloadPlane,
  serverPullCannotWipeCold,
  socketsMustSplit,
  tipEraseCost,
} from "../workers/download-tracker/src/mesh.js";

const HASH_A = "a".repeat(64);
const HASH_B = "b".repeat(64);

assert.equal(SPLIT_THE_WIRES, "SPLIT THE WIRES");
assert.equal(COLD_COPY_SURVIVAL, "COLD-COPY SURVIVAL");
assert.equal(TIP_TICK_MS_MIN, 500);
assert.equal(TIP_TICK_MS_MAX, 1000);
assert.equal(GATE_DWELL_S, 777);
assert.equal(TIP_SOCKET, "tip-tick-1s");
assert.equal(GATE_SOCKET, "gate-777");
assert.notEqual(TIP_SOCKET, GATE_SOCKET);
assert.equal(SPLIT_THE_WIRES_LAW.sockets_shared, false);
assert.deepEqual(SPLIT_THE_WIRES_LAW.tip.fields, ["presence", "tip_hash"]);
assert.equal(SPLIT_THE_WIRES_LAW.payload.mode, "pull-only");
assert.equal(SPLIT_THE_WIRES_LAW.update.kind, "proof");
assert.equal(SPLIT_THE_WIRES_LAW.update.not, "timer");
assert.equal(SPLIT_THE_WIRES_LAW.equivocation, "ends-peer");
assert.equal(SPLIT_THE_WIRES_LAW.emit_last, "locally");
assert.equal(SPLIT_THE_WIRES_LAW.phoenix, "local-only");
assert.equal(SPLIT_THE_WIRES_LAW.partition, "no-auto-splice");
assert.equal(SPLIT_THE_WIRES_LAW.heartbeat_loss.poison, false);
assert.equal(SPLIT_THE_WIRES_LAW.heartbeat_loss.apply_last_packet, false);
assert.equal(COLD_COPY_LAW.multiply_cold_copies, true);
assert.equal(COLD_COPY_LAW.live_body_sync, false);
assert.equal(COLD_COPY_LAW.tip_expensive_to_erase, true);
assert.equal(COLD_COPY_LAW.server_pull_wipes_cold, false);
assert.equal(COLD_COPY_LAW.hash_absolute_poison_refuse, true);
assert.equal(COLD_COPY_LAW.data_outlives_creators, true);

assert.equal(isTipTickInterval(499), false);
assert.equal(isTipTickInterval(500), true);
assert.equal(isTipTickInterval(1000), true);
assert.equal(isTipTickInterval(1001), false);

const split = socketsMustSplit(TIP_SOCKET, GATE_SOCKET);
assert.equal(split.ok, true);
assert.equal(split.shared, false);
assert.equal(socketsMustSplit(TIP_SOCKET, TIP_SOCKET).code, "STW-SOCKET-SHARED");
assert.equal(socketsMustSplit("", GATE_SOCKET).code, "STW-SOCKET-MISSING");

const tip = encodeTipTick({ presence: "live", tip_hash: HASH_A });
assert.equal(tip.ok, true);
assert.equal(tip.fixed_size, true);
assert.equal(tip.wire.length, TIP_TICK_FIXED_CHARS);
assert.equal(encodeTipTick({ presence: "live", tip_hash: HASH_A, payload: "body" }).code, "STW-TIP-PAYLOAD");
assert.equal(encodeTipTick({ presence: "live", tip_hash: HASH_A, extra: 1 }).code, "STW-TIP-PAYLOAD");
assert.equal(encodeTipTick({ presence: "ghost", tip_hash: HASH_A }).code, "STW-TIP-PRESENCE");
assert.equal(encodeTipTick({ presence: "live", tip_hash: "short" }).code, "STW-TIP-HASH");

const payload = payloadPlane();
assert.equal(payload.mode, "pull-only");
assert.equal(payload.push, false);
assert.equal(mayPushPayload(), false);
assert.equal(payload.socket, GATE_SOCKET);
assert.notEqual(payload.socket, TIP_SOCKET);

assert.equal(judgeUpdate({ timer_only: true }).code, "STW-UPDATE-FAIL-CLOSED");
assert.equal(judgeUpdate({ cite_prev: HASH_A }).code, "STW-UPDATE-FAIL-CLOSED");
assert.equal(judgeUpdate({ cite_prev: HASH_A, lockset: "LOCKSET", clock_desync: true }).code, "STW-CLOCK-DESYNC");
assert.equal(judgeUpdate({ cite_prev: HASH_A, lockset: "LOCKSET", ambiguous: true }).code, "STW-AMBIGUOUS-ISOLATE");
assert.equal(judgeUpdate({ cite_prev: HASH_A, lockset: "LOCKSET", now_s: 10, last_valid_cite_s: 0 }).code, "STW-GATE-DWELL");
const proved = judgeUpdate({ cite_prev: HASH_A, lockset: "LOCKSET", now_s: 800, last_valid_cite_s: 0 });
assert.equal(proved.ok, true);
assert.equal(proved.kind, "proof");
assert.equal(proved.not, "timer");

const loss = judgeHeartbeatLoss();
assert.equal(loss.poison, false);
assert.equal(loss.apply_last_packet, false);
assert.equal(loss.action, "loss-only");

assert.equal(judgeEquivocation([{ height: 1, tip_hash: HASH_A }, { height: 1, tip_hash: HASH_B }]).code, "STW-EQUIVOCATION");
assert.equal(judgeEquivocation([{ height: 1, tip_hash: HASH_A }, { height: 1, tip_hash: HASH_A }]).ok, true);
assert.equal(judgeEmitLast().scope, "locally");
assert.equal(judgePhoenix({ hunt: true }).code, "STW-PHOENIX-HUNT-REFUSE");
assert.equal(judgePhoenix({}).scope, "local-only");
assert.equal(judgePartition().auto_splice, false);

const grown = multiplyColdCopies(["a"]);
assert.equal(grown.multiply, true);
assert.equal(grown.may_grow, true);
assert.equal(judgeLiveBodySync().code, "CCS-LIVE-BODY-SYNC-REFUSE");
assert.equal(tipEraseCost().expensive, true);
const held = serverPullCannotWipeCold(["cold-1", "cold-2"], { wipe: true });
assert.equal(held.code, "CCS-COLD-WIPE-REFUSE");
assert.deepEqual(held.remain, ["cold-1", "cold-2"]);
assert.equal(judgePoison({ hash: HASH_A, expected: HASH_B }).code, "CCS-POISON-REFUSE");
assert.equal(judgePoison({ hash: HASH_A, expected: HASH_A }).ok, true);
assert.equal(dataOutlivesCreators({ creator_absent: true }).outlives, true);
assert.equal(dataOutlivesCreators({}).creator_death_deletes, false);

const card = meshLaw();
assert.equal(card.split_the_wires.law, SPLIT_THE_WIRES);
assert.equal(card.cold_copy_survival.law, COLD_COPY_SURVIVAL);
assert.equal(card.sockets.ok, true);
assert.equal(card.author, "Aziel Eliab only");

assert.match(LIVE_NODES_COPY, /SPLIT THE WIRES/);
assert.match(LIVE_NODES_COPY, /COLD-COPY SURVIVAL/);
assert.match(LIVE_NODES_COPY, /0\.5–1s tip tick/);
assert.match(LIVE_NODES_COPY, /presence\+tip hash only fixed-size/);
assert.match(LIVE_NODES_COPY, /payload pull-only second plane/);
assert.match(LIVE_NODES_COPY, /update=proof not timer/);
assert.match(LIVE_NODES_COPY, /777s dwell/);
assert.match(LIVE_NODES_COPY, /clock desync≠yes/);
assert.match(LIVE_NODES_COPY, /ambiguous=isolate/);
assert.match(LIVE_NODES_COPY, /equivocation ends peer/);
assert.match(LIVE_NODES_COPY, /emit last locally/);
assert.match(LIVE_NODES_COPY, /Phoenix local only/);
assert.match(LIVE_NODES_COPY, /partition no auto-splice/);
assert.match(LIVE_NODES_COPY, /heartbeat loss≠poison≠apply last packet/);
assert.match(LIVE_NODES_COPY, /never share a socket/);
assert.match(LIVE_NODES_COPY, /multiply cold copies/);
assert.match(LIVE_NODES_COPY, /refuse live body sync/);
assert.match(LIVE_NODES_COPY, /tip expensive to erase/);
assert.match(LIVE_NODES_COPY, /server pull cannot wipe cold replicas/);
assert.match(LIVE_NODES_COPY, /hash-absolute poison refuse/);
assert.match(LIVE_NODES_COPY, /data outlives creators/);

const html = meshStripHtml();
assert.match(html, /SPLIT THE WIRES/);
assert.match(html, /COLD-COPY SURVIVAL/);

const script = meshClientScript();
assert.match(script, /var TIP_SOCKET = "tip-tick-1s"/);
assert.match(script, /var GATE_SOCKET = "gate-777"/);
assert.match(script, /STW-SOCKET-SHARED/);
assert.match(script, /TIP_SOCKET === GATE_SOCKET/);
assert.match(script, /CCS-LIVE-BODY-SYNC-REFUSE/);
assert.match(script, /heartbeat loss≠poison≠apply last packet/);
assert.match(script, /Phoenix local only/);
assert.match(script, /partition no auto-splice/);
assert.match(script, /no auto-heal/);
assert.match(script, /product: MESH_PRODUCT/);
assert.match(script, /azinterface/);
assert.match(script, /\/v1\/mesh\/status/);
assert.match(script, /\/v1\/mesh\/nodes/);
assert.equal(script.includes("apply last packet"), true);
assert.equal(/live body sync/i.test(LIVE_NODES_COPY), true);

console.log("worker mesh law SPLIT THE WIRES + COLD-COPY SURVIVAL ok");
