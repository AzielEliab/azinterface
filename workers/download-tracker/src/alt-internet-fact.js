/**
 * The not-live sentence aziel-runtime currentAltInternetFact computes.
 * alt_internet_live and packet_path_live stay false. A same-machine frame
 * is not a second device. Cap-7 and .aziel stay names.
 * Author: Aziel Eliab. Identity is Aziel Eliab only.
 */

const RADIO_ABSENT = "QNM-RADIO-ABSENT";
const ORDER = ["lan", "wifi", "bluetooth", "rf", "photon"];
const NET = "/sys/class/net";

export const HEAD =
  "An alternative internet is not live (alt_internet_live is false). A packet path is not live (packet_path_live is false).";

export const TAIL = [
  "Still missing: a packet that leaves this machine and arrives on a different machine id.",
  "A same-machine mesh frame does not count.",
  "Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP.",
  "WireGuard, OpenVPN, an L3 exit pool, kernel UDP, and TUN/TAP stay SLOT.",
  "Public mail send, the kernel, and boot stay not live.",
  "The public door stays FG-STUB.",
  "Isolation is single-node security-awareness.",
  "Phoenix is a local wait and re-seal.",
  "That is not a loopback fence.",
].join(" ");

function builtin(name) {
  try {
    if (typeof process === "undefined" || typeof process.getBuiltinModule !== "function") return null;
    return process.getBuiltinModule(name);
  } catch {
    return null;
  }
}

function carrierClause(id, row) {
  const code = (row && row.code) || RADIO_ABSENT;
  if (!row || row.state === "REFUSE") {
    if (id === "lan" && row && row.up === false && row.hardware) {
      return `LAN interface ${row.hardware} is down (${code}).`;
    }
    if (id === "lan") return `LAN hardware is absent (${code}).`;
    if (id === "wifi") return `Wi-Fi hardware is absent (${code}).`;
    if (id === "bluetooth") return `Bluetooth hardware is absent (${code}).`;
    if (id === "rf") return `RF hardware is absent (${code}).`;
    return `Photon camera or flash is absent (${code}).`;
  }
  if (id === "lan") {
    const where = row.address ? ` at ${row.address}` : "";
    const name = row.hardware || "unnamed";
    return `LAN interface ${name}${where} is present on this machine and is not a second device.`;
  }
  const hw = row.hardware ? ` ${row.hardware}` : "";
  if (id === "wifi") return `Wi-Fi hardware${hw} is present on this machine and is not a second device.`;
  if (id === "bluetooth") return `Bluetooth hardware${hw} is present on this machine and is not a second device.`;
  if (id === "rf") return `RF hardware${hw} is present on this machine and is not a second device.`;
  return `Photon camera or flash hardware${hw} is present on this machine and is not a second device.`;
}

function machineClause(machineId) {
  if (machineId) {
    return `This machine id is ${machineId}. A second device stays false while both ends share that id.`;
  }
  return "This machine id is absent (MESH-HOST-ABSENT). A second device stays false without two different ids.";
}

/** Standing fact for a probe result. visible false does not invent radios. */
export function notLiveSentenceFromProbe({ visible, carriers, machineId } = {}) {
  if (!visible) {
    return `${HEAD} This isolate cannot see host hardware (worker_hardware is false). ${TAIL}`;
  }
  const rows = carriers || {};
  const clauses = ORDER.map((id) => carrierClause(id, rows[id]));
  return `${HEAD} ${clauses.join(" ")} ${machineClause(machineId || null)} ${TAIL}`;
}

function readText(fs, path) {
  try {
    return fs.readFileSync(path, "utf8").trim();
  } catch {
    return "";
  }
}

function hostHardwareVisible(fs) {
  try {
    return fs.existsSync(NET);
  } catch {
    return false;
  }
}

function readMachineId(fs) {
  const text = readText(fs, "/etc/machine-id");
  return /^[a-f0-9]{32}$/.test(text) ? text : null;
}

function dirHasEntries(fs, path) {
  try {
    if (!fs.existsSync(path)) return false;
    const st = fs.statSync(path);
    if (!st.isDirectory()) return false;
    return fs.readdirSync(path).filter((name) => name && name !== "." && name !== "..").length > 0;
  } catch {
    return false;
  }
}

function ifaceUp(fs, pathMod, name) {
  if (readText(fs, pathMod.join(NET, name, "operstate")) !== "up") return false;
  const carrierPath = pathMod.join(NET, name, "carrier");
  if (!fs.existsSync(carrierPath)) return true;
  const carrier = readText(fs, carrierPath);
  return carrier === "1" || carrier === "";
}

function defaultRouteIface(fs) {
  try {
    const text = fs.readFileSync("/proc/net/route", "utf8");
    let fallback = null;
    for (const line of text.split("\n").slice(1)) {
      const cols = line.trim().split(/\s+/);
      if (cols.length < 4) continue;
      const flags = Number.parseInt(cols[3], 16);
      if (!Number.isFinite(flags) || (flags & 1) === 0) continue;
      if (cols[1] !== "00000000") continue;
      const name = cols[0];
      if (!name || name === "lo") continue;
      if (cols[2] && cols[2] !== "00000000") return name;
      if (!fallback) fallback = name;
    }
    return fallback;
  } catch {
    return null;
  }
}

