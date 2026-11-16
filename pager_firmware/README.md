# Pager firmware (POC)

PlatformIO project for the LOLIN32 Lite pager. **Written, not yet compiled or
tested.** `pager_alert_test/` stays as the bench test sketch.

## First upload (USB)
1. Copy `include/secrets.example.h` to `include/secrets.h` and fill it in
   (Wi-Fi networks, web page login, OTA password). Optional: without it the
   pager opens the setup hotspot and its page has no password.
2. Upload the `lolin32_lite` environment over USB. This firmware uses its own
   partition table (OTA + a small LittleFS area), so the first upload replaces
   whatever layout was on the board.

## Wi-Fi (same scheme as the desktop notifier light)
- Tries networks it has joined before (saved on the pager) and the ones in
  `secrets.h`, strongest first. The ring shows dim blue while scanning,
  orange while joining.
- If none connects: open hotspot **PoolPager-Setup** for 5 min (ring
  purple). Join it from a phone and pick the network.
- Once connected: for 60 s a hotspot named **PoolPager-<ip>** (e.g.
  `PoolPager-192-168-1-87`) shows the IP in a phone's Wi-Fi list; the ring
  blinks purple. Serial monitor: type `i`.
- Hold the touch pad for 5 s while powering up to forget saved networks.

## Boot lights (as the desktop notifier light)
Blue progress bar while scanning, orange while joining a network, steady
purple (middle 6 LEDs) while the setup hotspot is up, a green flash when
joined through it, then a middle-6 purple blink for up to 60 s while the
PoolPager-<ip> hotspot shows the IP. Wi-Fi connects in the background, so the
pager works straight away: a touch, a serial command, docking / lifting, or
(once connected) opening the page or any page action takes the ring over from
the boot lights. The page is available once Wi-Fi is connected (during the
setup hotspot the hotspot's own page is used instead).

Docking or lifting always switches to Docked / Lifted (stops demo and light
modes); only the self test isn't interrupted.

## Touch pad
- **1 tap:** light on in the last light mode (not while reserved: confirm /
  waiting / your turn / acknowledged). During "your turn" a tap acknowledges.
- **2 taps:** next light mode (solid, blink, party, knight rider, breathe,
  comet, rainbow, pulse).
- **3 taps within 3 s:** everything off: lights, buzzer, motor, demo mode.
  (For now this also drops a reservation state; the real queue firmware will
  need to keep the reservation.)

## The pager's page: `http://<ip>/` (or `http://<name>.local/`)
- Status, refreshed every second: state, battery, dock, touch pad, Wi-Fi
  network / IP / signal, base link (not available until the base talks
  ESP-NOW), firmware, uptime.
- Pager states: docked, lifted, confirm, waiting, your turn, acknowledge,
  and **demo mode** (cycles through them).
- Light modes as the notifier: solid, blink, party, knight rider, breathe,
  comet, rainbow, pulse, off, with colour picker, brightness and speed
  (saved on the pager).
- Colour tests: pool ball colours 1-8 and a few basics (shown solid).
- Tests: self test (all outputs), ring colours, LED chase, beep, beeper
  on/off (for a meter), vibrate, identify.
- Admin: rename (used as the network name after a reboot), firmware update
  (`/update`, upload a `.bin`), forget Wi-Fi, reboot.
- Login: `ADMIN_USER` / `ADMIN_PASSWORD` from `secrets.h`.

## Later uploads over Wi-Fi
- Browser: `http://<ip>/update`, upload `.pio/build/lolin32_lite/firmware.bin`.
- PlatformIO: set `upload_port` in `platformio.ini` to the pager's IP, set the
  `PAGER_OTA_PASSWORD` environment variable, then
  `pio run -e lolin32_lite_ota -t upload`.

Pins: `docs/pager_wiring.md` (ring 26, buzzer 27, motor 25, touch 4,
dock 34, battery 35).
