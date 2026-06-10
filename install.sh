#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_SCRIPT="$SCRIPT_DIR/ram_menubar.py"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
# The venv symlinks resolve to Homebrew's framework Python (bin/python3.14).
# Only Python.app/Contents/MacOS/Python can show macOS GUI (menu-bar status items).
# Use realpath to resolve .venv/bin/python3 -> actual Homebrew binary, then find Python.app.
GUI_PYTHON="$("$VENV_PYTHON" -c "
import sys, os, itertools
p = os.path.realpath(sys.executable)   # resolve .venv symlink to actual binary
parts = p.split(os.sep)
for i in range(len(parts), 0, -1):
    c = os.sep.join(parts[:i] + ['Resources', 'Python.app', 'Contents', 'MacOS', 'Python'])
    if os.path.exists(c):
        print(c)
        break
else:
    print(p)
")"
VENV_SITE="$("$VENV_PYTHON" -c "import sysconfig; print(sysconfig.get_path('purelib'))")"
PLIST_LABEL="com.pnz.ram-menubar"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_OUT="$HOME/Library/Logs/ram-menubar.log"
LOG_ERR="$HOME/Library/Logs/ram-menubar-err.log"

echo "PNZ RAM Monitor Installer"

SYSTEM_PYTHON=$(command -v python3 2>/dev/null || true)
if [[ -z "$SYSTEM_PYTHON" ]]; then
    echo "python3 not found. Install via: brew install python"
    exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at $VENV_DIR..."
    $SYSTEM_PYTHON -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_PYTHON" -m pip install --quiet --upgrade pip
"$VENV_PYTHON" -m pip install --quiet --upgrade rumps psutil

if [[ -f "$PLIST_PATH" ]]; then
    launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true
fi

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${GUI_PYTHON}</string>
    <string>${APP_SCRIPT}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ProcessType</key>
  <string>Interactive</string>
  <key>LimitLoadToSessionType</key>
  <string>Aqua</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${VENV_SITE}</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_OUT}</string>
  <key>StandardErrorPath</key>
  <string>${LOG_ERR}</string>
</dict>
</plist>
PLIST

launchctl bootstrap gui/$(id -u) "$PLIST_PATH"
echo "RAM Monitor is now running."
