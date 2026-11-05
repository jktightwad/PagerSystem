// Pool pager ESP-NOW range test - BASE (stays at the pool table)
//
// Listens for pings from the walker unit and replies to each one with a pong
// that includes the signal strength (RSSI) the base measured for that ping.
//
// Requires Arduino-ESP32 core 3.x (Boards Manager: "esp32" by Espressif).
// Board: "WEMOS LOLIN32 Lite" (or "ESP32 Dev Module").
// Both units MUST use the same CHANNEL and USE_LR_MODE values.

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

#if ESP_ARDUINO_VERSION_MAJOR < 3
#error "This sketch needs Arduino-ESP32 core 3.x or newer"
#endif

#define CHANNEL      1      // Wi-Fi channel 1-13; must match walker
#define USE_LR_MODE  0      // 1 = Espressif Long Range mode; must match walker
#ifndef LED_PIN
#define LED_PIN      22     // LOLIN32 Lite onboard LED (believed active LOW; check yours)
#endif

const uint32_t MAGIC = 0x504F4F4C;  // "POOL"

enum : uint8_t { MSG_PING = 1, MSG_PONG = 2 };

struct __attribute__((packed)) Packet {
  uint32_t magic;
  uint8_t  type;
  uint32_t seq;
  int8_t   rssiAtBase;  // RSSI the base measured for the ping (pong only)
};

struct Reply {
  uint8_t mac[6];
  Packet  pkt;
};

static QueueHandle_t replyQueue;
static volatile uint32_t pingsReceived = 0;

// Runs in the Wi-Fi task: keep it short, hand work to loop() via a queue
static void onRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len != sizeof(Packet)) return;
  Packet in;
  memcpy(&in, data, sizeof(in));
  if (in.magic != MAGIC || in.type != MSG_PING) return;

  Reply r;
  memcpy(r.mac, info->src_addr, 6);
  r.pkt.magic = MAGIC;
  r.pkt.type = MSG_PONG;
  r.pkt.seq = in.seq;
  r.pkt.rssiAtBase = info->rx_ctrl ? info->rx_ctrl->rssi : 0;
  xQueueSend(replyQueue, &r, 0);
  pingsReceived++;
}

static void setupRadio() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

#if USE_LR_MODE
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);
#endif

  // Force the channel (promiscuous toggle is the common workaround)
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

  esp_wifi_set_max_tx_power(80);  // units of 0.25 dBm -> 20 dBm (driver clamps to max)

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    while (true) delay(1000);
  }
  esp_now_register_recv_cb(onRecv);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // off (active LOW)

  replyQueue = xQueueCreate(16, sizeof(Reply));
  setupRadio();

  Serial.printf("\nRange test BASE ready. MAC %s  channel %d  LR %s\n",
                WiFi.macAddress().c_str(), CHANNEL, USE_LR_MODE ? "on" : "off");
}

void loop() {
  Reply r;
  if (xQueueReceive(replyQueue, &r, pdMS_TO_TICKS(10)) == pdTRUE) {
    if (!esp_now_is_peer_exist(r.mac)) {
      esp_now_peer_info_t peer = {};
      memcpy(peer.peer_addr, r.mac, 6);
      peer.channel = 0;  // current channel
      peer.ifidx = WIFI_IF_STA;
      peer.encrypt = false;
      esp_now_add_peer(&peer);
    }
    esp_now_send(r.mac, (const uint8_t *)&r.pkt, sizeof(r.pkt));

    // Brief LED flash per ping so you can see the base is hearing the walker
    digitalWrite(LED_PIN, LOW);
    delay(20);
    digitalWrite(LED_PIN, HIGH);
  }

  static uint32_t lastPrint = 0;
  if (millis() - lastPrint > 5000) {
    lastPrint = millis();
    Serial.printf("pings received so far: %lu\n", (unsigned long)pingsReceived);
  }
}
