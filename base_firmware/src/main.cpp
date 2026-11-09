// Pool pager BASE firmware - step 1: network
//
// Joins the strongest Wi-Fi network listed in secrets.h; if none is in range
// it starts its own hotspot (FALLBACK_AP_SSID) so it can still be reached.
// Serves a status page at http://<ip>/ (and http://<BASE_HOSTNAME>.local
// where the network allows mDNS). Queue, badge reader and pager radio come
// in the next steps.
//
// STATUS: written, not compiled or tested.

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#error "Missing include/secrets.h: copy include/secrets.example.h to include/secrets.h and fill it in"
#endif

struct WifiCred { const char *ssid; const char *pass; };
static const WifiCred WIFI_LIST[] = WIFI_NETWORKS;
static const size_t WIFI_COUNT = sizeof(WIFI_LIST) / sizeof(WIFI_LIST[0]);

static WebServer server(80);
static bool apMode = false;

// Scan, then try the listed networks that are in range, strongest first
static bool connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(BASE_HOSTNAME);
  int found = WiFi.scanNetworks();
  Serial.printf("Wi-Fi scan: %d networks\n", found);

  struct Candidate { size_t idx; int rssi; };
  Candidate cand[WIFI_COUNT];
  size_t n = 0;
  for (size_t i = 0; i < WIFI_COUNT; i++) {
    int best = -1000;
    for (int j = 0; j < found; j++)
      if (WiFi.SSID(j) == WIFI_LIST[i].ssid && WiFi.RSSI(j) > best) best = WiFi.RSSI(j);
    if (best > -1000) cand[n++] = {i, best};
  }
  WiFi.scanDelete();
  // strongest first
  for (size_t a = 0; a < n; a++)
    for (size_t b = a + 1; b < n; b++)
      if (cand[b].rssi > cand[a].rssi) { Candidate t = cand[a]; cand[a] = cand[b]; cand[b] = t; }

  for (size_t k = 0; k < n; k++) {
    const WifiCred &c = WIFI_LIST[cand[k].idx];
    Serial.printf("Joining \"%s\" (RSSI %d)...\n", c.ssid, cand[k].rssi);
    WiFi.begin(c.ssid, c.pass);
    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) delay(250);
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("Connected: IP %s, channel %d\n", WiFi.localIP().toString().c_str(), WiFi.channel());
      return true;
    }
    Serial.println("  failed");
    WiFi.disconnect(true);
  }
  return false;
}

static void startHotspot() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(FALLBACK_AP_SSID, FALLBACK_AP_PASS);
  apMode = true;
  Serial.printf("No listed network in range: hotspot \"%s\" at http://%s\n",
                FALLBACK_AP_SSID, WiFi.softAPIP().toString().c_str());
}

static void handleRoot() {
  String ip = apMode ? WiFi.softAPIP().toString() : WiFi.localIP().toString();
  String page =
    "<!doctype html><meta name=viewport content='width=device-width'>"
    "<title>Pool pager</title><h2>Pool pager base</h2>"
    "<p>Network: " + String(apMode ? FALLBACK_AP_SSID " (own hotspot)" : WiFi.SSID().c_str()) +
    "<br>IP: " + ip +
    (apMode ? String("") : "<br>Signal: " + String(WiFi.RSSI()) + " dBm<br>Channel: " + String(WiFi.channel())) +
    "<br>Up: " + String(millis() / 1000) + " s</p>"
    "<p>Queue and pagers: coming in the next step.</p>";
  server.send(200, "text/html", page);
}

void setup() {
  Serial.begin(115200);
  uint32_t t = millis();
  while (!Serial && millis() - t < 3000) delay(10);   // native-USB boards
  Serial.println("\nPool pager base");

  if (!connectWifi()) startHotspot();

  if (MDNS.begin(BASE_HOSTNAME)) {
    MDNS.addService("http", "tcp", 80);
    Serial.printf("mDNS: http://%s.local (may not work on office networks)\n", BASE_HOSTNAME);
  }
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  server.handleClient();

  // Reconnect if the office Wi-Fi drops
  static uint32_t lastCheck = 0;
  if (!apMode && millis() - lastCheck > 10000) {
    lastCheck = millis();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wi-Fi lost, reconnecting...");
      if (!connectWifi()) startHotspot();
    }
  }
}
