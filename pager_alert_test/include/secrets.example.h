// Copy this file to secrets.h (same folder) and fill in your values.
// secrets.h is excluded from git by .gitignore: never commit real values.
// Without secrets.h the sketch still builds and runs, just without Wi-Fi / OTA.
#pragma once

// Wi-Fi networks to try (WPA2-Personal / shared password). The strongest one
// in range is used. Add as many lines as you like.
#define WIFI_NETWORKS { \
    {"office-network", "office-password"}, \
    {"home-network",   "home-password"}, \
}

// Name the pager uses on the network (OTA upload target: <name>.local)
#define PAGER_HOSTNAME  "pager-1"

// Password PlatformIO / Arduino IDE must give to upload over the air
#define OTA_PASSWORD    "change-me-ota"
