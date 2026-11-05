// Pager alert hardware test: 16-LED WS2812 ring, piezo beeper, vibration motor,
// acknowledge button, dock-sense and battery readings.
//
// Simulates the real "your turn" alert so we can judge how noticeable it is:
//   Serial 'a' = start alert, press the pager button (or 's') = acknowledge.
//
// Libraries: "Adafruit NeoPixel" (1.12 or newer for Arduino-ESP32 core 3.x).
// Board: WEMOS LOLIN32 Lite, Arduino-ESP32 core 3.x. Serial 115200.
// Wiring: see docs/pager_wiring.md. Check pin numbers against your board's
// silkscreen before wiring.
//
// STATUS: written, not compiled or tested.

#include <Adafruit_NeoPixel.h>

// ---- Pins (all avoid ESP32 strapping pins 0, 2, 5, 12, 15) ----
#define PIN_RING      26   // WS2812 DIN, via 330 ohm resistor
#define PIN_BEEPER    25   // NPN base (1k) -> piezo
#define PIN_VIBE      27   // NPN base (330R-1k) or logic-level MOSFET gate (100R) -> motor
#define PIN_BUTTON    33   // to GND; RTC pin so it can wake from deep sleep later
#define PIN_DOCK_ADC  34   // 100k/100k divider from the dock 5 V tap (ADC1)
#define PIN_BATT_ADC  35   // 100k/100k divider from battery + (ADC1)
#define PIN_BOARD_LED 22   // onboard LED (believed active LOW)

// ---- Options ----
#define RING_LEDS        16
#define MAX_BRIGHTNESS   64     // 0-255. 16 LEDs at full white can draw ~1 A; keep low
#define ACTIVE_BEEPER    1      // 1 = active buzzer (has its own oscillator, just on/off)
                                // 0 = passive piezo / magnetic buzzer (driven with a tone)
#define VIBE_STRENGTH    180    // 0-255 PWM duty. A 3 V motor on a 4.2 V LiPo: ~180 = ~3 V
#define BEEP_FREQ_HZ     2700   // passive only: try 2000-4000 to find the loudest
#define DIVIDER_RATIO    2.0f   // both dividers are 100k/100k

Adafruit_NeoPixel ring(RING_LEDS, PIN_RING, NEO_GRB + NEO_KHZ800);

enum State { IDLE, ALERT, ACKED };
State state = IDLE;
uint32_t stateSince = 0;

// ---------------- Outputs ----------------

void beeper(bool on) {
#if ACTIVE_BEEPER
  digitalWrite(PIN_BEEPER, on ? HIGH : LOW);
#else
  if (on) tone(PIN_BEEPER, BEEP_FREQ_HZ);
  else noTone(PIN_BEEPER);
#endif
}

// Motor is driven with 20 kHz PWM (above hearing) so its strength can be set
void vibe(bool on) { ledcWrite(PIN_VIBE, on ? VIBE_STRENGTH : 0); }

void ringFill(uint32_t color) {
  ring.fill(color);
  ring.show();
}

void allOff() {
  beeper(false);
  vibe(false);
  ringFill(0);
}

// ---------------- Inputs ----------------

float readVolts(int pin) {
  // analogReadMilliVolts uses the chip's calibration; divider restores the real voltage
  return analogReadMilliVolts(pin) * DIVIDER_RATIO / 1000.0f;
}

bool onDock() { return readVolts(PIN_DOCK_ADC) > 4.0f; }

// Debounced press detection (true once per press)
bool buttonPressed() {
  static bool last = HIGH;
  static uint32_t changedAt = 0;
  static bool reported = false;
  bool now = digitalRead(PIN_BUTTON);
  if (now != last) {
    last = now;
    changedAt = millis();
    reported = false;
  }
  if (now == LOW && !reported && millis() - changedAt > 30) {
    reported = true;
    return true;
  }
  return false;
}

// ---------------- Patterns ----------------

void setState(State s) {
  state = s;
  stateSince = millis();
  allOff();
  const char *names[] = {"IDLE", "ALERT", "ACKED"};
  Serial.printf("-> %s\n", names[s]);
}

// Alert: rotating orange comet on the ring, beep-beep-beep, vibration pulses.
// After 30 s it escalates (faster, brighter, longer vibration).
void runAlert() {
  uint32_t t = millis() - stateSince;
  bool escalated = t > 30000;

  // Ring: comet with a fading tail
  uint16_t stepMs = escalated ? 40 : 70;
  int head = (t / stepMs) % RING_LEDS;
  uint8_t bright = escalated ? 255 : 160;
  ring.clear();
  for (int i = 0; i < 5; i++) {
    int idx = (head - i + RING_LEDS) % RING_LEDS;
    uint8_t level = bright >> i;
    ring.setPixelColor(idx, ring.Color(level, level * 2 / 5, 0));  // orange
  }
  ring.show();

  // Beeper: 3 short beeps, then a pause; 2 s cycle (1 s when escalated)
  uint32_t cycle = escalated ? 1000 : 2000;
  uint32_t c = t % cycle;
  bool beepOn = (c < 120) || (c >= 200 && c < 320) || (c >= 400 && c < 520);
  beeper(beepOn);

  // Vibration: 400 ms buzz per cycle (800 ms when escalated)
  vibe(c < (escalated ? 800u : 400u));
}

