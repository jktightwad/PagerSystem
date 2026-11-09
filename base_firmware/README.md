# Base firmware (proof of concept)

PlatformIO project for the pool pager base. **Step 1: network** (joins the
office Wi-Fi from a list in `secrets.h`, falls back to its own hotspot,
serves a status page). Queue, badge reader and pager radio come next.

**Status: written, not compiled or tested.**

## Secrets
Same pattern as the Desktop Notifier:
1. Copy `include/secrets.example.h` to `include/secrets.h`.
2. Fill in the office SSID and shared password (`WIFI_NETWORKS`; several
   networks allowed, strongest in range wins), and change every
   `change-me` / `replace-with` value.
3. `include/secrets.h` is in `.gitignore`: it never goes to GitHub.

## Build
Open this folder in PlatformIO. Environments:
- `esp32c3_supermini_alt_spi` (default): SuperMini base, PN5180 MISO 0 /
  MOSI 1 / SCK 4 / NSS 7 / BUSY 3 / RST 10.
- `lolin32_lite`: LOLIN32 Lite as the base.

The serial monitor shows which network it joined and its IP address. Open
`http://<that IP>/` from a PC or phone on the same network.

Note: the office access point sets the Wi-Fi channel. Once the pager radio
is added, the pagers either follow that channel or a separate radio-bridge
ESP32 is used (see `docs/design.md`).
