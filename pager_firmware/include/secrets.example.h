// Copy this file to secrets.h (same folder) and fill in your values.
// secrets.h is excluded from git by .gitignore: never commit real values.
// Without secrets.h the pager still works: it opens the PoolPager-Setup
// hotspot to choose a network, and its page has no password.
#pragma once

// Wi-Fi networks to try, besides the ones the pager has joined before (every
// network it joins, including through the PoolPager-Setup hotspot, is saved
// on the pager). The strongest one in range is used.
#define WIFI_NETWORKS { \
    {"office-network", "office-password"}, \
    {"home-network",   "home-password"}, \
}

// Login for the pager's web page, its /update page and OTA uploads
#define ADMIN_USER      "admin"
#define ADMIN_PASSWORD  "change-me-admin"
#define OTA_PASSWORD    "change-me-ota"