// Acknowledged: green fill, one confirmation chirp, back to idle after 3 s
void runAcked() {
  uint32_t t = millis() - stateSince;
  int lit = min((int)(t / 30), RING_LEDS);
  ring.clear();
  for (int i = 0; i < lit; i++) ring.setPixelColor(i, ring.Color(0, 180, 0));
  ring.show();
  beeper(t < 150);
  if (t > 3000) setState(IDLE);
}

// Idle: one dim blue blip every 3 s so you can see it's alive
void runIdle() {
  uint32_t t = (millis() - stateSince) % 3000;
  ring.clear();
  if (t < 100) ring.setPixelColor(0, ring.Color(0, 0, 20));
  ring.show();
}

// Step through each output on its own, to check wiring
void componentTest() {
  allOff();
  Serial.println("Ring: red, green, blue, white");
  uint32_t colors[] = {ring.Color(255, 0, 0), ring.Color(0, 255, 0),
                       ring.Color(0, 0, 255), ring.Color(255, 255, 255)};
  for (uint32_t col : colors) {
    ringFill(col);
    delay(700);
  }
  ringFill(0);
  Serial.println("Ring: one LED at a time");
  for (int i = 0; i < RING_LEDS; i++) {
    ring.clear();
    ring.setPixelColor(i, ring.Color(0, 0, 255));
    ring.show();
    delay(60);
  }
  ringFill(0);
  Serial.println("Beeper: 3 x 200 ms");
  for (int i = 0; i < 3; i++) {
    beeper(true);
    delay(200);
    beeper(false);
    delay(200);
  }
  Serial.println("Vibration: 1 s");
  vibe(true);
  delay(1000);
  vibe(false);
  Serial.println("Component test done");
}

void printStatus() {
  Serial.printf("Battery %.2f V | Dock input %.2f V (%s) | Button %s\n",
                readVolts(PIN_BATT_ADC), readVolts(PIN_DOCK_ADC),
                onDock() ? "ON DOCK" : "off dock",
                digitalRead(PIN_BUTTON) == LOW ? "pressed" : "released");
}

#if !ACTIVE_BEEPER
// Sweep the passive piezo to find its loudest frequency
void beepSweep() {
  for (int f = 1500; f <= 5000; f += 250) {
    Serial.printf("%d Hz\n", f);
    tone(PIN_BEEPER, f);
    delay(400);
  }
  noTone(PIN_BEEPER);
}
#endif

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BEEPER, OUTPUT);
  ledcAttach(PIN_VIBE, 20000, 8);  // 20 kHz, 8-bit duty
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BOARD_LED, OUTPUT);
  digitalWrite(PIN_BOARD_LED, HIGH);
  analogSetAttenuation(ADC_11db);  // ~0-3.1 V input range

  ring.begin();
  ring.setBrightness(MAX_BRIGHTNESS);
  allOff();

  Serial.println("\nPager alert test");
  Serial.println("a = alert, s = stop/ack, t = component test, b = battery/dock/button status"
#if !ACTIVE_BEEPER
                 ", f = beeper frequency sweep"
#endif
  );
  printStatus();
  setState(IDLE);
}

void loop() {
  if (Serial.available()) {
    switch (Serial.read()) {
      case 'a': setState(ALERT); break;
      case 's': if (state == ALERT) setState(ACKED); else setState(IDLE); break;
      case 't': componentTest(); setState(IDLE); break;
      case 'b': printStatus(); break;
#if !ACTIVE_BEEPER
      case 'f': beepSweep(); break;
#endif
    }
  }

  bool pressed = buttonPressed();
  if (pressed && state == ALERT) {
    Serial.printf("Acknowledged after %.1f s\n", (millis() - stateSince) / 1000.0f);
    setState(ACKED);
  } else if (pressed && state == IDLE) {
    printStatus();  // handy: press the button to see battery/dock status
  }

  switch (state) {
    case ALERT: runAlert(); break;
    case ACKED: runAcked(); break;
    case IDLE:  runIdle();  break;
  }

  // Dock change report
  static bool lastDock = onDock();
  bool dock = onDock();
  if (dock != lastDock) {
    lastDock = dock;
    Serial.printf("Dock: %s\n", dock ? "placed on dock" : "lifted off dock");
  }

  delay(10);
}
