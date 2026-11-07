# Test plan (draft)

Behaviour under test is the **proposed** design in `docs/design.md`
("Players, pagers and pairing", "Pickup detection", "Web-first UI").
Where the expected result is a guess at what you'll want, it's marked
**(confirm)**; open questions are collected at the end.

Terms: **SCAN** = fob tapped at the base, **LIFT** = pager leaves the dock,
**DOCK** = pager placed back, **CLAIM** = button pressed on a lifted pager,
**ACK** = button pressed on a paging pager. Timings (30 s / 60 s / 10 s /
2 s) are starting values to tune.

Result column: P = pass, F = fail (note what happened), - = not run.

## 1. Binding a pager to a person

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| B01 | Registered fob, all pagers docked | SCAN, then LIFT pager 3 within 30 s | Pager 3 bound to the fob owner; pager chirps + ring flashes its ball colour; base beeps; web shows name next to pager 3 | |
| B02 | Same | LIFT pager 3, then SCAN within 60 s | Same as B01 | |
| B03 | Same | LIFT pager 3, press CLAIM, then SCAN | Same as B01 | |
| B04 | Same | SCAN, wait 31 s, then LIFT | No bind; pager 3 shows as "unbound" on the web; next SCAN within 60 s binds it | |
| B05 | Same | LIFT, wait 61 s, then SCAN | No bind; base says "press the button on your pager, then scan" (or treat as a new SCAN waiting for a lift) **(confirm)** | |
| B06 | Two pagers lifted (3 and 5), both unbound | SCAN | Not bound; base asks to press the pager button then scan | |
| B07 | Two pagers lifted, both unbound | CLAIM on 5, then SCAN | Pager 5 bound; pager 3 still unbound | |
| B08 | Two people | Person A SCAN, person B SCAN, then one pager LIFT | Ambiguous: bind to... **(confirm: most recent scan, or ask both to CLAIM?)** | |
| B09 | Person A SCAN | Person A LIFTs two pagers (picks up 2 from top of stack) | One bound, the other flagged "please return pager N" | |
| B10 | Pager 3 bound to A | A SCANs again | Base shows "you already have pager 3" (no second bind) | |
| B11 | Pager 3 bound to A | B presses CLAIM on pager 3 and SCANs | Rejected or re-bound to B **(confirm)**; event logged | |
| B12 | Unregistered fob | SCAN then LIFT | Registration prompt on the web ("new fob, enter name"); pager held for it for ~2 min **(confirm)** | |
| B13 | No fob (visitor) | LIFT pager 6, choose "I have pager 6" on the web, enter name | Pager 6 bound to that name | |
| B14 | Pager 3 bound | CLAIM pressed again with no SCAN | No change; pager shows its ball colour (bound) | |
| B15 | CLAIM pressed | No SCAN within 30 s | Claim expires; pager gives a short "timed out" pattern | |
| B16 | SCAN | Fob read twice by accident (held on the reader) | Counted as one scan | |
| B17 | Any | Fob held at the edge of range (flaky read) | Either a clean read or nothing; never a wrong CSN | |
| B18 | Two fobs on the reader at once | SCAN | Read one or neither; no crash **(confirm)** | |

## 2. Queue and paging

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| Q01 | Empty queue | A binds a pager | A is #1 in the queue | |
| Q02 | A, B, C, D, E waiting (in that order) | "Next game: 2" | A and B paged; C, D, E move up | |
| Q03 | Same | "Next game: 4" | A, B, C, D paged | |
| Q04 | Only 2 waiting | "Next game: 4" | Both paged; base/web says only 2 available **(confirm)** | |
| Q05 | Empty queue | "Next game" | Nothing paged; message "queue empty" | |
| Q06 | A paged | A presses ACK | Pager stops alerting, green confirmation; web shows "A on the way" | |
| Q07 | A paged | No ACK within the timeout | A skipped; next waiting person paged; A **(confirm: removed / moved back one / kept at front as "missed")** | |
| Q08 | A paged, ACKed | A DOCKs pager at the table | A marked arrived; pager unbound | |
| Q09 | A paged, not ACKed | A DOCKs pager at the table | Counts as arrived (ACK implied) | |
| Q10 | A waiting (not paged) | A DOCKs pager | After ~10 s grace, A leaves the queue | |
| Q11 | A waiting | A DOCKs and LIFTs again within 10 s | A keeps their place | |
| Q12 | A paged | Alert runs past 30 s | Alert escalates (faster, brighter) | |
| Q13 | A paged | Cancel from the web | Pager stops; A returns to... **(confirm)** | |
| Q14 | Several waiting | Admin "page all" | Every bound pager alerts with the announcement pattern | |
| Q15 | Several waiting | Admin "mute all" | Beeper and vibration off on all pagers; lights still work **(confirm)** | |
| Q16 | A waiting | A removes themselves on the web | A leaves the queue; pager shows "return me" pattern **(confirm)** | |
| Q17 | Web "join from desk" | Person never picks up a pager | Reservation expires after the time limit **(confirm limit)** | |
| Q18 | Web "join from desk" | Person arrives, SCAN + LIFT | Bound and keeps original queue position | |
| Q19 | Game in progress | "Next game" pressed twice by accident | Second press ignored or asks to confirm | |
| Q20 | 8 people bound | Person 9 SCANs | "No pagers available"; offer web-only queue place **(confirm)** | |

