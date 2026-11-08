// Pager alert hardware test: 16-LED WS2812 ring, piezo beeper, vibration motor,
// acknowledge button, dock-sense and battery readings.
//
// Demonstrates the pager's light/sound states (colour scheme decided with
// the user; only pure red, green and blue are used, they blend cleanly):
//   DOCKED  red glow: slow pulse while charging, steady when full
//   LIFTED  red charge gauge (lit LEDs = battery %), until the base confirms
//   CONFIRM blue flash + chirp: pager is bound to its holder
//   WAITING bound, in the queue: brief dim blue blip every 5 s (proposal)
//   ALERT   green spinning light + beeps + vibration: your turn
//   ACKED   button pressed: green changes to blue, stays blue until docked
// Serial: d = dock, u = lift, k = confirm, a = your turn, s or button = ack.
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
#define ACTIVE_DRIVE_HZ  0      // active only: 0 = plain on/off (normal). >0 = pulse the
                                // buzzer at this rate instead; use 'f' to compare by ear
#define DIVIDER_RATIO    2.0f   // both dividers are 100k/100k

Adafruit_NeoPixel ring(RING_LEDS, PIN_RING, NEO_GRB + NEO_KHZ800);

enum State { DOCKED, LIFTED, CONFIRM, WAITING, ALERT, ACKED, LIGHT };
State state = DOCKED;
uint32_t stateSince = 0;

// ---------------- Outputs ----------------

// Plain DC on/off for the beeper pin (also used to restore it after tone())
void beeperDc(bool on) {
  pinMode(PIN_BEEPER, OUTPUT);
  digitalWrite(PIN_BEEPER, on ? HIGH : LOW);
}

void beeperTone(int hz) {
  if (hz > 0) {
    tone(PIN_BEEPER, hz);
  } else {
    noTone(PIN_BEEPER);
    beeperDc(false);
  }
}

void beeper(bool on) {
#if ACTIVE_BEEPER && ACTIVE_DRIVE_HZ == 0
  beeperDc(on);
#elif ACTIVE_BEEPER
  beeperTone(on ? ACTIVE_DRIVE_HZ : 0);
#else
  beeperTone(on ? BEEP_FREQ_HZ : 0);
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
  ring.setBrightness(MAX_BRIGHTNESS);  // light test may have changed it
  stateSince = millis();
  allOff();
  const char *names[] = {"DOCKED", "LIFTED", "CONFIRM", "WAITING", "ALERT", "ACKED", "LIGHT"};
  Serial.printf("-> %s\n", names[s]);
}

// Colour at a level (0-255) relative to MAX_BRIGHTNESS
uint32_t red(uint8_t v)   { return ring.Color(v, 0, 0); }
uint32_t green(uint8_t v) { return ring.Color(0, v, 0); }
uint32_t blue(uint8_t v)  { return ring.Color(0, 0, v); }

// Battery as 0-100 %. Linear 3.3 V -> 0 %, 4.15 V -> 100 % (rough; a LiPo
// curve isn't linear). Without the battery divider fitted, simulate 70 %.
int batteryPercent(bool *simulated) {
  float v = readVolts(PIN_BATT_ADC);
  *simulated = v < 2.5f;
  if (*simulated) return 70;
  return constrain((int)((v - 3.3f) / (4.15f - 3.3f) * 100.0f), 0, 100);
}

// DOCKED: faint red. Slow pulse while charging, steady once the battery reads full.
void runDocked() {
  bool sim;
  bool full = batteryPercent(&sim) >= 100;
  uint8_t v = 24;
  if (!full) {
    uint32_t t = (millis() - stateSince) % 3000;          // 3 s breathe
    uint32_t tri = t < 1500 ? t : 3000 - t;
    v = 6 + tri * 30 / 1500;                               // 6..36
  }
  ringFill(red(v));
}

// LIFTED: red charge gauge, one LED per 6.25 %, until the base confirms.
void runLifted() {
  bool sim;
  int pct = batteryPercent(&sim);
  int lit = (pct * RING_LEDS + 99) / 100;                  // round up: 1 % shows 1 LED
  ring.clear();
  for (int i = 0; i < lit; i++) ring.setPixelColor(i, red(160));
  ring.show();
  static uint32_t lastPrint = 0;
  if (millis() - lastPrint > 5000 || lastPrint < stateSince) {
    lastPrint = millis();
    Serial.printf("Charge gauge: %d %% (%d of %d LEDs)%s\n", pct, lit, RING_LEDS, sim ? " (simulated)" : "");
  }
}

