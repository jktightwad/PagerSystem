// The pager's web page (served at /). Polls /api/status once a second and
// sends test / admin actions to /api/cmd.
#pragma once

static const char PAGE_HTML[] PROGMEM = R"HTML(<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pool pager</title>
<style>
:root{--bg:#f4f5f7;--card:#fff;--ink:#1d2330;--muted:#6b7280;--line:#e3e6ea;--acc:#1f6feb;--ok:#1a7f37;--bad:#cf222e}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#181b21;--ink:#e6e8eb;--muted:#9aa3ad;--line:#2a2f37;--acc:#4c8dff;--ok:#3fb950;--bad:#f85149}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.4 system-ui,sans-serif}
main{max-width:720px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:4px 0 12px}h2{font-size:15px;margin:0 0 10px;color:var(--muted);font-weight:600}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px 16px}
.k{color:var(--muted);font-size:12px}.v{font-size:16px;font-variant-numeric:tabular-nums}
.btns{display:flex;flex-wrap:wrap;gap:8px}
button,a.btn{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:8px;padding:8px 12px;font:inherit;cursor:pointer;text-decoration:none}
button:hover,a.btn:hover{border-color:var(--acc)}button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.red{color:var(--bad)}.green{color:var(--ok)}.sw{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:-1px;border:1px solid var(--line)}
input{font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink)}
#msg{min-height:20px;color:var(--muted);font-size:13px}
</style></head><body><main>
<h1 id="title">Pool pager</h1>

<div class="card"><h2>Status</h2><div class="grid">
<div><div class="k">State</div><div class="v" id="state">-</div></div>
<div><div class="k">Battery</div><div class="v" id="batt">-</div></div>
<div><div class="k">Dock</div><div class="v" id="dock">-</div></div>
<div><div class="k">Touch pad</div><div class="v" id="touch">-</div></div>
<div><div class="k">Wi-Fi</div><div class="v" id="wifi">-</div></div>
<div><div class="k">Wi-Fi signal</div><div class="v" id="rssi">-</div></div>
<div><div class="k">Base link</div><div class="v" id="base">-</div></div>
<div><div class="k">Firmware / uptime</div><div class="v" id="fw">-</div></div>
</div></div>

<div class="card"><h2>Light modes</h2>
<div class="btns" id="fxbtns"></div>
<div class="btns" style="margin-top:10px;align-items:center">
<label>Colour <input type="color" id="color" onchange="light({color:this.value.slice(1)})"></label>
<label>Brightness <input type="range" id="bright" min="1" max="100" onchange="light({bright:this.value})"></label>
<label>Speed <input type="range" id="speed" min="0" max="100" onchange="light({speed:this.value})"></label>
</div>
<div class="k" style="margin-top:6px">Brightness above ~25 % draws a lot from the 3.3 V regulator; keep it short.</div>
<h2 style="margin-top:12px">Colour tests</h2>
<div class="btns" id="presets"></div>
</div>

<div class="card"><h2>Pager states</h2><div class="btns">
<button onclick="cmd('dock')">Docked</button><button onclick="cmd('lift')">Lifted (gauge)</button>
<button onclick="cmd('confirm')">Confirm</button><button onclick="cmd('waiting')">Waiting</button>
<button onclick="cmd('alert')">Your turn (alert)</button><button onclick="cmd('ack')">Acknowledge</button>
<button id="demo" onclick="cmd(demoOn?'demo_off':'demo_on')">Demo mode</button>
</div></div>

<div class="card"><h2>Tests</h2><div class="btns">
<button onclick="cmd('selftest')">Self test (all outputs)</button>
<button onclick="cmd('red')">Ring red</button><button onclick="cmd('green')">Ring green</button>
<button onclick="cmd('blue')">Ring blue</button><button onclick="cmd('white')">Ring white</button>
<button onclick="cmd('chase')">LED chase</button><button onclick="cmd('off')">Ring off</button>
<button onclick="cmd('beep')">Beep</button><button onclick="cmd('beep_hold')">Beeper on / off (for a meter)</button><button onclick="cmd('vibe')">Vibrate</button>
<button onclick="cmd('identify')">Identify (flash + beep)</button>
</div></div>

