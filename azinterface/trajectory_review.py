"""TrajectoryLock review on the suite desk.

Pulls a NASA GIBS MODIS Terra true-color tile for an event place and time.
A frame is returned only when the bytes are a JPEG. Otherwise the review
names the gap. No stand-in image.
"""

from __future__ import annotations

import base64
import json
import math
from datetime import datetime, timedelta
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import Request, urlopen
import urllib.error

SOURCE = "NASA GIBS"
PRODUCT = "MODIS_Terra_CorrectedReflectance_TrueColor"
ZOOM = 8
SEARCH_DAYS = 7
USER_AGENT = "Mozilla/5.0 TrajectoryLock/0.1 (local research workbench; Aziel Eliab)"
JPEG = b"\xff\xd8\xff"
Fetch = Callable[[str], tuple[int, bytes]]


def review_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TrajectoryLock review</title>
<style>
:root { color-scheme: light dark; --bg:#f4f0e6; --ink:#1a1713; --muted:#5c564a; --line:#ddd4c2; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#100f0c; --ink:#f4efe4; --muted:#c8bfae; --line:#3d382e; }
}
body { margin:0; font:16px/1.5 ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
main { padding:1rem 1.1rem 2rem; max-width:44rem; }
label { display:block; margin:0.55rem 0 0.2rem; }
input { font:inherit; width:100%; min-height:44px; padding:0.4rem 0.55rem; border:1px solid var(--line); border-radius:10px; background:transparent; color:inherit; }
button { font:inherit; min-height:44px; margin-top:0.8rem; border-radius:10px; background:#c9a227; color:#1a1404; border:0; font-weight:650; padding:0.55rem 0.9rem; }
:focus-visible { outline:2px solid #c9a227; outline-offset:3px; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; }
p, label { color:var(--muted); }
img { max-width:100%; height:auto; border:1px solid var(--line); border-radius:12px; margin-top:0.8rem; }
</style>
</head>
<body>
<main>
  <h1>TrajectoryLock</h1>
  <p>Enter the event place and time. Run check pulls a NASA GIBS frame for that place at or nearest that time, then traces what was measured.</p>
  <form id="review">
    <label for="place">Place</label>
    <input id="place" name="place" autocomplete="off" placeholder="City or site">
    <label for="lat">Latitude</label>
    <input id="lat" name="lat" inputmode="decimal" placeholder="34.05">
    <label for="lon">Longitude</label>
    <input id="lon" name="lon" inputmode="decimal" placeholder="-118.25">
    <label for="when">Event time</label>
    <input id="when" name="when" placeholder="2020-06-15T18:00:00Z">
    <button id="run-check" type="submit">Run check</button>
  </form>
  <img id="frame" alt="" hidden>
  <pre id="trace">No frame yet. A picture appears here only after NASA GIBS returns a JPEG.</pre>
</main>
<script>
document.getElementById("review").addEventListener("submit", async function (ev) {
  ev.preventDefault();
  var trace = document.getElementById("trace");
  var frame = document.getElementById("frame");
  var button = document.getElementById("run-check");
  frame.hidden = true;
  frame.removeAttribute("src");
  trace.textContent = "Pulling the frame…";
  button.disabled = true;
  var body = {
    place: document.getElementById("place").value,
    lat: document.getElementById("lat").value,
    lon: document.getElementById("lon").value,
    time: document.getElementById("when").value
  };
  try {
    var res = await fetch("/suite/trajectorylock/review", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    });
    var data = await res.json();
    trace.textContent = data.trace || data.error || "The review returned no trace.";
    if (data.image_jpeg_b64) {
      frame.alt = "NASA GIBS true color for " + (data.frame_time || "the event");
      frame.src = "data:image/jpeg;base64," + data.image_jpeg_b64;
      frame.hidden = false;
    }
  } catch (e) {
    trace.textContent = "The review could not be reached on this computer. Stay on the suite page and run the check again.";
  }
  button.disabled = false;
});
</script>
</body>
</html>
"""


def default_fetch(url: str) -> tuple[int, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/jpeg,application/json;q=0.9,*/*;q=0.8"})
    try:
        with urlopen(req, timeout=20) as res:
            return int(res.status), res.read(2_000_000)
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(8000)
        except Exception:  # noqa: BLE001
            body = b""
        return int(exc.code), body
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, b""


def review_event(
    *,
    place: str = "",
    lat: Any = None,
    lon: Any = None,
    when: str = "",
    fetch: Fetch | None = None,
) -> dict[str, Any]:
    """Review one event. `fetch` is injected in tests so they do not touch the network."""
    getter = fetch or default_fetch
    claimed_place = (place or "").strip()
    claimed_time = (when or "").strip()
    event = _parse_when(claimed_time)
    gaps: list[str] = []
    if event is None:
        gaps.append("Event time is missing or is not a date this review can read.")
        return _finish(ok=False, claimed_place=claimed_place, claimed_time=claimed_time, gaps=gaps)

    coords = _coords(lat, lon)
    geocoded = None
    if coords is None and claimed_place:
        coords, geocoded, geo_gap = _geocode(claimed_place, getter)
        if geo_gap:
            gaps.append(geo_gap)
    if coords is None:
        if not claimed_place:
            gaps.append("No place and no latitude/longitude were given.")
        return _finish(
            ok=False,
            claimed_place=claimed_place,
            claimed_time=claimed_time,
            event=event,
            gaps=gaps,
            geocoded=geocoded,
        )

    lat_f, lon_f = coords
    tx, ty = _tile_xy(lat_f, lon_f, ZOOM)
    found: tuple[datetime, str, bytes] | None = None
    for delta in sorted(range(-SEARCH_DAYS, SEARCH_DAYS + 1), key=lambda item: (abs(item), item)):
        day = event + timedelta(days=delta)
        stamp = day.strftime("%Y-%m-%d")
        url = _tile_url(stamp, ZOOM, tx, ty)
        status, body = getter(url)
        if status == 200 and body.startswith(JPEG):
            found = (day, url, body)
            break
        if status == 0 and delta == 0:
            gaps.append("NASA GIBS could not be reached from this computer.")
    if found is None:
        if not any("could not be reached" in gap for gap in gaps):
            gaps.append(
                f"NASA GIBS returned no JPEG for this place within {SEARCH_DAYS} days of {event.date().isoformat()}."
            )
        return _finish(
            ok=False,
            claimed_place=claimed_place,
            claimed_time=claimed_time,
            event=event,
            lat=lat_f,
            lon=lon_f,
            tile=(ZOOM, tx, ty),
            gaps=gaps,
            geocoded=geocoded,
        )

    frame, url, blob = found
    delta_days = (frame.date() - event.date()).days
    if delta_days != 0:
        gaps.append(
            f"The nearest NASA GIBS frame is {frame.date().isoformat()}, {abs(delta_days)} day(s) from the event date."
        )
    return _finish(
        ok=True,
        claimed_place=claimed_place,
        claimed_time=claimed_time,
        event=event,
        lat=lat_f,
        lon=lon_f,
        tile=(ZOOM, tx, ty),
        frame=frame,
        delta_days=delta_days,
        image=blob,
        source_url=url,
        gaps=gaps,
        geocoded=geocoded,
    )


def accept_product_imagery(data: dict[str, Any]) -> dict[str, Any] | None:
    """Keep a product imagery payload only when its picture is a real JPEG or it names gaps."""
    if not isinstance(data, dict):
        return None
    raw = data.get("image_jpeg_b64") or data.get("jpeg_b64")
    if raw:
        try:
            blob = base64.b64decode(str(raw), validate=False)
        except Exception:  # noqa: BLE001
            return None
        if not blob.startswith(JPEG):
            return None
        data = dict(data)
        data["image_jpeg_b64"] = base64.b64encode(blob).decode("ascii")
        data["imagery_via"] = "trajectorylock ui"
        return data
    if data.get("gaps"):
        data = dict(data)
        data["image_jpeg_b64"] = None
        data["imagery_via"] = "trajectorylock ui"
        return data
    return None


def _finish(
    *,
    ok: bool,
    claimed_place: str,
    claimed_time: str,
    gaps: list[str],
    event: datetime | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tile: tuple[int, int, int] | None = None,
    frame: datetime | None = None,
    delta_days: int | None = None,
    image: bytes | None = None,
    source_url: str | None = None,
    geocoded: str | None = None,
) -> dict[str, Any]:
    image_b64 = None
    if image and image.startswith(JPEG):
        image_b64 = base64.b64encode(image).decode("ascii")
    claimed = {"place": claimed_place or None, "time": claimed_time or None}
    measured: dict[str, Any] = {
        "source": SOURCE,
        "product": PRODUCT,
        "lat": lat,
        "lon": lon,
        "frame_time": frame.date().isoformat() if frame else None,
        "time_delta_days": delta_days,
        "geocoded_name": geocoded,
    }
    if tile:
        measured["tile"] = {"z": tile[0], "x": tile[1], "y": tile[2]}
    lines = [
        f"Claimed: {claimed_place or 'coordinates only'} at {claimed_time or 'no time'}.",
        f"Measured: source {SOURCE}, product {PRODUCT}.",
    ]
    if lat is not None and lon is not None:
        lines.append(f"Measured coordinates: {lat:.5f}, {lon:.5f}.")
    if geocoded:
        lines.append(f"Geocoded name: {geocoded}.")
    if frame is not None and delta_days is not None:
        lines.append(f"Frame date {frame.date().isoformat()} ({delta_days} days from the event date).")
    if image_b64 and source_url:
        lines.append(f"Imagery evidence: JPEG from {source_url}.")
    else:
        lines.append("Imagery evidence: none. No JPEG was returned.")
    if gaps:
        lines.append("Gaps: " + " ".join(gaps))
    else:
        lines.append("Gaps: none on the imagery pull.")
    return {
        "ok": ok and bool(image_b64),
        "source": SOURCE,
        "product": PRODUCT,
        "place": claimed_place or None,
        "lat": lat,
        "lon": lon,
        "event_time": event.isoformat() if event else None,
        "frame_time": frame.date().isoformat() if frame else None,
        "time_delta_days": delta_days,
        "image_jpeg_b64": image_b64,
        "source_url": source_url if image_b64 else None,
        "gaps": gaps,
        "claimed": claimed,
        "measured": measured,
        "trace": "\n".join(lines),
    }


def _parse_when(text: str) -> datetime | None:
    if not text:
        return None
    cleaned = text.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _coords(lat: Any, lon: Any) -> tuple[float, float] | None:
    if lat is None or lon is None:
        return None
    if isinstance(lat, str) and not lat.strip():
        return None
    if isinstance(lon, str) and not lon.strip():
        return None
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return None
    return lat_f, lon_f


def _geocode(place: str, fetch: Fetch) -> tuple[tuple[float, float] | None, str | None, str | None]:
    url = "https://nominatim.openstreetmap.org/search?q=" + quote(place) + "&format=jsonv2&limit=1"
    status, body = fetch(url)
    if status != 200 or not body:
        return None, None, "The place could not be geocoded (Nominatim did not answer)."
    try:
        rows = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None, "The place could not be geocoded (Nominatim did not return JSON)."
    if not isinstance(rows, list) or not rows:
        return None, None, f"No coordinates were found for {place}."
    row = rows[0] if isinstance(rows[0], dict) else {}
    coords = _coords(row.get("lat"), row.get("lon"))
    if coords is None:
        return None, None, f"No coordinates were found for {place}."
    name = str(row.get("display_name") or place)
    return coords, name, None


def _tile_xy(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    lat = max(-85.0, min(85.0, lat))
    n = 2**zoom
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n)
    return max(0, min(n - 1, x)), max(0, min(n - 1, y))


def _tile_url(day: str, zoom: int, x: int, y: int) -> str:
    return (
        "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
        f"{PRODUCT}/default/{day}/GoogleMapsCompatible_Level9/{zoom}/{y}/{x}.jpg"
    )