// CONFIRM: three quick blue flashes + chirp, then WAITING.
void runConfirm() {
  uint32_t t = millis() - stateSince;
  bool on = (t % 300) < 180;
  ringFill(on && t < 900 ? blue(200) : 0);
  beeper(t < 80);
  if (t > 1000) setState(WAITING);
}

// WAITING: brief dim blue blip every 5 s (bound, in the queue).
void runWaiting() {
  uint32_t t = (millis() - stateSince) % 5000;
  ringFill(t < 150 ? blue(40) : 0);
}

// ALERT: green comet, beep-beep-beep, vibration pulses. Escalates after 30 s.
void runAlert() {
  uint32_t t = millis() - stateSince;
  bool escalated = t > 30000;

  uint16_t stepMs = escalated ? 40 : 70;
  int head = (t / stepMs) % RING_LEDS;
  uint8_t bright = escalated ? 255 : 160;
  ring.clear();
  for (int i = 0; i < 5; i++) {
    int idx = (head - i + RING_LEDS) % RING_LEDS;
    ring.setPixelColor(idx, green(bright >> i));
  }
  ring.show();

  uint32_t cycle = escalated ? 1000 : 2000;
  uint32_t c = t % cycle;
  bool beepOn = (c < 120) || (c >= 200 && c < 320) || (c >= 400 && c < 520);
  beeper(beepOn);
  vibe(c < (escalated ? 800u : 400u));
}

// ACKED: blue fills the ring with a chirp, then stays steady blue until docked.
void runAcked() {
  uint32_t t = millis() - stateSince;
  int lit = min((int)(t / 30), RING_LEDS);
  ring.clear();
  for (int i = 0; i < lit; i++) ring.setPixelColor(i, blue(lit < RING_LEDS ? 200 : 120));
  ring.show();
  beeper(t < 150);
}

// ---------------- Light test ----------------
// Steady colours for judging the ring through the face / diffusion rig.
struct Rgb { uint8_t r, g, b; const char *name; };
// WS2812 green looks much brighter than red, so yellow/orange need little
// green and purple needs little red. Tune by eye through the real face with
// the 'c' command and copy the printed table back here.
Rgb BALLS[] = {
  {255, 110, 0, "1 yellow"}, {0, 0, 255, "2 blue"}, {255, 0, 0, "3 red"},
  {80, 0, 255, "4 purple"},  {255, 35, 0, "5 orange"}, {0, 200, 0, "6 green"},
  {130, 0, 15, "7 maroon"},  {255, 255, 255, "8 white"}};
const int NUM_BALLS = sizeof(BALLS) / sizeof(BALLS[0]);
const uint8_t BRIGHT_STEPS[] = {4, 8, 16, 32, 64, 96, 128, 192, 255};
int lightColor = 0;
int lightStep = 4;   // index into BRIGHT_STEPS (64)

void showLight() {
  const Rgb &c = BALLS[lightColor];
  uint8_t b = BRIGHT_STEPS[lightStep];
  ring.setBrightness(b);
  ring.fill(ring.Color(c.r, c.g, c.b));
  ring.show();
  Serial.printf("Light: %s (R %u G %u B %u) at brightness %u/255%s\n", c.name, c.r, c.g, c.b, b,
                b > 64 ? "  (above 64: use battery/USB 5 V, not the 3V pin, for long)" : "");
}

// 'c R G B' sets the colour currently shown, e.g. "c 255 100 0"
void setColorCommand() {
  int r = Serial.parseInt(), g = Serial.parseInt(), b = Serial.parseInt();
  if (state != LIGHT) setState(LIGHT);
  BALLS[lightColor].r = constrain(r, 0, 255);
  BALLS[lightColor].g = constrain(g, 0, 255);
  BALLS[lightColor].b = constrain(b, 0, 255);
  showLight();
}

// Print the colour table in a form that can be pasted back into the sketch
void printColorTable() {
  Serial.println("Rgb BALLS[] = {");
  for (int i = 0; i < NUM_BALLS; i++)
    Serial.printf("  {%u, %u, %u, \"%s\"},\n", BALLS[i].r, BALLS[i].g, BALLS[i].b, BALLS[i].name);
  Serial.println("};");
}