<div class="card"><h2>Admin</h2>
<div class="btns" style="margin-bottom:10px">
<input id="name" maxlength="24" placeholder="pager name"><button onclick="rename()">Rename</button></div>
<div class="btns">
<a class="btn" href="/update">Firmware update</a>
<button onclick="if(confirm('Forget all saved Wi-Fi networks and reboot into the PoolPager-Setup hotspot?'))cmd('forgetwifi')">Forget Wi-Fi</button>
<button onclick="if(confirm('Reboot the pager?'))cmd('reboot')">Reboot</button>
</div></div>
<div id="msg"></div>
</main>
<script>
let demoOn=false;
const FX=[['solid','Solid'],['blink','Blink'],['party','Party'],['knight_rider','Knight Rider'],['breathe','Breathe'],
          ['comet','Comet'],['rainbow','Rainbow'],['pulse','Pulse'],['off','Off']];
// colour tests: pool ball colours (as tuned in pager_alert_test) and basics
const PRE=[['1 yellow','ff6e00'],['2 blue','0000ff'],['3 red','ff0000'],['4 purple','5000ff'],['5 orange','ff2300'],
           ['6 green','00c800'],['7 maroon','82000f'],['8 white','ffffff'],['Green','00ff00'],['Cyan','00ffff'],['Magenta','ff00ff']];
function build(){
  $('fxbtns').innerHTML=FX.map(f=>'<button id="fx_'+f[0]+'" onclick="light({fx:\''+f[0]+'\'})">'+f[1]+'</button>').join('');
  $('presets').innerHTML=PRE.map(p=>'<button onclick="light({fx:\'solid\',color:\''+p[1]+'\'})"><span class="sw" style="background:#'+p[1]+'"></span>'+p[0]+'</button>').join('');
}
async function light(o){
  const q=Object.entries(o).map(([k,v])=>k+'='+encodeURIComponent(v)).join('&');
  try{const r=await fetch('/api/light?'+q,{method:'POST'});$('msg').textContent=await r.text();}catch(e){$('msg').textContent='No answer from the pager';}
  poll();
}
const $=id=>document.getElementById(id);
function bars(r){return r>=-55?'excellent':r>=-67?'good':r>=-75?'fair':'weak'}
async function cmd(c){
  try{const r=await fetch('/api/cmd?c='+encodeURIComponent(c),{method:'POST'});$('msg').textContent=await r.text();}
  catch(e){$('msg').textContent='No answer from the pager';}
  poll();
}
async function rename(){
  const n=$('name').value.trim(); if(!n)return;
  const r=await fetch('/api/name?n='+encodeURIComponent(n),{method:'POST'}); $('msg').textContent=await r.text(); poll();
}
async function poll(){
  try{
    const s=await (await fetch('/api/status')).json();
    document.title=s.name; $('title').textContent=s.name;
    if(document.activeElement!==$('name')) $('name').value=s.name;
    $('state').textContent=s.state;
    demoOn=s.demo; $('demo').classList.toggle('on',demoOn);
    $('batt').textContent=s.batt_v.toFixed(2)+' V ('+s.batt_pct+' %)';
    $('dock').textContent=(s.docked?'on dock':'off dock')+' ('+s.dock_v.toFixed(2)+' V)';
    $('touch').innerHTML=s.touch?'<span class="green">touched</span>':'released';
    $('wifi').textContent=s.wifi.connected?(s.wifi.ssid+' / '+s.wifi.ip):'not connected';
    $('rssi').textContent=s.wifi.connected?(s.wifi.rssi+' dBm ('+bars(s.wifi.rssi)+'), ch '+s.wifi.ch):'-';
    $('base').textContent=s.base.available?(s.base.rssi+' dBm'):'not available yet';
    FX.forEach(f=>{const b=$('fx_'+f[0]); if(b) b.classList.toggle('on', s.state==='Light mode' && s.light.fx===f[0]);});
    const a=document.activeElement;
    if(a!==$('color')) $('color').value='#'+s.light.color;
    if(a!==$('bright')) $('bright').value=s.light.bright;
    if(a!==$('speed')) $('speed').value=s.light.speed;
    const u=s.uptime_s; $('fw').textContent=s.fw+' / '+Math.floor(u/3600)+'h '+Math.floor(u%3600/60)+'m';
  }catch(e){$('state').innerHTML='<span class="red">offline</span>';}
}
build(); poll(); setInterval(poll,1000);
</script></body></html>)HTML";
