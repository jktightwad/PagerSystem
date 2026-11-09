// Copy this file to secrets.h (same folder) and fill in your values.
// secrets.h is excluded from git by .gitignore: never commit real values.
#pragma once

// Wi-Fi networks to try (shared-password / WPA2-Personal networks). The
// strongest one in range is used. Add as many lines as you like.
#define WIFI_NETWORKS { \
    {"office-network", "office-password"}, \
    {"home-network",   "home-password"}, \
}

// Base's own hotspot, used for setup when no listed network is in range.
// Password must be at least 8 characters.
#define FALLBACK_AP_SSID  "PoolPager-Base"
#define FALLBACK_AP_PASS  "change-me-please"

// Name the base answers to on the network (http://<name>.local where mDNS works)
#define BASE_HOSTNAME     "poolpager"

// Admin password for settings, page all, mute all
#define ADMIN_PASSWORD    "change-me-admin"

// Password the pagers use to fetch firmware updates from the base
#define OTA_PASSWORD      "change-me-ota"

// Shared key that signs every pager <-> base message (any long random text,
// identical on the base and every pager)
#define PAGER_LINK_KEY    "replace-with-32-or-more-random-characters"

// Salt for hashing badge serial numbers before they are stored (any long
// random text; changing it later invalidates registered badges)
#define BADGE_HASH_SALT   "replace-with-another-long-random-string"
