# PNZ RAM Monitor

A lightweight macOS menu bar application that shows live RAM usage at a glance and lists memory-intensive processes. 

Built specifically to support macOS 26+ (Tahoe) via **SwiftBar**.

```
RAM 68%   ← appears in your menu bar, updates every 5 seconds
```

Clicking the title opens a dropdown displaying:
- Used memory / Total memory and percentage
- Swap usage
- Top 5 processes by RAM consumption
- Click-to-kill option on each process to terminate memory-hogging processes immediately.

---

## Requirements

- **macOS:** macOS 10.15 Catalina or later (Fully supports macOS 26 Tahoe)
- **SwiftBar:** Installed via Homebrew cask: `brew install --cask swiftbar`
- **Python:** Python 3.10+ installed via Homebrew or standard system installation

---

## Install

1. Clone or copy the folder:
   ```bash
   git clone git@github.com:kapilthakare-cyberpunk/ram-menubar-watcher.git
   cd ram-menubar-watcher
   ```

2. Run the installer:
   ```bash
   ./install.sh
   ```

The installer will:
- Clean up legacy LaunchAgent plist and Applications bundle configurations.
- Verify and install SwiftBar via Homebrew Cask if missing.
- Set up a project-local virtual environment (`.venv/`) and install Python dependencies (`psutil`).
- Make the plugin script `plugins/ram.5s.py` executable.

---

## Configuration

### 1. Launch SwiftBar
Start SwiftBar from your Applications folder, or run:
```bash
open -a SwiftBar
```

### 2. Set Plugin Directory
When prompted, select the plugins folder in this repository:
```text
/Users/kapilthakare/scripts/ram-menubar/plugins
```

If you already have a configured SwiftBar plugin directory, you can instead create a symbolic link to our plugin script inside it:
```bash
ln -s "$(pwd)/plugins/ram.5s.py" "/YOUR/EXISTING/PLUGINS/DIR/ram.5s.py"
```

### 3. Change Refresh Interval / Settings
To adjust settings, edit the config constants at the top of [plugins/ram.5s.py](file:///Users/kapilthakare/scripts/ram-menubar/plugins/ram.5s.py):
```python
# Configuration
WARN_THRESHOLD = 60   # % -> yellow warning in menu bar
CRIT_THRESHOLD = 80   # % -> red warning in menu bar
TOP_N          = 5    # number of processes shown
```
To change the refresh interval, rename the file to reflect the new interval (e.g. rename to `ram.10s.py` for a 10-second refresh interval).

---

## Uninstall

To remove legacy elements and configurations:
```bash
./uninstall.sh
```

To uninstall SwiftBar completely:
```bash
brew uninstall --cask swiftbar
```

---

## Project Structure

```text
ram-menubar/
├── plugins/
│   └── ram.5s.py    # SwiftBar plugin script (uses psutil from .venv)
├── install.sh       # One-shot installer (venv setup, legacy cleanup, cask install)
├── uninstall.sh     # Teardown legacy configurations
├── ram_menubar.py   # Legacy rumps script (preserved for reference)
└── README.md        # This file
```
