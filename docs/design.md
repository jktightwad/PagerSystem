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
- **Base:** ESP32 with touchscreen, name entry so everyone can see the queue.
- **Charging:** stacked pagers with pass-through pogo contacts.
- **Budget first:** cheapest options, phased purchasing.
- **Security:** security team has approved badge tap and wants to use the
  system as a pen test scenario (scope to be confirmed in writing).

## Proposed (not yet decided)
- **Base display:** "Cheap Yellow Display" ESP32 (2.8" ESP32-2432S028R, or a
  3.5" variant for easier name entry). Its own ESP32 runs ESP-NOW at first.
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
1. Tap badge (or type name) on the base, lift the top pager off the stack.
2. Queue shows names in order.
3. "Next" on the base alerts the next pager; holder presses its button to
   acknowledge. No acknowledgement within X minutes: skip to the next person.
4. Pager back on the stack = leave queue.
5. Low battery warning; flag pagers left off the dock too long.

## Badge tap
- Office fobs are **HID iCLASS, SE enabled** (Flipper Picopass read the CSN).
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

## Hardening (cheap, planned)
- Salted hash of CSNs, ESP-NOW encryption (check encrypted peer limit fits
  8 pagers + bridge), message counters against replay.
- If the base later joins Wi-Fi (Slack/Teams), treat it as untrusted IoT.
  Teams needs Workflows webhooks (Office 365 connectors retired May 2026).

## Open questions
- Range test results (see `range_test/`).
- Badge reader experiment: ST25R3916 or PN5180?
- 5 V two stacks vs 12 V single stack.
- Queue rules: acknowledgement timeout, max game time?
- LOLIN32 Lite battery connector (PH 2.0 vs XH 2.54), USB chip, LED pin.
- Security's pen test scope.

## Phases
1. Prove it: range test, pager alert test, badge CSN read test.
2. Base UI + full pager set.
3. Charging stacks + 3D-printed enclosures.
4. Optional: radio bridge with external antenna, Slack/Teams.
