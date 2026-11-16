// Pool pager firmware (proof of concept)
//
// Hardware: LOLIN32 Lite, 16-LED WS2812 ring, active buzzer, vibration motor,
// touch module, dock sense and battery dividers (docs/pager_wiring.md).
//
// Wi-Fi (same scheme as the desktop notifier light):
//   - tries the networks it has joined before (saved on the pager) and the
//     ones in include/secrets.h, strongest first, hidden ones last
//   - if none connects: opens the open hotspot "PoolPager-Setup" for 5 min
//     (ring purple); join it from a phone and pick the network
//   - once connected: for 60 s runs a hotspot named "PoolPager-<ip>" (e.g.
//     PoolPager-192-168-1-87) so the IP can be read from a phone's Wi-Fi list
//     (ring blinks purple); also printed on the serial monitor
//   - hold the touch pad for 5 s while powering up to forget saved networks
// Boot lights (as the desktop notifier): blue progress bar while scanning,
// orange while joining, steady purple (middle 6) during the setup hotspot,
// green flash when joined through it, then middle-6 purple blink while the
// PoolPager-<ip> hotspot is up. Any page action or touch stops the blink.
// Touch: 1 tap = light on (not while reserved; "your turn" = acknowledge),
// 2 taps = next light mode, 3 taps within 3 s = everything off.
// Light modes (as the notifier): solid, blink, party, knight rider, breathe,
// comet, rainbow, pulse, off; colour, brightness and speed from the page.
// Web page at http://<ip>/ : status, pager states, demo mode, tests, rename,
// forget Wi-Fi, reboot, firmware update (/update). Password from secrets.h.
// OTA: ArduinoOTA (PlatformIO env lolin32_lite_ota) or the /update page.
//
// The base doesn't talk ESP-NOW yet, so the base link signal shows
// "not available yet".
//
// STATUS: written, not compiled or tested.

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <ElegantOTA.h>
#include <WiFiManager.h>
#include <LittleFS.h>
#include <Preferences.h>
#include <Adafruit_NeoPixel.h>
#include <esp_wifi.h>
#include <algorithm>
#include "wifi_store.h"
#include "page.h"

#if __has_include("secrets.h")
#include "secrets.h"
#endif
#ifndef ADMIN_USER
#define ADMIN_USER     "admin"
#endif
#ifndef ADMIN_PASSWORD
#define ADMIN_PASSWORD ""          // empty: page has no password
#endif
#ifndef OTA_PASSWORD
#define OTA_PASSWORD   ""
#endif

#define FW_VERSION "0.1"

// ---- Pins (docs/pager_wiring.md) ----
#define PIN_RING      26
#define PIN_BEEPER    27
#define PIN_VIBE      25
#define PIN_TOUCH      4
#define TOUCH_ACTIVE_HIGH 1
#define PIN_DOCK_ADC  34
#define PIN_BATT_ADC  35
#define PIN_BOARD_LED 22

// ---- Options ----
#define RING_LEDS      16
#define MAX_BRIGHTNESS 64
#define VIBE_STRENGTH  230     // motor on 3.3 V: ~230 / 255 = ~3 V
#define DIVIDER_RATIO  2.0f

Adafruit_NeoPixel ring(RING_LEDS, PIN_RING, NEO_GRB + NEO_KHZ800);
WebServer server(80);
WiFiManager wm;
Preferences prefs;
WifiStore wifiStore;
String pagerName;

// ======================= Outputs / inputs =======================
// pinMode every time, as in pager_alert_test (where the beeper tested fine)
void beeper(bool on) { pinMode(PIN_BEEPER, OUTPUT); digitalWrite(PIN_BEEPER, on ? HIGH : LOW); }
bool beepHold = false;           // "Beeper on" test: stays on so it can be measured
void vibe(bool on) { ledcWrite(PIN_VIBE, on ? VIBE_STRENGTH : 0); }
void ringFill(uint32_t c) { ring.fill(c); ring.show(); }
void allOff() { beeper(false); vibe(false); ringFill(0); }
uint32_t rgb(uint8_t r, uint8_t g, uint8_t b) { return ring.Color(r, g, b); }

float readVolts(int pin) { return analogReadMilliVolts(pin) * DIVIDER_RATIO / 1000.0f; }
bool onDock() { return readVolts(PIN_DOCK_ADC) > 4.0f; }
bool touched() { return digitalRead(PIN_TOUCH) == (TOUCH_ACTIVE_HIGH ? HIGH : LOW); }
int batteryPercent() {
  float v = readVolts(PIN_BATT_ADC);
  return constrain((int)((v - 3.3f) / (4.15f - 3.3f) * 100.0f), 0, 100);
}

