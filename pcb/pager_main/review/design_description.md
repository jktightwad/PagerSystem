# Pager board: design description for review

**Board:** `pager_main`. 54 x 48 mm, 2-layer FR4 (thickness as ordered; JLC default 1.6 mm). JLC Economic PCBA, top side only.
**Status:** not yet built. DRC is clean (2 starved-thermal warnings). An independent script checks
that every pad sits on the net the design says (0 differences). Nothing has been measured on
hardware yet.

## What it does
This is a table-queue pager. A ring of 16 addressable RGB LEDs shows status. An active buzzer and a
vibration motor give alerts. A touch sensor acknowledges. The pagers stack on a charging base
through spring (pogo) contacts. The ESP32-S3 handles Wi-Fi to the queue server.

## Power
```
LiPo + --- P1.2 (BAT+) --- SW1 (storage switch) --- VBAT --+-- U1 B+ (module's battery input / charger)
LiPo - --- P1.1 ------------------------------------ GND   +-- LED1-16 VDD (+ CL1-16 100 nF each, C3 47 uF bulk)
                                                            +-- BZ1 + (active buzzer, switched low side by Q1)
                                                            +-- motor + (P2.2, switched low side by Q2, D1 flyback)
                                                            +-- R6/R7 divider -> GP2 (battery voltage)
Dock pogo 5V --- J2.2 --- POGO5V --+-- U1 5V pin (module charges the LiPo from it)
                                   +-- R8/R9 divider -> GP1 (docked / not docked)
U1 3V3 (module regulator) --- J1.3 touch module VCC
```
- Single 1S LiPo, 3.0 to 4.2 V. The LEDs, buzzer and motor run straight from VBAT. Only the touch
  module uses the module's 3.3 V.
- Charging is done by the charger on the SuperMini module (U1), fed from the dock's 5 V through U1's
  5 V pin. The board itself has no charger.
- SW1 is a storage switch. It is normally on, so a switched-off pager does not charge.

## Signals (ESP32-S3 GPIO)
| GPIO | Net | Use |
|---|---|---|
| GP1 | DOCK_SENSE | dock 5 V / 2 (R8, R9 100k; C2 100 nF), analog in |
| GP2 | BAT_SENSE | VBAT / 2 (R6, R7 100k; C1 100 nF), analog in |
| GP4 | TOUCH | touch module output (module on J1, 3.3 V) |
| GP5 | RING_IO | LED data, through R5 330R to LED1 DIN; LEDs chained DOUT to DIN |
| GP12 | BUZ_IO | buzzer on/off: R1 330R to Q1 gate, R2 100k pull-down |
| GP13 | MOT_IO | motor (PWM): R3 330R to Q2 gate, R4 100k pull-down |

## Expected currents (estimates, not measured)
- **LEDs:** up to about 60 mA each at full white, if they match the WS2812B. That would be about 1 A for
  16. Firmware caps brightness at 64/255, which brings the worst case to roughly 250 mA. The TZ2812's own
  datasheet figure has not been checked.
- **Buzzer:** 30 mA (manufacturer figure at 5 V).
- **Motor:** unknown. Coreless vibration motors are typically under 100 mA, but this one is not measured.
- **ESP32-S3:** Wi-Fi transmit peaks of a few hundred mA, drawn through the module's regulator.

## Please check in particular
1. **LED supply range.** The TZ-5050S2RGB-5V-I4-H1 (C26167850) listing / datasheet I read gives 3.5 to
   7.5 V operating, with 3.0 V as an absolute figure. The battery runs down to 3.0 V. Is that
   acceptable, and what happens to the LEDs between 3.0 and 3.5 V?
2. **LED data level.** The data line is 3.3 V and VDD is up to 4.2 V. That is within spec if the input
   threshold is 0.7 x VDD (as on the WS2812B), but the TZ2812 datasheet value has not been checked.
3. **Dock input protection.** POGO5V goes straight to U1's 5 V pin, with no reverse-polarity
   protection and nothing to stop a charged pager feeding the other pagers on the stack through the
   pogo bus. A series Schottky (B5819W) or an ideal-diode IC was considered and not added. One worry
   is that a 0.3 to 0.45 V drop could stop U1's charger working properly; its charger IC is unknown.
4. **Buzzer.** It is an active buzzer with no diode across it. Is one needed? The datasheet does not say
   whether it is magnetic or piezo inside.
5. **MOSFET drive.** AO3400A gates are driven at 3.3 V through 330R with 100k pull-downs. Is that
   adequate for the motor current? The motor is PWM'd at about 20 kHz in firmware.
6. **Battery-sense drain.** The R6/R7 divider draws about 21 uA continuously whenever SW1 is on.
7. **Decoupling and bulk capacitance.** Is 47 uF (C3) plus 100 nF per LED enough for VBAT, given the
   LED, motor and Wi-Fi current steps?
8. **Layout.** The module is mounted underneath on castellated pads. Its antenna sits at the board's
   right edge over a copper keep-out on both layers. The ground pours on both layers are stitched
   with about 190 vias.
   - Is the antenna keep-out sufficient?
   - Does any part of the LED or driver layout look like a return-path problem?

## Not checked yet / estimates
- The SS12F44 switch's end-leg spacing (11.2 mm) and the module antenna length (5 mm) are estimates.
- The orientation of the LEDs, buzzer and diode will be checked in JLC's placement preview before
  ordering.
- The firmware for this board (ESP32-S3 pin map above) is not written yet. The current firmware is for
  the LOLIN32 Lite prototype.
