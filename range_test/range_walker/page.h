// Live results page served by range_walker.ino
#pragma once
#include <Arduino.h>

static const char PAGE[] PROGMEM = R"HTML(<!doctype html>
<html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Pager range test</title>
<style>
body{font-family:system-ui,sans-serif;margin:16px;background:#fff;color:#111}
#big{font-size:64px;font-weight:700;margin:8px 0}
.good{color:#1a7f37}.ok{color:#9a6700}.bad{color:#cf222e}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:12px}
td,th{border-bottom:1px solid #ddd;padding:6px 4px;text-align:left}
input{font-size:18px;padding:8px;width:60%}button{font-size:18px;padding:8px 14px}
small{color:#666}
</style></head><body>
<h2>Pager range test</h2>
<div><small>Last 5 s, answered:</small></div>
<div id=big>--</div>
<div id=rssi>--</div>
<p><small id=info></small></p>
<p><input id=name placeholder="Spot name, e.g. Desk 12"> <button onclick="rec()">Record</button></p>
<p><small>Stand still ~15 s before recording. A record uses the last 15 s.</small></p>
<table><thead><tr><th>Spot</th><th>OK %</th><th>Pager RSSI</th><th>Base RSSI</th></tr></thead><tbody id=rows></tbody></table>
<p><a href="/results.csv">Download results (CSV)</a></p>
<script>
function cls(p){return p>=95?'good':p>=80?'ok':'bad'}
async function poll(){
 try{
  const s=await (await fetch('/stats')).json();
  const b=document.getElementById('big');
  b.textContent=s.pings? s.pct+'%':'--'; b.className=s.pongs?cls(s.pct):'bad';
  if(!s.pongs&&s.pings) b.textContent='NO CONTACT';
  document.getElementById('rssi').textContent=s.pongs?
   'Pager RSSI '+s.rw+' (min '+s.mw+') | Base RSSI '+s.rb+' (min '+s.mb+')':'';
  document.getElementById('info').textContent='Channel '+s.ch+', LR mode '+(s.lr?'on':'off')+', up '+s.up+' s';
  document.getElementById('rows').innerHTML=s.spots.map(x=>
   '<tr><td>'+x.n+'</td><td class='+cls(x.p)+'>'+x.p+'</td><td>'+x.rw+' / '+x.mw+'</td><td>'+x.rb+' / '+x.mb+'</td></tr>').join('');
 }catch(e){document.getElementById('big').textContent='walker?'}
}
async function rec(){
 const n=document.getElementById('name').value.trim()||'Spot';
 await fetch('/record?name='+encodeURIComponent(n)); document.getElementById('name').value=''; poll();
}
setInterval(poll,2000); poll();
</script></body></html>)HTML";