// Debounced touch: true once per touch
bool touchPressed() {
  static bool last = false, reported = false;
  static uint32_t changedAt = 0;
  bool now = touched();
  if (now != last) { last = now; changedAt = millis(); reported = false; }
  if (now && !reported && millis() - changedAt > 30) { reported = true; return true; }
  return false;
}

// ======================= States =======================
enum State { DOCKED, LIFTED, CONFIRM, WAITING, ALERT, ACKED, TEST, LIGHT, LAMP };
const char* STATE_NAMES[] = {"Docked", "Lifted", "Confirm", "Waiting", "Your turn", "Acknowledged", "Self test", "Light test", "Light mode"};
// "reservation mode": the pager is bound / in the queue / being paged
bool reserved(State s) { return s == CONFIRM || s == WAITING || s == ALERT || s == ACKED; }
State state = DOCKED;
uint32_t stateSince = 0;
bool demoMode = false;
uint32_t discoveryUntil = 0;     // PoolPager-<ip> hotspot up until then
bool discoveryBlink = false;     // middle-6 purple blink while it's up (stops on any page action)
uint32_t beepUntil = 0, vibeUntil = 0;

void setState(State s) {
  state = s; stateSince = millis();
  ring.setBrightness(MAX_BRIGHTNESS);   // light modes use their own brightness
  allOff();
  Serial.printf("-> %s\n", STATE_NAMES[s]);
}

void runDocked() {
  bool full = batteryPercent() >= 100;
  uint8_t v = 24;
  if (!full) {
    uint32_t t = (millis() - stateSince) % 3000, tri = t < 1500 ? t : 3000 - t;
    v = 6 + tri * 30 / 1500;
  }
  ringFill(rgb(v, 0, 0));
}
void runLifted() {
  int lit = (batteryPercent() * RING_LEDS + 99) / 100;
  ring.clear();
  for (int i = 0; i < lit; i++) ring.setPixelColor(i, rgb(160, 0, 0));
  ring.show();
}
void runConfirm() {
  uint32_t t = millis() - stateSince;
  ringFill((t % 300) < 180 && t < 900 ? rgb(0, 0, 200) : 0);
  beeper(t < 80);
  if (t > 1000) setState(WAITING);
}
void runWaiting() { ringFill((millis() - stateSince) % 5000 < 150 ? rgb(0, 0, 40) : 0); }
void runAlert() {
  uint32_t t = millis() - stateSince;
  bool esc = t > 30000;
  int head = (t / (esc ? 40 : 70)) % RING_LEDS;
  ring.clear();
  for (int i = 0; i < 5; i++) ring.setPixelColor((head - i + RING_LEDS) % RING_LEDS, rgb(0, (esc ? 255 : 160) >> i, 0));
  ring.show();
  uint32_t c = t % (esc ? 1000 : 2000);
  beeper((c < 120) || (c >= 200 && c < 320) || (c >= 400 && c < 520));
  vibe(c < (esc ? 800u : 400u));
}
void runAcked() {
  uint32_t t = millis() - stateSince;
  int lit = std::min((int)(t / 30), RING_LEDS);
  ring.clear();
  for (int i = 0; i < lit; i++) ring.setPixelColor(i, rgb(0, 0, lit < RING_LEDS ? 200 : 120));
  ring.show();
  beeper(t < 150);
}
// Self test, non-blocking: red, green, blue, white, chase, 3 beeps, vibrate
void runTest() {
  uint32_t t = millis() - stateSince;
  if (t < 4000) {
    const uint32_t cols[] = {rgb(255, 0, 0), rgb(0, 255, 0), rgb(0, 0, 255), rgb(255, 255, 255)};
    ringFill(cols[t / 1000]);
  } else if (t < 4000 + RING_LEDS * 100) {
    ring.clear(); ring.setPixelColor((t - 4000) / 100, rgb(0, 0, 255)); ring.show();
  } else if (t < 7000) {
    ringFill(0);
    uint32_t b = t - (4000 + RING_LEDS * 100);
    beeper(b < 1350 && (b % 450) < 200);
  } else if (t < 8500) {
    beeper(false); vibe(true);
  } else {
    vibe(false);
    Serial.println("Self test done");
    setState(onDock() ? DOCKED : LIFTED);
  }
}

