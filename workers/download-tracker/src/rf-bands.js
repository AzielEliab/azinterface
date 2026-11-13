/**
 * QNM-RF-BANDS-1.0 cite for the AZInterface worker.
 *
 * AM, FM, and SDR satellite receive (sat_rx) are enabled and absent-hardware
 * gated the same way LAN, Wi-Fi, Bluetooth, RF, and photon are. Missing
 * hardware refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live
 * stay false when that hardware is absent. A present SDR does not demodulate.
 *
 * XM SDARS and satellite_relay stay HELD. No spend, no SKU, no plan, no
 * checkout. Cap-7 is not ICANN. This cite reads local device nodes only.
 * Author: Aziel Eliab.
 */

export const RF_BAND_SPEC = "QNM-RF-BANDS-1.0";
export const TRAFFIC_SPEC = "QNM-TRAFFIC-PATHS-1.0";
export const RADIO_ABSENT = "QNM-RADIO-ABSENT";
export const AUTHOR = "Aziel Eliab";

export const OPEN_PATHS = Object.freeze(["lan", "wifi", "bluetooth", "rf", "photon", "am", "fm", "sat_rx"]);
export const HELD_PATHS = Object.freeze(["xm_sdars", "satellite_relay"]);

const OPEN_ALIASES = Object.freeze({
  am: "am",
  fm: "fm",
  sat_rx: "sat_rx",
  "sat-rx": "sat_rx",
  satrx: "sat_rx",
});
const HELD_ALIASES = Object.freeze({
  xm_sdars: "xm_sdars",
  "xm-sdars": "xm_sdars",
  xm: "xm_sdars",
  siriusxm: "xm_sdars",
  satellite_relay: "satellite_relay",
  "satellite-relay": "satellite_relay",
  satrelay: "satellite_relay",
});
const SWITCH_PHY = Object.freeze({
  lan: "absent-until-interface",
  wifi: "absent-until-hardware",
  bluetooth: "absent-until-hardware",
  rf: "absent-until-sdr",
  photon: "absent-until-light",
  am: "absent-until-sdr",
  fm: "absent-until-sdr",
  sat_rx: "absent-until-sdr",
  xm_sdars: "absent-until-siriusxm-tuner",
  satellite_relay: "absent",
});

export function classifyCarrier(raw) {
  const text = String(raw || "").trim().toLowerCase();
  if (HELD_ALIASES[text]) return ["held", HELD_ALIASES[text]];
  if (OPEN_ALIASES[text]) return ["open", OPEN_ALIASES[text]];
  return null;
}

function builtin(name) {
  try {
    if (typeof process === "undefined" || typeof process.getBuiltinModule !== "function") return null;
    return process.getBuiltinModule(name);
  } catch {
    return null;
  }
}

function at(root, rel) {
  if (!root) return `/${rel}`;
  const pathMod = builtin("node:path");
  if (pathMod) return pathMod.join(root, rel);
  return `${String(root).replace(/\/$/, "")}/${rel}`;
}

function dirHas(fs, path) {
  try {
    if (!fs || !fs.existsSync(path)) return false;
    const st = fs.statSync(path);
    if (!st.isDirectory()) return false;
    return fs.readdirSync(path).filter((name) => name && name !== "." && name !== "..").length > 0;
  } catch {
    return false;
  }
}

function fileHas(fs, path) {
  try {
    return Boolean(fs && fs.existsSync(path));
  } catch {
    return false;
  }
}

export function probeSdr(root, fs) {
  const io = fs || null;
  if (!io) return { present: false, kind: null };
  if (fileHas(io, at(root, "dev/swradio0")) || dirHas(io, at(root, "sys/class/sdr")) || dirHas(io, at(root, "sys/bus/usb/drivers/dvb_usb_rtl28xxu"))) {
    return { present: true, kind: "sdr" };
  }
  return { present: false, kind: null };
}

export function probeSiriusXm(root, fs) {
  const io = fs || null;
  if (!io) return { present: false, kind: null };
  if (fileHas(io, at(root, "dev/siriusxm0")) || dirHas(io, at(root, "sys/class/siriusxm"))) {
    return { present: true, kind: "siriusxm-tuner" };
  }
  return { present: false, kind: null };
}

export function probeSatelliteTerminal(root, fs) {
  const io = fs || null;
  if (!io) return { present: false, kind: null };
  const candidates = [
    ["dev/starlink0", "starlink", "file"],
    ["dev/iridium0", "iridium", "file"],
    ["sys/class/starlink", "starlink", "dir"],
    ["sys/class/iridium", "iridium", "dir"],
  ];
  for (const [rel, kind, mode] of candidates) {
    const path = at(root, rel);
    if (mode === "file" ? fileHas(io, path) : dirHas(io, path)) return { present: true, kind };
  }
  return { present: false, kind: null };
}

function flags(enabled, held) {
  return {
    enabled,
    live: false,
    held,
    hardware_live: false,
    packet_live: false,
    transmit: false,
    checkout: false,
    skus: false,
    plans: false,
    spend: false,
    purchased: false,
    paid_ok: false,
    paid_terminal: false,
    worker_hardware: false,
    mock: false,
  };
}

function openBand(id, band, probe, absent, present) {
  const seen = probe.present === true && Boolean(probe.kind);
  const kind = probe.kind || "";
  return {
    id,
    parent: "rf",
    spec: RF_BAND_SPEC,
    band,
    receive_only: true,
    device: "sdr",
    hardware: seen ? kind : false,
    state: seen ? "HW-PRESENT" : "REFUSE",
    code: seen ? null : RADIO_ABSENT,
    mesh_traffic: false,
    note: seen ? present.replace("{kind}", kind) : absent,
    ...flags(true, false),
  };
}

