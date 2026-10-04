function humanLines(obj) {
  var lines = [];
  function push(text) {
    if (!text) return;
    if (lines.indexOf(text) !== -1) return;
    lines.push(text);
  }
  if (!obj || typeof obj !== "object") {
    push("Done.");
    return lines;
  }
  var display = obj.display && typeof obj.display === "object" ? obj.display : null;
  if (display && display.title) push(sentence(display.title));
  if (display && display.summary) push(codeToSentence(display.summary));
  var fields = (display && display.fields) || [];
  for (var i = 0; i < fields.length; i++) {
    var row = fields[i];
    if (!row || row.label == null) continue;
    push(fieldSentence(String(row.label), row.value, obj));
  }
  if (!display) {
    if (obj.error) push(sentence(obj.error));
    else if (obj.note) push(sentence(obj.note));
  }
  if (Array.isArray(obj.pairs)) {
    for (var p = 0; p < obj.pairs.length; p++) {
      var pair = obj.pairs[p];
      if (!pair || typeof pair !== "object") continue;
      var id = pair.pair_id || "a cite";
      var hand = pair.handshake ? " The handshake is " + pair.handshake + "." : "";
      var via = pair.via ? " The via is " + pair.via + "." : "";
      push("A pair cite " + id + " is stored." + hand + via);
    }
  }
  if (Array.isArray(obj.witnesses)) {
    var n = 0;
    for (var w = 0; w < obj.witnesses.length; w++) {
      if (obj.witnesses[w] && typeof obj.witnesses[w] === "object") n += 1;
    }
    if (n) push(n === 1 ? "1 witness is listed. The row is metadata." : n + " witnesses are listed. The rows are metadata.");
  }
  if (obj.ok === false) {
    var blob = lines.join(" ");
    var explained = /refus|cannot|can't|terminal|failed|stub|required|unknown|not one of|not accepted|never/i.test(blob);
    if (!explained) {
      if (obj.error && lines.indexOf(sentence(obj.error)) === -1) push(sentence(obj.error));
      else if (obj.code && knownCode(obj.code)) push(knownCode(obj.code));
      else if (obj.code) push("This request was refused. The reason is " + obj.code + ".");
      else push("This request was refused.");
    }
    if (!/refus/i.test(lines.join(" "))) push("This step is refused.");
  }
  if (obj.next && lines.join(" ").indexOf(String(obj.next)) === -1) push("Next: " + obj.next);
  if (!lines.length) push("Done.");
  return lines;
}

function sentence(text) {
  var s = String(text == null ? "" : text).trim();
  if (!s) return "";
  if (/[.!?]$/.test(s)) return s;
  return s + ".";
}

function looksLikeCode(text) {
  return /^[A-Z0-9][A-Z0-9_.-]{2,}$/.test(String(text || "").trim());
}

function knownCode(code) {
  var map = {
    "AIH-CYCLE-TERMINAL": "Memorial is the last page. It cannot be left.",
    "AIH-CYCLE-LOCKED": "That step is refused. The page moves one step at a time.",
    "AIH-CYCLE-UNKNOWN": "That name is not one of the five sealed pages.",
    "AIH-INTEGRITY-REQUIRED": "ON is refused until an integrity check has passed.",
    "GENESIS_SEED_REQUIRED": "A one-time seed is required. It is hashed and then discarded.",
    "GENESIS_ALREADY_KEYED": "The genesis key is already set. It cannot be set again.",
    "INTEGRITY_FAIL": "Integrity failed. The page stays locked, and ON is refused.",
    "STUB": "This action is refused. It is not live.",
    "FG-HALLUC-TOOL": "That operation is not known.",
    "PRE_LOCKED": "The page is still locked. Living presence is off.",
    "HOLD_NOT_FOUND": "That hold is not in the witness list.",
    "PAIR_NOT_FOUND": "That pair cite is not stored.",
    "PAIR_EXISTS": "That pair cite is already stored.",
    "PAIR_CAP": "The pair list is full. No new cite was stored.",
    "QNS-HANDSHAKE-LOCKED": "That pair step is refused. The handshake is not at the required stage.",
    "SCORCH_LOCAL_ADVISORY": "This is a local advisory. It does not wipe another device."
  };
  return map[code] || "";
}