function lanIpv4(os, name) {
  try {
    const rows = os.networkInterfaces()[name] || [];
    const hit = rows.find((addr) => (addr.family === "IPv4" || addr.family === 4) && addr.internal !== true);
    return hit ? hit.address : null;
  } catch {
    return null;
  }
}

function probeLan(fs, os, pathMod) {
  try {
    if (!fs.existsSync(NET)) return { present: false, kind: null, address: null, up: false };
    const names = fs.readdirSync(NET).filter((name) => name && name !== "lo" && name !== "." && name !== "..");
    const preferred = defaultRouteIface(fs);
    if (preferred && preferred !== "lo" && names.includes(preferred) && ifaceUp(fs, pathMod, preferred)) {
      const address = lanIpv4(os, preferred);
      if (address) return { present: true, kind: preferred, address, up: true };
    }
    for (const name of names) {
      if (!ifaceUp(fs, pathMod, name)) continue;
      const address = lanIpv4(os, name);
      if (address) return { present: true, kind: name, address, up: true };
    }
    if (names.length) {
      const name = names[0];
      return { present: true, kind: name, address: lanIpv4(os, name), up: false };
    }
  } catch {
    /* no sysfs */
  }
  return { present: false, kind: null, address: null, up: false };
}

function probeWifi(fs, pathMod) {
  if (dirHasEntries(fs, "/sys/class/ieee80211") || netHasWireless(fs, pathMod)) {
    return { present: true, kind: "ieee80211" };
  }
  return { present: false, kind: null };
}

function netHasWireless(fs, pathMod) {
  try {
    if (!fs.existsSync(NET)) return false;
    for (const name of fs.readdirSync(NET)) {
      if (fs.existsSync(pathMod.join(NET, name, "wireless"))) return true;
    }
    return false;
  } catch {
    return false;
  }
}

function probeBluetooth(fs) {
  if (dirHasEntries(fs, "/sys/class/bluetooth")) return { present: true, kind: "bluetooth" };
  return { present: false, kind: null };
}

function probeRf(fs) {
  if (fs.existsSync("/dev/swradio0") || dirHasEntries(fs, "/sys/class/sdr") || dirHasEntries(fs, "/sys/bus/usb/drivers/dvb_usb_rtl28xxu")) {
    return { present: true, kind: "sdr" };
  }
  return { present: false, kind: null };
}

function probeModem(fs) {
  if (dirHasEntries(fs, "/sys/class/wwan") || fs.existsSync("/dev/cdc-wdm0")) {
    return { present: true, kind: "modem" };
  }
  try {
    if (!fs.existsSync(NET)) return { present: false, kind: null };
    for (const name of fs.readdirSync(NET)) {
      if (/^wwan|^rmnet|^cdc-wdm/i.test(name)) return { present: true, kind: name };
    }
  } catch {
    /* no sysfs */
  }
  return { present: false, kind: null };
}

function probeFlashCamera(fs) {
  if (fs.existsSync("/dev/video0")) return { present: true, kind: "camera" };
  const leds = "/sys/class/leds";
  try {
    if (!fs.existsSync(leds)) return { present: false, kind: null };
    for (const name of fs.readdirSync(leds)) {
      if (/flash|torch/i.test(name)) return { present: true, kind: name };
    }
  } catch {
    /* no leds */
  }
  return { present: false, kind: null };
}

function track2CarrierProbe(fs, os, pathMod) {
  const rfHw = probeRf(fs);
  const modem = probeModem(fs);
  const rf = rfHw.present ? rfHw : modem;
  const rows = [
    ["lan", probeLan(fs, os, pathMod)],
    ["wifi", probeWifi(fs, pathMod)],
    ["bluetooth", probeBluetooth(fs)],
    ["rf", rf],
    ["photon", probeFlashCamera(fs)],
  ];
  const carriers = {};
  for (const [id, probe] of rows) {
    const down = probe.present === true && probe.up === false;
    if (probe.present && !down) {
      carriers[id] = {
        id,
        state: "HW-PRESENT",
        hardware: probe.kind,
        address: probe.address || null,
        up: true,
        code: null,
        mock: false,
      };
    } else if (down) {
      carriers[id] = {
        id,
        state: "REFUSE",
        hardware: probe.kind,
        address: probe.address || null,
        up: false,
        code: RADIO_ABSENT,
        mock: false,
      };
    } else {
      carriers[id] = {
        id,
        state: "REFUSE",
        hardware: false,
        address: null,
        up: false,
        code: RADIO_ABSENT,
        mock: false,
      };
    }
  }
  return { carriers };
}

/** The sentence this process can actually compute. No caller watch. Flags stay false. */
export function notLiveSentence() {
  const fs = builtin("node:fs");
  const os = builtin("node:os");
  const pathMod = builtin("node:path");
  if (!fs || !os || !pathMod || !hostHardwareVisible(fs)) {
    return notLiveSentenceFromProbe({ visible: false });
  }
  try {
    const probe = track2CarrierProbe(fs, os, pathMod);
    return notLiveSentenceFromProbe({
      visible: true,
      carriers: probe.carriers,
      machineId: readMachineId(fs),
    });
  } catch {
    return notLiveSentenceFromProbe({
      visible: true,
      carriers: {},
      machineId: readMachineId(fs),
    });
  }
}
