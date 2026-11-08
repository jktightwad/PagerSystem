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

## Radio range (POC result)
- Home trial (shop and back yard), ESP32-C3 SuperMini base, LOLIN32 Lite
  walker, channel 1, LR mode off: solid near the base, marginal to failing
  at -85 to -96 dBm. **Line of sight made the biggest difference**; the base
  side heard ~3-5 dB worse than the walker (consistent with the SuperMini's
  small antenna, not proven).
- **Accepted as good enough for the POC.** Office test still to do.
- **Base stays low-profile and reachable** (pagers dock on it), so height for
  range comes from moving the antenna or radio, not the base:
  - enclosure keeps a mounting point (printed knockout) for an **SMA
    bulkhead** + u.FL pigtail: stubby antenna on the base, or a cable to a
    small antenna mounted higher;
  - or a **remote radio module** (small ESP32 with external antenna) mounted
    high, linked to the base by a thin power + serial cable.
- Further options if needed: LR mode, a mains-powered relay node.
- User guidance later: keep pagers on top of the desk, not in drawers or
  behind monitors.

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

## Web-first UI and queue model (proposed)
- **All screens are a web page served by the base** on the **office Wi-Fi**
  (authorized). Any browser works; a dedicated screen is optional (tablet /
  old phone in kiosk mode at the table). Ask IT for a fixed IP or DHCP
  reservation; QR code at the table. Check whether the network is
  WPA2-Enterprise (802.1X): supported on ESP32 but configured differently.
- **Radio bridge:** a separate small ESP32 runs ESP-NOW on a fixed channel
  for the pagers and talks to the base over serial, because the base's
  channel follows the office access point.
- **Base hardware needs no screen:** radio bridge, PN5180, local feedback
  (LEDs / small ring + beeper) at the reader.
- **Flows:** register once (web "Register" -> tap fob at base -> enter name);
  join the queue from your desk; at the table tap fob and lift a pager (the
  lift tells the base which pager); visitors pick/type a name instead.
- **Auth without passwords:** fob registration shows a one-time code that
  links the browser to the person; only that browser or that person's fob
  can change their reservation; admin password for settings / page all /
  mute all. Plain HTTP, so nothing sensitive goes through the page.
- **Capacity:** clients poll every few seconds (ESP32 holds ~10 sockets).
- Queue model: see "Players, pagers and pairing".

## Players, pagers and pairing (proposed)
- **Everyone gets their own pager.** The queue is a list of people. When the
  table frees up, someone chooses "next game: 2 / 3 / 4 players"; the base
  pages the next N waiting people. **Partners are chosen at the table**, not
  by the system.