## 3. Docking, charging and pickup detection

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| D01 | Stack of 4 on the dock | LIFT the top pager | Only that pager reports LIFT | |
| D02 | Same | Lift the top 2 together | Both report LIFT; base asks to return the extra | |
| D03 | Same | Pager wobbles off contact for < 2 s | No LIFT reported | |
| D04 | Same | Dock power unplugged | All pagers report LIFT together; base flags "dock power fault", not pickups | |
| D05 | Dock power restored | | All report DOCK; state returns to normal | |
| D06 | Pager docked | Battery charging | Board charge LED on; web shows "charging" | |
| D07 | Full stack of 8 charging | All batteries low | Every pager charges; measure voltage at the top pager's input (must stay above ~4.3 V) | |
| D08 | Pager docked upside down / rotated | | Can't make contact (keyed shape) or no damage (polarity protection) | |
| D09 | Pager lifted | Battery low | Low-battery warning on pager and web | |
| D10 | Pager left off the dock | More than N hours | Web flags "pager N not returned" | |
| D11 | Pager taken out of radio range | | Base shows "pager N not responding" after its heartbeat is missed | |

## 4. Radio and reliability

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| R01 | Pager at the farthest desk | Paged | Alert arrives within ~2 s | |
| R02 | Pager out of range | Paged | Base retries; marks undelivered; pages the next person after the timeout | |
| R03 | Pager comes back into range while paged | | Alert delivered late but still works | |
| R04 | Base reboots | | Pagers and queue state recovered (queue kept in flash) **(confirm)** | |
| R05 | Pager reboots while bound | | Binding kept (base is the source of truth) | |
| R06 | Radio bridge unplugged | | Web shows "pager radio offline" | |
| R07 | Office Wi-Fi down | | Pagers keep working (ESP-NOW is independent); web unavailable; local base feedback still works | |
| R08 | Office AP changes channel | | Base reconnects; pager radio unaffected (separate bridge) | |
| R09 | Two messages in quick succession | | Both handled in order | |

## 5. Web page

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| W01 | Browser on office network | Open the base address | Queue, pager status, buttons visible | |
| W02 | Register | Press Register, tap fob within 30 s, enter name | Profile created; one-time code links this browser | |
| W03 | Register | No fob within 30 s | Times out cleanly | |
| W04 | Browser linked to A | A tries to remove B from the queue | Refused | |
| W05 | Unlinked browser | Tries to change a reservation | Refused | |
| W06 | Admin | Wrong admin password | Refused; repeated attempts slowed down | |
| W07 | 10+ browsers open | All polling | Base stays responsive | |
| W08 | Phone and desktop | | Layout works at phone width | |
| W09 | Kiosk tablet at the table | Left on the page for a day | Still updating | |

## 6. Security (pen test prep)

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| S01 | Recorded ESP-NOW "ACK" message | Replayed | Rejected (counter) | |
| S02 | Forged ESP-NOW message without the key | Sent | Rejected (MAC check) | |
| S03 | Flipper emulating a registered fob's CSN | Scanned | Accepted (known limitation: CSN is not secret). Documented, low impact | |
| S04 | Base flash dumped | | Only hashed CSNs found | |
| S05 | OTA upload without the password | | Refused | |
| S06 | Unsigned / modified firmware via OTA | | Refused once signing is added | |
| S07 | Web API called directly (no browser) | Without auth | Refused for anything but read-only status | |
| S08 | Serial port on the base | Connected | No secrets printed | |

## 7. OTA updates

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| O01 | Pager docked, idle, older version | New version uploaded to base | Pager updates, reboots, reports new version | |
| O02 | Pager bound / in the queue | New version available | Waits until docked and unbound | |
| O03 | Download interrupted (pager lifted) | | Old firmware keeps running; retries later | |
| O04 | Corrupt file uploaded | | Rejected by the base (not an ESP32 image) or by the pager (MD5) | |
| O05 | Several pagers need updating | | One at a time | |
| O06 | Older version uploaded | | Pagers roll back (versions differ) | |

## 8. Power and battery

| ID | Given | When | Expected | Result |
|---|---|---|---|---|
| P01 | Full battery | Off the dock, normal use | Lasts a full working day (measure) | |
| P02 | Long alert at full brightness | | No brown-out / reboot (motor + LEDs + radio together) | |
| P03 | Battery almost empty | | Low-battery warning before it shuts down; ring colours dim | |
| P04 | Pager left off overnight | | Measure remaining charge | |

## Open questions raised by these tests
1. B05 / B08: what to do when a scan and a pickup can't be matched cleanly?
2. B11: can a bound pager be re-claimed by someone else?
3. B12: hold a pager for an unregistered fob while they register?
4. Q04: page fewer players than asked if the queue is short?
5. Q07: what happens to someone who misses their page?
6. Q13 / Q16: cancelled or self-removed: back in the queue or out?
7. Q15: does "mute all" keep the lights on?
8. Q17: how long does a web reservation wait for the person to pick up?
9. Q20: queue place without a pager when all 8 are out?
10. R04: must the queue survive a base reboot?
