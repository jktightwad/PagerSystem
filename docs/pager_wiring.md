# Pager wiring (draft)

Through-hole / stripboard only. **Not yet built or verified.** Check every pin
number against the silkscreen on your LOLIN32 Lite before soldering. The pins
below were chosen to avoid ESP32 strapping pins (0, 2, 5, 12, 15) and to keep
analog inputs on ADC1 (GPIO 32-39), because ADC2 can't be used while the radio
is on.

## Pin map (matches `pager_alert_test.ino`)

| Function | LOLIN32 pin | Parts |
|---|---|---|
| WS2812 ring DIN | GPIO 26 | 330 Ω series resistor, close to the ring |
| Active buzzer | GPIO 25 | 1 kΩ to NPN base |
| Vibration motor (3 V coreless) | GPIO 27 | NPN (330 Ω) or logic-level MOSFET, see below |
| Acknowledge button | GPIO 33 | Button to GND (internal pull-up). RTC pin, can wake from deep sleep |
| Dock sense | GPIO 34 | 100 kΩ / 100 kΩ divider from the dock 5 V (before the diode) |
| Battery voltage | GPIO 35 | 100 kΩ / 100 kΩ divider from battery + |
| Onboard LED | GPIO 22 | On the board |

## Power

```
Dock pogo 5V ──┬──────────────────────────────► pass-through to top pogo (thick wire)
               ├── 100k ──┬── 100k ── GND        (dock sense -> GPIO 34)
               │          └──► GPIO 34
               └── 1N5819 ──► LOLIN32 "5V" pin   (charges the LiPo via onboard charger)

LiPo + ──┬──► LOLIN32 JST battery connector
         ├──► WS2812 ring +5V/VCC   (+ 470 µF electrolytic across ring VCC/GND)
         ├──► buzzer +, motor +      (switched on their GND side)
         └── 100k ──┬── 100k ── GND  (battery sense -> GPIO 35)
                    └──► GPIO 35
```

- **Battery + tap:** if your board has no BAT pin, take battery + from the
  JST lead (splice, or a JST Y-lead).
- **To verify:** that feeding 5 V into the LOLIN32 "5V" pin charges the
  battery (it should be the same net as USB VBUS, but check the schematic or
  test with a meter on the charge LED).
- The diode drops ~0.3-0.4 V, so the charger sees ~4.6 V. That's above the
  TP4054's minimum, but measure it on the real stack.
- **WS2812 on battery voltage (3.0-4.2 V)** with 3.3 V data usually works
  reliably. Powering the ring from 5 V would need a level shifter on DIN.
- **Ring current:** up to ~1 A at full white on 16 LEDs. The sketch caps
  brightness at 64/255. The ring also draws a small idle current even when
  dark. If standby time turns out poor, add a P-channel MOSFET to switch the
  ring's supply.

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
- One ESP32-C3 SuperMini on the bench had a **dead GPIO 5 input** (pad
  measured 3.3 V, chip read 0). Fixed by moving MISO to GPIO 0 and MOSI to
  GPIO 1 via the `PN5180_SCK/MISO/MOSI` build flags in `platformio.ini`.
