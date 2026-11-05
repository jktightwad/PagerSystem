// OTA proof of concept - PAGER side
//
// Joins the base's access point, compares its own FW_VERSION with the base's
// /version, and if they differ downloads and installs /pager.bin, then reboots
// into the new firmware. The download is verified against the MD5 the base
// sends; a failed or interrupted download leaves the current firmware running.
//
// In the real pager this only happens while ON THE DOCK (charging, not in the
// queue), triggered by the version the base broadcasts over ESP-NOW.
//
// Test: flash v1 over USB. Change FW_VERSION to 2, Sketch -> Export Compiled
// Binary, upload that .bin to the base page with version 2. Press 'u' (or wait
// for the periodic check): the pager updates and the onboard LED blinks twice.
//
// Board: WEMOS LOLIN32 Lite, Arduino-ESP32 core 3.x.
// Tools -> Partition Scheme: one WITH OTA, e.g. "Minimal SPIFFS (1.9MB APP
// with OTA)". The base's partition scheme does not matter for this.
//
// STATUS: written, not compiled or tested.

#include <WiFi.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>

#define FW_VERSION   1

#define AP_SSID      "PoolPager-OTA"
#define AP_PASS      "change-me-please"
#define BASE_URL     "http://192.168.4.1"
#ifndef LED_PIN
#define LED_PIN      22                  // onboard LED (believed active LOW)
#endif
#define CHECK_EVERY_MS 60000

static bool connectToBase() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(AP_SSID, AP_PASS);
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > 10000) {
      Serial.println("Base AP not found");
      WiFi.disconnect(true);
      return false;
    }
    delay(200);
  }
  return true;
}

static int fetchBaseVersion() {
  HTTPClient http;
  http.begin(BASE_URL "/version");
  int code = http.GET();
  int v = (code == 200) ? http.getString().toInt() : -1;
  http.end();
  return v;
}

static void checkForUpdate() {
  Serial.printf("Running v%d, checking base...\n", FW_VERSION);
  if (!connectToBase()) return;

  int baseVersion = fetchBaseVersion();
  if (baseVersion <= 0) {
    Serial.println("Base has no firmware stored");
  } else if (baseVersion == FW_VERSION) {
    Serial.println("Up to date");
  } else {
    // Any difference installs, so the base can also roll pagers back
    Serial.printf("Base has v%d, updating...\n", baseVersion);
    WiFiClient client;
    httpUpdate.onProgress([](int done, int total) {
      Serial.printf("  %d / %d bytes\r", done, total);
    });
    httpUpdate.rebootOnUpdate(true);
    t_httpUpdate_return r = httpUpdate.update(client, BASE_URL "/pager.bin");
    // Only reached if the update did not happen
    if (r == HTTP_UPDATE_FAILED) {
      Serial.printf("\nUpdate failed: %s\n", httpUpdate.getLastErrorString().c_str());
    }
  }
  WiFi.disconnect(true);
}

static void blinkVersion() {
  for (int i = 0; i < FW_VERSION; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(250);
    digitalWrite(LED_PIN, HIGH);
    delay(250);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  Serial.printf("\nPager OTA test, firmware v%d. 'u' = check now\n", FW_VERSION);
  blinkVersion();
  checkForUpdate();
}

void loop() {
  static uint32_t lastCheck = millis();
  if (Serial.available() && Serial.read() == 'u') {
    checkForUpdate();
    lastCheck = millis();
  }
  if (millis() - lastCheck > CHECK_EVERY_MS) {
    checkForUpdate();
    lastCheck = millis();
  }
  // Show the version every 5 s so the update is visible without a serial monitor
  static uint32_t lastBlink = 0;
  if (millis() - lastBlink > 5000) {
    blinkVersion();
    lastBlink = millis();
  }
}
