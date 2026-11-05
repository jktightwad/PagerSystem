# ESP-NOW range test

**Status: written but not yet compiled or tested.**

- **Base** (`range_base/`): stays where the real base will go. Currently the
  ESP32-C3 SuperMini (`env:esp32c3_supermini`), powered by a USB charger.
- **Walker** (`range_test/range_walker/`): a LOLIN32 Lite (`env:lolin32_lite`)
  carried around, powered by a LiPo or USB power bank. **No laptop needed**:
  it runs its own Wi-Fi hotspot with a live results page for your phone.

Both sketches must use the same `CHANNEL` and `USE_LR_MODE` values.

## Setup
1. Open `range_test/range_base` in PlatformIO, select `env:esp32c3_supermini`,
   Clean, Upload.
2. Open `range_test/range_walker`, select `env:lolin32_lite`, Clean, Upload.
3. Power both. On your phone, join Wi-Fi **PoolPager-Range** (password
   **pooltable**) and open **http://192.168.4.1**. Your phone may warn that
   the network has no internet; stay connected anyway.
4. With both boards side by side the page should show ~100% (green).

The walker's onboard LED stays lit while the base is answering. The base LED
flashes once per ping it hears.

## Procedure
1. Base at its real location, ideally raised (shelf/wall height).
2. At each test spot: **stand still ~15 s**, type a spot name, tap **Record**.
3. Include the farthest desks, spots behind walls, kitchen/meeting rooms.
4. Repeat the worst spots with `USE_LR_MODE 1` in **both** sketches.
5. Optional: repeat with another `CHANNEL` (e.g. 6 or 11) on **both**, in case
   office Wi-Fi is busy on channel 1.
6. Tap **Download results (CSV)** and send the file (or a screenshot).

Results are kept in memory only: they're lost if the walker resets or its
battery dies, so download before switching it off.

Loss shown is raw (no retries). The real system retries until acknowledged,
so occasional loss is fine; long runs of NO CONTACT are not. The phone's own
Wi-Fi traffic to the walker shares the channel, so results err on the
cautious side.

| Answered | RSSI | Meaning |
|---|---|---|
| ~100% | above -70 | Solid |
| 90-100% | -70 to -80 | Fine (retries cover it) |
| below ~80% or NO CONTACT | below about -85 | Unreliable spot |

The SuperMini has a small onboard antenna. If results are poor, repeat with a
LOLIN32 as the base before blaming ESP-NOW.
