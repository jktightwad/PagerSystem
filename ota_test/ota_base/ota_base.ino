// OTA proof of concept - BASE side
//
// Runs a password-protected Wi-Fi access point (no office Wi-Fi involved) and
// holds the current pager firmware:
//   GET  /            upload page (use a phone/laptop joined to the AP)
//   POST /upload      upload pager.bin + its version number
//   GET  /version     current pager firmware version (plain text)
//   GET  /pager.bin   the firmware, with an x-MD5 header so the pager can
//                     verify the download before switching to it
//
// In the real base, the version is also broadcast over ESP-NOW and the AP is
// only switched on while a docked pager is updating.
//
// Board: any ESP32 (CYD later). Arduino-ESP32 core 3.x.
// Tools -> Partition Scheme: one with a large filesystem, e.g.
// "Default 4MB with spiffs" (LittleFS uses that partition). Serial 115200.
//
// STATUS: written, not compiled or tested.

#include <WiFi.h>
#include <WebServer.h>
#include <LittleFS.h>
#include <MD5Builder.h>

#define AP_SSID     "PoolPager-OTA"
#define AP_PASS     "change-me-please"   // WPA2, at least 8 characters
#define AP_CHANNEL  1                    // must match the ESP-NOW channel later

WebServer server(80);

static File uploadFile;
static MD5Builder uploadMd5;
static size_t uploadSize = 0;

static String readText(const char *path) {
  File f = LittleFS.open(path, "r");
  if (!f) return "";
  String s = f.readString();
  f.close();
  s.trim();
  return s;
}

static void writeText(const char *path, const String &s) {
  File f = LittleFS.open(path, "w");
  if (f) {
    f.print(s);
    f.close();
  }
}

static void handleRoot() {
  String page =
    "<!doctype html><meta name=viewport content='width=device-width'>"
    "<h2>Pool pager firmware</h2>"
    "<p>Current version: <b>" + readText("/version.txt") + "</b><br>"
    "MD5: " + readText("/pager.md5") + "</p>"
    "<form method=POST action=/upload enctype=multipart/form-data>"
    "<p>New version number: <input name=version type=number min=1 required></p>"
    "<p>Firmware (.bin): <input name=fw type=file accept=.bin required></p>"
    "<p><button>Upload</button></p></form>"
    "<p>Pagers on the dock will update when they see a different version.</p>";
  server.send(200, "text/html", page);
}

// Called repeatedly while the file streams in
static void handleUploadData() {
  HTTPUpload &up = server.upload();
  if (up.status == UPLOAD_FILE_START) {
    uploadFile = LittleFS.open("/pager.tmp", "w");
    uploadMd5.begin();
    uploadSize = 0;
    Serial.printf("Upload start: %s\n", up.filename.c_str());
  } else if (up.status == UPLOAD_FILE_WRITE) {
    if (uploadFile) uploadFile.write(up.buf, up.currentSize);
    uploadMd5.add(up.buf, up.currentSize);
    uploadSize += up.currentSize;
  } else if (up.status == UPLOAD_FILE_END) {
    if (uploadFile) uploadFile.close();
    uploadMd5.calculate();
    Serial.printf("Upload end: %u bytes\n", (unsigned)uploadSize);
  } else if (up.status == UPLOAD_FILE_ABORTED) {
    if (uploadFile) uploadFile.close();
    LittleFS.remove("/pager.tmp");
    uploadSize = 0;
  }
}

// Called once after the upload completes
static void handleUploadDone() {
  String version = server.arg("version");
  // An ESP32 app image starts with magic byte 0xE9; reject anything else
  File f = LittleFS.open("/pager.tmp", "r");
  int first = f ? f.read() : -1;
  if (f) f.close();

  if (uploadSize == 0 || first != 0xE9 || version.toInt() <= 0) {
    LittleFS.remove("/pager.tmp");
    server.send(400, "text/plain", "Rejected: not an ESP32 firmware image, or no version number");
    return;
  }
  LittleFS.remove("/pager.bin");
  LittleFS.rename("/pager.tmp", "/pager.bin");
  writeText("/pager.md5", uploadMd5.toString());
  writeText("/version.txt", version);
  Serial.printf("Stored pager firmware v%s, MD5 %s\n", version.c_str(), uploadMd5.toString().c_str());
  server.sendHeader("Location", "/");
  server.send(303);
}

static void handleVersion() {
  server.send(200, "text/plain", readText("/version.txt"));
}

static void handleFirmware() {
  File f = LittleFS.open("/pager.bin", "r");
  if (!f) {
    server.send(404, "text/plain", "no firmware stored");
    return;
  }
  Serial.printf("Serving firmware to %s\n", server.client().remoteIP().toString().c_str());
  server.sendHeader("x-MD5", readText("/pager.md5"));  // HTTPUpdate verifies this
  server.streamFile(f, "application/octet-stream");
  f.close();
}

void setup() {
  Serial.begin(115200);
  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS mount failed");
    while (true) delay(1000);
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS, AP_CHANNEL);
  Serial.printf("\nOTA base: AP \"%s\" at %s, channel %d\n", AP_SSID,
                WiFi.softAPIP().toString().c_str(), AP_CHANNEL);
  Serial.printf("Stored pager firmware: v%s\n", readText("/version.txt").c_str());

  server.on("/", HTTP_GET, handleRoot);
  server.on("/upload", HTTP_POST, handleUploadDone, handleUploadData);
  server.on("/version", HTTP_GET, handleVersion);
  server.on("/pager.bin", HTTP_GET, handleFirmware);
  server.begin();
}

void loop() {
  server.handleClient();
}
