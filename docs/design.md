# Pool table pager: design notes

Status: design phase. Nothing below is final until marked **Decided**.

## Goal
People reserve the next turn at the office pool table, take a rechargeable
pager to their desk, and get alerted (light, buzzer, vibration) when it's their
turn. Must work without office Wi-Fi. At least 4 pagers; currently planning 8.

## Decided
- **Radio:** ESP-NOW (ESP32 to ESP32, no router). Pending range test.
- **Pager board:** WEMOS LOLIN32 Lite (cost). Through-hole / stripboard build,
  no SMD. Large enclosure (hard to lose, room for a big LiPo).
- **Base:** ESP32 with touchscreen showing the queue, plus an on-screen
  keyboard to:
  - register a name against a fob (first tap of an unknown fob), and
  - pick a name from the registered list, or type a new one, when no fob
    is available.
- **Base input:** touchscreen keyboard for typing names, plus a **rotary
  encoder with push button** (EC11-type, through-hole) to scroll the name
  list and choose add / edit / delete / select. LVGL supports encoder input
  alongside touch.
- **Pager alerts:** 16-LED WS2812 ring, piezo beeper, vibration motor,
  acknowledge button (see `docs/pager_wiring.md`).
- **OTA updates:** pagers update themselves from the base when they see a
  different firmware version (see "OTA updates" below).
- **Charging:** stacked pagers with pass-through pogo contacts.
- **Budget first:** cheapest options, phased purchasing.
- **Security:** security team has approved badge tap and wants to use the
  system as a pen test scenario (scope to be confirmed in writing).

## Proposed (not yet decided)
- **Base display:** "Cheap Yellow Display" ESP32. The 2.8" resistive model
  (ESP32-2432S028R) is cheapest but cramped for an on-screen keyboard; a
  3.5" variant (capacitive if budget allows) is the better fit for name
  entry. UI built with LVGL (has keyboard and list widgets). Its own ESP32
  runs ESP-NOW at first. The CYD's microSD slot can hold pager firmware for
  OTA and the name list.
- **Charging bus:** 5 V, two stacks of 4 (cheapest). Alternative: one stack of
  8 on a 12 V bus with a buck module per pager.
- **Stack contacts:** 4-pin magnetic pogo pairs (2 pins V+, 2 GND), keyed
  3D-printed nesting so units only stack one way. Per pager: Schottky
  (1N5819) on the tap to its own input, never in the pass-through path.
- **Pager I/O:** piezo buzzer, vibration motor (2N2222 + 1N4148 flyback),
  LEDs or short WS2812 strip (powered from battery), one acknowledge button,
  dock-sense divider and battery divider on **ADC1 pins (GPIO32-39)**, since
  ADC2 is unavailable while the radio is on.
- **Power strategy:** radio stays listening while off the dock (pagers are off
  the dock for short periods). To be confirmed by measuring current.

## Queue flow (proposed)
1. Tap badge on the base: a known fob shows the name; an unknown fob opens
   the keyboard to register a name. No fob: pick from the name list or type a
   name. Then lift the top pager off the stack.
2. Queue shows names in order.
3. "Next" on the base alerts the next pager; holder presses its button to
   acknowledge. No acknowledgement within X minutes: skip to the next person.
4. Pager back on the stack = leave queue.
5. Low battery warning; flag pagers left off the dock too long.

## Badge tap
- Office fobs are **HID iCLASS, SE enabled** (Flipper Picopass read the CSN).
- **Confirmed working: PN5180** (`pn5180_csn_test/`) reads the CSN with no
  keys, using ACTALL / IDENTIFY / SELECT in ISO 15693 mode with the PN5180's
  hardware CRC disabled. Reply CRC verified in software: CRC-16 (reflected
  poly 0x8408), preset **E012h, not inverted**. Stable across repeated reads.
  Still to check: matches Flipper byte order, colleague fob differs, read
  range, reading through the 3D-printed front panel.
- Plan: identify by **CSN only**, store a salted hash, never touch the SE
  access data. CSN is not secret and can be replayed: fine for a pool queue.
- RC522 / PN532 can't read iCLASS.
- Candidates, cheapest first:
  - **ST25R3916 module (ELECHOUSE)**: same chip as the Flipper; iCLASS CSN
    read needs porting from Picopass. No existing ESP32 port found.
  - **PN5180**: iCLASS only via a discontinued library; mixed reports.
  - Fallback: CSN-configured HID R10/R40 reader over Wiegand (documented
    ESP32/Arduino use, higher cost), or OMNIKEY 5427CK on an ESP32-S3 USB host.
- Name entry always available as a fallback.

## OTA updates (proposed; proof of concept in `ota_test/`)
- Pager firmware has a version number and reports it to the base over
  ESP-NOW. The base broadcasts the version of the firmware it holds.
- A pager updates only when **on the dock** (powered), **not in the queue**,
  and the versions **differ** (so uploading an older build rolls back).
- The base switches on a WPA2 access point on the ESP-NOW channel; the
  pager joins it, downloads `pager.bin` over HTTP, verifies it against the
  MD5 the base sends, installs to the spare OTA slot and reboots. One pager
  at a time; the AP goes off afterwards.
- New firmware gets onto the base via an upload page (phone or laptop joined
  to the base AP), or later from the microSD card.
- Pagers need an OTA partition scheme (e.g. "Minimal SPIFFS (1.9MB APP with
  OTA)"), so the first flash of every pager must use it.
- **To verify:** whether automatic rollback after a bad boot is available
  with the stock Arduino bootloader. Until then, test each release on one
  pager before uploading it to the base.
- **Security (pen test relevant):** an OTA path is the easiest way to take
  over a device. Planned: AP password, MD5 integrity check now; firmware
  signing (only accept images signed with our key) before deployment.
- Base updates itself over USB for now; OTA for the base later.

## Hardening (cheap, planned)
- Salted hash of CSNs, ESP-NOW encryption (check encrypted peer limit fits
  8 pagers + bridge), message counters against replay.
- If the base later joins Wi-Fi (Slack/Teams), treat it as untrusted IoT.
  Teams needs Workflows webhooks (Office 365 connectors retired May 2026).

## Open questions
- Range test results (see `range_test/`).
- Badge reader: **PN5180 chosen** (CSN read confirmed); range and panel
  thickness still to test.
- Base display size: 2.8" vs 3.5" CYD for the keyboard.
- **Base pin budget:** the CYD exposes only a few spare GPIOs. PN5180 (SPI +
  BUSY + RST + NSS) plus encoder (A, B, push) likely won't fit directly.
  Options: (a) a LOLIN32 as a co-processor for the PN5180 (and later the
  external-antenna radio), talking to the CYD over UART; (b) an I2C encoder
  module; (c) share the SD card's SPI bus with the PN5180. Check the exact
  CYD model's free pins first.
- 5 V two stacks vs 12 V single stack.
- Queue rules: acknowledgement timeout, max game time?
- LOLIN32 Lite battery connector (PH 2.0 vs XH 2.54), USB chip, LED pin.
- Security's pen test scope.

## Phases
1. Prove it: range test, pager alert test, badge CSN read test.
2. Base UI + full pager set.
3. Charging stacks + 3D-printed enclosures.
4. Optional: radio bridge with external antenna, Slack/Teams.