- **Pagers are numbered like pool balls** (1-8). The LED ring shows the
  ball's colour when idle/bound: 1 yellow, 2 blue, 3 red, 4 purple,
  5 orange, 6 green, 7 maroon, 8 white (black can't be lit).
- **Binding a person to a pager** works from three events, in any order:
  `SCAN` (fob at the base), `LIFT` (pager leaves the dock) and `CLAIM`
  (button pressed on a lifted pager). Rules, highest priority first:
  1. **CLAIM then SCAN** (within 30 s): bind that pager. Always unambiguous.
  2. **SCAN then LIFT** (within 30 s): bind the lifted pager.
  3. **LIFT then SCAN** (within 60 s): bind if exactly one lifted pager is
     unbound; if several are, ask "press the button on your pager, then scan".
  4. Web fallback: "I have pager N" for visitors / no fob.
  Binding is confirmed by a chirp + ring flash in the ball colour on the
  pager and a beep at the base.
- **Docking means different things by state:** while waiting = leave the
  queue (after a ~10 s grace period); while paged = "arrived" (turn used);
  unbound = just returned.
- **Web "join from desk"** holds a queue position until the person binds a
  pager (time limit to be decided).

## Pager enclosure and stacking (proposed)
- Looks like a pool ball: **coloured outer border** (ball colour), **white
  centre** (0.8 mm, light passes through) with the **black number**. The
  16-LED ring sits under the white centre so the face glows. **Measured
  ring: 68.2 mm OD, 53.6 mm ID** (pins DI, 5V, DO, GND). White centre about
  72-75 mm; total pager about 90-100 mm (coaster sized). Electronics and
  battery sit under the ring (the LOLIN32 doesn't fit inside 53.6 mm flat).
- Even glow: LEDs are ~12 mm apart, so allow 10 mm+ between ring and face,
  or add a diffuser layer; test-print a few gap heights.
  Number printed thick / full-depth black so it doesn't glow through.
- **Stacking:** the white centre is slightly raised; the underside has a
  matching recess, so each pager seats on the one below.
- **Orientation key:** pogo connector **off-centre in the coloured border**
  (only one rotation makes contact, so polarity is guaranteed); a **flat or
  notch** on the raised face + matching recess makes it drop in one way and
  takes the load; **magnets** beside the pogo pins pull it into place. All
  numbers in a stack face the same way.
- **Docked glow:** a docked pager lights its ring faintly in its ball colour
  (optionally slow pulse while charging, steady when battery >= ~4.15 V).
  With a **translucent border**, every pager in the stack glows, and a dark
  one shows a bad contact at or below it.
- **Button:** TTP223 touch module (active-high) in the **stacking recess on
  the underside** (the recess that keys onto the pager below). **Ignored
  while docked.**
- **Construction (proposed):** coloured **ball** body printed face down (one
  design for all pagers, printed in each ball colour) + swappable white
  **top hat** number insert: hollow crown with 0.8 mm face passes through the
  ball face and stands proud (stacking key); D-shaped brim behind the face
  sets the number upright. **Base** screws on with counterbored screws and
  carries the stacking recess + touch sensor. Fit test in
  `enclosure/ball_fit_test/`. Ball can be scaled larger than the reference
  picture; the pogo keystone goes in the solid (coloured) area.
- **Pager number is a firmware setting** (set from the web page), so a
  swapped insert needs the number updated too.

## Pickup detection with pass-through charging
- Each pager senses 5 V on its **own bottom pogo pins** (divider -> GPIO 34).
  Lifting the top pager removes 5 V only from that pager; it reports
  "lifted" over ESP-NOW. Pagers below are unaffected.
- Base handling: debounce (off dock > ~2 s); several lifted at once -> ask
  to return extras; **all** lifted at once -> dock power fault, not pickups;
  lifted with nobody waiting -> "who took pager N?".

## Pager/base messaging security
- Do not rely on ESP-NOW's built-in encryption: it is limited to 7 encrypted
  peers by default (max 17, build-time setting), and we have 8+ devices.
- Instead every message carries a **counter** (anti-replay) and a **MAC
  computed with a shared secret key** (authenticity). Messages don't need to
  be hidden, only proven genuine. Works for direct messages and broadcasts.

## Ideas from baycom/rps (proposed, not decided)
Reviewed github.com/baycom/rps (GPL-3.0, ESP32 + SX127x 433 MHz transmitter
that pages commercial restaurant pagers: LRS, POCSAG, Retekess). Ideas only;
no code copied.
- **Plan B for pagers:** buy commercial 433 MHz pagers with their own
  charging stack (e.g. Retekess) and build only the base + transmitter
  (ESP32 + SX1278). Gains: pagers and dock solved, 433 MHz goes through walls
  better. Losses: one-way (no acknowledge), no LED ring, protocols are
  reverse-engineered and change between pager models.
- **HTTP paging API** (`/page?...`) for Slack/Teams, automation and phone use.
  Ours must require authentication (rps leaves it open).
- **Wi-Fi with AP fallback:** join office Wi-Fi if configured, else run the
  base's own access point for settings.
- **Settings page** saved as JSON on flash; **factory reset** by holding a
  button for 5 s.
- **Cancel**, **page all** (e.g. "table closed") and **mute all** commands.
- **Configurable alert duration and repeat interval**, then auto-skip to the
  next person if unacknowledged.
- **Dock-based numbering:** pagers get their ID from the base while on the
  dock, so no manual pager numbers.
- **Embed web files** (`board_build.embed_txtfiles`) instead of HTML inside
  the .ino; avoids the prototype-scanner problem hit in the range test.
- **Live UI updates** via WebSocket / Server-Sent Events.
- **Ethernet (PoE) base variant** (e.g. Olimex ESP32-POE) for Slack/Teams
  without depending on Wi-Fi, if IT allows a wired port.
- **Boot self-test** showing radio / reader failure on the display.

## Hardening (cheap, planned)
- Salted hash of CSNs; authenticated ESP-NOW messages (counter + shared-key
  MAC, see "Pager/base messaging security").
- If the base later joins Wi-Fi (Slack/Teams), treat it as untrusted IoT.
  Teams needs Workflows webhooks (Office 365 connectors retired May 2026).

## Open questions
- Office range test (see `range_test/`); home POC trial done.
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
