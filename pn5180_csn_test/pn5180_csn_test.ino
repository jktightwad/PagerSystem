// PN5180 HID iCLASS CSN read test
//
// Goal: read the same CSN that the Flipper's Picopass app shows, using only
// the anti-collision commands (no keys, no access to the SE data).
//
// Command sequence (from the Flipper Picopass app source, bettse/picopass):
//   0x0A        ACTALL    -> card answers with a bare SOF (no data)
//   0x0C        IDENTIFY  -> 8-byte anti-collision CSN + 2-byte CRC
//   0x81 + 8B   SELECT    -> 8-byte CSN + 2-byte CRC   <- the number we want
//
// The PN5180 is put in ISO 15693 mode (RF config 0x0D TX / 0x8D RX, per the
// datasheet), with its automatic 15693 CRC turned OFF because iCLASS uses a
// different CRC preset. The reply CRC is checked in software against a few
// candidate presets and the result is printed, since the exact iCLASS preset
// is not yet confirmed (the datasheet lists E012h; Picopass also uses 0xE012).
//
// Library: "PN5180" by playfultechnology (github.com/playfultechnology/PN5180)
// Install only ONE PN5180 library: ATrappmann's uses the same header name.
// Board: WEMOS LOLIN32 Lite, Arduino-ESP32 core 3.x. Serial 115200.
//
// STATUS: written, not compiled or tested.

#include <SPI.h>
#include <PN5180.h>

// Connect BOTH 5V (RF power) and 3.3V (logic) on the PN5180 board.
// SCK/MISO/MOSI are the board's default SPI pins (the library calls
// SPI.begin() with no arguments):
//   classic ESP32 / LOLIN32 Lite: SCK 18, MISO 19, MOSI 23
//   ESP32-C3 SuperMini:           SCK 4,  MISO 5,  MOSI 6
// NSS/BUSY/RST can be overridden from platformio.ini build_flags.
#ifndef PN5180_NSS
#define PN5180_NSS   5
#endif
#ifndef PN5180_BUSY
#define PN5180_BUSY  17
#endif
#ifndef PN5180_RST
#define PN5180_RST   16
#endif

// Print the full CSN (needed to compare with the Flipper). Set to 0 to show
// only the first and last byte, e.g. when pasting output somewhere public.
#define SHOW_FULL_CSN 1

#define CRC_RX_CONFIG 0x12   // datasheet Table 91
#define CRC_TX_CONFIG 0x19   // datasheet Table 98

#define CMD_ACTALL   0x0A
#define CMD_IDENTIFY 0x0C
#define CMD_SELECT   0x81

PN5180 nfc(PN5180_NSS, PN5180_BUSY, PN5180_RST);

// PN5180 registers are sent least significant byte first
static void writeRegisterAndMask(uint8_t reg, uint32_t mask) {
  uint8_t cmd[] = {PN5180_WRITE_REGISTER_AND_MASK, reg,
                   (uint8_t)(mask), (uint8_t)(mask >> 8),
                   (uint8_t)(mask >> 16), (uint8_t)(mask >> 24)};
  nfc.sendBytes(cmd, sizeof(cmd));
}

// Send raw bytes over RF and collect the reply.
// Returns the number of bytes received (0 = no reply / timeout).
static int transceive(const uint8_t *tx, size_t txLen, uint8_t *rx, size_t rxMax,
                      uint16_t timeoutMs, uint32_t *rxStatusOut) {
  nfc.clearIRQ();
  nfc.setIdle();
  nfc.activateTransceive();

  uint8_t cmd[2 + 16];
  cmd[0] = PN5180_SEND_DATA;
  cmd[1] = 0x00;  // all bits of the last byte are valid
  memcpy(cmd + 2, tx, txLen);
  nfc.sendBytes(cmd, 2 + txLen);

  uint32_t start = millis();
  while (!(nfc.readRegister(IRQ_STATUS) & RX_IRQ_STAT)) {
    if (millis() - start > timeoutMs) {
      if (rxStatusOut) *rxStatusOut = 0;
      return 0;
    }
  }

  uint32_t rxStatus = nfc.readRegister(RX_STATUS);
  if (rxStatusOut) *rxStatusOut = rxStatus;
  uint16_t len = rxStatus & 0x1FF;  // lowest 9 bits = bytes received
  if (len == 0) return 0;
  if (len > rxMax) len = rxMax;

  uint8_t rd[] = {PN5180_READ_DATA, 0x00};
  nfc.sendBytes(rd, sizeof(rd));
  nfc.readBytes(rx, len);
  return len;
}

