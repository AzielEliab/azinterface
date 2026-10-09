/**
 * AZInterface human page for AZNews + 4DMap (GET /aznews, alias /newsmap).
 * Everything on it is read through this host's newsmap door (the one aziel-runtime
 * FragGate door, slug 4dmap): one globe read marked as a look (?view=1, mints the view
 * receipts for the headlines it shows) and one status read (dry_run, mints nothing).
 * Map: equirectangular, Natural Earth land, colored pins, color key, last 10, permalinks
 * (?pin=pin-N). No second map, no store copy, nothing installed. Author: Aziel Eliab.
 */
import { LAND_PATH, LAND_SOURCE } from "./land-110m.js";

export const NEWSMAP_PAGE_PATHS = Object.freeze(["/aznews", "/newsmap"]);
export const RUNTIME_GLOBE = "https://aziel-runtime.vibelock.workers.dev/aznews";

const PAGE = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZNews + 4DMap — AZInterface — Aziel Eliab</title>
<meta name="description" content="AZNews headlines, Open-Meteo weather, the computed sky, and 4DMap colored pins, read through the AZInterface newsmap door. Author Aziel Eliab.">
<style>
body{font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0d1117;color:#e6edf3}
.wrap{max-width:1180px;margin:0 auto;padding:16px}
a{color:#79c0ff}h1{font-size:22px;margin:4px 0}h2{font-size:17px;margin:18px 0 6px}
.muted{color:#8b949e}.flags span{display:inline-block;margin:2px 6px 2px 0;padding:2px 8px;border-radius:10px;background:#21262d}
.flags .t{background:#1f6f3f}.flags .f{background:#6e2b2b}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:16px}@media(max-width:860px){.grid{grid-template-columns:1fr}}
#map{width:100%;height:auto;background:#0b2239;border:1px solid #30363d;border-radius:8px}
#map .land{fill:#2d3b2d;stroke:#4b5b4b;stroke-width:.15}#map .grat{stroke:#1d3a57;stroke-width:.15;fill:none}
#map circle{stroke:#000;stroke-width:.25;cursor:pointer}#map circle.sel{stroke:#fff;stroke-width:.8}
.panel{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 12px}
ul{padding-left:18px;margin:6px 0}li{margin:3px 0}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;border:1px solid #000;margin-right:6px;vertical-align:middle}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #30363d;padding:3px 6px;text-align:left;font-size:13px}
</style></head><body><div class="wrap">
<p class="muted"><a href="/">AZInterface</a> · <a href="__GLOBE__">runtime globe</a> · <a href="/v1/newsmap">/v1/newsmap</a> · <a href="/openapi.json">openapi</a></p>
<h1>AZNews + 4DMap</h1>
<p class="muted" id="plain">Reading the newsmap door… Until it answers, nothing here reads live, joined, or merged.</p>
<div class="flags" id="flags"></div>
<div class="grid">
  <div>
    <svg id="map" viewBox="0 0 360 180" role="img" aria-label="World map with AZNews and 4DMap pins">
      <g class="grat" id="grat"></g><path class="land" d="__LAND__"></path><g id="pins"></g>
    </svg>
    <p class="muted" style="font-size:12px">Map: equirectangular. Land: __LANDSRC__. Pins with no resolved place are listed but not drawn.</p>
    <div class="panel" id="detail"><span class="muted">Select a pin to see it here. Each pin has a permalink.</span></div>
    <h2>Headlines</h2><div id="news" class="panel muted">Loading…</div>
  </div>
  <div>
    <h2>Color key</h2><div id="key" class="panel"></div>
    <h2>Last 10 pins</h2><div id="last" class="panel muted">Loading…</div>
    <h2>Sky</h2><div id="sky" class="panel muted">Loading…</div>
    <h2>Weather</h2><div id="weather" class="panel muted">Loading…</div>
  </div>
</div>
<h2>How this page reads</h2>
<p class="muted" id="how">This page keeps no copy of the news and runs no engine. It makes two reads through this host's newsmap door to the aziel-runtime FragGate door (slug 4dmap): <code>GET /v1/newsmap/globe?view=1</code>, which counts as one look and mints the view receipts for the headlines shown, and <code>GET /v1/newsmap</code>, which is forwarded with dry_run and mints nothing. The door checks the pin ↔ item join itself before it shows joined. Author: Aziel Eliab.</p>
</div>
<script>
(function(){
  var RT = "__RTORIGIN__";
  function el(t, txt, cls){ var e=document.createElement(t); if(txt!=null) e.textContent=String(txt); if(cls) e.className=cls; return e; }
  function clear(id){ var e=document.getElementById(id); e.textContent=""; e.classList.remove("muted"); return e; }
  function safeHref(u){ u=String(u||""); return u.indexOf("https://")===0 ? u : null; }
  function hexOk(h){ return /^#[0-9a-fA-F]{3,8}$/.test(String(h||"")) ? h : "#999"; }
  var grat=document.getElementById("grat"), ns="http://www.w3.org/2000/svg";
  for (var x=0;x<=360;x+=30){ var l=document.createElementNS(ns,"line"); l.setAttribute("x1",x);l.setAttribute("x2",x);l.setAttribute("y1",0);l.setAttribute("y2",180); grat.appendChild(l); }
  for (var y=0;y<=180;y+=30){ var m=document.createElementNS(ns,"line"); m.setAttribute("x1",0);m.setAttribute("x2",360);m.setAttribute("y1",y);m.setAttribute("y2",y); grat.appendChild(m); }
  var wanted = new URLSearchParams(location.search).get("pin");
  var COLORS = {}, byId = {};
  function colorOf(p){ return hexOk(p.color_hex || (COLORS[p.pin_type] && COLORS[p.pin_type].hex)); }
  function show(p){
    var box=clear("detail");
    var h=el("b", p.event || p.pin_id); box.appendChild(h); box.appendChild(el("br"));
    var c=COLORS[p.pin_type]||{}; box.appendChild(el("span", (c.color||p.color||"") + " · " + (c.label||p.pin_type||""), "muted")); box.appendChild(el("br"));
    box.appendChild(el("span", "Date: " + (p.date || "undated"))); box.appendChild(el("br"));
    var g=p.geo; box.appendChild(el("span", "Place: " + (g ? (g.name||"") + " (" + Number(g.lat).toFixed(3) + ", " + Number(g.lon).toFixed(3) + ")" : "none resolved" + (p.geo_reason ? " (" + p.geo_reason + ")" : ""))));
    if (p.report_location_source){ box.appendChild(el("br")); box.appendChild(el("span", "Report location source: " + p.report_location_source)); }
    box.appendChild(el("br"));
    var a=el("a","Permalink ?pin=" + p.pin_id); a.href="?pin=" + encodeURIComponent(p.pin_id); box.appendChild(a);
    box.appendChild(document.createTextNode(" · "));
    var r=el("a","runtime pin"); r.href=RT + "/aznews?pin=" + encodeURIComponent(p.pin_id); box.appendChild(r);
    document.querySelectorAll("#map circle").forEach(function(cn){ cn.classList.toggle("sel", cn.getAttribute("data-pin")===p.pin_id); });
  }
  function flags(nm){
    var f=clear("flags");
    [["live",nm.live],["joined",nm.joined],["merged",nm.merged],["lattice_live",nm.lattice_live],["standalone",nm.standalone],["installed",nm.installed]].forEach(function(k){ f.appendChild(el("span", k[0] + ": " + (k[1]===true), k[1]===true ? "t" : "f")); });
    var c=nm.door_join_check;
    document.getElementById("plain").textContent = nm.joined===true
      ? "This door checked the join itself just now: the newest stored item (" + (c&&c.item_id) + ") has " + (c&&c.pins_on_item) + " pin(s), and pin " + (c&&c.pin_id) + " opens that same item with a matching report hash. The runtime's own join check agrees."
      : "Not shown as joined here: " + (nm.join_reason || "the door did not answer") + ". Live, joined and merged read false on this page.";
  }
  async function getJson(u){ var r=await fetch(u,{headers:{accept:"application/json"}}); return r.json(); }
  getJson("/v1/newsmap").then(flags).catch(function(){ document.getElementById("plain").textContent="The newsmap door did not answer. Nothing here reads live."; });
  getJson("/v1/newsmap/globe?view=1").then(function(g){
    var d = g.runtime || g; COLORS = d.colors || {};
    var key=clear("key"); Object.keys(COLORS).forEach(function(t){ var c=COLORS[t]; var li=el("div"); var s=el("span","", "dot"); s.style.background=hexOk(c.hex); li.appendChild(s); li.appendChild(el("span", (c.color||"") + " — " + (c.label||t))); key.appendChild(li); });
    var layer=document.getElementById("pins"); var drawn=0;
    (d.pins||[]).forEach(function(p){ byId[p.pin_id]=p; var g2=p.geo; if(!g2||!isFinite(Number(g2.lat))||!isFinite(Number(g2.lon))) return; var c=document.createElementNS(ns,"circle"); c.setAttribute("cx", Number(g2.lon)+180); c.setAttribute("cy", 90-Number(g2.lat)); c.setAttribute("r", 1.6); c.setAttribute("fill", colorOf(p)); c.setAttribute("data-pin", p.pin_id); var t=document.createElementNS(ns,"title"); t.textContent=(p.event||p.pin_id) + " — " + (g2.name||""); c.appendChild(t); c.addEventListener("click", function(){ history.replaceState(null,"","?pin="+encodeURIComponent(p.pin_id)); show(p); }); layer.appendChild(c); drawn++; });
    var last=clear("last"); var ol=el("ol"); (d.last10||[]).forEach(function(p){ var li=el("li"); var s=el("span","","dot"); s.style.background=colorOf(p); li.appendChild(s); var a=el("a", p.event || p.pin_id); a.href="?pin="+encodeURIComponent(p.pin_id); a.addEventListener("click", function(ev){ ev.preventDefault(); history.replaceState(null,"","?pin="+encodeURIComponent(p.pin_id)); show(byId[p.pin_id]||p); }); li.appendChild(a); li.appendChild(el("span"," " + (p.added_at||""), "muted")); ol.appendChild(li); }); last.appendChild(ol);
    var news=clear("news"); var ul=el("ul"); (d.items||[]).forEach(function(i){ var li=el("li"); var href=safeHref(i.link); var a=el(href?"a":"span", i.title||i.item_id); if(href){a.href=href;a.rel="noopener";} li.appendChild(a); li.appendChild(el("span"," — " + (i.outlet||"") + " · " + (i.published||""), "muted")); ul.appendChild(li); }); news.appendChild(ul);
    var sky=clear("sky"); var s=d.sky||{};
    if (s.sun) sky.appendChild(el("div","Sun: " + s.sun.tropical_sign + " (tropical), in " + s.sun.constellation + " (IAU)"));
    if (s.moon) sky.appendChild(el("div","Moon: " + (s.moon.phase_name||"") + " · " + (s.moon.illuminated_percent!=null ? s.moon.illuminated_percent + "% lit" : "") + (s.moon.trend ? " · " + s.moon.trend : "") + (s.moon.next_new_moon ? " · next new moon " + s.moon.next_new_moon : "")));
    if (s.seasons) sky.appendChild(el("div","Season: north " + s.seasons.northern_hemisphere + ", south " + s.seasons.southern_hemisphere));
    var vis=Array.isArray(s.visible_tonight)?s.visible_tonight:[];
    if (vis.length){ sky.appendChild(el("div","Visible tonight (at local solar midnight):")); var vul=el("ul"); vis.slice(0,6).forEach(function(a){ var names=(Array.isArray(a.visible)?a.visible:[]).map(function(v){return v&&v.name;}).filter(Boolean).slice(0,6); vul.appendChild(el("li",(a.anchor_name||a.anchor_id||"") + ": " + (names.join(", ")||"none listed"))); }); sky.appendChild(vul); }
    if (s.computed_at) sky.appendChild(el("div","Computed " + s.computed_at, "muted"));
    var w=clear("weather"); var tb=el("table"); var hr=el("tr"); ["Area","°C","Conditions"].forEach(function(h){hr.appendChild(el("th",h));}); tb.appendChild(hr);
    ((d.weather&&d.weather.regions)||[]).forEach(function(r){ var tr=el("tr"); tr.appendChild(el("td",(r.anchor&&r.anchor.name)||"")); tr.appendChild(el("td", r.reading && r.reading.temperature_2m!=null ? r.reading.temperature_2m : "")); tr.appendChild(el("td",(r.conditions||"") + (r.severe&&r.severe.length ? " · severe: " + r.severe.join(", ") : ""))); tb.appendChild(tr); });
    w.appendChild(tb); if (d.weather && d.weather.source) w.appendChild(el("div", typeof d.weather.source === "string" ? d.weather.source : (d.weather.source.text || "Weather data by Open-Meteo.com"), "muted"));
    if (wanted && byId[wanted]) show(byId[wanted]);
    else if (wanted) document.getElementById("detail").textContent = "Pin " + wanted + " is not among the newest pins here. Open it on the runtime globe: " + RT + "/aznews?pin=" + wanted;
  }).catch(function(){ ["news","last","sky","weather"].forEach(function(id){ document.getElementById(id).textContent="The newsmap door did not answer."; }); });
})();
</script></body></html>`;

export function newsmapPageHtml(runtimeOrigin = "https://aziel-runtime.vibelock.workers.dev") {
  return PAGE.replace("__LAND__", LAND_PATH).replace("__LANDSRC__", LAND_SOURCE).replace(/__GLOBE__/g, runtimeOrigin + "/aznews").replace("__RTORIGIN__", runtimeOrigin);
}
