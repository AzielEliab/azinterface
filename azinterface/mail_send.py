"""Local SMTP handoff on the existing suite door.

The desk submits one message to an SMTP host named in the request.
sent is true only when that host accepts the recipients.
Mail send does not run on the public worker. This does not store a username.
"""

from __future__ import annotations

import re
import smtplib
from email.message import EmailMessage
from typing import Any

_ADDR = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _local(body: dict[str, Any]) -> dict[str, Any]:
    body["public_worker_mail_send"] = False
    return body


def submit_smtp(payload: dict[str, Any]) -> dict[str, Any]:
    sender = str(payload.get("from") or payload.get("sender") or "").strip()
    recipient = str(payload.get("to") or payload.get("recipient") or "").strip()
    subject = str(payload.get("subject") or "").strip()
    body = str(payload.get("body") or "").strip()
    host = str(payload.get("host") or "").strip()
    port = payload.get("port")
    problem = _problem(sender, recipient, subject, body, host, port)
    if problem:
        return _local({"ok": False, "sent": False, "error": problem, "status": "The message was not submitted."})
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    raw = message.as_bytes()
    try:
        with smtplib.SMTP(host, int(port), timeout=5) as smtp:
            refused = smtp.sendmail(sender, [recipient], raw)
    except (OSError, smtplib.SMTPException) as exc:
        return _local({
            "ok": False,
            "sent": False,
            "error": f"SMTP did not accept the message. {exc}",
            "status": "SMTP did not accept the message.",
        })
    if refused:
        return _local({
            "ok": False,
            "sent": False,
            "refused": {str(key): str(val) for key, val in refused.items()},
            "status": "SMTP did not accept the message.",
        })
    return _local({
        "ok": True,
        "sent": True,
        "accepted": [recipient],
        "from": sender,
        "subject": subject,
        "bytes": len(raw),
        "status": (
            "The named SMTP host accepted this message. "
            "sent names that host only. "
            "Public mail send is not live. "
            "public_worker_mail_send is false. "
            "Mail send does not run on the public worker."
        ),
    })


def mail_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZMail</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
* { box-sizing: border-box; }
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; max-width:40rem; }
h1 { font-size:1.35rem; margin:0 0 0.35rem; }
p, label { color:var(--muted); }
label { display:block; margin:0.45rem 0 0.15rem; }
input, textarea { font:inherit; width:100%; min-height:44px; padding:0.4rem 0.55rem; border:1px solid var(--line); border-radius:10px; background:transparent; color:inherit; }
textarea { min-height:7rem; }
button { font:inherit; min-height:44px; border-radius:10px; background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.45rem 0.8rem; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
#status { min-height:1.5rem; white-space:pre-wrap; }
</style>
</head>
<body>
<main>
  <h1>AZMail</h1>
  <p>This desk hands a message to the SMTP host named here. sent names that host only. Public mail send is not live. Mail send does not run on the public worker. public_worker_mail_send stays false. The desk reports acceptance only after that host takes the recipients.</p>
  <label for="from">From</label>
  <input id="from" autocomplete="off">
  <label for="to">To</label>
  <input id="to" autocomplete="off">
  <label for="subject">Subject</label>
  <input id="subject" autocomplete="off">
  <label for="body">Message</label>
  <textarea id="body"></textarea>
  <label for="host">SMTP host</label>
  <input id="host" autocomplete="off">
  <label for="port">SMTP port</label>
  <input id="port" inputmode="numeric" autocomplete="off">
  <p><button id="send" type="button">Send</button></p>
  <p id="status" role="status">No message has been submitted.</p>
</main>
<script>
document.getElementById("send").addEventListener("click", function () {
  var status = document.getElementById("status");
  status.textContent = "Submitting the message…";
  var body = {
    from: document.getElementById("from").value,
    to: document.getElementById("to").value,
    subject: document.getElementById("subject").value,
    body: document.getElementById("body").value,
    host: document.getElementById("host").value,
    port: Number(document.getElementById("port").value)
  };
  fetch("/suite/azmail/send", {
    method: "POST",
    headers: { "content-type": "application/json", "accept": "application/json" },
    body: JSON.stringify(body)
  }).then(function (res) { return res.json(); }).then(function (data) {
    status.textContent = data.status || data.error || "The message was not submitted.";
  }).catch(function () {
    status.textContent = "The message was not submitted.";
  });
});
</script>
</body>
</html>
"""


def _problem(sender: str, recipient: str, subject: str, body: str, host: str, port: Any) -> str | None:
    if not _ADDR.fullmatch(sender) or not _ADDR.fullmatch(recipient):
        return "Mail send needs a from address and a to address."
    if not subject or len(body) < 12 or not any(ch.isalpha() for ch in body):
        return "Mail send needs a subject and a message."
    if not host or any(ch.isspace() for ch in host):
        return "Mail send needs an SMTP host."
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        return "Mail send needs an SMTP port."
    return None