// Demo mode: steps through the states a pager goes through in use
void runDemo() {
  static const State seq[] = {DOCKED, LIFTED, CONFIRM, WAITING, ALERT, ACKED};
  static const uint32_t dur[] = {5000, 5000, 1200, 6000, 8000, 4000};
  static int step = 0;
  static uint32_t stepAt = 0;
  if (millis() - stepAt > dur[step] || stepAt == 0) {
    step = stepAt == 0 ? 0 : (step + 1) % 6;
    stepAt = millis();
    setState(seq[step]);
  }
}

// ======================= Light modes (as the desktop notifier light) =======================
enum Effect { FX_OFF, FX_SOLID, FX_BLINK, FX_PARTY, FX_KNIGHT, FX_BREATHE, FX_COMET, FX_RAINBOW, FX_PULSE };
const char* FX_NAMES[] = {"Off", "Solid", "Blink", "Party", "Knight Rider", "Breathe", "Comet", "Rainbow", "Pulse"};
const char* FX_KEYS[]  = {"off", "solid", "blink", "party", "knight_rider", "breathe", "comet", "rainbow", "pulse"};
const int FX_COUNT = 9;
Effect fx = FX_SOLID;            // last light mode (a single tap turns it on)
uint32_t fxColor = 0xFF0000;     // 0xRRGGBB
uint8_t fxBright = 64;           // 0-255 (on the 3.3 V regulator: keep it moderate)
unsigned long fxDelay = 35;      // ms, from the speed slider (notifier: 200 * e^(-0.035 * speed))
unsigned long fxLast = 0;
int fxPos = 0, fxDir = 1;