// CRC-16, reflected polynomial 0x8408 (as used by ISO 15693), configurable
// preset and final inversion
static uint16_t crc16(const uint8_t *data, size_t len, uint16_t preset, bool invert) {
  uint16_t crc = preset;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (int b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0x8408 : (crc >> 1);
  }
  return invert ? ~crc : crc;
}

// Reports which CRC variant (if any) matches a 10-byte reply (8 data + 2 CRC)
static const char *crcMatch(const uint8_t *r) {
  uint16_t got = r[8] | (r[9] << 8);
  if (crc16(r, 8, 0xE012, false) == got) return "E012 (no invert)";
  if (crc16(r, 8, 0xE012, true) == got)  return "E012 (inverted)";
  if (crc16(r, 8, 0xFFFF, true) == got)  return "FFFF inverted (std 15693)";
  // Some readers byte-swap the stored CRC; check that too
  got = r[9] | (r[8] << 8);
  if (crc16(r, 8, 0xE012, false) == got) return "E012 (no invert, swapped)";
  return "NO MATCH";
}

static void printBytes(const uint8_t *b, int n) {
  for (int i = 0; i < n; i++) Serial.printf("%02X ", b[i]);
}

static void printCsn(const uint8_t *csn) {
#if SHOW_FULL_CSN
  printBytes(csn, 8);
#else
  Serial.printf("%02X .. .. .. .. .. .. %02X ", csn[0], csn[7]);
#endif
}

// One complete read attempt. Returns true and fills csn[8] on success.
static bool readCsn(uint8_t *csn, bool verbose) {
  uint8_t rx[16];
  uint32_t st;
  bool ok = false;

  nfc.loadISO15693config();
  if (!nfc.activateRF()) {
    Serial.printf("RF on failed. IRQ_STATUS %08lX (check the 5V supply to the PN5180)\n",
                  (unsigned long)nfc.readRegister(IRQ_STATUS));
    return false;
  }
  delay(10);  // let the card power up (Picopass uses a 10 ms guard time)

  // iCLASS CRC differs from standard 15693: disable the hardware CRC both ways
  writeRegisterAndMask(CRC_TX_CONFIG, 0xFFFFFFFE);
  writeRegisterAndMask(CRC_RX_CONFIG, 0xFFFFFFFE);

  do {
    uint8_t actall[] = {CMD_ACTALL};
    int n = transceive(actall, 1, rx, sizeof(rx), 20, &st);
    if (verbose) Serial.printf("  ACTALL   -> %d bytes, RX_STATUS %08lX\n", n, (unsigned long)st);

    uint8_t identify[] = {CMD_IDENTIFY};
    n = transceive(identify, 1, rx, sizeof(rx), 50, &st);
    if (verbose) {
      Serial.printf("  IDENTIFY -> %d bytes, RX_STATUS %08lX  ", n, (unsigned long)st);
      printBytes(rx, n);
      Serial.println();
    }
    if (n != 10) break;
    if (verbose) Serial.printf("  IDENTIFY CRC: %s\n", crcMatch(rx));

    uint8_t select[9] = {CMD_SELECT};
    memcpy(select + 1, rx, 8);  // echo the anti-collision CSN
    n = transceive(select, sizeof(select), rx, sizeof(rx), 50, &st);
    if (verbose) {
      Serial.printf("  SELECT   -> %d bytes, RX_STATUS %08lX  ", n, (unsigned long)st);
      printBytes(rx, n);
      Serial.println();
    }
    if (n != 10) break;
    if (verbose) Serial.printf("  SELECT CRC:   %s\n", crcMatch(rx));

    memcpy(csn, rx, 8);
    ok = true;
  } while (false);

  nfc.disableRF();
  return ok;
}

