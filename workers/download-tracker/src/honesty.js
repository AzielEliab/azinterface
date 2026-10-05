/**
 * Standing facts shared with aziel-runtime and AZ-OS.
 * A caller who posts a live flag does not change these facts.
 * software_count stays 33. The runtime Softwares catalog stays a different list.
 * Author: Aziel Eliab. Identity is Aziel Eliab only.
 */

/** SHA-256 of public/azinterface-0.1.0.tar.gz */
export const COUNTED_TARBALL_SHA256 =
  "0282a37a5edbdd8b8a15e0b148ebd5aabd0ffe8eaf78b10bc94c1e012c457a5b";

export const VEILLOCK_STATUS =
  "VeilLock stays local_only. It is not a public-door live and has no public FragGate door.";

export const STANDING_SENTENCES = Object.freeze([
  "Internet base is present. Not live.",
  "Not an OS yet.",
  "The kernel base is present. It has not booted a machine.",
  "Public mail send is not live.",
  "VeilLock stays local_only. It is not a public-door live and has no public FragGate door.",
  "Whitestone is worker-only and has no public FragGate door.",
]);

const FALSE_FLAGS = Object.freeze([
  "alt_internet_live",
  "packet_path_live",
  "second_device",
  "mail_send",
  "public_smtp_send",
  "public_worker_mail_send",
  "kernel_base",
  "booted",
  "installed",
  "os_yet",
  "public_worker_boot",
  "public_worker_kernel",
  "host_os_booted",
]);

export function standingText() {
  return STANDING_SENTENCES.join(" ");
}

/** Facts a posted payload cannot flip. `caller` is ignored on purpose. */
export function standingFacts(caller) {
  void caller;
  return {
    alt_internet_live: false,
    packet_path_live: false,
    second_device: false,
    mail_send: false,
    public_smtp_send: false,
    public_worker_mail_send: false,
    kernel: false,
    kernel_base: false,
    booted: false,
    installed: false,
    os_yet: false,
    is_os: false,
    public_worker_boot: false,
    public_worker_kernel: false,
    host_kernel: false,
    host_os_booted: false,
    internet_base: { present: true, live: false, installed: false },
    veillock: "local_only",
    veillock_public_door: false,
    whitestone_worker_only: true,
    whitestone_public_door: false,
    public_door: "FG-STUB",
    smtp_send: "FG-STUB",
    wireguard: "SLOT",
    openvpn: "SLOT",
    l3: "SLOT",
    kernel_udp: "SLOT",
    tun_tap: "SLOT",
    isolation: "single-node security-awareness",
    phoenix: "local wait and re-seal",
    lines: {
      internet: STANDING_SENTENCES[0],
      os: STANDING_SENTENCES[1],
      kernel: STANDING_SENTENCES[2],
      mail: STANDING_SENTENCES[3],
      veillock: STANDING_SENTENCES[4],
      whitestone: STANDING_SENTENCES[5],
    },
    text: standingText(),
  };
}

/** Write the standing facts onto a status object. Caller flags are not copied. */
export function sealStanding(body, caller) {
  const facts = standingFacts(caller);
  body.honesty = facts;
  for (const key of FALSE_FLAGS) body[key] = false;
  return body;
}
