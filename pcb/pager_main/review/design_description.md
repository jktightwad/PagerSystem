# Pager board: design description for review

**Board:** `pager_main`. 54 x 48 mm, 2-layer FR4 (thickness as ordered; JLC default 1.6 mm). JLC Economic PCBA, top side only.
**Status:** revised after a first review (power switch, ideal diode, VBAT ring, bulk cap, buzzer diode,
motor on 3.3 V, then a lower passive buzzer) and routed (EasyEDA autorouter + local fixes). DRC: 0 errors, 0 connection warnings
(silkscreen-only warnings remain); every pad is on the net the design says. Nothing has been measured on this board yet.

## What it does
This is a table-queue pager. A ring of 16 addressable RGB LEDs shows status. A passive (magnetic) buzzer and a
vibration motor give alerts. A touch sensor acknowledges. The pagers stack on a charging base
through spring (pogo) contacts. The ESP32-S3 handles Wi-Fi to the queue server.

## Power
```
LiPo + -- P1.2 (BAT+) -- Q3 AO3401A P-MOSFET (S -> D) -- VBAT --+-- U1 B+ (module's battery input / charger)
            |                 gate (SW_G)                         +-- VBAT ring (1.0 mm copper circle inside the LEDs)
            +-- R10 100k -----+                                   |     -> LED1-16 VDD, CL1-16 100 nF each
                              SW1 (slide switch) -- GND           +-- C3, C4 47 uF bulk
LiPo - -- P1.1 -------------------------------------- GND         +-- BZ1 + (passive buzzer, low side Q1, D3 across it)
                                                                  +-- R6/R7 divider -> GP2 (battery voltage)
Dock pogo 5V -- J2.2 -- POGO5V --+-- U2 LM66100 ideal diode (VIN -> VOUT, CE = VOUT) -- MOD5V -- U1 5V pin
                                 +-- R8/R9 divider -> GP1 (docked / not docked)
U1 3V3 (module regulator) --+-- J1.3 touch module VCC
                             +-- motor + (P2.2, 3 V motor; low side Q2, D1 across it)
```
- Single 1S LiPo, 3.0 to 4.2 V. The LEDs and buzzer run straight from VBAT. The 3 V vibration motor
  and the touch module run from the module's 3.3 V regulator.
- **Power switch:** SW1 (an SS12F44, rated 300 mA per JLC listings) only switches Q3's gate, so the board
  current (up to about 1.3 A) flows through Q3, not the switch. With the switch off, the module's charger can
  still partly charge the battery through Q3's body diode, to roughly 3.5 V.
- **Dock input:** U2 blocks backfeed (a SuperMini puts about 3.2 V out of its 5 V pin with real current
  behind it; measured: 3.24 V into 1 kOhm). It also blocks a reversed dock connection (VIN rated to -6 V)
  and drops about 0.05 V. Measured charging through a 1N5819 instead: a 0.44 V drop. The SuperMini still
  charged with 4.45 V at its 5 V pin.
- **VBAT copper:** a 1.0 mm ring inside the LEDs, open only beside the module cut-out. From Q3: LEDs
  27-58 mOhm, module B+ 74 mOhm (single shortest path; parallel paths make it lower).
- **Placement for short power paths:** battery pads and Q3 / R10 in the bottom-left corner, motor pads and
  Q2 / D1 in the top-left corner, battery sense and buzzer driver above the module next to their GPIOs.
  The LED chain starts at about 1 o'clock (LED1 next to GPIO 5); firmware needs a rotation offset.

## Signals (ESP32-S3 GPIO)
| GPIO | Net | Use |
|---|---|---|
| GP1 | DOCK_SENSE | dock 5 V / 2 (R8, R9 100k; C2 100 nF), analog in |
| GP2 | BAT_SENSE | VBAT / 2 (R6, R7 100k; C1 100 nF), analog in |
| GP4 | TOUCH | touch module output (module on J1, 3.3 V) |
| GP5 | RING_IO | LED data, through R5 330R to LED1 DIN; LEDs chained DOUT to DIN |
| GP12 | BUZ_IO | buzzer tone (PWM, about 2.7 kHz): R1 330R to Q1 gate, R2 100k pull-down |
| GP13 | MOT_IO | motor (PWM): R3 330R to Q2 gate, R4 100k pull-down |

## Expected currents (estimates, not measured)
- **LEDs:** up to about 60 mA each at full white, if they match the WS2812B. That would be about 1 A for
  16. Firmware caps brightness at 64/255, which brings the worst case to roughly 250 mA. The TZ2812's own
  datasheet figure has not been checked.
- **Buzzer:** XHXDZ SMD8530-16R (C49246948), 16 Ohm coil, rated 3.6 V (2.5-4.5 V), max 100 mA at rated voltage with a
  1/2-duty square wave (datasheet). It must only be driven with PWM: with Q1 held on, the coil alone (16 Ohm) would
  take about 260 mA at 4.2 V. R2 holds Q1 off at reset.
- **Motor:** unknown. Coreless vibration motors are typically under 100 mA, but this one is not measured.
- **ESP32-S3:** Wi-Fi transmit peaks of a few hundred mA, drawn through the module's regulator.

## Please check in particular
1. **LED supply range.** The TZ-5050S2RGB-5V-I4-H1 (C26167850) listing / datasheet gives 3.5 to 7.5 V
   operating (3.0 V absolute); the battery runs down to 3.0 V. The plan is a firmware low-battery limit of
   about 3.5 V for the LEDs. Is that enough?
2. **LED data level.** 3.3 V data with VDD up to 4.2 V: in spec if the input threshold is 0.7 x VDD, as on
   the WS2812B. The TZ2812 value has not been checked.
3. **Q3 power switch.** AO3401A with the gate pulled to BAT+ by 100k and switched to GND by SW1. Is the gate
   drive at 3.0 V battery adequate for about 1.3 A peak? Is the body-diode charging path acceptable?
4. **U2 (LM66100) wiring:** CE tied to VOUT (datasheet 8.3.2), pin 4 (N/C) used as a stepping stone for that
   link, and ST tied to GND.
5. **MOSFET drive (Q1, Q2).** AO3400A gates driven at 3.3 V through 330R, with 100k pull-downs. The 3 V motor
   is PWM'd at about 20 kHz from the module's 3.3 V. Is the module regulator adequate for motor + Wi-Fi?
6. **Decoupling and bulk.** 2 x 47 uF (C3, C4) plus 100 nF per LED on VBAT. Enough for the LED, motor and
   Wi-Fi current steps from a 500 mAh cell?
7. **Layout.**
   - The module is mounted underneath on castellated pads, with its antenna at the board edge and copper
     keep-outs on both layers.
   - The ground pours on both layers are stitched with vias.
   - Is the antenna keep-out sufficient?
   - Does any part of the LED or driver layout look like a return-path problem?

## Not checked yet / estimates
- The buzzer's VBAT path resistance was not recalculated after the buzzer change (it is now fed from D3's VBAT pad
  with a 0.5 mm track).
- The SS12F44 switch's end-leg spacing (11.2 mm) and the module antenna length (5 mm) are estimates.
- The orientation of the LEDs, buzzer and diode will be checked in JLC's placement preview before
  ordering.
- The firmware for this board (ESP32-S3 pin map above) is not written yet. The current firmware is for
  the LOLIN32 Lite prototype.
