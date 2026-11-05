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
| Piezo beeper | GPIO 25 | 1 kΩ to NPN base |
| Vibration motor | GPIO 27 | 1 kΩ to NPN base |
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
         ├──► piezo +, motor +       (switched on their GND side by the NPNs)
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

## Drivers (identical for beeper and motor)

```
GPIO ── 1k ──► 2N2222 base
               2N2222 emitter ── GND
               2N2222 collector ── load (-)
               load (+) ── LiPo +
Motor only: 1N4148 across the motor, cathode (band) to LiPo +
```

- **Beeper type:** set `ACTIVE_BEEPER` in the sketch. Active buzzers just
  need on/off. Passive piezos and magnetic buzzers are driven with a tone;
  use the `f` command to find the loudest frequency.

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