uint8_t cR() { return (fxColor >> 16) & 0xFF; }
uint8_t cG() { return (fxColor >> 8) & 0xFF; }
uint8_t cB() { return fxColor & 0xFF; }
uint16_t fxHue() {               // hue of fxColor for ColorHSV (0-65535)
  float r = cR() / 255.0f, g = cG() / 255.0f, b = cB() / 255.0f;
  float mx = std::max(r, std::max(g, b)), mn = std::min(r, std::min(g, b)), d = mx - mn, h = 0;
  if (d > 0) {
    if (mx == r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (mx == g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h /= 6;
  }
  return (uint16_t)(h * 65535);
}
unsigned long fxDelayFor(Effect e) {
  float k = 1;
  switch (e) { case FX_BREATHE: k = 2; break; case FX_PARTY: case FX_COMET: k = 2.5; break;
               case FX_KNIGHT: case FX_BLINK: k = 3; break; case FX_PULSE: k = 2; break; default: break; }
  return constrain((unsigned long)(fxDelay * k), 2UL, 2000UL);
}
void fade(float f) {             // dim every LED (trails)
  for (int i = 0; i < RING_LEDS; i++) {
    uint32_t c = ring.getPixelColor(i);
    ring.setPixelColor(i, rgb(((c >> 16) & 0xFF) * f, ((c >> 8) & 0xFF) * f, (c & 0xFF) * f));
  }
}
void startLamp(Effect e) {
  demoMode = false;
  fx = e;
  setState(LAMP);
  ring.setBrightness(fxBright);
  fxPos = 0; fxDir = 1; fxLast = 0;
  Serial.printf("Light mode: %s\n", FX_NAMES[fx]);
}
void runLamp() {
  ring.setBrightness(fxBright);
  uint32_t col = rgb(cR(), cG(), cB());
  unsigned long now = millis();
  switch (fx) {
    case FX_OFF:   ringFill(0); break;
    case FX_SOLID: ringFill(col); break;
    case FX_BLINK:
      if (now - fxLast > fxDelayFor(FX_BLINK) * 4 + 100) { fxLast = now; ringFill(ring.getPixelColor(0) ? 0 : col); }
      break;
    case FX_PARTY:
      if (now - fxLast > fxDelayFor(FX_PARTY)) {
        fxLast = now;
        for (int i = 0; i < RING_LEDS; i++) ring.setPixelColor(i, rgb(random(25), random(25), random(25)));
        for (int i = 0; i < 3; i++) ring.setPixelColor(random(RING_LEDS), ring.ColorHSV(fxHue() + random(-10923, 10923)));
        ring.show();
      }
      break;
    case FX_KNIGHT:
      if (now - fxLast > fxDelayFor(FX_KNIGHT)) {
        fxLast = now;
        fade(0.7);
        for (int d = -2; d <= 2; d++) {
          int i = fxPos + d; if (i < 0 || i >= RING_LEDS) continue;
          int div = d == 0 ? 1 : (abs(d) == 1 ? 2 : 8);
          ring.setPixelColor(i, rgb(cR() / div, cG() / div, cB() / div));
        }
        ring.show();
        fxPos += fxDir;
        if (fxPos < 0 || fxPos >= RING_LEDS) { fxDir = -fxDir; fxPos += fxDir; }
      }
      break;
    case FX_BREATHE:
      if (now - fxLast > std::max(3UL, fxDelayFor(FX_BREATHE) / 4)) {
        static float phase = 0;
        fxLast = now; phase += 0.03f;
        float v = 0.2f + 0.8f * (0.5f * (1 + sin(phase)));
        ringFill(rgb(cR() * v, cG() * v, cB() * v));
      }
      break;
    case FX_COMET:
      if (now - fxLast > fxDelayFor(FX_COMET)) {
        fxLast = now;
        fade(0.8);
        ring.setPixelColor(fxPos, col);
        ring.show();
        fxPos = (fxPos + 1) % RING_LEDS;
      }
      break;
    case FX_RAINBOW:
      if (now - fxLast > std::max(2UL, fxDelay / 16)) {
        static uint16_t base = 0;
        fxLast = now;
        base += 24 + (uint8_t)((220 - std::min(fxDelay, 200UL)) * 0.6f);
        for (int i = 0; i < RING_LEDS; i++) ring.setPixelColor(i, ring.ColorHSV(base + i * 65536L / RING_LEDS));
        ring.show();
      }
      break;
    case FX_PULSE:       // two dots from opposite sides meeting in the middle and back
      if (now - fxLast > fxDelayFor(FX_PULSE)) {
        fxLast = now;
        fade(0.7);
        int l = fxPos, r = RING_LEDS - 1 - fxPos;
        ring.setPixelColor(l, col); ring.setPixelColor(r, col);
        ring.show();
        if (fxDir > 0) { if (r - l <= 1) fxDir = -1; else fxPos++; }
        else { if (fxPos > 0) fxPos--; else fxDir = 1; }
      }
      break;
  }
}

// ======================= Boot / discovery lights (as the desktop notifier) =======================
// progress bar: lit part in colour, next LED at quarter brightness
void drawBar(uint32_t color, float frac) {
  frac = constrain(frac, 0.0f, 1.0f);
  int filled = (int)(frac * RING_LEDS);
  ring.setBrightness(MAX_BRIGHTNESS);
  ring.clear();
  for (int i = 0; i < filled; i++) ring.setPixelColor(i, color);
  if (filled < RING_LEDS) ring.setPixelColor(filled, rgb(((color >> 16) & 0xFF) / 4, ((color >> 8) & 0xFF) / 4, (color & 0xFF) / 4));
  ring.show();
}
void middle6(uint32_t color) {   // 6 LEDs in the middle of the ring
  ring.setBrightness(MAX_BRIGHTNESS);
  ring.clear();
  for (int i = RING_LEDS / 2 - 3; i <= RING_LEDS / 2 + 2; i++) ring.setPixelColor(i, color);
  ring.show();
}
const uint32_t BOOT_PURPLE = 0x8000FF;
void stopDiscoveryBlink() {      // any page action / touch takes over the ring
  if (discoveryBlink) { discoveryBlink = false; ringFill(0); }
}

// ======================= Touch gestures =======================
// 1 tap: light on (not while reserved; while "your turn" it acknowledges)
// 2 taps: next light mode (not while reserved)
// 3 taps within 3 s: everything off (lights, buzzer, motor, demo)
const uint32_t TAP_GAP_MS = 450;     // a tap this long after the last one ends the gesture
uint32_t tapTimes[3] = {0, 0, 0};
int tapsPending = 0;
uint32_t lastTapAt = 0;

void silenceAll() {
  demoMode = false; beepHold = false; beepUntil = vibeUntil = 0;
  stopDiscoveryBlink();
  startLamp(FX_OFF);
  Serial.println("Touch x3: everything off");
}
void onTap() {
  uint32_t now = millis();
  tapTimes[0] = tapTimes[1]; tapTimes[1] = tapTimes[2]; tapTimes[2] = now;
  if (tapTimes[0] && now - tapTimes[0] <= 3000) {           // third tap within 3 s
    tapsPending = 0; tapTimes[0] = tapTimes[1] = tapTimes[2] = 0;
    silenceAll();
    return;
  }
  stopDiscoveryBlink();
  if (state == ALERT) { demoMode = false; setState(ACKED); }  // acknowledge straight away
  tapsPending++; lastTapAt = now;
}
void serviceTaps() {
  if (touchPressed()) onTap();
  if (tapsPending && millis() - lastTapAt > TAP_GAP_MS) {
    int n = tapsPending; tapsPending = 0;
    if (reserved(state)) return;
    if (n == 1) {                                            // light on
      if (!(state == LAMP && fx != FX_OFF)) startLamp(fx == FX_OFF ? FX_SOLID : fx);
    } else {                                                 // next light mode
      // lit: step Solid -> Blink -> ... -> Pulse -> Solid; dark: start at the last mode
      Effect next = (state == LAMP && fx != FX_OFF) ? (Effect)(fx % (FX_COUNT - 1) + 1) : (fx == FX_OFF ? FX_SOLID : fx);
      startLamp(next);
    }
  }
}

// ======================= Wi-Fi =======================
#ifdef WIFI_NETWORKS
struct BuiltinNet { const char* ssid; const char* pass; };
static const BuiltinNet BUILTIN_NETWORKS[] = WIFI_NETWORKS;
#endif

std::vector<WifiCred> knownNetworks() {
  std::vector<WifiCred> v = wifiStore.networks();
#ifdef WIFI_NETWORKS
  for (const BuiltinNet& n : BUILTIN_NETWORKS) {
    bool dup = false;
    for (const WifiCred& k : v) if (k.ssid == n.ssid) dup = true;
    if (!dup) v.push_back({n.ssid, n.pass});
  }
#endif
  return v;
}

void rememberCurrentNetwork() {
  if (WiFi.status() == WL_CONNECTED) wifiStore.remember(WiFi.SSID(), WiFi.psk());
}

// Known networks in range strongest first, then unseen (maybe hidden) ones.
// Ring: blue bar while scanning, orange while joining.
bool tryKnownNetworks() {
  std::vector<WifiCred> known = knownNetworks();
  if (known.empty()) { Serial.println("[WiFi] No known networks"); return false; }
  Serial.printf("[WiFi] Scanning for %u known network(s)...\n", (unsigned)known.size());
  // blue progress bar while scanning (as the notifier)
  WiFi.scanDelete();
  WiFi.scanNetworks(true);
  uint32_t s0 = millis();
  int found;
  while ((found = WiFi.scanComplete()) == WIFI_SCAN_RUNNING && millis() - s0 < 10000) {
    drawBar(rgb(0, 0, 255), (millis() - s0) / 10000.0f);
    delay(120);
  }
  struct Cand { size_t idx; int rssi; };
  std::vector<Cand> c;
  for (size_t k = 0; k < known.size(); k++) {
    int best = -1000;
    for (int i = 0; i < found; i++) if (WiFi.SSID(i) == known[k].ssid && WiFi.RSSI(i) > best) best = WiFi.RSSI(i);
    c.push_back({k, best});
  }
  WiFi.scanDelete();
  std::stable_sort(c.begin(), c.end(), [](const Cand& a, const Cand& b) { return a.rssi > b.rssi; });
  for (const Cand& x : c) {
    const WifiCred& n = known[x.idx];
    bool seen = x.rssi != -1000;
    Serial.printf("[WiFi] Trying \"%s\"%s...\n", n.ssid.c_str(), seen ? "" : " (not seen, may be hidden)");
    WiFi.begin(n.ssid.c_str(), n.pass.c_str());
    uint32_t s = millis(), ms = seen ? 15000u : 8000u;
    while (WiFi.status() != WL_CONNECTED && millis() - s < ms) {   // orange bar while joining
      drawBar(rgb(255, 128, 0), (millis() - s) / (float)ms);
      delay(120);
    }
    if (WiFi.status() == WL_CONNECTED) { ringFill(0); return true; }
    WiFi.disconnect();
  }
  ringFill(0);
  return false;
}

bool runPortal() {
  Serial.println("[WiFi] Opening hotspot PoolPager-Setup for 5 min: join it and pick the network");
  middle6(BOOT_PURPLE);                          // steady purple while the setup hotspot is up
  wm.setConfigPortalTimeout(300);
  bool ok = wm.startConfigPortal("PoolPager-Setup");
  ringFill(0);
  if (ok) { ringFill(rgb(0, 255, 0)); delay(120); ringFill(0); }   // green flash: joined
  return ok;
}

// Hotspot named after the IP for 60 s, so it can be read from a phone
void announceIp() {
  String ip = WiFi.localIP().toString();
  ip.replace(".", "-");
  String ap = "PoolPager-" + ip;
  WiFi.softAP(ap.c_str());
  discoveryUntil = millis() + 60000;
  discoveryBlink = true;
  Serial.printf("[WiFi] Hotspot \"%s\" for 60 s (shows the IP)\n", ap.c_str());
}

void wifiConnect() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(pagerName.c_str());
  bool forget = prefs.getBool("forget", false);
  if (forget) {                                   // set by "Forget Wi-Fi"
    prefs.putBool("forget", false);
    wifiStore.clear();
    WiFi.disconnect(true, true);
  }
  bool ok = !forget && tryKnownNetworks();
  if (!ok) ok = runPortal();
  if (ok) {
    rememberCurrentNetwork();
    Serial.printf("[WiFi] Connected: %s, IP %s, %d dBm\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str(), WiFi.RSSI());
    WiFi.mode(WIFI_AP_STA);
    announceIp();
  } else {
    Serial.println("[WiFi] Not connected (pager works without Wi-Fi; retrying every minute)");
  }
}

// From loop(): reconnect / try other known networks once a minute if down
void wifiService() {
  static bool was = false;
  static uint32_t lastTry = 0;
  bool now = WiFi.status() == WL_CONNECTED;
  if (now != was) {
    was = now;
    if (now) { rememberCurrentNetwork(); Serial.printf("[WiFi] Connected, IP %s\n", WiFi.localIP().toString().c_str()); }
    else Serial.println("[WiFi] Disconnected");
  }
  if (!now && millis() - lastTry > 60000) { lastTry = millis(); tryKnownNetworks(); }
  if (discoveryUntil && millis() > discoveryUntil) {
    discoveryUntil = 0;
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_STA);
    stopDiscoveryBlink();
  }
}

// ======================= Web page =======================
bool authed() {
  if (strlen(ADMIN_PASSWORD) == 0) return true;
  if (server.authenticate(ADMIN_USER, ADMIN_PASSWORD)) return true;
  server.requestAuthentication();
  return false;
}

void handleStatus() {
  if (!authed()) return;
  bool conn = WiFi.status() == WL_CONNECTED;
  String j = "{";
  j += "\"name\":\"" + pagerName + "\",\"fw\":\"" FW_VERSION "\",";
  j += "\"uptime_s\":" + String(millis() / 1000) + ",";
  j += "\"state\":\"" + String(STATE_NAMES[state]) + "\",\"demo\":" + String(demoMode ? "true" : "false") + ",";
  j += "\"batt_v\":" + String(readVolts(PIN_BATT_ADC), 2) + ",\"batt_pct\":" + String(batteryPercent()) + ",";
  j += "\"dock_v\":" + String(readVolts(PIN_DOCK_ADC), 2) + ",\"docked\":" + String(onDock() ? "true" : "false") + ",";
  j += "\"touch\":" + String(touched() ? "true" : "false") + ",";
  j += "\"wifi\":{\"connected\":" + String(conn ? "true" : "false");
  if (conn) j += ",\"ssid\":\"" + WiFi.SSID() + "\",\"ip\":\"" + WiFi.localIP().toString() + "\",\"rssi\":" + String(WiFi.RSSI()) + ",\"ch\":" + String(WiFi.channel());
  char hex[8]; snprintf(hex, sizeof(hex), "%06lx", (unsigned long)fxColor);
  j += "},\"light\":{\"fx\":\"" + String(FX_KEYS[fx]) + "\",\"on\":" + String(state == LAMP && fx != FX_OFF ? "true" : "false") +
       ",\"color\":\"" + String(hex) + "\",\"bright\":" + String(fxBright * 100 / 255) +
       ",\"speed\":" + String((int)round(-log(fxDelay / 200.0) / 0.035)) + "}";
  j += ",\"base\":{\"available\":false}}";
  server.send(200, "application/json", j);
}

void handleCmd() {
  if (!authed()) return;
  String c = server.arg("c");
  String reply = "OK: " + c;
  stopDiscoveryBlink();
  if (c != "demo_on" && c != "demo_off" && c != "forgetwifi" && c != "reboot") demoMode = false;
  if (c != "beep_hold") beepHold = false;
  if      (c == "dock")     setState(DOCKED);
  else if (c == "lift")     setState(LIFTED);
  else if (c == "confirm")  setState(CONFIRM);
  else if (c == "waiting")  setState(WAITING);
  else if (c == "alert")    setState(ALERT);
  else if (c == "ack")      setState(ACKED);
  else if (c == "selftest") setState(TEST);
  else if (c == "demo_on")  { demoMode = true; reply = "Demo mode on"; }
  else if (c == "demo_off") { demoMode = false; setState(onDock() ? DOCKED : LIFTED); reply = "Demo mode off"; }
  else if (c == "red" || c == "green" || c == "blue" || c == "white" || c == "off") {
    setState(LIGHT);
    ringFill(c == "red" ? rgb(255, 0, 0) : c == "green" ? rgb(0, 255, 0) : c == "blue" ? rgb(0, 0, 255) : c == "white" ? rgb(255, 255, 255) : 0);
  }
  else if (c == "chase") {
    setState(LIGHT);
    for (int k = 0; k < RING_LEDS; k++) { ring.clear(); ring.setPixelColor(k, rgb(0, 0, 255)); ring.show(); delay(80); }
    ringFill(0);
  }
  else if (c == "beep")     { beeper(true); beepUntil = millis() + 300; }
  else if (c == "beep_hold") { beepHold = !beepHold; beeper(beepHold); beepUntil = 0;
                               reply = beepHold ? "Beeper ON (GPIO 27 high) until pressed again" : "Beeper off"; }
  else if (c == "vibe")     { vibe(true); vibeUntil = millis() + 1000; }
  else if (c == "identify") {
    setState(LIGHT);
    for (int k = 0; k < 3; k++) { ringFill(rgb(255, 255, 255)); beeper(true); delay(150); ringFill(0); beeper(false); delay(150); }
  }
  else if (c == "forgetwifi") {
    prefs.putBool("forget", true);
    server.send(200, "text/plain", "Forgetting Wi-Fi, rebooting into the PoolPager-Setup hotspot");
    delay(500); ESP.restart();
  }
  else if (c == "reboot") { server.send(200, "text/plain", "Rebooting"); delay(500); ESP.restart(); }
  else reply = "Unknown command: " + c;
  server.send(200, "text/plain", reply);
}

// light mode / colour / brightness / speed: /api/light?fx=party&color=ff8800&bright=25&speed=50
void handleLight() {
  if (!authed()) return;
  stopDiscoveryBlink();
  beepHold = false;
  if (server.hasArg("color")) fxColor = strtoul(server.arg("color").c_str(), nullptr, 16) & 0xFFFFFF;
  if (server.hasArg("bright")) fxBright = (uint8_t)(constrain((int)server.arg("bright").toInt(), 0, 100) * 255 / 100);
  if (server.hasArg("speed")) fxDelay = (unsigned long)(200.0 * exp(-0.035 * constrain((int)server.arg("speed").toInt(), 0, 100)));
  Effect e = fx;
  if (server.hasArg("fx")) for (int i = 0; i < FX_COUNT; i++) if (server.arg("fx") == FX_KEYS[i]) e = (Effect)i;
  if (server.hasArg("fx") || state != LAMP) startLamp(e);
  else ring.setBrightness(fxBright);
  prefs.putUInt("fxColor", fxColor); prefs.putUChar("fxBright", fxBright); prefs.putULong("fxDelay", fxDelay);
  server.send(200, "text/plain", String("Light: ") + FX_NAMES[fx]);
}

void handleName() {
  if (!authed()) return;
  String n = server.arg("n");
  n.trim();
  String clean;
  for (unsigned i = 0; i < n.length(); i++) {            // keep it a valid host name
    char ch = n[i];
    if (isalnum(ch) || ch == '-') clean += (char)tolower(ch);
  }
  if (clean.length() < 1 || clean.length() > 24) { server.send(400, "text/plain", "Use 1-24 letters, digits or -"); return; }
  prefs.putString("name", clean);
  server.send(200, "text/plain", "Renamed to " + clean + " (used as the network name after a reboot)");
  pagerName = clean;
}

void webStart() {
  server.on("/", []() { if (authed()) { stopDiscoveryBlink(); server.send_P(200, "text/html", PAGE_HTML); } });
  server.on("/api/light", HTTP_POST, handleLight);
  server.on("/api/status", handleStatus);
  server.on("/api/cmd", HTTP_POST, handleCmd);
  server.on("/api/name", HTTP_POST, handleName);
  ElegantOTA.begin(&server);
  if (strlen(ADMIN_PASSWORD)) ElegantOTA.setAuth(ADMIN_USER, ADMIN_PASSWORD);
  ElegantOTA.onStart([]() { demoMode = false; setState(LIGHT); ringFill(rgb(0, 0, 60)); });
  server.begin();
  MDNS.begin(pagerName.c_str());
  MDNS.addService("http", "tcp", 80);

  ArduinoOTA.setHostname(pagerName.c_str());
  if (strlen(OTA_PASSWORD)) ArduinoOTA.setPassword(OTA_PASSWORD);
  ArduinoOTA.onStart([]() { demoMode = false; setState(LIGHT); Serial.println("OTA: receiving update"); });
  ArduinoOTA.onProgress([](unsigned int done, unsigned int total) {
    int lit = RING_LEDS * done / total;
    ring.clear();
    for (int i = 0; i < lit; i++) ring.setPixelColor(i, rgb(0, 0, 255));
    ring.show();
  });
  ArduinoOTA.onError([](ota_error_t e) { Serial.printf("OTA: error %u\n", e); allOff(); });
  ArduinoOTA.begin();
}

// ======================= Setup / loop =======================
void setup() {
  Serial.begin(115200);
  pinMode(PIN_BEEPER, OUTPUT);
  beeper(false);
  ledcAttach(PIN_VIBE, 20000, 8);
  vibe(false);
  pinMode(PIN_TOUCH, TOUCH_ACTIVE_HIGH ? INPUT_PULLDOWN : INPUT_PULLUP);
  pinMode(PIN_BOARD_LED, OUTPUT);
  digitalWrite(PIN_BOARD_LED, HIGH);
  analogSetAttenuation(ADC_11db);
  ring.begin();
  ring.setBrightness(MAX_BRIGHTNESS);
  ringFill(0);

  prefs.begin("pager", false);
  char def[16];
  snprintf(def, sizeof(def), "pager-%06llx", (unsigned long long)(ESP.getEfuseMac() >> 24) & 0xFFFFFF);
  pagerName = prefs.getString("name", def);
  fxColor = prefs.getUInt("fxColor", 0xFF0000);
  fxBright = prefs.getUChar("fxBright", 64);
  fxDelay = prefs.getULong("fxDelay", 35);
  Serial.printf("\nPool pager %s, firmware %s\n", pagerName.c_str(), FW_VERSION);

  if (!LittleFS.begin(true)) Serial.println("LittleFS: mount failed");
  wifiStore.load();

  // Touch held for 5 s at power-up: forget saved networks
  if (touched()) {
    Serial.println("Touch held: keep holding 5 s to forget Wi-Fi");
    uint32_t s = millis();
    while (touched() && millis() - s < 5000) { ringFill(((millis() / 250) % 2) ? rgb(60, 0, 60) : 0); delay(20); }
    if (millis() - s >= 5000) { prefs.putBool("forget", true); Serial.println("Wi-Fi will be forgotten"); }
    ringFill(0);
  }

  wifiConnect();
  webStart();
  setState(onDock() ? DOCKED : LIFTED);
  Serial.println("Serial: i = Wi-Fi status, a = alert, s = ack, t = self test, d = demo on/off");
}

void loop() {
  server.handleClient();
  ElegantOTA.loop();
  ArduinoOTA.handle();
  wifiService();

  if (Serial.available()) {
    char c = Serial.read();
    if (c != 'i' && c != '\n' && c != '\r') stopDiscoveryBlink();
    if (c == 'i') {
      if (WiFi.status() == WL_CONNECTED)
        Serial.printf("%s: %s, IP %s, %d dBm, http://%s/ or http://%s.local/\n", pagerName.c_str(), WiFi.SSID().c_str(),
                      WiFi.localIP().toString().c_str(), WiFi.RSSI(), WiFi.localIP().toString().c_str(), pagerName.c_str());
      else Serial.println("Wi-Fi not connected");
    }
    if (c == 'a') { demoMode = false; setState(ALERT); }
    if (c == 's' && state == ALERT) setState(ACKED);
    if (c == 't') { demoMode = false; setState(TEST); }
    if (c == 'd') { demoMode = !demoMode; if (!demoMode) setState(onDock() ? DOCKED : LIFTED); }
  }

  serviceTaps();

  if (beepUntil && millis() > beepUntil) { beepUntil = 0; beeper(false); }
  if (beepHold) beeper(true);
  if (vibeUntil && millis() > vibeUntil) { vibeUntil = 0; vibe(false); }

  if (demoMode) runDemo();
  // middle-6 purple blink while the PoolPager-<ip> hotspot is up, until a page action or a touch
  if (discoveryBlink) {
    if ((millis() / 400) % 2) middle6(BOOT_PURPLE); else ringFill(0);
  } else {
    switch (state) {
      case DOCKED:  runDocked();  break;
      case LIFTED:  runLifted();  break;
      case CONFIRM: runConfirm(); break;
      case WAITING: runWaiting(); break;
      case ALERT:   runAlert();   break;
      case ACKED:   runAcked();   break;
      case TEST:    runTest();    break;
      case LIGHT:   break;
      case LAMP:    runLamp();    break;
    }
  }

  // dock change (not in demo / tests)
  static bool lastDock = onDock();
  bool dock = onDock();
  if (dock != lastDock) {
    lastDock = dock;
    Serial.printf("Dock: %s\n", dock ? "placed" : "lifted");
    if (!demoMode && state != TEST && state != LIGHT && state != LAMP) setState(dock ? DOCKED : LIFTED);
  }
  delay(5);
}