void setup() {
  Serial.begin(115200);
  // Boards with native USB serial (e.g. ESP32-C3 SuperMini) need the monitor
  // to connect first, or the startup messages are lost. Wait up to 5 s.
  uint32_t waitStart = millis();
  while (!Serial && millis() - waitStart < 5000) delay(10);
  delay(200);
  Serial.println("\nPN5180 iCLASS CSN test");
  Serial.printf("Pins: NSS %d, BUSY %d, RST %d, default SPI SCK %d MISO %d MOSI %d\n",
                PN5180_NSS, PN5180_BUSY, PN5180_RST, SCK, MISO, MOSI);
  pinMode(PN5180_BUSY, INPUT);
  Serial.printf("BUSY pin reads %s before reset (should be LOW when idle)\n",
                digitalRead(PN5180_BUSY) ? "HIGH" : "LOW");
  nfc.begin();
  Serial.println("PN5180 reset done");

  // Check the SPI link before anything else: the PN5180 must raise BUSY in
  // response to a command. If it doesn't, RF/card errors are meaningless.
  // Then read the version bytes from EEPROM (0x10: product, 0x12: firmware,
  // 0x14: EEPROM version, 2 bytes each; addresses as used by the ATrappmann
  // PN5180 library). All 00 or all FF means data isn't coming back on MISO.
  while (true) {
    // sendBytes() overwrites cmd with what came back on MISO while sending.
    // Per the datasheet (Fig. 8) the PN5180 answers FF FF FF during a command.
    uint8_t cmd[] = {PN5180_READ_EEPROM, 0x10, 6};
    bool ok = nfc.sendBytes(cmd, sizeof(cmd));
    uint8_t v[6] = {0};
    if (ok) ok = nfc.readBytes(v, sizeof(v));
    Serial.println();
    Serial.printf("MISO during command: %02X %02X %02X (expect FF FF FF)\n", cmd[0], cmd[1], cmd[2]);
    if (!ok) {
      Serial.println("PN5180 NOT responding over SPI (BUSY never went HIGH).");
      Serial.printf("Check: 3.3V at the module, GND, NSS -> GPIO %d, SCK -> GPIO %d, MOSI -> GPIO %d, BUSY -> GPIO %d, RST -> GPIO %d.\n",
                    PN5180_NSS, SCK, MOSI, PN5180_BUSY, PN5180_RST);
    } else {
      Serial.printf("Version bytes: %02X %02X %02X %02X %02X %02X\n", v[0], v[1], v[2], v[3], v[4], v[5]);
      bool allZero = true, allFF = true;
      for (uint8_t b : v) {
        if (b != 0x00) allZero = false;
        if (b != 0xFF) allFF = false;
      }
      if (!allZero && !allFF) {
        Serial.printf("SPI link OK: product v%d.%d, firmware v%d.%d. Starting reads.\n",
                      v[1], v[0], v[3], v[2]);
        break;
      }
      Serial.println("Commands reach the PN5180 (BUSY works) but replies are all 00 or FF:");
      Serial.printf("check MISO (PN5180 MISO -> GPIO %d) and MOSI (PN5180 MOSI -> GPIO %d), SCK -> GPIO %d.\n",
                    MISO, MOSI, SCK);
    }
    Serial.println("Retrying in 3 s...");
    delay(3000);
    nfc.hardReset();
  }
  Serial.println("Commands: v = toggle verbose, i = try standard ISO 15693 inventory (wiring check)");
}

void loop() {
  static bool verbose = true;
  static uint8_t lastCsn[8];
  static bool haveLast = false;
  static uint32_t sameCount = 0;

  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'v') {
      verbose = !verbose;
      Serial.printf("verbose %s\n", verbose ? "on" : "off");
    } else if (c == 'i') {
      // Standard 15693 tags answer this; iCLASS fobs are expected NOT to
      uint8_t uid[8];
      if (nfc.getInventory(uid)) {
        Serial.print("ISO 15693 tag UID: ");
        for (int i = 7; i >= 0; i--) Serial.printf("%02X", uid[i]);
        Serial.println();
      } else {
        Serial.println("No ISO 15693 tag (expected for iCLASS)");
      }
    }
  }

  uint8_t csn[8];
  if (readCsn(csn, verbose)) {
    bool same = haveLast && memcmp(csn, lastCsn, 8) == 0;
    sameCount = same ? sameCount + 1 : 1;
    memcpy(lastCsn, csn, 8);
    haveLast = true;
    Serial.print("CSN: ");
    printCsn(csn);
    Serial.printf(" %s (read %lu times in a row)\n", same ? "same" : "NEW", (unsigned long)sameCount);
  } else if (verbose) {
    Serial.println("no card");
  }
  delay(1000);
}
