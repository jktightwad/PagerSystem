// Pool pager ESP-NOW range test - WALKER (carry it around the office)
//
// Sends a ping every PING_INTERVAL_MS. The base replies with a pong, so each
// successful round trip proves BOTH directions work (base -> pager alert and
// pager -> base acknowledge), like the real system.
//
// No laptop needed: the walker runs its own Wi-Fi hotspot with a live results
// page. Join "PoolPager-Range" on your phone (password below) and open
// http://192.168.4.1 . At each spot, stand still ~15 s, type a name and tap
// Record. Results can be downloaded as CSV. (Serial output still works too.)
//
// The phone's Wi-Fi shares the ESP-NOW channel, which may lower results
// slightly, so the numbers err on the cautious side.
//
// Pings are broadcast, so there are no automatic retries: the loss figure is
// the raw worst case. The real system will retry until acknowledged.
//
// Requires Arduino-ESP32 core 3.x. Board: "WEMOS LOLIN32 Lite".
// Both units MUST use the same CHANNEL and USE_LR_MODE values.
//
// Power it from a LiPo or a USB power bank while walking.
//
// STATUS: written, not compiled or tested.

#include <WiFi.h>
#include <WebServer.h>
#include <esp_now.h>
#include <esp_wifi.h>

#if ESP_ARDUINO_VERSION_MAJOR < 3
#error "This sketch needs Arduino-ESP32 core 3.x or newer"
#endif

#define CHANNEL           1     // must match base
#define USE_LR_MODE       0     // must match base
#ifndef LED_PIN
#define LED_PIN           22    // LOLIN32 Lite onboard LED (believed active LOW; check yours)
#endif
#define PING_INTERVAL_MS  250
#define REPORT_MS         5000
#define HISTORY_WINDOWS   3     // a recorded spot = the last 3 windows (15 s)
#define MAX_SPOTS         60

#define AP_SSID           "PoolPager-Range"
#define AP_PASS           "pooltable"   // at least 8 characters

const uint32_t MAGIC = 0x504F4F4C;  // "POOL"
const uint8_t BROADCAST[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

enum : uint8_t { MSG_PING = 1, MSG_PONG = 2 };

struct __attribute__((packed)) Packet {
  uint32_t magic;
  uint8_t  type;
  uint32_t seq;
  int8_t   rssiAtBase;
};

// One 5 s measurement window
struct Window {
  uint32_t pings = 0, pongs = 0;
  int32_t  sumW = 0, sumB = 0;  // RSSI sums (walker side, base side)
  int8_t   minW = 0, minB = 0;
};

struct Spot {
  char     name[32];
  uint32_t atSec;
  Window   w;  // the HISTORY_WINDOWS windows combined
};

// Updated from the Wi-Fi task, read in loop()
static portMUX_TYPE statsLock = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t winPongs = 0;
static volatile int32_t  winRssiWalkerSum = 0, winRssiBaseSum = 0;
static volatile int8_t   winRssiWalkerMin = 0, winRssiBaseMin = 0;
static volatile uint32_t lastPongMs = 0;

static uint32_t seq = 0;
static uint32_t winPings = 0;

static Window history[HISTORY_WINDOWS];  // most recent windows, [0] = newest
static uint8_t historyCount = 0;
static Spot spots[MAX_SPOTS];
static uint8_t spotCount = 0;

WebServer server(80);

// ---------------- ESP-NOW ----------------

static void onRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len != sizeof(Packet)) return;
  Packet in;
  memcpy(&in, data, sizeof(in));
  if (in.magic != MAGIC || in.type != MSG_PONG) return;

  int8_t rssiWalker = info->rx_ctrl ? info->rx_ctrl->rssi : 0;

  portENTER_CRITICAL(&statsLock);
  if (winPongs == 0 || rssiWalker < winRssiWalkerMin) winRssiWalkerMin = rssiWalker;
  if (winPongs == 0 || in.rssiAtBase < winRssiBaseMin) winRssiBaseMin = in.rssiAtBase;
  winPongs = winPongs + 1;
  winRssiWalkerSum = winRssiWalkerSum + rssiWalker;
  winRssiBaseSum = winRssiBaseSum + in.rssiAtBase;
  lastPongMs = millis();
  portEXIT_CRITICAL(&statsLock);
}

static void setupRadio() {
  // AP for the phone + STA for ESP-NOW, both on CHANNEL
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(AP_SSID, AP_PASS, CHANNEL);

#if USE_LR_MODE
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);  // phone AP stays normal
#endif

  esp_wifi_set_max_tx_power(80);

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    while (true) delay(1000);
  }
  esp_now_register_recv_cb(onRecv);

  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, BROADCAST, 6);
  peer.channel = 0;
  peer.ifidx = WIFI_IF_STA;
  peer.encrypt = false;
  esp_now_add_peer(&peer);
}

// ---------------- Stats ----------------

static int pct(const Window &w) {
  // A late pong can land in the next window, so cap at 100%
  return w.pings ? min(100, (int)(100 * w.pongs / w.pings)) : 0;
}
static int avgW(const Window &w) { return w.pongs ? w.sumW / (int32_t)w.pongs : 0; }
static int avgB(const Window &w) { return w.pongs ? w.sumB / (int32_t)w.pongs : 0; }

static Window combinedHistory() {
  Window c;
  bool first = true;
  for (int i = 0; i < historyCount; i++) {
    const Window &h = history[i];
    c.pings += h.pings;
    c.sumW += h.sumW;
    c.sumB += h.sumB;
    if (h.pongs) {
      if (first || h.minW < c.minW) c.minW = h.minW;
      if (first || h.minB < c.minB) c.minB = h.minB;
      first = false;
    }
    c.pongs += h.pongs;
  }
  return c;
}

