# ESP-NOW range test

Two LOLIN32 Lite boards. **Status: written but not yet compiled or tested.**

## Setup
1. Arduino IDE → Boards Manager → install **esp32 by Espressif, version 3.x**.
2. Board: **WEMOS LOLIN32 Lite**. If the IDE can't find the port, the board's
   USB chip may need a driver (CH340 on many LOLIN32 Lite boards; check yours).
3. Flash `range_base` to board A, `range_walker` to board B.
4. Board A: USB charger at the pool table, ideally raised (shelf/wall height).
5. Board B: laptop, Serial Monitor at **115200**.

The onboard LED on the walker stays lit while the base is answering. The base
LED flashes once per ping it hears.

## Procedure
1. Start next to the base and confirm ~100% answered.
2. Walk to each test spot, **stand still ~15 s** (3 report lines), note results.
3. Include the farthest desks, spots behind walls, kitchen/meeting rooms.
4. Repeat the worst spots with **USE_LR_MODE 1** on **both** boards.
5. Optional: repeat with a different **CHANNEL** (e.g. 6 or 11) on both boards,
   in case office Wi-Fi is busy on channel 1.

Loss shown is raw (no retries). The real system retries until acknowledged,
so occasional loss is fine; long runs of "NO CONTACT" are not.

## Results

| Spot | Distance (approx) | Walls/obstacles | Answered % | RSSI walker avg/min | RSSI base avg/min | LR mode |
|---|---|---|---|---|---|---|
| | | | | | | |