void lightCommand(char cmd) {
  bool entering = (state != LIGHT);
  if (entering) setState(LIGHT);
  switch (cmd) {
    case 'l': if (!entering) lightColor = (lightColor + 1) % NUM_BALLS; break;  // next ball colour
    case '+': if (lightStep < (int)sizeof(BRIGHT_STEPS) - 1) lightStep++; break;
    case '-': if (lightStep > 0) lightStep--; break;
    case 'w': lightColor = NUM_BALLS - 1; break;                   // white
    case 'g': lightStep = 0; break;                                 // docked-glow level
  }
  showLight();
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

// Play the plain DC beep (an active buzzer's own tone) as a loudness reference
void beepReference() {
  Serial.println("  REF: plain on/off (buzzer's own tone)");
  beeperDc(true);
  delay(700);
  beeperDc(false);
  delay(500);
}

// Sweep drive frequencies to find the loudest / most noticeable. For an
// active buzzer the pitch is set by its internal oscillator, so pulsing it
// mainly changes the sound character; the REF beep is replayed every few
// steps to compare against. A phone sound-meter app gives numbers.
void beepSweep() {
  const int freqs[] = {250, 500, 750, 1000, 1500, 2000, 2300, 2500, 2700, 3000,
                       3300, 3600, 4000, 4500, 5000};
  Serial.println("Beeper sweep (note the step that sounds loudest):");
  beepReference();
  int step = 1;
  for (int f : freqs) {
    Serial.printf("  #%d: %d Hz\n", step, f);
    beeperTone(f);
    delay(700);
    beeperTone(0);
    delay(500);
    if (step % 4 == 0) beepReference();
    step++;
  }
  beepReference();
  Serial.println("Done. Set ACTIVE_DRIVE_HZ (active) or BEEP_FREQ_HZ (passive) to the winner,");
  Serial.println("or leave ACTIVE_DRIVE_HZ 0 if REF was loudest.");
}

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
  Serial.println("States: d = dock, u = lift, k = confirm, a = your turn, s = ack (or press the button)");
  Serial.println("t = component test, b = battery/dock/button status,");
  Serial.println("f = beeper frequency sweep, r = reference beep");
  Serial.println("Light test: l = next ball colour, + / - = brightness, w = white, g = faint glow, s = off");
  Serial.println("  c R G B = set the shown colour (e.g. c 255 100 0), p = print colour table");
  printStatus();
  setState(onDock() ? DOCKED : LIFTED);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'd': setState(DOCKED); break;
      case 'u': setState(LIFTED); break;
      case 'k': setState(CONFIRM); break;
      case 'a': setState(ALERT); break;
      case 's':
        if (state == ALERT) setState(ACKED);
        else if (state == LIGHT) setState(onDock() ? DOCKED : LIFTED);
        break;
      case 't': componentTest(); setState(onDock() ? DOCKED : LIFTED); break;
      case 'b': printStatus(); break;
      case 'f': beepSweep(); break;
      case 'r': beepReference(); break;
      case 'l': case '+': case '-': case 'w': case 'g': lightCommand(c); break;
      case 'c': setColorCommand(); break;
      case 'p': printColorTable(); break;
    }
  }

  bool pressed = buttonPressed();
  if (pressed && state == ALERT) {
    Serial.printf("Acknowledged after %.1f s\n", (millis() - stateSince) / 1000.0f);
    setState(ACKED);
  } else if (pressed) {
    printStatus();  // handy: press the button to see battery/dock status
  }

  switch (state) {
    case ALERT: runAlert(); break;
    case ACKED: runAcked(); break;
    case DOCKED:  runDocked();  break;
    case LIFTED:  runLifted();  break;
    case CONFIRM: runConfirm(); break;
    case WAITING: runWaiting(); break;
    case LIGHT: break;   // holds the colour set by showLight()
  }

  // Dock change report
  static bool lastDock = onDock();
  bool dock = onDock();
  if (dock != lastDock) {
    lastDock = dock;
    Serial.printf("Dock: %s\n", dock ? "placed on dock" : "lifted off dock");
    if (state != LIGHT) setState(dock ? DOCKED : LIFTED);
  }

  delay(10);
}
