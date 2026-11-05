// Pool pager ESP-NOW range test - WALKER (carry it around the office)
//
// Sends a ping every PING_INTERVAL_MS. The base replies with a pong, so each
// successful round trip proves BOTH directions work (base -> pager alert and
// pager -> base acknowledge), like the real system.
//
// Every 5 s it prints: round trips answered, loss %, and signal strength
// measured at each end. Keep it on a laptop (USB serial monitor, 115200)
// while walking, and stand still ~15 s at each desk you test.
//
// Pings are broadcast, so there are no automatic retries: the loss figure is
// the raw worst case. The real system will retry until acknowledged.
//
// Requires Arduino-ESP32 core 3.x. Board: "WEMOS LOLIN32 Lite".
// Both units MUST use the same CHANNEL and USE_LR_MODE values.

#include <WiFi.h>
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

const uint32_t MAGIC = 0x504F4F4C;  // "POOL"
const uint8_t BROADCAST[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

enum : uint8_t { MSG_PING = 1, MSG_PONG = 2 };

struct __attribute__((packed)) Packet {
  uint32_t magic;
  uint8_t  type;
  uint32_t seq;
  int8_t   rssiAtBase;
};

// Updated from the Wi-Fi task, read in loop()
static portMUX_TYPE statsLock = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t winPongs = 0;
static volatile int32_t  winRssiWalkerSum = 0, winRssiBaseSum = 0;
static volatile int8_t   winRssiWalkerMin = 0, winRssiBaseMin = 0;
static volatile uint32_t lastPongMs = 0;

static uint32_t seq = 0;
static uint32_t winPings = 0;
static uint32_t totalPings = 0, totalPongs = 0;

static void onRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len != sizeof(Packet)) return;
  Packet in;
  memcpy(&in, data, sizeof(in));
  if (in.magic != MAGIC || in.type != MSG_PONG) return;

  int8_t rssiWalker = info->rx_ctrl ? info->rx_ctrl->rssi : 0;

  portENTER_CRITICAL(&statsLock);
  if (winPongs == 0 || rssiWalker < winRssiWalkerMin) winRssiWalkerMin = rssiWalker;
  if (winPongs == 0 || in.rssiAtBase < winRssiBaseMin) winRssiBaseMin = in.rssiAtBase;
  winPongs++;
  winRssiWalkerSum += rssiWalker;
  winRssiBaseSum += in.rssiAtBase;
  lastPongMs = millis();
  portEXIT_CRITICAL(&statsLock);
}

static void setupRadio() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

#if USE_LR_MODE
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);
#endif

  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

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

static void report() {
  uint32_t pongs;
  int32_t sumW, sumB;
  int8_t minW, minB;
  portENTER_CRITICAL(&statsLock);
  pongs = winPongs;  sumW = winRssiWalkerSum;  sumB = winRssiBaseSum;
  minW = winRssiWalkerMin;  minB = winRssiBaseMin;
  winPongs = 0;  winRssiWalkerSum = 0;  winRssiBaseSum = 0;
  portEXIT_CRITICAL(&statsLock);

  totalPings += winPings;
  totalPongs += pongs;

  // A late pong can land in the next window, so cap at 100%
  float ok = winPings ? min(100.0f, 100.0f * pongs / winPings) : 0;
  if (pongs) {
    Serial.printf("%5lus  answered %3lu/%3lu (%5.1f%%)  RSSI walker avg %4ld min %4d | base avg %4ld min %4d\n",
                  millis() / 1000, (unsigned long)pongs, (unsigned long)winPings, ok,
                  (long)(sumW / (int32_t)pongs), minW, (long)(sumB / (int32_t)pongs), minB);
  } else {
    Serial.printf("%5lus  answered   0/%3lu (  0.0%%)  NO CONTACT\n",
                  millis() / 1000, (unsigned long)winPings);
  }
  winPings = 0;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // off

  setupRadio();

  Serial.printf("\nRange test WALKER ready. MAC %s  channel %d  LR %s\n",
                WiFi.macAddress().c_str(), CHANNEL, USE_LR_MODE ? "on" : "off");
  Serial.println("RSSI guide (rough): -50 excellent, -70 good, -80 marginal, -90 near the limit");
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
    report();
  }
}