static void closeWindow() {
  Window w;
  portENTER_CRITICAL(&statsLock);
  w.pongs = winPongs;  w.sumW = winRssiWalkerSum;  w.sumB = winRssiBaseSum;
  w.minW = winRssiWalkerMin;  w.minB = winRssiBaseMin;
  winPongs = 0;  winRssiWalkerSum = 0;  winRssiBaseSum = 0;
  portEXIT_CRITICAL(&statsLock);
  w.pings = winPings;
  winPings = 0;

  for (int i = HISTORY_WINDOWS - 1; i > 0; i--) history[i] = history[i - 1];
  history[0] = w;
  if (historyCount < HISTORY_WINDOWS) historyCount++;

  if (w.pongs) {
    Serial.printf("%5lus  answered %3lu/%3lu (%3d%%)  RSSI walker avg %4d min %4d | base avg %4d min %4d\n",
                  millis() / 1000, (unsigned long)w.pongs, (unsigned long)w.pings, pct(w),
                  avgW(w), (int)w.minW, avgB(w), (int)w.minB);
  } else {
    Serial.printf("%5lus  answered   0/%3lu (  0%%)  NO CONTACT\n", millis() / 1000, (unsigned long)w.pings);
  }
}

// ---------------- Web page ----------------

// The page HTML/JS lives in page.h: the .ino prototype scanner would
// mistake its JavaScript functions for C++ ones.
#include "page.h"

static String jsonEscape(const char *s) {
  String o;
  for (; *s; s++) {
    if (*s == '"' || *s == '\\') o += '\\';
    if ((uint8_t)*s >= 0x20) o += *s;
  }
  return o;
}

static void handleStats() {
  const Window &w = history[0];
  String j = "{";
  j += "\"up\":" + String(millis() / 1000);
  j += ",\"ch\":" + String(CHANNEL) + ",\"lr\":" + String(USE_LR_MODE);
  j += ",\"pings\":" + String(historyCount ? w.pings : 0);
  j += ",\"pongs\":" + String(historyCount ? w.pongs : 0);
  j += ",\"pct\":" + String(pct(w));
  j += ",\"rw\":" + String(avgW(w)) + ",\"mw\":" + String((int)w.minW);
  j += ",\"rb\":" + String(avgB(w)) + ",\"mb\":" + String((int)w.minB);
  j += ",\"spots\":[";
  for (int i = 0; i < spotCount; i++) {
    const Spot &s = spots[i];
    if (i) j += ",";
    j += "{\"n\":\"" + jsonEscape(s.name) + "\",\"p\":" + String(pct(s.w));
    j += ",\"rw\":" + String(avgW(s.w)) + ",\"mw\":" + String((int)s.w.minW);
    j += ",\"rb\":" + String(avgB(s.w)) + ",\"mb\":" + String((int)s.w.minB) + "}";
  }
  j += "]}";
  server.send(200, "application/json", j);
}

static void handleRecord() {
  if (spotCount >= MAX_SPOTS) {
    server.send(507, "text/plain", "full");
    return;
  }
  Spot &s = spots[spotCount++];
  strlcpy(s.name, server.arg("name").c_str(), sizeof(s.name));
  s.atSec = millis() / 1000;
  s.w = combinedHistory();
  Serial.printf("Recorded \"%s\": %d%% answered, pager RSSI %d, base RSSI %d\n",
                s.name, pct(s.w), avgW(s.w), avgB(s.w));
  server.send(200, "text/plain", "ok");
}

static void handleCsv() {
  String c = "spot,seconds,answered_pct,pings,pongs,pager_rssi_avg,pager_rssi_min,base_rssi_avg,base_rssi_min,channel,lr_mode\n";
  for (int i = 0; i < spotCount; i++) {
    const Spot &s = spots[i];
    String name = s.name;
    name.replace(",", " ");
    c += name + "," + s.atSec + "," + pct(s.w) + "," + s.w.pings + "," + s.w.pongs + "," +
         avgW(s.w) + "," + (int)s.w.minW + "," + avgB(s.w) + "," + (int)s.w.minB + "," +
         CHANNEL + "," + USE_LR_MODE + "\n";
  }
  server.sendHeader("Content-Disposition", "attachment; filename=range_results.csv");
  server.send(200, "text/csv", c);
}

// ---------------- Main ----------------

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // off

  setupRadio();

  server.on("/", HTTP_GET, [] { server.send_P(200, "text/html", PAGE); });
  server.on("/stats", HTTP_GET, handleStats);
  server.on("/record", HTTP_GET, handleRecord);
  server.on("/results.csv", HTTP_GET, handleCsv);
  server.begin();

  Serial.printf("\nRange test WALKER ready. MAC %s  channel %d  LR %s\n",
                WiFi.macAddress().c_str(), CHANNEL, USE_LR_MODE ? "on" : "off");
  Serial.printf("Phone: join Wi-Fi \"%s\" (password \"%s\"), open http://%s\n",
                AP_SSID, AP_PASS, WiFi.softAPIP().toString().c_str());
}

void loop() {
  static uint32_t lastPing = 0, lastReport = 0;

  if (millis() - lastPing >= PING_INTERVAL_MS) {
    lastPing = millis();
    Packet p = {MAGIC, MSG_PING, ++seq, 0};
    esp_now_send(BROADCAST, (const uint8_t *)&p, sizeof(p));
    winPings++;
  }

  // LED on while the base is answering (pong within the last second)
  digitalWrite(LED_PIN, (millis() - lastPongMs < 1000) ? LOW : HIGH);

  if (millis() - lastReport >= REPORT_MS) {
    lastReport = millis();
    closeWindow();
  }

  server.handleClient();
}