function codeToSentence(text) {
  var raw = String(text || "").trim();
  var known = knownCode(raw);
  if (known) return known;
  if (looksLikeCode(raw)) return "This request was refused. The reason is " + raw + ".";
  return sentence(raw);
}

function yn(value) {
  if (value === true || value === "true" || value === "True") return true;
  if (value === false || value === "false" || value === "False") return false;
  return null;
}

function fieldSentence(label, value, obj) {
  var key = String(label);
  var flag = yn(value);
  var text = value == null ? "" : String(value);
  if (key === "site_state" || key === "current" || key === "cycle") return "The page is " + (text || "OFF") + ".";
  if (key === "living_presence") return flag === false ? "Living presence is off." : "Living presence is on.";
  if (key === "integrity_ok") return flag === false ? "Integrity has not passed." : "Integrity has passed.";
  if (key === "next") return text ? "The next sealed step is " + text + "." : "There is no next step. Memorial stays in place.";
  if (key === "requested") return "The requested step was " + text + ".";
  if (key === "from") return "It moved from " + text + ".";
  if (key === "to") return "It moved to " + text + ".";
  if (key === "genesis_hash") return text ? "The genesis hash is " + text + "." : "No genesis hash is stored.";
  if (key === "keyed" || key === "genesis_keyed") return flag === false ? "A genesis key is not set." : "A genesis key is set.";
  if (key === "username_stored") return flag === true ? "The username was stored." : "The username is not stored.";
  if (key === "genesis_sealed" || key === "cycles_sealed") return "The five page steps are sealed.";
  if (key === "cloud_asleep") return "There is no cloud-asleep mode.";
  if (key === "remote_wipe") return "This does not wipe another device.";
  if (key === "local_only") return "This stays on this computer.";
  if (key === "vault_contents") return "Vault contents are not shown.";
  if (key === "hub_collapse") return "Interface is not Hub.";
  if (key === "lambgate") return "LambGate is not part of this path.";
  if (key === "software_tab" || key === "softwares_tab_qns") return "This is not an extra door.";
  if (key === "version") return "The version is " + text + ".";
  if (key === "spec") return "The spec is " + text + ".";
  if (key === "digest") return text ? "The integrity record is " + text + "." : "";
  if (key === "pipeline" || key === "path") return "The path is cited. FragGate remains the door.";
  if (key === "owner" || key === "pipeline_owner") return "The fabric owner is " + (text || "aziel-runtime") + ".";
  if (key === "4dmap") return "4DMap is an inspection frame on aziel-runtime, and it is not an extra door.";
  if (key === "qns_cd") return "Pair custody follows " + text + ".";
  if (key === "qnsd") return "The via runs on " + text + ".";
  if (key === "count") return "The count is " + text + ".";
  if (key === "op") return "The operation was " + text.replace(/_/g, " ") + ".";
  if (key === "code") {
    if (obj && obj.ok === false) return knownCode(text) || ("This request was refused. The reason is " + text + ".");
    if (text === "SCORCH_LOCAL_ADVISORY") return "This is a local advisory. It does not wipe another device.";
    return "";
  }
  if (key === "event") return "The refused event was " + text.replace(/_/g, " ") + ".";
  if (key === "allowed") return "The allowed vias are " + text + ".";
  if (key === "handshake") return text ? "The handshake is " + text + "." : "";
  if (key === "via") return text ? "The via is " + text + "." : "";
  if (key === "pair_id") return text ? "The pair cite is " + text + "." : "";
  if (key === "photon_id") return text ? "The photon cite is " + text + "." : "";
  if (key === "hold_id") return text ? "The hold cite is " + text + "." : "";
  if (key === "status") return text ? "The record is " + text + "." : "";
  if (key === "join_live") return flag === true ? "A news item landed as a pin." : "No news item has landed as a pin.";
  if (flag === false) return "The " + key.replace(/_/g, " ") + " is off.";
  if (flag === true) return "The " + key.replace(/_/g, " ") + " is on.";
  if (!text) return "";
  if (looksLikeCode(text)) return codeToSentence(text);
  return sentence(key.replace(/_/g, " ") + " is " + text);
}
