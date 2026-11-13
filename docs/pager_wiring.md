# Pager wiring (draft)

## Power plan (current)
```
bottom pogo 5V --+------------------------------> top pogo 5V   (pass-through to the next pager up)
                 +- 100k -+- 100k - GND
                 |        +--> GPIO 34          (dock sense)
                 +- 1N5819 --> USB-C plug pigtail VBUS --> LOLIN32 USB-C  (onboard charger -> battery)
bottom pogo GND -+-------------------------------> top pogo GND, pigtail GND

battery + --> P-MOSFET (gate from a GPIO) --> boost board Vin --> 5 V: LED ring + buzzer
LOLIN32 3V3 --> vibration motor (+), switched on its GND side by an NPN (GPIO 27), diode across the motor
LED ring DI <-- 330R <-- (74AHCT125 level shifter, if 3.3 V data proves unreliable at 5 V) <-- GPIO 26
```
- Top and bottom pogo connectors are both at 6 o'clock, directly above each
  other, so the pass-through is two short wires.
- The boost board (3-pin Vin / GND / Vo) has no enable pin; the P-MOSFET
  switches its input so the boost and the ring's idle current are off when
  dark. Set the ring data pin LOW before switching off.
- The buzzer (TDB05, 5 V part) runs from the boost 5 V: the firmware turns
  the boost on for beeps as well as light.
- These small boosts are usually rated ~0.5 A out: keep the ring brightness
  capped (pure red / green / blue at moderate brightness is well inside it).
- Layout: `enclosure/layout/`.

The sections below are the earlier stripboard notes; pin numbers still apply.

Through-hole / stripboard only. **Not yet built or verified.** Check every pin
number against the silkscreen on your LOLIN32 Lite before soldering. All pins
below were confirmed present on the USB-C LOLIN32 Lite pinout. The pins
below were chosen to avoid ESP32 strapping pins (0, 2, 5, 12, 15) and to keep
analog inputs on ADC1 (GPIO 32-39), because ADC2 can't be used while the radio
is on.

## Pin map (matches `pager_alert_test.ino`)

| Function | LOLIN32 pin | Parts |
|---|---|---|
| WS2812 ring DI (data in) | GPIO 26 | 330 Ω series resistor, close to the ring. DO not connected |
| Active buzzer | GPIO 25 | 1 kΩ to NPN base |
| Vibration motor (3 V coreless) | GPIO 27 | NPN (330 Ω) or logic-level MOSFET, see below |
| Touch module OUT (acknowledge) | GPIO 33 | Module VCC to 3V3, GND to GND, OUT to GPIO 33. Sketch assumes OUT goes HIGH when touched (`TOUCH_ACTIVE_HIGH 1`); set 0 for a plain button to GND. RTC pin, can wake from deep sleep |
| Dock sense | GPIO 34 | 100 kΩ / 100 kΩ divider from the pogo 5 V (before the diode) |
| Battery voltage | GPIO 35 | 100 kΩ / 100 kΩ divider from battery + |
| Onboard LED | GPIO 22 | On the board |

## Power

The LOLIN32 Lite (USB-C, CH340C version) has **no 5V pin and no BAT pin** on
its headers: only **3V** and **G**. Battery + is only on the JST connector
(surface-mount; silkscreen `+` on the pin nearest the board edge).

```
Dock pogo 5V ──┬──────────────────────────────► pass-through to top pogo (thick wire)
               ├── 100k ──┬── 100k ── GND        (dock sense -> GPIO 34)
               │          └──► GPIO 34
               └── 1N5819 ──► USB-C plug pigtail VBUS ──► LOLIN32 USB-C port
Dock pogo GND ─────────────► USB-C plug pigtail GND      (onboard charger + LED)

LiPo ─► female JST pigtail ─► stripboard BAT+/GND rails ─► male JST pigtail ─► LOLIN32 JST
BAT+ rail ───────────────────────────────────────┬──► WS2812 ring VCC (+ 470 µF to GND)
                                                 ├──► buzzer +, motor + (switched on GND side)
                                                 └── 100k ──┬── 100k ── GND  (battery sense)
                                                            └──► GPIO 35
```

- **Battery tap:** the board's JST connector is surface-mount (no
  through-hole pins), so the battery is routed through the stripboard with
  two JST pigtails (female from the battery, male to the board). Battery and
  board stay unmodified. Match pigtail size to the board (PH 2.0 vs XH 2.54)
  and check polarity with a meter before plugging into the board.
- Optional: a through-hole slide switch in the BAT+ rail for storage. A
  switched-off pager does not charge on the dock.
- **Charging uses a short USB-C plug pigtail** (male USB-C breakout or cut
  cable) plugged into the board inside the pager, with VBUS/GND wired to the
  pogo pins. Same approach as SkHCrusher/customer-pager (micro-USB plug).
  To reprogram, unplug the pigtail and plug in a PC cable (or use OTA).
