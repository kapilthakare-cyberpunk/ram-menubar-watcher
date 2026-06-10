#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  uninstall.sh  —  PNZ RAM Monitor uninstaller
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PLIST_LABEL="com.pnz.ram-menubar"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

echo ""
echo "→  Unloading LaunchAgent…"
launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true

echo "→  Removing plist…"
rm -f "$PLIST_PATH"

echo ""
echo "✅  PNZ RAM Monitor uninstalled."
echo "   (Script files kept at $(dirname "${BASH_SOURCE[0]}") — delete manually if needed.)"
echo ""
