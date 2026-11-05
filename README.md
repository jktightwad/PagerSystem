# Pool table pager

Queue pager system for the office pool table, similar to restaurant pagers.
ESP32 pagers talk to a touchscreen base over ESP-NOW (no Wi-Fi network needed),
charge on a stackable pogo-pin dock, and alert with light, buzzer and vibration.

**All sketches are written but not yet compiled or tested on hardware.**
Arduino-ESP32 core 3.x is required.

## Building with PlatformIO
Each test folder is its own PlatformIO project (`platformio.ini` inside it),
using the pioarduino platform for Arduino-ESP32 core 3.x. Open the folder in
VS Code / PlatformIO and pick the environment for your board:
- `lolin32_lite`: WEMOS LOLIN32 Lite (pagers)
- `esp32c3_supermini`: ESP32-C3 SuperMini (temporary base); not available
  for `pager_alert_test`, whose pins only exist on the classic ESP32

From a terminal: `pio run -e esp32c3_supermini -t upload`, then
`pio device monitor`. The folders also still open in the Arduino IDE.

| Folder | What it is |
|---|---|
| `docs/design.md` | Decisions, proposals, open questions |
| `docs/pager_wiring.md` | Pager pin map, power and driver wiring; PN5180 wiring |
| `range_test/` | ESP-NOW range test (base + walker) |
| `pager_alert_test/` | WS2812 ring, beeper, vibration, button, dock/battery readings |
| `pn5180_csn_test/` | Read the HID iCLASS CSN with a PN5180 (no keys) |
| `ota_test/` | Over-the-air update proof of concept (base AP + pager) |

## Libraries
- Adafruit NeoPixel (1.12+) for `pager_alert_test`
- PN5180 by playfultechnology (GPL-3.0) for `pn5180_csn_test`.
  Don't install ATrappmann's PN5180 library at the same time (same header name).