- Alternative: a TP4056 charger module charging the LiPo directly from the
  pogo 5 V; frees the USB-C port but adds a part per pager.
- **Check LiPo polarity** before plugging in: cheap LiPo JST leads are often
  reversed relative to the board. Connector size reported as PH 2.0 or
  XH 2.54 by different sources; compare with the actual board.
- **Bench testing without a battery:** use the **3V** pin as "LiPo +" for
  the ring, buzzer and motor (ring at the sketch's default brightness).
- **WS2812 on battery voltage (3.0-4.2 V)** with 3.3 V data usually works.
- **Ring current:** up to ~1 A at full white on 16 LEDs; the sketch caps
  brightness at 64/255. If standby time is poor, add a P-channel MOSFET to
  switch the ring's supply.

## Beeper: active buzzer (GPIO 25)

```
 LiPo + ──┬──────────────┐
          │              │
      1N4148         Buzzer (+)   (longer leg / "+" mark)
     (optional,       Buzzer (-)
      band to LiPo +)    │
          └──────────────┤
                         C
 GPIO 25 ── 1 kΩ ──────► B  2N2222 / PN2222A
                         E
                         │
                        GND
```
- Sketch: `ACTIVE_BEEPER 1` (default). Check the buzzer's rated voltage;
  a 5 V-only part will be quieter at LiPo voltage.
- TO-92 2N2222A / PN2222A is usually E-B-C (flat face toward you, legs
  down). Check the datasheet for your exact part.

## Vibration: 3 V coreless motor (GPIO 27)

Same type as the SkHCrusher/customer-pager parts list ("Vibration motor
3.7V"): a small coreless vibration motor with its eccentric weight already
fitted. These usually draw well under 300 mA, so the **2N2222 option is
expected to be enough**; measure the running current at 3 V to confirm:

| Running current | Driver |
|---|---|
| under ~300 mA | 2N2222 with a **330 Ω** base resistor |
| ~300 mA - 1 A, or unknown | logic-level MOSFET (TO-220): **IRLZ44N** or **IRLB8721**, 100 Ω gate resistor, 100 kΩ gate-to-GND |

```
 LiPo + ──┬───────────────┐
          │               │
       1N5819          Motor (+)
      (band to         Motor (-)
       LiPo +)            │
          └───────────────┤
                          D
 GPIO 27 ── 100 Ω ──┬───► G   IRLZ44N / IRLB8721  (G-D-S, check datasheet)
                    │     S
                  100 kΩ  │
                    │     │
                   GND   GND
```
(2N2222 version: same, with GPIO 27 -> 330 Ω -> base, emitter to GND,
collector to motor (-), no 100 kΩ.)

- **1N5819 Schottky across the motor is required** (band toward LiPo +).
- **470 µF electrolytic** across LiPo + / GND near the motor and ring, so
  motor start-up doesn't brown out the ESP32.
- The sketch drives the motor with 20 kHz PWM; `VIBE_STRENGTH` (0-255) sets
  the strength. ~180 averages ~3 V from a full LiPo.
- Optional: 100 nF ceramic across the motor terminals for noise.
- Bench test without a battery: use the LOLIN32 **3V3** pin as "LiPo +"
  (not 5V for a 3 V motor).
- Run the motor and buzzer grounds back to the LOLIN32 GND separately from
  the LED ring's ground.

## PN5180 (base unit, badge test)

| PN5180 | ESP32 |
|---|---|
| 5V | 5V (RF power) |
| 3.3V | 3.3V (logic) |
| GND | GND |
| NSS | GPIO 5 |
| MOSI | GPIO 23 |
| MISO | GPIO 19 |
| SCK | GPIO 18 |
| BUSY | GPIO 17 |
| RST | GPIO 16 |

GPIO, IRQ, AUX and REQ are not used. Pins match the playfultechnology
library README. GPIO 5 is a strapping pin, which is fine for NSS (the
library's own suggested wiring); move it if boot problems appear.

### Troubleshooting SPI (learned on the bench)
- `SPI send error 3`: commands aren't reaching the PN5180 (power, NSS, SCK,
  MOSI) or BUSY isn't wired.
- `MISO during command: 00 00 00` and version bytes all 00: no data coming
  back. Check MISO, then run the sketch's GPIO loopback test (type `l` with a
  jumper from the MOSI pin to the MISO pin).
- On the ESP32-C3 SuperMini, **using GPIO 5 as MISO didn't work** in this
  setup (replies read as zeros), although the pin works for other uses; the
  cause wasn't established. Moving MISO to GPIO 0 and MOSI to GPIO 1 fixed it
  (`env:esp32c3_supermini_alt_spi` in `pn5180_csn_test/platformio.ini`).