function heldBand(id, band, device, probe, absent, present, extra) {
  const seen = probe.present === true && Boolean(probe.kind);
  const kind = probe.kind || "";
  return {
    id,
    parent: "rf",
    spec: RF_BAND_SPEC,
    band,
    receive_only: true,
    device,
    hardware: seen ? kind : false,
    state: "HELD",
    code: seen ? null : RADIO_ABSENT,
    subscription_held: false,
    mesh_traffic: false,
    note: seen ? present.replace("{kind}", kind) : absent,
    ...flags(false, true),
    ...extra,
  };
}

function relayRow(probe) {
  const seen = probe.present === true && Boolean(probe.kind);
  const kind = probe.kind || "";
  const absent = "Satellite relay stays HELD. Transmit is off. No spend, no SKU, no plan, no checkout. Without a terminal the relay refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.";
  const present = "Satellite relay terminal {kind} is present. The switch stays HELD. Transmit stays off. live, hardware_live, and packet_live stay false. Presence is not a purchase and not a checkout.";
  return {
    id: "satellite_relay",
    spec: RF_BAND_SPEC,
    device: "amateur-or-commercial-terminal",
    hardware: seen ? kind : false,
    state: "HELD",
    code: seen ? null : RADIO_ABSENT,
    software_path: false,
    encryption_allowed: false,
    envelope_spec: "FED-MESH-1.0",
    envelope_kind: "store-and-forward",
    note: seen ? present.replace("{kind}", kind) : absent,
    ...flags(false, true),
  };
}

function bandsOf(root, fs) {
  const sdr = probeSdr(root, fs);
  const tuner = probeSiriusXm(root, fs);
  const am = openBand(
    "am",
    "530-1700 kHz",
    sdr,
    "AM receive needs an SDR. The mesh does not transmit on AM. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
    "AM device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
  );
  const fm = openBand(
    "fm",
    "88-108 MHz",
    sdr,
    "FM receive needs an SDR. The mesh does not transmit on FM. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
    "FM device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
  );
  const sat = openBand(
    "sat_rx",
    "satellite-downlink",
    sdr,
    "Satellite receive (weather, GNSS, amateur downlinks) needs an SDR. Without an SDR the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
    "Satellite receive device {kind} is present. The switch is on. live, hardware_live, and packet_live stay false. This code does not demodulate. Nothing is purchased.",
  );
  sat.kinds = ["weather", "gnss", "amateur-downlink"];
  const xm = heldBand(
    "xm_sdars",
    "2320-2345 MHz",
    "siriusxm-tuner",
    tuner,
    "XM SDARS stays HELD. It needs a licensed SiriusXM tuner and a paid plan. No SKU, no checkout, no spend. Without the tuner the band refuses QNM-RADIO-ABSENT. live, hardware_live, and packet_live stay false.",
    "XM SDARS device {kind} is present. The switch stays HELD. live, hardware_live, and packet_live stay false. No spend, no SKU, no plan, no checkout.",
    { encrypted: true, subscription: true, one_way: true },
  );
  return { am, fm, xm_sdars: xm, sat_rx: sat };
}

function pathRow(row) {
  const body = {
    id: row.id,
    enabled: row.enabled === true,
    live: false,
    hardware_live: false,
    packet_live: false,
    held: row.held === true,
    spend: false,
    checkout: false,
    mock: false,
    phy: SWITCH_PHY[row.id],
  };
  if (row.id === "am" || row.id === "fm" || row.id === "sat_rx" || row.id === "xm_sdars" || row.id === "satellite_relay") {
    body.state = row.state;
    body.code = row.code;
  }
  return body;
}

function switchFive(id) {
  return {
    id,
    enabled: true,
    live: false,
    hardware_live: false,
    packet_live: false,
    held: false,
    spend: false,
    checkout: false,
    mock: false,
    phy: SWITCH_PHY[id],
  };
}

export function rfBandCite(root) {
  const fs = builtin("node:fs");
  const base = root ? String(root) : "";
  const io = fs;
  const bands = bandsOf(base, io);
  const relay = relayRow(probeSatelliteTerminal(base, io));
  const paths = {
    lan: switchFive("lan"),
    wifi: switchFive("wifi"),
    bluetooth: switchFive("bluetooth"),
    rf: switchFive("rf"),
    photon: switchFive("photon"),
    am: pathRow(bands.am),
    fm: pathRow(bands.fm),
    sat_rx: pathRow(bands.sat_rx),
    xm_sdars: pathRow(bands.xm_sdars),
    satellite_relay: pathRow(relay),
  };
  return {
    spec: RF_BAND_SPEC,
    author: AUTHOR,
    traffic_paths_spec: TRAFFIC_SPEC,
    traffic_paths_enabled: true,
    traffic_paths_live: false,
    traffic_paths_open: OPEN_PATHS.slice(),
    traffic_paths_held: HELD_PATHS.slice(),
    paid_satellite_held: true,
    paid_satellite_checkout: false,
    paid_satellite_skus: false,
    paid_satellite_plans: false,
    paid_satellite_spend: false,
    cap7_is_icann: false,
    public_icann: false,
    cap7_public_icann: false,
    cap7_name_only: true,
    cap7_registrar_live: false,
    get_never_enables: true,
    radio_phy: false,
    mock: false,
    paths,
    rf_bands: bands,
    satellite_relay: relay,
  };
}

export function bandRow(cite, id) {
  if (!cite || typeof cite !== "object") return {};
  if (id === "satellite_relay" && cite.satellite_relay && typeof cite.satellite_relay === "object") return cite.satellite_relay;
  const bands = cite.rf_bands;
  if (bands && typeof bands === "object" && bands[id] && typeof bands[id] === "object") return bands[id];
  return {};
}
